"""Plan S0: GET /api/v1/health/db."""

import socket

from fastapi.testclient import TestClient
from sqlalchemy.engine import make_url

from app.core.config import Settings
from tests.conftest import client_for, with_database_url

HEALTH_DB = "/api/v1/health/db"


def unused_local_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def test_health_db_up(client: TestClient) -> None:
    response = client.get(HEALTH_DB)

    assert response.status_code == 200
    assert response.json() == {
        "connectivity": "ok",
        "migration_version": None,
        "simple_query": 1,
    }
    assert response.headers["X-Request-ID"].startswith("req_")


def test_health_db_unreachable_503_envelope(test_settings: Settings) -> None:
    port = unused_local_port()
    unreachable = with_database_url(test_settings, host="127.0.0.1", port=port)
    secret = make_url(unreachable.database_url).password

    for test_client in client_for(unreachable):
        response = test_client.get(
            HEALTH_DB, headers={"X-Request-ID": "req_test_unreachable"}
        )

    assert response.status_code == 503
    assert response.json() == {
        "error": {
            "code": "INTERNAL_ERROR",
            "message": "Database health check failed.",
            "request_id": "req_test_unreachable",
        }
    }
    assert response.headers["X-Request-ID"] == "req_test_unreachable"
    for detail in (secret, str(port), "127.0.0.1", "smart_ambulance_test"):
        assert detail and detail not in response.text
