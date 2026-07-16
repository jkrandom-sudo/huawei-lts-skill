#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import time
from pathlib import Path
from typing import Any


SERVER_NAME = "huawei-lts"
PLACEHOLDER_ENV = {
    "HUAWEI_ACCESS_KEY": "REPLACE_WITH_YOUR_AK",
    "HUAWEI_SECRET_KEY": "REPLACE_WITH_YOUR_SK",
    "HUAWEI_REGION": "REPLACE_WITH_YOUR_REGION",
    "HUAWEI_PROJECT_ID": "REPLACE_WITH_YOUR_PROJECT_ID",
}
VALID_PLATFORMS = {"cursor", "claude", "opencode", "codex"}


class InstallError(RuntimeError):
    pass


def _backup(path: Path) -> None:
    stamp = time.strftime("%Y%m%d%H%M%S") + f".{time.time_ns() % 1_000_000_000:09d}"
    shutil.copy2(path, path.with_name(path.name + f".bak.{stamp}"))


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise InstallError(f"Cannot parse JSON config: {path}") from error
    if not isinstance(value, dict):
        raise InstallError(f"JSON config root must be an object: {path}")
    return value


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        _backup(path)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _stdio_entry(command: str) -> dict[str, Any]:
    return {"command": command, "args": [], "env": dict(PLACEHOLDER_ENV)}


