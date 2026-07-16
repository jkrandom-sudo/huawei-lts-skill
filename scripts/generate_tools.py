#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import huaweicloudsdklts.v2.model as lts_model
from huaweicloudsdklts.v2 import LtsClient

from huawei_lts_mcp.generated_tools import TOOL_NAMES
from huawei_lts_mcp.schema import model_schema


OUTPUT = Path(__file__).resolve().parents[1] / "src/huawei_lts_mcp/generated_catalog.json"


def camel_to_snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def render_catalog() -> list[dict]:
    result = []
    for name in TOOL_NAMES:
        request_name = name + "Request"
        schema = model_schema(getattr(lts_model, request_name))
        schema["properties"] = {
            "region": {"type": "string", "description": "Overrides HUAWEI_REGION."},
            "project_id": {"type": "string", "description": "Overrides HUAWEI_PROJECT_ID."},
            **schema["properties"],
        }
        result.append(
            {
                "name": name,
                "sdk_method": camel_to_snake(name),
                "request_class": request_name,
                "description": f"Huawei Cloud LTS operation {name}.",
                "input_schema": schema,
            }
        )
    return result


def validate_catalog() -> list[str]:
    errors: list[str] = []
    generated = render_catalog()
    if not OUTPUT.exists():
        return [f"missing generated catalog: {OUTPUT}"]
    try:
        checked_in = json.loads(OUTPUT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [f"invalid generated catalog: {error}"]
    if checked_in != generated:
        errors.append("generated catalog is stale; run scripts/generate_tools.py --write")
    for item in generated:
        if not hasattr(LtsClient, item["sdk_method"]):
            errors.append(f"missing SDK method: {item['sdk_method']}")
        if not hasattr(lts_model, item["request_class"]):
            errors.append(f"missing request model: {item['request_class']}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the checked-in LTS tool catalog.")
    parser.add_argument("--check", action="store_true", help="Fail if SDK bindings drifted.")
    parser.add_argument("--write", action="store_true", help="Regenerate the checked-in catalog.")
    args = parser.parse_args()
    if args.write:
        OUTPUT.write_text(
            json.dumps(render_catalog(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"wrote {OUTPUT}")
    errors = validate_catalog()
    if errors:
        for error in errors:
            print(error)
        return 1
    if args.check:
        print(f"catalog valid: {len(TOOL_NAMES)} tools")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
