#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="${HUAWEI_LTS_INSTALL_DIR:-$HOME/.local/share/huawei-lts-skill}"
PLATFORMS="all"
SKIP_RUNTIME=0

usage() {
  echo "Usage: ./install.sh [--platforms cursor,claude,opencode,codex] [--skip-runtime]"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --platforms) PLATFORMS="${2:?--platforms requires a value}"; shift 2 ;;
    --skip-runtime) SKIP_RUNTIME=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

python3 "$SOURCE_DIR/scripts/deploy.py" install \
  --source "$SOURCE_DIR" --destination "$INSTALL_DIR" --home "$HOME" \
  --platforms "$PLATFORMS"

if [[ "$SKIP_RUNTIME" -eq 0 ]]; then
  if ! command -v uv >/dev/null 2>&1; then
    echo "uv is required. Install it from https://docs.astral.sh/uv/" >&2
    exit 1
  fi
  (cd "$INSTALL_DIR" && uv sync --frozen --no-dev)
fi

python3 "$INSTALL_DIR/scripts/manage_install.py" install \
  --home "$HOME" --command "$INSTALL_DIR/.venv/bin/huawei-lts-mcp" \
  --platforms "$PLATFORMS" --state "$INSTALL_DIR/install-state.json"

echo "Installed Huawei LTS Skill and MCP for: $PLATFORMS"
echo "Replace the HUAWEI_* placeholders in each selected client's MCP config, then restart the client."
