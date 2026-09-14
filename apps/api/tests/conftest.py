"""API test fixtures (plan A2).

Tests use smart_ambulance_test, never the dev or demo database (db:3477-3485): the URL
from settings gets that database name swapped in, and Alembic upgrades it once.
"""

from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy.engine import make_url

from app.core.config import Settings, get_settings
from app.main import app

TEST_DATABASE = "smart_ambulance_test"
ALEMBIC_INI = Path(__file__).resolve().parents[1] / "alembic.ini"


def with_database_url(settings: Settings, **url_parts: object) -> Settings:
    url = make_url(settings.database_url).set(**url_parts)
    return settings.model_copy(
        update={"database_url": url.render_as_string(hide_password=False)}
    )


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    return with_database_url(get_settings(), database=TEST_DATABASE)


@pytest.fixture(scope="session")
def migrated_test_settings(test_settings: Settings) -> Settings:
    config = Config(str(ALEMBIC_INI))
    config.attributes["database_url"] = test_settings.database_url
    command.upgrade(config, "head")
    return test_settings


def client_for(settings: Settings) -> Iterator[TestClient]:
    app.dependency_overrides[get_settings] = lambda: settings
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def client(migrated_test_settings: Settings) -> Iterator[TestClient]:
    yield from client_for(migrated_test_settings)
