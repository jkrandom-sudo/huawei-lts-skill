#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR_INPUT="${HUAWEI_LTS_INSTALL_DIR:-$HOME/.local/share/huawei-lts-skill}"
PLATFORMS=""

usage() {
  echo "Usage: ./uninstall.sh [--platforms cursor,claude,opencode,codex] [--install-dir PATH]"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --platforms) PLATFORMS="${2:?--platforms requires a value}"; shift 2 ;;
    --install-dir) INSTALL_DIR_INPUT="${2:?--install-dir requires a value}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

INSTALL_DIR="$(python3 "$SOURCE_DIR/scripts/deploy.py" resolve \
  --source "$SOURCE_DIR" --destination "$INSTALL_DIR_INPUT" --home "$HOME" \
  --platforms all)"

MANAGER="$INSTALL_DIR/scripts/manage_install.py"
DEPLOY="$INSTALL_DIR/scripts/deploy.py"
if [[ ! -f "$MANAGER" ]]; then MANAGER="$SOURCE_DIR/scripts/manage_install.py"; fi
if [[ ! -f "$DEPLOY" ]]; then DEPLOY="$SOURCE_DIR/scripts/deploy.py"; fi

if [[ -z "$PLATFORMS" ]]; then
  PLATFORMS="$(python3 "$DEPLOY" owned --source "$SOURCE_DIR" \
    --destination "$INSTALL_DIR" --home "$HOME" --platforms all)"
fi
python3 "$DEPLOY" verify --source "$SOURCE_DIR" --destination "$INSTALL_DIR" \
  --home "$HOME" --platforms "$PLATFORMS"
python3 "$MANAGER" uninstall --home "$HOME" --platforms "$PLATFORMS" \
  --state "$INSTALL_DIR/install-state.json"
python3 "$DEPLOY" uninstall --source "$SOURCE_DIR" --destination "$INSTALL_DIR" \
  --home "$HOME" --platforms "$PLATFORMS"
echo "Removed Huawei LTS Skill, MCP config entries, and installed runtime."
