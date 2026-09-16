from fastapi.testclient import TestClient

from app.main import app


def test_configured_cors_origin_is_allowed():
    response = TestClient(app).options(
        "/api/v1/health/db",
        headers={
            "Origin": "http://127.0.0.1:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:5173"
