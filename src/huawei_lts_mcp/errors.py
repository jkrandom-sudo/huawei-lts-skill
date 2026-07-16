from __future__ import annotations

from typing import Any

from .config import ConfigError


def normalize_error(error: Exception) -> dict[str, Any]:
    status = getattr(error, "status_code", None)
    error_code = getattr(error, "error_code", None)
    message = getattr(error, "error_msg", None) or str(error) or type(error).__name__
    if status in (401, 403):
        error_type, retryable = "authentication_or_permission", False
    elif status == 429:
        error_type, retryable = "rate_limited", True
    elif isinstance(status, int) and status >= 500:
        error_type, retryable = "service_unavailable", True
    elif status == 400 or isinstance(error, (ConfigError, ValueError, TypeError)):
        error_type, retryable = "invalid_request", False
    elif isinstance(error, (TimeoutError, ConnectionError)):
        error_type, retryable = "network_error", True
    else:
        error_type, retryable = "unexpected_error", False
    return {
        "type": error_type,
        "message": message,
        "request_id": getattr(error, "request_id", None),
        "error_code": error_code,
        "retryable": retryable,
    }
