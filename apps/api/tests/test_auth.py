from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt

from app.db.models import Role, User
from app.db.session import get_session
from app.services import issue_token


def test_malformed_token_is_rejected_with_authentication_error(client):
    response = client.get("/api/v1/ambulances", headers={"Authorization": "Bearer malformed-token"})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_ERROR"


def test_expired_token_is_rejected_with_authentication_error(client, test_settings):
    token = jwt.encode(
        {"sub": str(uuid4()), "exp": datetime.now(UTC) - timedelta(minutes=1)},
        test_settings.jwt_secret,
        algorithm=test_settings.jwt_algorithm,
    )
    response = client.get("/api/v1/ambulances", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_ERROR"


def test_valid_login_token_can_read_ambulances(client, test_settings):
    with get_session(test_settings.database_url)() as session:
        role = session.query(Role).filter_by(code="DISPATCHER").one()
        user = User(name="Auth Test", email=f"{uuid4().hex}@auth.invalid", password_hash="unused", status="ACTIVE", roles=[role])
        session.add(user)
        session.commit()
        token = issue_token(test_settings, user)
    response = client.get("/api/v1/ambulances", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
