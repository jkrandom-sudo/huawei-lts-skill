import pytest

from huawei_lts_mcp.catalog import TOOL_BY_NAME
from huawei_lts_mcp.config import LtsConfig
from huawei_lts_mcp.runtime import invoke_tool


class FakeRequest:
    openapi_types = {}
    attribute_map = {}


class FakeClient:
    def list_log_groups(self, request):
        assert isinstance(request, FakeRequest)
        return {"log_groups": [{"log_group_name": "group-placeholder"}]}


@pytest.mark.asyncio
async def test_invoke_tool_uses_explicit_scope_and_serializes_result(monkeypatch):
    config = LtsConfig.from_env(
        {
            "HUAWEI_ACCESS_KEY": "ak-placeholder",
            "HUAWEI_SECRET_KEY": "sk-placeholder",
        }
    )
    monkeypatch.setattr("huawei_lts_mcp.runtime.request_class", lambda _: FakeRequest)
    seen = {}

    def client_factory(received_config, scope):
        seen["scope"] = scope
        return FakeClient()

    result = await invoke_tool(
        TOOL_BY_NAME["ListLogGroups"],
        {"region": "region-placeholder", "project_id": "project-placeholder"},
        config=config,
        client_factory=client_factory,
    )

    assert seen["scope"].region == "region-placeholder"
    assert seen["scope"].project_id == "project-placeholder"
    assert result == {"log_groups": [{"log_group_name": "group-placeholder"}]}
