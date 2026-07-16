from __future__ import annotations

import json
from dataclasses import dataclass
from importlib.resources import files
from typing import Any


@dataclass(frozen=True)
class ToolSpec:
    name: str
    sdk_method: str
    request_class: str
    description: str
    input_schema: dict[str, Any]


def _load_specs() -> tuple[ToolSpec, ...]:
    path = files("huawei_lts_mcp").joinpath("generated_catalog.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    return tuple(ToolSpec(**item) for item in payload)


TOOL_SPECS = _load_specs()
TOOL_BY_NAME = {spec.name: spec for spec in TOOL_SPECS}
