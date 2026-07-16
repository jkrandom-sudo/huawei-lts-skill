import pytest

from huawei_lts_mcp.config import ConfigError, LtsConfig


def test_config_requires_credentials_without_leaking_secret():
    with pytest.raises(ConfigError) as caught:
        LtsConfig.from_env({"HUAWEI_SECRET_KEY": "super-secret"})

    assert "HUAWEI_ACCESS_KEY" in str(caught.value)
    assert "super-secret" not in str(caught.value)


def test_explicit_scope_overrides_environment_defaults():
    config = LtsConfig.from_env(
        {
            "HUAWEI_ACCESS_KEY": "ak-placeholder",
            "HUAWEI_SECRET_KEY": "sk-placeholder",
            "HUAWEI_REGION": "region-default",
            "HUAWEI_PROJECT_ID": "project-default",
        }
    )

    scope = config.resolve_scope(region="region-explicit", project_id="project-explicit")

    assert scope.region == "region-explicit"
    assert scope.project_id == "project-explicit"


def test_scope_reports_actionable_missing_project_id():
    config = LtsConfig.from_env(
        {
            "HUAWEI_ACCESS_KEY": "ak-placeholder",
            "HUAWEI_SECRET_KEY": "sk-placeholder",
            "HUAWEI_REGION": "region-default",
        }
    )

    with pytest.raises(ConfigError, match="HUAWEI_PROJECT_ID"):
        config.resolve_scope()
