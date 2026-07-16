from huaweicloudsdklts.v2 import LtsClient

from huawei_lts_mcp.client import build_client
from huawei_lts_mcp.config import LtsConfig, LtsScope


def test_build_client_resolves_region_name_for_sdk_builder():
    config = LtsConfig(
        access_key="ak-placeholder",
        secret_key="sk-placeholder",
    )
    scope = LtsScope(
        region="cn-north-4",
        project_id="project-placeholder",
    )

    client = build_client(config, scope)

    assert isinstance(client, LtsClient)