def _load_state(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {"version": 1, "platforms": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def _save_state(path: Path | None, state: dict[str, Any]) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
        stream.write(json.dumps(state, ensure_ascii=False, indent=2) + "\n")
    os.replace(temporary, path)
    os.chmod(path, 0o600)


def _capture_json_entry(path: Path, root_key: str) -> dict[str, Any]:
    data = _load_json(path)
    servers = data.get(root_key)
    entry = servers.get(SERVER_NAME) if isinstance(servers, dict) else None
    return {"kind": "json", "path": str(path), "root_key": root_key, "entry": entry}


def _merge_mcp_servers(path: Path, command: str) -> None:
    data = _load_json(path)
    servers = data.setdefault("mcpServers", {})
    if not isinstance(servers, dict):
        raise InstallError(f"mcpServers must be an object: {path}")
    servers[SERVER_NAME] = _stdio_entry(command)
    _write_json(path, data)


def _merge_opencode(path: Path, command: str) -> None:
    data = _load_json(path)
    data.setdefault("$schema", "https://opencode.ai/config.json")
    servers = data.setdefault("mcp", {})
    if not isinstance(servers, dict):
        raise InstallError(f"mcp must be an object: {path}")
    servers[SERVER_NAME] = {
        "type": "local",
        "command": [command],
        "enabled": True,
        "environment": dict(PLACEHOLDER_ENV),
    }
    _write_json(path, data)


CODEX_BLOCK = re.compile(
    r"(?ms)^\[mcp_servers\.huawei-lts\]\n.*?(?=^\[(?!mcp_servers\.huawei-lts\.env\])|\Z)"
)


def _codex_block(command: str) -> str:
    quoted = json.dumps(command)
    lines = [
        "[mcp_servers.huawei-lts]",
        f"command = {quoted}",
        "args = []",
        "enabled = true",
        "",
        "[mcp_servers.huawei-lts.env]",
    ]
    lines.extend(f"{key} = {json.dumps(value)}" for key, value in PLACEHOLDER_ENV.items())
    return "\n".join(lines) + "\n"


def _merge_codex(path: Path, command: str) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    cleaned = CODEX_BLOCK.sub("", text).rstrip()
    updated = (cleaned + "\n\n" if cleaned else "") + _codex_block(command)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        _backup(path)
    path.write_text(updated, encoding="utf-8")


def install_configs(
    home: Path,
    command: str,
    platforms: set[str],
    *,
    state_path: Path | None = None,
) -> None:
    unknown = platforms - VALID_PLATFORMS
    if unknown:
        raise InstallError("Unknown platform(s): " + ", ".join(sorted(unknown)))
    state = _load_state(state_path)
    saved = state.setdefault("platforms", {})
    if "cursor" in platforms:
        saved.setdefault("cursor", _capture_json_entry(home / ".cursor/mcp.json", "mcpServers"))
        _merge_mcp_servers(home / ".cursor/mcp.json", command)
    if "claude" in platforms:
        saved.setdefault("claude", _capture_json_entry(home / ".claude.json", "mcpServers"))
        _merge_mcp_servers(home / ".claude.json", command)
    if "opencode" in platforms:
        saved.setdefault("opencode", _capture_json_entry(home / ".config/opencode/opencode.json", "mcp"))
        _merge_opencode(home / ".config/opencode/opencode.json", command)
    if "codex" in platforms:
        codex_path = home / ".codex/config.toml"
        original = codex_path.read_text(encoding="utf-8") if codex_path.exists() else ""
        match = CODEX_BLOCK.search(original)
        saved.setdefault(
            "codex",
            {"kind": "toml", "path": str(codex_path), "entry": match.group(0) if match else None},
        )
        _merge_codex(home / ".codex/config.toml", command)
    _save_state(state_path, state)


def _remove_json_entry(path: Path, root_key: str) -> None:
    if not path.exists():
        return
    data = _load_json(path)
    servers = data.get(root_key)
    if isinstance(servers, dict) and SERVER_NAME in servers:
        del servers[SERVER_NAME]
        _write_json(path, data)


def _restore_json_entry(path: Path, root_key: str, entry: Any) -> None:
    data = _load_json(path)
    servers = data.setdefault(root_key, {})
    if not isinstance(servers, dict):
        raise InstallError(f"{root_key} must be an object: {path}")
    if entry is None:
        servers.pop(SERVER_NAME, None)
    else:
        servers[SERVER_NAME] = entry
    _write_json(path, data)


def uninstall_configs(
    home: Path, platforms: set[str], *, state_path: Path | None = None
) -> None:
    state = _load_state(state_path)
    saved = state.get("platforms", {})
    if "cursor" in platforms:
        prior = saved.get("cursor")
        if prior:
            _restore_json_entry(Path(prior["path"]), prior["root_key"], prior["entry"])
        else:
            _remove_json_entry(home / ".cursor/mcp.json", "mcpServers")
    if "claude" in platforms:
        prior = saved.get("claude")
        if prior:
            _restore_json_entry(Path(prior["path"]), prior["root_key"], prior["entry"])
        else:
            _remove_json_entry(home / ".claude.json", "mcpServers")
    if "opencode" in platforms:
        prior = saved.get("opencode")
        if prior:
            _restore_json_entry(Path(prior["path"]), prior["root_key"], prior["entry"])
        else:
            _remove_json_entry(home / ".config/opencode/opencode.json", "mcp")
    if "codex" in platforms:
        path = home / ".codex/config.toml"
        if path.exists():
            original = path.read_text(encoding="utf-8")
            updated = CODEX_BLOCK.sub("", original).rstrip()
            prior = saved.get("codex", {}).get("entry")
            if prior:
                updated = (updated + "\n\n" if updated else "") + prior.rstrip()
            updated += "\n"
            if updated != original:
                _backup(path)
                path.write_text(updated, encoding="utf-8")
    for platform in platforms:
        saved.pop(platform, None)
    _save_state(state_path, state)


def _platforms(value: str) -> set[str]:
    result = {item.strip().lower() for item in value.split(",") if item.strip()}
    return set(VALID_PLATFORMS) if result == {"all"} else result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("install", "uninstall"))
    parser.add_argument("--home", type=Path, required=True)
    parser.add_argument("--command")
    parser.add_argument("--platforms", default="all")
    parser.add_argument("--state", type=Path)
    args = parser.parse_args()
    platforms = _platforms(args.platforms)
    if args.action == "install":
        if not args.command:
            parser.error("--command is required for install")
        install_configs(args.home, args.command, platforms, state_path=args.state)
    else:
        uninstall_configs(args.home, platforms, state_path=args.state)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
