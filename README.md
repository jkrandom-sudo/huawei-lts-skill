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
- [`uv`](https://docs.astral.sh/uv/)
- At least one supported client
- Huawei Cloud AK/SK with permissions appropriate to the operations you use

## Install

```bash
git clone https://github.com/<owner>/huawei-lts-skill.git
cd huawei-lts-skill
./install.sh
```

Install selected clients only:

```bash
./install.sh --platforms cursor,claude
./install.sh --platforms opencode,codex
```

The installer deploys the runtime to `~/.local/share/huawei-lts-skill`, creates
an isolated `.venv`, installs the Skill, backs up existing client configs, and
merges the `huawei-lts` MCP entry. Override the deployment location with
`HUAWEI_LTS_INSTALL_DIR=~/some/subdirectory`.

## Configure credentials

After installation, replace these placeholders in every selected client's MCP
configuration:

```text
HUAWEI_ACCESS_KEY=REPLACE_WITH_YOUR_AK
HUAWEI_SECRET_KEY=REPLACE_WITH_YOUR_SK
HUAWEI_REGION=REPLACE_WITH_YOUR_REGION
HUAWEI_PROJECT_ID=REPLACE_WITH_YOUR_PROJECT_ID
```

Configuration locations:

| Client | Skill directory | MCP configuration |
|---|---|---|
| Cursor | `~/.cursor/skills/huawei-lts` | `~/.cursor/mcp.json` |
| Claude Code | `~/.claude/skills/huawei-lts` | `~/.claude.json` |
| OpenCode | `~/.config/opencode/skills/huawei-lts` | `~/.config/opencode/opencode.json` |
| Codex | `~/.codex/skills/huawei-lts` | `~/.codex/config.toml` |

Do not commit client configurations containing real credentials. Restart the
client after editing its configuration.

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

## Upgrade and uninstall

Pull or download the new repository version and rerun `./install.sh`. Installation
is idempotent and backs up affected client configs before updating them.

```bash
./uninstall.sh
./uninstall.sh --platforms cursor,codex
```

Uninstall removes only this Skill, its MCP entries, and its deployed runtime. It
does not touch Huawei Cloud resources or unrelated client configuration.

## Development

```bash
uv sync --extra dev
uv run pytest
uv run python scripts/generate_tools.py --check
```

The checked-in tool manifest matches the current 92-tool MCP surface. When the
Huawei LTS SDK changes, update the manifest deliberately and run the catalog
validation before release.

## Troubleshooting

- `uv is required`: install uv and rerun the installer.
- MCP does not start: confirm the configured command exists under the deployed
  `.venv/bin/` directory and restart the client.
- Missing credential/scope error: replace all four `HUAWEI_*` placeholders.
- Empty resource list: verify that region and project ID belong together.
- Permission error: grant only the LTS permissions required for the intended use.

The MCP never prints AK/SK. Cloud errors are normalized with an error category,
request ID when available, and a retryability hint.

## License

MIT. Huawei Cloud SDK packages retain their respective licenses.
