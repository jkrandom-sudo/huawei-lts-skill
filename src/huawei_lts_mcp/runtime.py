from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import Any

import huaweicloudsdklts.v2.model as lts_model

from .adapter import apply_arguments, to_jsonable
from .catalog import ToolSpec
from .client import build_client
from .config import LtsConfig, LtsScope


ClientFactory = Callable[[LtsConfig, LtsScope], Any]


def request_class(name: str) -> type:
    return getattr(lts_model, name)


async def invoke_tool(
    spec: ToolSpec,
    arguments: dict[str, Any],
    *,
    config: LtsConfig,
    client_factory: ClientFactory = build_client,
) -> Any:
    request_arguments = dict(arguments)
    region = request_arguments.pop("region", None)
    project_id = request_arguments.pop("project_id", None)
    if spec.name == "ListAccessConfig" and "body" not in request_arguments:
        request_arguments["body"] = {}
    scope = config.resolve_scope(region=region, project_id=project_id)
    request = apply_arguments(request_class(spec.request_class)(), request_arguments)
    client = client_factory(config, scope)
    operation = getattr(client, spec.sdk_method)
    response = await asyncio.to_thread(operation, request)
    return to_jsonable(response)
