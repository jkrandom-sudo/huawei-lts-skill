import json
import stat
from pathlib import Path

import pytest

from scripts.manage_install import InstallError, install_configs, uninstall_configs


PLATFORMS = {"cursor", "claude", "opencode", "codex"}


def test_install_merges_all_platform_configs_and_creates_backups(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    cursor = home / ".cursor" / "mcp.json"
    cursor.parent.mkdir(parents=True)
    cursor.write_text('{"mcpServers":{"existing":{"command":"keep"}}}\n')
    command = str(home / ".local" / "share" / "huawei-lts-skill" / ".venv" / "bin" / "huawei-lts-mcp")

    install_configs(home, command, PLATFORMS)

    cursor_data = json.loads(cursor.read_text())
    assert cursor_data["mcpServers"]["existing"]["command"] == "keep"
    assert cursor_data["mcpServers"]["huawei-lts"]["command"] == command
    assert cursor_data["mcpServers"]["huawei-lts"]["env"]["HUAWEI_ACCESS_KEY"] == "REPLACE_WITH_YOUR_AK"
    assert list(cursor.parent.glob("mcp.json.bak.*"))
    assert "huawei-lts" in json.loads((home / ".claude.json").read_text())["mcpServers"]
    assert "huawei-lts" in json.loads((home / ".config/opencode/opencode.json").read_text())["mcp"]
    assert "[mcp_servers.huawei-lts]" in (home / ".codex/config.toml").read_text()


def test_install_is_idempotent(tmp_path):
    home = tmp_path / "home"
    home.mkdir()

    install_configs(home, "/command/one", {"cursor"})
    install_configs(home, "/command/two", {"cursor"})

    data = json.loads((home / ".cursor/mcp.json").read_text())
    assert list(data["mcpServers"]) == ["huawei-lts"]
    assert data["mcpServers"]["huawei-lts"]["command"] == "/command/two"


def test_malformed_json_is_preserved(tmp_path):
    home = tmp_path / "home"
    path = home / ".cursor/mcp.json"
    path.parent.mkdir(parents=True)
    path.write_text("{broken")

    with pytest.raises(InstallError):
        install_configs(home, "/command", {"cursor"})

    assert path.read_text() == "{broken"
    assert not list(path.parent.glob("mcp.json.bak.*"))


def test_uninstall_restores_previous_huawei_lts_entries(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    cursor = home / ".cursor/mcp.json"
    cursor.parent.mkdir(parents=True)
    cursor.write_text(json.dumps({"mcpServers": {"huawei-lts": {"command": "previous"}}}))
    state = tmp_path / "install-state.json"
    install_configs(home, "/command", PLATFORMS, state_path=state)
    data = json.loads(cursor.read_text())
    data["mcpServers"]["existing"] = {"command": "keep"}
    cursor.write_text(json.dumps(data))

    uninstall_configs(home, PLATFORMS, state_path=state)

    assert json.loads(cursor.read_text())["mcpServers"] == {
        "huawei-lts": {"command": "previous"},
        "existing": {"command": "keep"},
    }
    assert "huawei-lts" not in json.loads((home / ".claude.json").read_text())["mcpServers"]
    assert "huawei-lts" not in json.loads((home / ".config/opencode/opencode.json").read_text())["mcp"]
    assert "[mcp_servers.huawei-lts]" not in (home / ".codex/config.toml").read_text()


def test_install_state_is_owner_read_write_only(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    state = tmp_path / "install-state.json"

    install_configs(home, "/command", {"cursor"}, state_path=state)

    assert stat.S_IMODE(state.stat().st_mode) == 0o600
