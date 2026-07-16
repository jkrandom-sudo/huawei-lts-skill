# Contributing

Use Python 3.10+ and uv. Keep runtime dependencies limited to the MCP SDK and
Huawei Cloud core/LTS SDKs unless a new dependency has a demonstrated runtime
need.

Before submitting changes:

```bash
uv sync --extra dev
uv run pytest
uv run python scripts/generate_tools.py --check
bash -n install.sh uninstall.sh
```

Never add real AK/SK values, tenant IDs, log resource names, developer-specific
absolute paths, or business repository names. Examples must use placeholders.
Add a failing test before changing runtime or installer behavior.
