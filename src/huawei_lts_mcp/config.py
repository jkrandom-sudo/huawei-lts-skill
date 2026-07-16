from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


class ConfigError(ValueError):
    """Safe configuration error that never includes credential values."""


@dataclass(frozen=True)
class LtsScope:
    region: str
    project_id: str


@dataclass(frozen=True)
class LtsConfig:
    access_key: str
    secret_key: str
    region: str | None = None
    project_id: str | None = None

    @classmethod
    def from_env(cls, env: Mapping[str, str]) -> "LtsConfig":
        access_key = env.get("HUAWEI_ACCESS_KEY", "").strip()
        secret_key = env.get("HUAWEI_SECRET_KEY", "").strip()
        missing = [
            name
            for name, value in (
                ("HUAWEI_ACCESS_KEY", access_key),
                ("HUAWEI_SECRET_KEY", secret_key),
            )
            if not value
        ]
        if missing:
            raise ConfigError("Missing required environment variable(s): " + ", ".join(missing))
        return cls(
            access_key=access_key,
            secret_key=secret_key,
            region=env.get("HUAWEI_REGION") or None,
            project_id=env.get("HUAWEI_PROJECT_ID") or None,
        )

    def resolve_scope(
        self, *, region: str | None = None, project_id: str | None = None
    ) -> LtsScope:
        resolved_region = region or self.region
        resolved_project = project_id or self.project_id
        missing = []
        if not resolved_region:
            missing.append("region or HUAWEI_REGION")
        if not resolved_project:
            missing.append("project_id or HUAWEI_PROJECT_ID")
        if missing:
            raise ConfigError("Missing LTS scope: " + ", ".join(missing))
        return LtsScope(region=resolved_region, project_id=resolved_project)
