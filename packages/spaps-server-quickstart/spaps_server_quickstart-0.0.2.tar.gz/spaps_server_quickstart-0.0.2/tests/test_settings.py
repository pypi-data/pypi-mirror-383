from __future__ import annotations

import pytest

from spaps_server_quickstart.settings import (
    BaseServiceSettings,
    create_settings_loader,
)


class ExampleSettings(BaseServiceSettings):
    app_name: str = "Example Service"
    service_slug: str = "example-service"
    database_url: str = "postgresql+asyncpg://user:pass@host:5432/example"
    redis_url: str = "redis://localhost:6379/1"


class NoSlugSettings(BaseServiceSettings):
    app_name: str = "Slugless Service"
    database_url: str = "postgresql+asyncpg://user:pass@host:5432/slugless"


def test_settings_loader_caches_instances() -> None:
    loader = create_settings_loader(ExampleSettings)
    first = loader()
    second = loader()

    assert first is second
    assert first.resolved_service_slug == "example-service"
    assert first.logger_namespace == "example-service"
    assert first.celery_app_name == "example_service"
    assert first.resolved_celery_broker_url == "redis://localhost:6379/1"
    assert first.resolved_celery_result_backend == "redis://localhost:6379/1"
    assert first.sync_database_url == "postgresql+psycopg://user:pass@host:5432/example"


def test_settings_slug_falls_back_to_app_name() -> None:
    settings = NoSlugSettings()

    assert settings.resolved_service_slug == "slugless-service"
    assert settings.celery_app_name == "slugless_service"


def test_database_url_validation() -> None:
    with pytest.raises(ValueError):
        ExampleSettings(database_url="")
