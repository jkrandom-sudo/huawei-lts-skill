#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR_INPUT="${HUAWEI_LTS_INSTALL_DIR:-$HOME/.local/share/huawei-lts-skill}"
PLATFORMS="all"
SKIP_RUNTIME=0

usage() {
  echo "Usage: ./install.sh [--platforms cursor,claude,opencode,codex] [--install-dir PATH] [--skip-runtime]"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --platforms) PLATFORMS="${2:?--platforms requires a value}"; shift 2 ;;
    --install-dir) INSTALL_DIR_INPUT="${2:?--install-dir requires a value}"; shift 2 ;;
    --skip-runtime) SKIP_RUNTIME=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

PLATFORMS="$(printf '%s' "$PLATFORMS" | tr '[:upper:]' '[:lower:]' | tr -d '[:space:]')"

INSTALL_DIR="$(python3 "$SOURCE_DIR/scripts/deploy.py" resolve \
  --source "$SOURCE_DIR" --destination "$INSTALL_DIR_INPUT" --home "$HOME" \
  --platforms "$PLATFORMS")"

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

friendly_path() {
  local path="$1"
  if [[ "$path" == "$HOME" ]]; then
    printf '~'
  elif [[ "$path" == "$HOME/"* ]]; then
    printf '~/%s' "${path#"$HOME/"}"
  else
    printf '%s' "$path"
  fi
}

print_platform_paths() {
  local platform="$1"
  local skill_path config_path
  case "$platform" in
    cursor)
      skill_path="$HOME/.cursor/skills/huawei-lts"
      config_path="$HOME/.cursor/mcp.json"
      ;;
    claude)
      skill_path="$HOME/.claude/skills/huawei-lts"
      config_path="$HOME/.claude.json"
      ;;
    opencode)
      skill_path="$HOME/.config/opencode/skills/huawei-lts"
      config_path="$HOME/.config/opencode/opencode.json"
      ;;
    codex)
      skill_path="$HOME/.agents/skills/huawei-lts"
      config_path="$HOME/.codex/config.toml"
      ;;
  esac
  echo "  $platform"
  echo "    Skill: $(friendly_path "$skill_path")"
  echo "    MCP config: $(friendly_path "$config_path")"
}

echo "Installed Huawei LTS Skill and MCP for: $PLATFORMS"
echo "Runtime: $(friendly_path "$INSTALL_DIR")"
if [[ "$PLATFORMS" == "all" ]]; then
  SELECTED_PLATFORMS=(cursor claude opencode codex)
else
  IFS=',' read -r -a SELECTED_PLATFORMS <<< "$PLATFORMS"
fi
for platform in "${SELECTED_PLATFORMS[@]}"; do
  platform="${platform//[[:space:]]/}"
  print_platform_paths "$platform"
done
echo "Replace the HUAWEI_* placeholders in each selected client's MCP config, then restart the client."
