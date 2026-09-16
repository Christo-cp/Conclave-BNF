from uuid import uuid4

import pytest
from geoalchemy2.elements import WKTElement

from app.db.models import Hospital, Incident, Role, User
from app.db.session import get_session
from app.services import issue_token


def make_user(session, settings, role_code: str, hospital_id=None):
    from sqlalchemy import select

    role = session.scalar(select(Role).where(Role.code == role_code))
    assert role is not None
    user = User(
        name=f"RBAC {role_code} {uuid4().hex[:6]}",
        email=f"{uuid4().hex}@rbac.invalid",
        password_hash="unused",
        status="ACTIVE",
        hospital_id=hospital_id,
        roles=[role],
    )
    session.add(user)
    session.commit()
    return user, {"Authorization": f"Bearer {issue_token(settings, user)}"}


@pytest.mark.parametrize("role_code", ["HOSPITAL_STAFF", "HOSPITAL_ADMIN", "AMBULANCE_CREW", "DEMO_CONTROLLER"])
def test_dispatch_match_requires_dispatcher_or_system_admin(client, test_settings, role_code):
    with get_session(test_settings.database_url)() as session:
        hospital = Hospital(hospital_code=f"H-{uuid4().hex[:8]}", name="RBAC Hospital", location=WKTElement("POINT(1 1)", srid=4326), latitude=1, longitude=1, status="ACTIVE", emergency_capable=True, data_mode="SIMULATED")
        session.add(hospital)
        session.flush()
        user, headers = make_user(session, test_settings, role_code, hospital.id if role_code.startswith("HOSPITAL") else None)
        incident = Incident(incident_code=f"INC-{uuid4().hex[:8]}", incident_type="TRAUMA", severity="CRITICAL", location=WKTElement("POINT(1 1)", srid=4326), latitude=1, longitude=1, patient_count=1, data_mode="SIMULATED", status="CREATED", created_by=user.id)
        session.add(incident)
        session.commit()
        response = client.post("/api/v1/dispatch/ambulances/match", headers=headers, json={"incident_id": str(incident.id)})
        assert response.status_code == 403
        assert response.json()["error"]["code"] == "AUTHORIZATION_ERROR"


def test_missing_incident_uses_error_envelope(client, test_settings):
    with get_session(test_settings.database_url)() as session:
        _, headers = make_user(session, test_settings, "DISPATCHER")
    response = client.get(f"/api/v1/incidents/{uuid4()}", headers=headers)
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"
