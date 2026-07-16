from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any

import huaweicloudsdklts.v2.model as lts_model


def _model_class(type_name: str) -> type | None:
    if type_name.startswith("list[") or type_name.startswith("dict("):
        return None
    return getattr(lts_model, type_name, None)


def _coerce(value: Any, type_name: str) -> Any:
    if value is None:
        return None
    if type_name.startswith("list[") and isinstance(value, list):
        item_type = type_name[5:-1]
        return [_coerce(item, item_type) for item in value]
    model_class = _model_class(type_name)
    if model_class and isinstance(value, dict):
        instance = model_class()
        return apply_arguments(instance, value)
    return value


def apply_arguments(model: Any, arguments: dict[str, Any]) -> Any:
    known = getattr(model, "openapi_types", {})
    unknown = sorted(set(arguments) - set(known))
    if unknown:
        raise ValueError("Unknown argument(s): " + ", ".join(unknown))
    for name, value in arguments.items():
        setattr(model, name, _coerce(value, known[name]))
    return model


def to_jsonable(value: Any) -> Any:
    if hasattr(value, "to_dict"):
        return to_jsonable(value.to_dict())
    if isinstance(value, dict):
        return {str(key): to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [to_jsonable(item) for item in value]
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value
