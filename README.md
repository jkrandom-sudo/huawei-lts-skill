# Huawei LTS Skill + MCP

A portable Agent Skill and lightweight stdio MCP server for Huawei Cloud Log
Tank Service (LTS). It supports Cursor, Claude Code, OpenCode, and Codex without
cloning the full upstream Huawei Cloud MCP repository.

## What is included

- Root `SKILL.md` with progressive references and safe LTS workflows.
- A Python MCP server exposing 92 LTS operations backed by the official Huawei
  Cloud Python SDK.
- Automatic macOS/Linux installers for four coding agents.
- Locked runtime dependencies and tests that require no cloud credentials.

The runtime dependencies are limited to MCP Python SDK v1,
`huaweicloudsdkcore`, and `huaweicloudsdklts`, plus their required transitive
packages.

## Requirements

- macOS or Linux
- Python 3.10 or newer
- Git
- [`uv`](https://docs.astral.sh/uv/)
- At least one supported client
- Huawei Cloud AK/SK with permissions appropriate to the operations you use

## Quick install

Clone the repository under your user home and install all supported clients:

```bash
git clone https://github.com/jkrandom-sudo/huawei-lts-skill.git ~/huawei-lts-skill
cd ~/huawei-lts-skill
./install.sh
```

Install selected clients only:

```bash
./install.sh --platforms cursor,claude
./install.sh --platforms opencode,codex
```

The installer deploys the runtime, creates an isolated `.venv`, installs the
Skill, backs up existing client configurations, and merges the `huawei-lts`
MCP entry. Installation is idempotent.

### Choose the runtime directory

The default runtime directory is `~/.local/share/huawei-lts-skill`. Here, and
throughout this README, `~` is shorthand for the current user's home directory.

```bash
# Default: ~/.local/share/huawei-lts-skill
./install.sh --platforms codex

# A different directory under the user home
./install.sh --platforms codex --install-dir ~/tools/huawei-lts-skill

# Any writable absolute directory
./install.sh --platforms codex --install-dir /srv/huawei-lts-skill
```

The compatibility environment variable remains supported:

```bash
HUAWEI_LTS_INSTALL_DIR=~/tools/huawei-lts-skill ./install.sh --platforms codex
```

Directory precedence is `--install-dir`, then `HUAWEI_LTS_INSTALL_DIR`, then
the default. Relative paths such as `./runtime` are rejected; use
`~/runtime` or an absolute path. For a directory outside your home, make the
target or its parent writable by your current user. The installer never invokes
`sudo`.

For safety, `/`, your home directory itself, and non-empty directories not
owned by a previous Huawei LTS installation are rejected. The MCP configuration
always receives the resolved absolute executable path, including when the
friendly input or output uses `~`.

## Install from your coding agent

Open the relevant client's Agent or chat, paste the matching prompt below, and
approve the filesystem or network operations when the client asks. The prompts
use the default runtime directory; add `--install-dir <absolute-or-~/path>` only
when you want a custom location.

Never paste a real Huawei Cloud AK/SK into an Agent conversation. The installer
writes placeholders, which you replace locally after installation.

<details>
<summary>Claude Code installation prompt</summary>

```text
Install Huawei LTS Skill + MCP from
https://github.com/jkrandom-sudo/huawei-lts-skill for Claude Code.

1. Confirm this is macOS or Linux and that Git, Python 3.10+, and uv are
   available. If uv is missing, ask before installing it from the official uv
   documentation. Do not use sudo.
2. Clone the repository to ~/huawei-lts-skill. If that directory already exists,
   verify its origin URL, stop if it has uncommitted changes, otherwise update it
   with git pull --ff-only.
3. Run ./install.sh --platforms claude from the repository. Use the default
   runtime directory unless I explicitly provide a custom directory.
4. Verify that ~/.claude/skills/huawei-lts/SKILL.md exists, ~/.claude.json has a
   huawei-lts MCP entry, and the configured command is an existing absolute path.
5. Do not ask me to send or paste AK/SK values into this conversation, and never
   print credential values. Tell me to replace the HUAWEI_* placeholders locally.
6. Report installed paths using ~ for my home directory and remind me to restart
   Claude Code. After restart, I can run claude mcp get huawei-lts or use /mcp.
```

</details>

<details>
<summary>OpenCode installation prompt</summary>

```text
Install Huawei LTS Skill + MCP from
https://github.com/jkrandom-sudo/huawei-lts-skill for OpenCode.

1. Confirm this is macOS or Linux and that Git, Python 3.10+, and uv are
   available. If uv is missing, ask before installing it from the official uv
   documentation. Do not use sudo.
2. Clone the repository to ~/huawei-lts-skill. If that directory already exists,
   verify its origin URL, stop if it has uncommitted changes, otherwise update it
   with git pull --ff-only.
3. Run ./install.sh --platforms opencode from the repository. Use the default
   runtime directory unless I explicitly provide a custom directory.
4. Verify that ~/.config/opencode/skills/huawei-lts/SKILL.md exists,
   ~/.config/opencode/opencode.json has a huawei-lts local MCP entry, and its
   command contains an existing absolute executable path.
5. Do not ask me to send or paste AK/SK values into this conversation, and never
   print credential values. Tell me to replace the HUAWEI_* placeholders locally.
6. Report installed paths using ~ for my home directory and remind me to restart
   OpenCode. After restart, I can run opencode mcp list.
```

</details>

<details>
<summary>Codex installation prompt</summary>

```text
Install Huawei LTS Skill + MCP from
https://github.com/jkrandom-sudo/huawei-lts-skill for Codex.

1. Confirm this is macOS or Linux and that Git, Python 3.10+, and uv are
   available. If uv is missing, ask before installing it from the official uv
   documentation. Do not use sudo.
2. Clone the repository to ~/huawei-lts-skill. If that directory already exists,
   verify its origin URL, stop if it has uncommitted changes, otherwise update it
   with git pull --ff-only.
3. Run ./install.sh --platforms codex from the repository. Use the default
   runtime directory unless I explicitly provide a custom directory.
4. Verify that ~/.agents/skills/huawei-lts/SKILL.md exists, ~/.codex/config.toml
   has a [mcp_servers.huawei-lts] entry, and its command is an existing absolute
   path.
5. Do not ask me to send or paste AK/SK values into this conversation, and never
   print credential values. Tell me to replace the HUAWEI_* placeholders locally.
6. Report installed paths using ~ for my home directory and remind me to restart
   Codex. After restart, I can run codex mcp list or use /mcp.
```

</details>

<details>
<summary>Cursor installation prompt</summary>

```text
Install Huawei LTS Skill + MCP from
https://github.com/jkrandom-sudo/huawei-lts-skill for Cursor.

1. Confirm this is macOS or Linux and that Git, Python 3.10+, and uv are
   available. If uv is missing, ask before installing it from the official uv
   documentation. Do not use sudo.
2. Clone the repository to ~/huawei-lts-skill. If that directory already exists,
   verify its origin URL, stop if it has uncommitted changes, otherwise update it
   with git pull --ff-only.
3. Run ./install.sh --platforms cursor from the repository. Use the default
   runtime directory unless I explicitly provide a custom directory.
4. Verify that ~/.cursor/skills/huawei-lts/SKILL.md exists, ~/.cursor/mcp.json
   has a huawei-lts MCP entry, and its command is an existing absolute path.
5. Do not ask me to send or paste AK/SK values into this conversation, and never
   print credential values. Tell me to replace the HUAWEI_* placeholders locally.
6. Report installed paths using ~ for my home directory and remind me to restart
   Cursor. After restart, I can run cursor-agent mcp list or inspect Tools & MCP
   in Cursor settings.
```

</details>

## Configure credentials

After installation, replace these placeholders in every selected client's MCP
configuration:

```text
HUAWEI_ACCESS_KEY=REPLACE_WITH_YOUR_AK
HUAWEI_SECRET_KEY=REPLACE_WITH_YOUR_SK
HUAWEI_REGION=REPLACE_WITH_YOUR_REGION
HUAWEI_PROJECT_ID=REPLACE_WITH_YOUR_PROJECT_ID
```

Configuration and Skill locations:

| Client | Skill directory | MCP configuration |
|---|---|---|
| Cursor | `~/.cursor/skills/huawei-lts` | `~/.cursor/mcp.json` |
| Claude Code | `~/.claude/skills/huawei-lts` | `~/.claude.json` |
| OpenCode | `~/.config/opencode/skills/huawei-lts` | `~/.config/opencode/opencode.json` |
| Codex | `~/.agents/skills/huawei-lts` | `~/.codex/config.toml` |

Do not commit client configurations containing real credentials. Restart the
client after editing its configuration.

### Generated MCP configuration

The following examples document the generated structure. The example command
`/absolute/path/to/huawei-lts-skill/.venv/bin/huawei-lts-mcp` represents the
resolved form of the friendly default path
`~/.local/share/huawei-lts-skill/.venv/bin/huawei-lts-mcp`. Do not manually put
a literal `~` in the MCP `command`; let the installer write the correct absolute
path for the selected runtime directory.

Cursor (`~/.cursor/mcp.json`) and Claude Code (`~/.claude.json`) use the same
server entry:

```json
{
  "mcpServers": {
    "huawei-lts": {
      "command": "/absolute/path/to/huawei-lts-skill/.venv/bin/huawei-lts-mcp",
      "args": [],
      "env": {
        "HUAWEI_ACCESS_KEY": "REPLACE_WITH_YOUR_AK",
        "HUAWEI_SECRET_KEY": "REPLACE_WITH_YOUR_SK",
        "HUAWEI_REGION": "REPLACE_WITH_YOUR_REGION",
        "HUAWEI_PROJECT_ID": "REPLACE_WITH_YOUR_PROJECT_ID"
      }
    }
  }
}
```

OpenCode (`~/.config/opencode/opencode.json`):

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "huawei-lts": {
      "type": "local",
      "command": [
        "/absolute/path/to/huawei-lts-skill/.venv/bin/huawei-lts-mcp"
      ],
      "enabled": true,
      "environment": {
        "HUAWEI_ACCESS_KEY": "REPLACE_WITH_YOUR_AK",
        "HUAWEI_SECRET_KEY": "REPLACE_WITH_YOUR_SK",
        "HUAWEI_REGION": "REPLACE_WITH_YOUR_REGION",
        "HUAWEI_PROJECT_ID": "REPLACE_WITH_YOUR_PROJECT_ID"
      }
    }
  }
}
```

Codex (`~/.codex/config.toml`):

```toml
[mcp_servers.huawei-lts]
command = "/absolute/path/to/huawei-lts-skill/.venv/bin/huawei-lts-mcp"
args = []
enabled = true

