from __future__ import annotations

import re
from typing import Any

import huaweicloudsdklts.v2.model as lts_model


PRIMITIVES = {
    "str": {"type": "string"},
    "int": {"type": "integer"},
    "float": {"type": "number"},
    "bool": {"type": "boolean"},
    "object": {},
}


def type_schema(type_name: str, seen: frozenset[str] = frozenset()) -> dict[str, Any]:
    if type_name in PRIMITIVES:
        return dict(PRIMITIVES[type_name])
    list_match = re.fullmatch(r"list\[(.+)]", type_name)
    if list_match:
        return {"type": "array", "items": type_schema(list_match.group(1), seen)}
    dict_match = re.fullmatch(r"dict\([^,]+,\s*(.+)\)", type_name)
    if dict_match:
        return {"type": "object", "additionalProperties": type_schema(dict_match.group(1), seen)}
    if type_name in seen:
        return {"type": "object"}
    model_class = getattr(lts_model, type_name, None)
    if model_class is None:
        return {}
    return model_schema(model_class, seen | {type_name})


def model_schema(model_class: type, seen: frozenset[str] = frozenset()) -> dict[str, Any]:
    properties = {
        name: type_schema(type_name, seen)
        for name, type_name in getattr(model_class, "openapi_types", {}).items()
    }
    return {"type": "object", "properties": properties, "additionalProperties": False}
