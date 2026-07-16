#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="${HUAWEI_LTS_INSTALL_DIR:-$HOME/.local/share/huawei-lts-skill}"
PLATFORMS=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --platforms) PLATFORMS="${2:?--platforms requires a value}"; shift 2 ;;
    -h|--help) echo "Usage: ./uninstall.sh [--platforms cursor,claude,opencode,codex]"; exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 2 ;;
  esac
done

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
