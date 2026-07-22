import json
import os
import subprocess
from pathlib import Path

import pytest

from scripts import deploy as deploy_script


REPO = Path(__file__).resolve().parents[1]


def install_env(home: Path, **overrides: str) -> dict[str, str]:
    env = {**os.environ, "HOME": str(home)}
    env.pop("HUAWEI_LTS_INSTALL_DIR", None)
    env.update(overrides)
    return env


def run_install(
    home: Path, *args: str, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(REPO / "install.sh"), *args, "--skip-runtime"],
        cwd=REPO,
        env=env or install_env(home),
        text=True,
        capture_output=True,
    )


def run_uninstall(
    home: Path, *args: str, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(REPO / "uninstall.sh"), *args],
        cwd=REPO,
        env=env or install_env(home),
        text=True,
        capture_output=True,
    )


def test_install_and_uninstall_cli_in_temporary_home(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    env = {
        **os.environ,
        "HOME": str(home),
        "HUAWEI_LTS_INSTALL_DIR": str(home / ".local/share/huawei-lts-skill"),
    }

    installed = subprocess.run(
        ["bash", str(REPO / "install.sh"), "--platforms", "cursor", "--skip-runtime"],
        cwd=REPO,
        env=env,
        text=True,
        capture_output=True,
    )

    assert installed.returncode == 0, installed.stderr
    assert (home / ".cursor/skills/huawei-lts/SKILL.md").is_file()
    assert (home / ".cursor/mcp.json").is_file()
    assert (home / ".local/share/huawei-lts-skill/src/huawei_lts_mcp/server.py").is_file()

    removed = subprocess.run(
        ["bash", str(REPO / "uninstall.sh"), "--platforms", "cursor"],
        cwd=REPO,
        env=env,
        text=True,
        capture_output=True,
    )

    assert removed.returncode == 0, removed.stderr
    assert not (home / ".cursor/skills/huawei-lts").exists()
    assert not (home / ".local/share/huawei-lts-skill").exists()


def test_partial_uninstall_keeps_runtime_for_remaining_clients(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    install_dir = home / ".local/share/huawei-lts-skill"
    env = {**os.environ, "HOME": str(home), "HUAWEI_LTS_INSTALL_DIR": str(install_dir)}
    subprocess.run(
        ["bash", str(REPO / "install.sh"), "--platforms", "cursor,claude", "--skip-runtime"],
        cwd=REPO, env=env, check=True, capture_output=True, text=True,
    )

    subprocess.run(
        ["bash", str(REPO / "uninstall.sh"), "--platforms", "cursor"],
        cwd=REPO, env=env, check=True, capture_output=True, text=True,
    )

    assert install_dir.exists()
    assert (home / ".claude/skills/huawei-lts/SKILL.md").exists()


def test_uninstall_refuses_unowned_custom_directory(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    install_dir = home / "important-existing-directory"
    install_dir.mkdir()
    important = install_dir / "keep.txt"
    important.write_text("keep")
    env = {**os.environ, "HOME": str(home), "HUAWEI_LTS_INSTALL_DIR": str(install_dir)}

    removed = subprocess.run(
        ["bash", str(REPO / "uninstall.sh"), "--platforms", "cursor"],
        cwd=REPO, env=env, capture_output=True, text=True,
    )

    assert removed.returncode != 0
    assert important.read_text() == "keep"


def test_uninstall_refuses_platform_not_owned_by_installation(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    install_dir = home / ".local/share/huawei-lts-skill"
    unrelated = home / ".cursor/skills/huawei-lts"
    unrelated.mkdir(parents=True)
    (unrelated / "SKILL.md").write_text("unrelated")
    env = {**os.environ, "HOME": str(home), "HUAWEI_LTS_INSTALL_DIR": str(install_dir)}
    subprocess.run(
        ["bash", str(REPO / "install.sh"), "--platforms", "claude", "--skip-runtime"],
        cwd=REPO, env=env, check=True, capture_output=True, text=True,
    )

    removed = subprocess.run(
        ["bash", str(REPO / "uninstall.sh"), "--platforms", "cursor"],
        cwd=REPO, env=env, capture_output=True, text=True,
    )

    assert removed.returncode != 0
    assert (unrelated / "SKILL.md").read_text() == "unrelated"


def test_partial_uninstall_then_reinstall_restores_and_recaptures_previous_skill(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    install_dir = home / ".local/share/huawei-lts-skill"
    previous = home / ".cursor/skills/huawei-lts"
    previous.mkdir(parents=True)
    (previous / "SKILL.md").write_text("previous")
    env = {**os.environ, "HOME": str(home), "HUAWEI_LTS_INSTALL_DIR": str(install_dir)}
    subprocess.run(
        ["bash", str(REPO / "install.sh"), "--platforms", "cursor,claude", "--skip-runtime"],
        cwd=REPO, env=env, check=True, capture_output=True, text=True,
    )
    subprocess.run(
        ["bash", str(REPO / "uninstall.sh"), "--platforms", "cursor"],
        cwd=REPO, env=env, check=True, capture_output=True, text=True,
    )
    assert (previous / "SKILL.md").read_text() == "previous"

    reinstalled = subprocess.run(
        ["bash", str(REPO / "install.sh"), "--platforms", "cursor", "--skip-runtime"],
        cwd=REPO, env=env, capture_output=True, text=True,
    )

    assert reinstalled.returncode == 0, reinstalled.stderr
    assert "name: huawei-lts" in (previous / "SKILL.md").read_text()


def test_install_uses_default_directory_under_home(tmp_path):
    home = tmp_path / "home"
    home.mkdir()

    installed = run_install(home, "--platforms", "cursor")

    assert installed.returncode == 0, installed.stderr
    runtime = home / ".local/share/huawei-lts-skill"
    assert (runtime / "src/huawei_lts_mcp/server.py").is_file()
    config = json.loads((home / ".cursor/mcp.json").read_text())
    assert config["mcpServers"]["huawei-lts"]["command"] == str(
        runtime / ".venv/bin/huawei-lts-mcp"
    )


def test_install_dir_option_overrides_environment(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    env_dir = home / "from-env"
    cli_dir = home / "from-cli"
    env = install_env(home, HUAWEI_LTS_INSTALL_DIR=str(env_dir))

    installed = run_install(
        home,
        "--platforms",
        "cursor",
        "--install-dir",
        str(cli_dir),
        env=env,
    )

    assert installed.returncode == 0, installed.stderr
    assert (cli_dir / "src/huawei_lts_mcp/server.py").is_file()
    assert not env_dir.exists()


def test_environment_install_dir_overrides_default(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    install_dir = home / "from-env"
    env = install_env(home, HUAWEI_LTS_INSTALL_DIR=str(install_dir))

    installed = run_install(home, "--platforms", "cursor", env=env)

    assert installed.returncode == 0, installed.stderr
    assert (install_dir / "src/huawei_lts_mcp/server.py").is_file()
    assert not (home / ".local/share/huawei-lts-skill").exists()


def test_literal_tilde_install_dir_is_expanded(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    env = install_env(home, HUAWEI_LTS_INSTALL_DIR="~/custom runtime")

    installed = run_install(home, "--platforms", "cursor", env=env)

    assert installed.returncode == 0, installed.stderr
    runtime = home / "custom runtime"
    assert (runtime / "src/huawei_lts_mcp/server.py").is_file()
    config = json.loads((home / ".cursor/mcp.json").read_text())
    command = config["mcpServers"]["huawei-lts"]["command"]
    assert command == str(runtime / ".venv/bin/huawei-lts-mcp")
    assert "~" not in command


def test_install_allows_absolute_directory_outside_home_and_uninstalls_it(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    install_dir = tmp_path / "shared/huawei-lts-skill"

    installed = run_install(
        home, "--platforms", "cursor", "--install-dir", str(install_dir)
    )
    removed = run_uninstall(
        home, "--platforms", "cursor", "--install-dir", str(install_dir)
    )

    assert installed.returncode == 0, installed.stderr
    assert removed.returncode == 0, removed.stderr
    assert not install_dir.exists()


@pytest.mark.parametrize("unsafe", ["relative/runtime", "/"])
def test_install_rejects_relative_and_root_directories(tmp_path, unsafe):
    home = tmp_path / "home"
    home.mkdir()

    installed = run_install(
        home, "--platforms", "cursor", "--install-dir", unsafe
    )

    assert installed.returncode != 0
    assert "absolute path or a path beginning with ~" in installed.stderr


def test_install_rejects_home_directory(tmp_path):
    home = tmp_path / "home"
    home.mkdir()

    installed = run_install(
        home, "--platforms", "cursor", "--install-dir", str(home)
    )

    assert installed.returncode != 0
    assert (
        "Refusing to use the user home as the installation directory"
        in installed.stderr
    )


def test_install_rejects_unowned_non_empty_absolute_directory(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    install_dir = tmp_path / "existing"
    install_dir.mkdir()
    important = install_dir / "keep.txt"
    important.write_text("keep")

    installed = run_install(
        home, "--platforms", "cursor", "--install-dir", str(install_dir)
    )

    assert installed.returncode != 0
    assert "unowned non-empty directory" in installed.stderr
    assert important.read_text() == "keep"


def test_install_validates_existing_marker_before_writing_files(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    install_dir = tmp_path / "invalid-marker"
    install_dir.mkdir()
    marker = install_dir / ".huawei-lts-install.json"
    marker.write_text('{"id": "not-huawei-lts", "version": 1, "platforms": []}')
    important = install_dir / "README.md"
    important.write_text("do not overwrite")

    installed = run_install(
        home, "--platforms", "cursor", "--install-dir", str(install_dir)
    )

    assert installed.returncode != 0
    assert "Invalid installation ownership marker" in installed.stderr
    assert important.read_text() == "do not overwrite"
    assert not (install_dir / "scripts").exists()


@pytest.mark.skipif(os.geteuid() == 0, reason="root bypasses permission bits")
def test_install_reports_unwritable_parent_without_using_sudo(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    parent = tmp_path / "read-only"
    parent.mkdir()
    parent.chmod(0o500)
    install_dir = parent / "huawei-lts-skill"
    try:
        installed = run_install(
            home, "--platforms", "cursor", "--install-dir", str(install_dir)
        )
    finally:
        parent.chmod(0o700)

    assert installed.returncode != 0
    assert "not writable" in installed.stderr
    assert "sudo" not in installed.stdout + installed.stderr


def test_install_with_spaces_writes_absolute_commands_for_all_clients(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    install_dir = tmp_path / "shared tools/huawei lts"

    installed = run_install(
        home,
        "--platforms",
        "cursor,claude,opencode,codex",
        "--install-dir",
        str(install_dir),
    )

    assert installed.returncode == 0, installed.stderr
    command = str(install_dir / ".venv/bin/huawei-lts-mcp")
    cursor = json.loads((home / ".cursor/mcp.json").read_text())
    claude = json.loads((home / ".claude.json").read_text())
    opencode = json.loads((home / ".config/opencode/opencode.json").read_text())
    codex = (home / ".codex/config.toml").read_text()
    assert cursor["mcpServers"]["huawei-lts"]["command"] == command
    assert claude["mcpServers"]["huawei-lts"]["command"] == command
    assert opencode["mcp"]["huawei-lts"]["command"] == [command]
    assert f'command = "{command}"' in codex
    assert "~" not in command
    assert (home / ".agents/skills/huawei-lts/SKILL.md").is_file()
    assert not (home / ".codex/skills/huawei-lts").exists()


def test_install_summary_uses_tilde_for_home_paths_and_absolute_external_path(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    home_install = home / "tools/huawei-lts-skill"
    home_result = run_install(
        home, "--platforms", "cursor", "--install-dir", str(home_install)
    )

    assert home_result.returncode == 0, home_result.stderr
    assert "Runtime: ~/tools/huawei-lts-skill" in home_result.stdout
    assert "Skill: ~/.cursor/skills/huawei-lts" in home_result.stdout
    assert "MCP config: ~/.cursor/mcp.json" in home_result.stdout
    assert str(home) not in home_result.stdout

    external = tmp_path / "external/huawei-lts-skill"
    external_result = run_install(
        home, "--platforms", "codex", "--install-dir", str(external)
    )

    assert external_result.returncode == 0, external_result.stderr
    assert f"Runtime: {external}" in external_result.stdout
    assert "Skill: ~/.agents/skills/huawei-lts" in external_result.stdout


def test_install_summary_normalizes_platform_case_and_whitespace(tmp_path):
    home = tmp_path / "home"
    home.mkdir()

    installed = run_install(home, "--platforms", "Cursor, CODEX")

    assert installed.returncode == 0, installed.stderr
    assert "Installed Huawei LTS Skill and MCP for: cursor,codex" in installed.stdout
    assert "Skill: ~/.cursor/skills/huawei-lts" in installed.stdout
    assert "Skill: ~/.agents/skills/huawei-lts" in installed.stdout


def test_codex_upgrade_migrates_legacy_skill_and_preserves_both_backups(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    install_dir = home / ".local/share/huawei-lts-skill"
    install_dir.mkdir(parents=True)
    (install_dir / ".huawei-lts-install.json").write_text(
        json.dumps({"id": "huawei-lts-skill", "version": 1, "platforms": ["codex"]})
    )

    legacy = home / ".codex/skills/huawei-lts"
    legacy.mkdir(parents=True)
    (legacy / "SKILL.md").write_text("legacy installed copy")
    legacy_backup = install_dir / ".backups/skills/codex"
    legacy_backup.mkdir(parents=True)
    (legacy_backup / "SKILL.md").write_text("previous legacy skill")

    current = home / ".agents/skills/huawei-lts"
    current.mkdir(parents=True)
    (current / "SKILL.md").write_text("previous canonical skill")

    installed = run_install(
        home, "--platforms", "codex", "--install-dir", str(install_dir)
    )

    assert installed.returncode == 0, installed.stderr
    assert (legacy / "SKILL.md").read_text() == "previous legacy skill"
    assert "name: huawei-lts" in (current / "SKILL.md").read_text()
    current_backup = install_dir / ".backups/skills-v2/codex/SKILL.md"
    assert current_backup.read_text() == "previous canonical skill"
    marker = json.loads((install_dir / ".huawei-lts-install.json").read_text())
    assert marker["skill_paths"]["codex"] == ".agents/skills/huawei-lts"

    removed = run_uninstall(
        home, "--platforms", "codex", "--install-dir", str(install_dir)
    )

    assert removed.returncode == 0, removed.stderr
    assert (legacy / "SKILL.md").read_text() == "previous legacy skill"
    assert (current / "SKILL.md").read_text() == "previous canonical skill"
    assert not install_dir.exists()


def test_codex_migration_keeps_legacy_backup_until_marker_is_persisted(
    tmp_path, monkeypatch
):
    home = tmp_path / "home"
    home.mkdir()
    install_dir = home / ".local/share/huawei-lts-skill"
    install_dir.mkdir(parents=True)
    marker_path = install_dir / ".huawei-lts-install.json"
    marker_path.write_text(
        json.dumps({"id": "huawei-lts-skill", "version": 1, "platforms": ["codex"]})
    )
    legacy = home / ".codex/skills/huawei-lts"
    legacy.mkdir(parents=True)
    (legacy / "SKILL.md").write_text("legacy installed copy")
    legacy_backup = install_dir / ".backups/skills/codex"
    legacy_backup.mkdir(parents=True)
    (legacy_backup / "SKILL.md").write_text("previous legacy skill")

    original_write_text = Path.write_text

    def fail_marker_write(path, *args, **kwargs):
        if path == marker_path:
            raise OSError("simulated marker write failure")
        return original_write_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", fail_marker_write)

    with pytest.raises(OSError, match="simulated marker write failure"):
        deploy_script.install_skills(install_dir, home, {"codex"})

    assert (legacy / "SKILL.md").read_text() == "previous legacy skill"
    assert (legacy_backup / "SKILL.md").read_text() == "previous legacy skill"
