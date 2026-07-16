from datetime import datetime, timezone

from huawei_lts_mcp.adapter import apply_arguments, to_jsonable


class ExampleModel:
    openapi_types = {"project_id": "str", "page_size": "int"}
    attribute_map = {"project_id": "project_id", "page_size": "page_size"}

    def __init__(self):
        self.project_id = None
        self.page_size = None


def test_apply_arguments_sets_known_sdk_fields():
    request = ExampleModel()

    apply_arguments(request, {"project_id": "project-placeholder", "page_size": 50})

    assert request.project_id == "project-placeholder"
    assert request.page_size == 50


def test_apply_arguments_rejects_unknown_fields():
    request = ExampleModel()

    try:
        apply_arguments(request, {"unexpected": True})
    except ValueError as error:
        assert "unexpected" in str(error)
    else:
        raise AssertionError("unknown argument was accepted")


def test_to_jsonable_preserves_sdk_payload_fields():
    class Response:
        def to_dict(self):
            return {
                "count": 1,
                "observed_at": datetime(2026, 1, 2, tzinfo=timezone.utc),
            }

    assert to_jsonable(Response()) == {
        "count": 1,
        "observed_at": "2026-01-02T00:00:00+00:00",
    }
