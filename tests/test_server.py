import pytest

from huawei_lts_mcp.server import create_server


@pytest.mark.asyncio
async def test_server_lists_all_tools_without_credentials():
    server = create_server(env={})
    handlers = server.request_handlers
    list_handler = next(
        handler
        for request_type, handler in handlers.items()
        if request_type.__name__ == "ListToolsRequest"
    )

    response = await list_handler(type("Request", (), {"params": None})())
    tools = response.root.tools

    assert len(tools) == 92
    assert next(tool for tool in tools if tool.name == "ListLogs").inputSchema["type"] == "object"
