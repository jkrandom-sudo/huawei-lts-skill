from huawei_lts_mcp.config import ConfigError
from huawei_lts_mcp.errors import normalize_error


class ServiceError(Exception):
    status_code = 429
    request_id = "request-placeholder"
    error_code = "LTS.0001"
    error_msg = "rate limited"


def test_normalize_error_marks_rate_limit_retryable():
    result = normalize_error(ServiceError())

    assert result == {
        "type": "rate_limited",
        "message": "rate limited",
        "request_id": "request-placeholder",
        "error_code": "LTS.0001",
        "retryable": True,
    }


def test_normalize_error_classifies_missing_scope_as_invalid_request():
    result = normalize_error(ConfigError("Missing LTS scope: HUAWEI_PROJECT_ID"))

    assert result["type"] == "invalid_request"
    assert result["retryable"] is False
