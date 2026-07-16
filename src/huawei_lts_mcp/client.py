from __future__ import annotations

from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdklts.v2 import LtsClient
from huaweicloudsdklts.v2.region.lts_region import LtsRegion

from .config import LtsConfig, LtsScope


def build_client(config: LtsConfig, scope: LtsScope) -> LtsClient:
    credentials = BasicCredentials(
        ak=config.access_key,
        sk=config.secret_key,
        project_id=scope.project_id,
    )
    return (
        LtsClient.new_builder()
        .with_credentials(credentials)
        .with_region(LtsRegion.value_of(scope.region))
        .build()
    )
