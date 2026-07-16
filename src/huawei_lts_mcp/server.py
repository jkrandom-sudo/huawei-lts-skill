from __future__ import annotations

import json
import os
from collections.abc import Mapping
from typing import Any

import anyio
from mcp import types
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.shared.exceptions import McpError

from .catalog import TOOL_BY_NAME, TOOL_SPECS
from .config import LtsConfig
from .errors import normalize_error
from .runtime import invoke_tool


def create_server(*, env: Mapping[str, str] | None = None) -> Server:
    server = Server(
        "huawei-lts",
        version="0.1.0",
        instructions="Operate Huawei Cloud Log Tank Service through explicit LTS tools.",
    )
    environment = env if env is not None else os.environ

    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name=spec.name,
                title=spec.name,
                description=spec.description,
                inputSchema=spec.input_schema,
            )
            for spec in TOOL_SPECS
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
        spec = TOOL_BY_NAME.get(name)
        if spec is None:
            raise McpError(types.ErrorData(code=-32601, message=f"Unknown tool: {name}"))
        try:
            config = LtsConfig.from_env(environment)
            result = await invoke_tool(spec, arguments or {}, config=config)
        except Exception as error:
            normalized = normalize_error(error)
            raise McpError(
                types.ErrorData(
                    code=-32602 if normalized["type"] == "invalid_request" else -32603,
                    message=json.dumps(normalized, ensure_ascii=False),
                )
            ) from error
        return [
            types.TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, separators=(",", ":")),
            )
        ]

    return server


async def _run() -> None:
    server = create_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def main() -> None:
    anyio.run(_run)


if __name__ == "__main__":
    main()
