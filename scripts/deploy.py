#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path


PLATFORM_SKILL_DIRS = {
    "cursor": ".cursor/skills/huawei-lts",
    "claude": ".claude/skills/huawei-lts",
    "opencode": ".config/opencode/skills/huawei-lts",
    "codex": ".agents/skills/huawei-lts",
}
LEGACY_PLATFORM_SKILL_DIRS = {"codex": ".codex/skills/huawei-lts"}
REPO_FILES = ("SKILL.md", "README.md", "LICENSE", "pyproject.toml", "uv.lock")
REPO_DIRS = ("src", "scripts", "references", "examples")
SKILL_FILES = ("SKILL.md",)
SKILL_DIRS = ("references", "examples")
MARKER_NAME = ".huawei-lts-install.json"
MARKER_ID = "huawei-lts-skill"


def _safe_install_path(path: Path, home: Path) -> Path:
    resolved_home = home.expanduser().resolve()
    raw = str(path)
    if raw == "~":
        candidate = resolved_home
    elif raw.startswith("~/"):
        candidate = resolved_home / raw[2:]
    else:
        candidate = path
    if not candidate.is_absolute():
        raise ValueError(
            "Installation directory must be an absolute path or a path beginning with ~: "
            + raw
        )
    resolved = candidate.resolve()
    if resolved == Path(resolved.anchor):
        raise ValueError(
            "Installation directory must be an absolute path or a path beginning with ~, "
            f"and cannot be the filesystem root: {resolved}"
        )
    if resolved == resolved_home:
        raise ValueError(
            f"Refusing to use the user home as the installation directory: {resolved}"
        )
    return resolved


def _nearest_existing_parent(path: Path) -> Path:
    current = path
    while not current.exists():
        current = current.parent
    return current


def _require_writable_destination(path: Path) -> None:
    writable_target = _nearest_existing_parent(path)
    if not os.access(writable_target, os.W_OK | os.X_OK):
        raise ValueError(
            "Installation directory is not writable by the current user: "
            f"{path} (nearest existing path: {writable_target})"
        )


def _read_marker(marker_path: Path) -> dict:
    marker = json.loads(marker_path.read_text(encoding="utf-8"))
    if marker.get("id") != MARKER_ID or marker.get("version") != 1:
        raise ValueError(f"Invalid installation ownership marker: {marker_path}")
    return marker


def deploy_repo(source: Path, destination: Path, home: Path) -> None:
    destination = _safe_install_path(destination, home)
    marker_path = destination / MARKER_NAME
    if destination.exists() and any(destination.iterdir()):
        if not marker_path.is_file():
            raise ValueError(
                f"Refusing to install into unowned non-empty directory: {destination}"
            )
        _read_marker(marker_path)
    _require_writable_destination(destination)
    try:
        destination.mkdir(parents=True, exist_ok=True)
    except PermissionError as error:
        raise ValueError(
            f"Installation directory is not writable by the current user: {destination}"
        ) from error
    if not marker_path.exists():
        marker_path.write_text(
            json.dumps({"id": MARKER_ID, "version": 1, "platforms": []}) + "\n",
            encoding="utf-8",
        )
    for name in REPO_FILES:
        shutil.copy2(source / name, destination / name)
    for name in REPO_DIRS:
        target = destination / name
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(source / name, target)


def _load_marker(destination: Path, home: Path) -> tuple[Path, dict]:
    destination = _safe_install_path(destination, home)
    marker_path = destination / MARKER_NAME
    if not marker_path.is_file():
        raise ValueError(f"Refusing unowned installation directory: {destination}")
    return marker_path, _read_marker(marker_path)


def _installed_skill_path(marker: dict, platform: str) -> str:
    recorded_paths = marker.get("skill_paths", {})
    if not isinstance(recorded_paths, dict):
        raise ValueError("Invalid skill_paths in installation ownership marker")
    recorded = recorded_paths.get(platform)
    allowed = {PLATFORM_SKILL_DIRS[platform]}
    if platform in LEGACY_PLATFORM_SKILL_DIRS:
        allowed.add(LEGACY_PLATFORM_SKILL_DIRS[platform])
    if recorded is not None:
        if recorded not in allowed:
            raise ValueError(
                f"Invalid recorded Skill path for {platform}: {recorded}"
            )
        return recorded
    if platform in marker.get("platforms", []) and platform in LEGACY_PLATFORM_SKILL_DIRS:
        return LEGACY_PLATFORM_SKILL_DIRS[platform]
    return PLATFORM_SKILL_DIRS[platform]


