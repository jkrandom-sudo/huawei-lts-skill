from pathlib import Path

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


@pytest.mark.asyncio
async def test_stdio_initialize_and_list_tools_without_cloud_credentials():
    command = Path(__file__).resolve().parents[1] / ".venv/bin/huawei-lts-mcp"
    parameters = StdioServerParameters(command=str(command), env={})

    async with stdio_client(parameters) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            initialized = await session.initialize()
            tools = await session.list_tools()

    assert initialized.serverInfo.name == "huawei-lts"
    assert len(tools.tools) == 92
