import os
import subprocess
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]


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