def _skill_backup(source: Path, platform: str, relative_path: str) -> Path:
    if (
        platform == "codex"
        and relative_path == PLATFORM_SKILL_DIRS["codex"]
    ):
        return source / ".backups/skills-v2" / platform
    return source / ".backups/skills" / platform


def _restore_skill(target: Path, backup: Path, *, remove_backup: bool = True) -> None:
    if target.exists():
        shutil.rmtree(target)
    if backup.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(backup, target)
        if remove_backup:
            shutil.rmtree(backup)


def install_skills(source: Path, home: Path, platforms: set[str]) -> None:
    marker_path, marker = _load_marker(source, home)
    installed = set(marker.get("platforms", []))
    skill_paths = marker.setdefault("skill_paths", {})
    for platform in platforms:
        current_path = PLATFORM_SKILL_DIRS[platform]
        installed_path = _installed_skill_path(marker, platform)
        if platform in installed and installed_path != current_path:
            legacy_backup = _skill_backup(source, platform, installed_path)
            _restore_skill(
                home / installed_path,
                legacy_backup,
                remove_backup=False,
            )
            installed.remove(platform)
            skill_paths.pop(platform, None)
            marker["platforms"] = sorted(installed)
            marker_path.write_text(json.dumps(marker, indent=2) + "\n", encoding="utf-8")
            if legacy_backup.exists():
                shutil.rmtree(legacy_backup)

        target = home / current_path
        backup = _skill_backup(source, platform, current_path)
        if platform not in installed and target.exists():
            backup.parent.mkdir(parents=True, exist_ok=True)
            if not backup.exists():
                shutil.copytree(target, backup)
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True, exist_ok=True)
        for name in SKILL_FILES:
            shutil.copy2(source / name, target / name)
        for name in SKILL_DIRS:
            shutil.copytree(source / name, target / name)
        skill_paths[platform] = current_path
    marker["platforms"] = sorted(installed | platforms)
    marker_path.write_text(json.dumps(marker, indent=2) + "\n", encoding="utf-8")


def uninstall(home: Path, destination: Path, platforms: set[str]) -> None:
    marker_path, marker = _load_marker(destination, home)
    installed = set(marker.get("platforms", []))
    skill_paths = marker.get("skill_paths", {})
    for platform in platforms:
        installed_path = _installed_skill_path(marker, platform)
        target = home / installed_path
        backup = _skill_backup(destination, platform, installed_path)
        _restore_skill(target, backup)
        if isinstance(skill_paths, dict):
            skill_paths.pop(platform, None)
    remaining = installed - platforms
    if remaining:
        marker["platforms"] = sorted(remaining)
        marker_path.write_text(json.dumps(marker, indent=2) + "\n", encoding="utf-8")
    else:
        shutil.rmtree(destination)


def parse_platforms(value: str) -> set[str]:
    platforms = {item.strip().lower() for item in value.split(",") if item.strip()}
    if platforms == {"all"}:
        return set(PLATFORM_SKILL_DIRS)
    unknown = platforms - set(PLATFORM_SKILL_DIRS)
    if unknown:
        raise ValueError("Unknown platform(s): " + ", ".join(sorted(unknown)))
    return platforms


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "action", choices=("install", "uninstall", "verify", "owned", "resolve")
    )
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--home", type=Path, required=True)
    parser.add_argument("--platforms", default="all")
    args = parser.parse_args()
    platforms = parse_platforms(args.platforms)
    destination = _safe_install_path(args.destination, args.home)
    if args.action == "resolve":
        print(destination)
        return 0
    if args.action == "install":
        deploy_repo(args.source.resolve(), destination, args.home)
        install_skills(destination, args.home, platforms)
    elif args.action == "uninstall":
        uninstall(args.home, destination, platforms)
    else:
        _, marker = _load_marker(destination, args.home)
        owned = set(marker.get("platforms", []))
        if args.action == "verify":
            unowned = platforms - owned
            if unowned:
                raise ValueError("Refusing unowned platform(s): " + ", ".join(sorted(unowned)))
        else:
            print(",".join(sorted(owned)))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1) from None