[mcp_servers.huawei-lts.env]
HUAWEI_ACCESS_KEY = "REPLACE_WITH_YOUR_AK"
HUAWEI_SECRET_KEY = "REPLACE_WITH_YOUR_SK"
HUAWEI_REGION = "REPLACE_WITH_YOUR_REGION"
HUAWEI_PROJECT_ID = "REPLACE_WITH_YOUR_PROJECT_ID"
```

The installer merges only the `huawei-lts` entry and preserves unrelated
configuration. Existing files are copied to timestamped `.bak.*` files before
they are changed.

## Verify the installation

After replacing the credential placeholders, restart the selected client and
check its MCP status:

```bash
claude mcp get huawei-lts
opencode mcp list
codex mcp list
cursor-agent mcp list
```

You can also use `/mcp` in Claude Code or Codex, and **Tools & MCP** in Cursor.
For configuration behavior, see the official client documentation:

- [Claude Code MCP](https://code.claude.com/docs/en/mcp)
- [OpenCode MCP servers](https://opencode.ai/docs/mcp-servers/)
- [Codex MCP](https://learn.chatgpt.com/docs/extend/mcp)
- [Cursor MCP](https://docs.cursor.com/context/model-context-protocol)

## Use

```text
Use huawei-lts to list log groups in {region}, project_id={project_id}.
```

```text
Search {log_group_id}/{log_stream_id} for {keyword} during the last hour.
Give me a concise conclusion and redacted examples.
```

The Skill defaults to read-only inspection. Update, Delete, enable/disable, and
batch Create operations require an explicit impact summary and user confirmation.

## Upgrade

Check that your source checkout is clean, update it, and rerun the installer:

```bash
git -C ~/huawei-lts-skill status --short
git -C ~/huawei-lts-skill pull --ff-only
cd ~/huawei-lts-skill
./install.sh --platforms cursor,claude,opencode,codex
```

If you originally selected a custom runtime directory, pass that same directory
again:

```bash
./install.sh --platforms codex --install-dir /srv/huawei-lts-skill
```

## Uninstall

Remove selected clients or omit `--platforms` to remove all clients owned by
this installation:

```bash
cd ~/huawei-lts-skill
./uninstall.sh --platforms cursor,codex
./uninstall.sh
```

If you used a custom runtime directory, you must provide the same directory to
the uninstaller:

```bash
./uninstall.sh --platforms codex --install-dir /srv/huawei-lts-skill
```

Uninstall removes only this Skill, its MCP entries, and its deployed runtime. It
does not touch Huawei Cloud resources or unrelated client configuration.

## Development

```bash
uv sync --extra dev
uv run pytest
uv run python scripts/generate_tools.py --check
bash -n install.sh uninstall.sh
```

The checked-in tool manifest matches the current 92-tool MCP surface. When the
Huawei LTS SDK changes, update the manifest deliberately and run the catalog
validation before release.

## Troubleshooting

- `uv is required`: install uv and rerun the installer.
- `Installation directory must be an absolute path`: use `~/...` or `/...`, not
  a path relative to the current checkout.
- `Installation directory is not writable`: choose a directory writable by the
  current user or prepare the target directory first; do not run the whole
  installer with `sudo`.
- MCP does not start: confirm the configured absolute command exists under the
  selected runtime's `.venv/bin/` directory and restart the client.
- Missing credential/scope error: replace all four `HUAWEI_*` placeholders.
- Empty resource list: verify that region and project ID belong together.
- Permission error: grant only the LTS permissions required for the intended use.

The MCP never prints AK/SK. Cloud errors are normalized with an error category,
request ID when available, and a retryability hint.

## License

MIT. Huawei Cloud SDK packages retain their respective licenses.
