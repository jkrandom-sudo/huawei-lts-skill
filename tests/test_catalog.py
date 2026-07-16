import json
from importlib.resources import files

from huawei_lts_mcp.catalog import TOOL_SPECS


def test_catalog_registers_complete_current_tool_set():
    names = {spec.name for spec in TOOL_SPECS}

    assert len(names) == 92
    assert {
        "ListLogGroups",
        "ListLogs",
        "CreateLogGroup",
        "UpdateKeywordsAlarmRule",
        "DeleteTransfer",
        "ListHostGroup",
        "ShowAomMappingRules",
        "ConsumerGroupHeartBeat",
    } <= names


def test_every_tool_has_sdk_binding_and_object_schema():
    for spec in TOOL_SPECS:
        assert spec.sdk_method
        assert spec.request_class.endswith("Request")
        assert spec.input_schema["type"] == "object"
        assert isinstance(spec.input_schema["properties"], dict)


def test_complete_schema_catalog_is_checked_in_as_json():
    path = files("huawei_lts_mcp").joinpath("generated_catalog.json")

    data = json.loads(path.read_text(encoding="utf-8"))

    assert len(data) == 92
    assert data[0]["input_schema"]["type"] == "object"
