from datetime import UTC, datetime, timedelta
from uuid import uuid4

from argon2 import PasswordHasher
from geoalchemy2.elements import WKTElement
from sqlalchemy import select

from app.core.enums import MissionStatus
from app.db.models import (
    AcceptanceRequest,
    Ambulance,
    Hospital,
    Incident,
    Mission,
    Role,
    User,
)
from app.db.session import get_session
from app.services import issue_token

ph = PasswordHasher()


def make_user(session, settings, code: str, hospital_id=None) -> tuple[User, dict[str, str]]:
    role = session.scalar(select(Role).where(Role.code == code))
    if role is None:
        role = Role(code=code, name=code)
        session.add(role)
        session.flush()
    user = User(name=f"API {code}", email=f"{uuid4().hex}@example.invalid", password_hash=ph.hash("password"), status="ACTIVE", hospital_id=hospital_id, roles=[role])
    session.add(user)
    session.commit()
    return user, {"Authorization": f"Bearer {issue_token(settings, user)}"}


def test_resource_rbac_and_hospital_scope(client, test_settings):
    with get_session(test_settings.database_url)() as session:
        hospital_a = Hospital(hospital_code=f"H-{uuid4().hex[:8]}", name="A", location=WKTElement("POINT(1 1)", srid=4326), latitude=1, longitude=1, status="ACTIVE", emergency_capable=True, data_mode="SIMULATED")
        hospital_b = Hospital(hospital_code=f"H-{uuid4().hex[:8]}", name="B", location=WKTElement("POINT(2 2)", srid=4326), latitude=2, longitude=2, status="ACTIVE", emergency_capable=True, data_mode="SIMULATED")
        session.add_all([hospital_a, hospital_b])
        session.flush()
        _, no_role = make_user(session, test_settings, "DEMO_CONTROLLER")
        _, hospital_a_headers = make_user(session, test_settings, "HOSPITAL_ADMIN", hospital_a.id)

        assert client.get("/api/v1/ambulances", headers=no_role).status_code == 403
        assert client.get(f"/api/v1/hospitals/{hospital_b.id}", headers=hospital_a_headers).status_code == 403


def test_acceptance_reject_wrong_hospital_is_forbidden(client, test_settings):
    with get_session(test_settings.database_url)() as session:
        hospital_a = Hospital(hospital_code=f"H-{uuid4().hex[:8]}", name="A", location=WKTElement("POINT(1 1)", srid=4326), latitude=1, longitude=1, status="ACTIVE", emergency_capable=True, data_mode="SIMULATED")
        hospital_b = Hospital(hospital_code=f"H-{uuid4().hex[:8]}", name="B", location=WKTElement("POINT(2 2)", srid=4326), latitude=2, longitude=2, status="ACTIVE", emergency_capable=True, data_mode="SIMULATED")
        session.add_all([hospital_a, hospital_b])
        session.flush()
        user, headers = make_user(session, test_settings, "HOSPITAL_STAFF", hospital_a.id)
        incident = Incident(incident_code=f"INC-{uuid4().hex[:8]}", incident_type="TRAUMA", severity="CRITICAL", location=WKTElement("POINT(1 1)", srid=4326), latitude=1, longitude=1, patient_count=1, data_mode="SIMULATED", status="CREATED", created_by=user.id)
        request = AcceptanceRequest(incident_id=incident.id, hospital_id=hospital_b.id, status="PENDING", idempotency_key=uuid4().hex, expires_at=datetime.now(UTC) + timedelta(minutes=5))
        session.add_all([incident, request])
        session.commit()

        response = client.post(f"/api/v1/acceptance-requests/{request.id}/reject", headers=headers, json={"reason": "wrong facility"})
        assert response.status_code == 403
        assert response.json()["error"]["code"] == "AUTHORIZATION_ERROR"


def test_reservation_release_is_idempotent_at_api_boundary(client, test_settings):
    with get_session(test_settings.database_url)() as session:
        hospital = Hospital(hospital_code=f"H-{uuid4().hex[:8]}", name="A", location=WKTElement("POINT(1 1)", srid=4326), latitude=1, longitude=1, status="ACTIVE", emergency_capable=True, data_mode="SIMULATED")
        session.add(hospital)
        session.flush()
        user, headers = make_user(session, test_settings, "HOSPITAL_ADMIN", hospital.id)
        ambulance = Ambulance(ambulance_code=f"AMB-{uuid4().hex[:8]}", vehicle_type="ALS", status="AVAILABLE", data_mode="SIMULATED", version=1)
        session.add(ambulance)
        session.flush()
        incident = Incident(incident_code=f"INC-{uuid4().hex[:8]}", incident_type="TRAUMA", severity="CRITICAL", location=WKTElement("POINT(1 1)", srid=4326), latitude=1, longitude=1, patient_count=1, data_mode="SIMULATED", status="CREATED", created_by=user.id)
        session.add(incident)
        session.flush()
        from app.db.models import HospitalResource

        resource = HospitalResource(hospital_id=hospital.id, resource_type="ICU", total_capacity=1, available_capacity=1, reserved_capacity=0, occupied_capacity=0, status="ACTIVE", last_updated_at=datetime.now(UTC), version=1)
        request = AcceptanceRequest(incident_id=incident.id, hospital_id=hospital.id, status="PENDING", idempotency_key=uuid4().hex, expires_at=datetime.now(UTC) + timedelta(minutes=5))
        session.add_all([resource, request])
        session.commit()
        payload = {"acceptance_request_id": str(request.id), "incident_id": str(incident.id), "hospital_id": str(hospital.id), "hospital_resource_id": str(resource.id), "expires_at": (datetime.now(UTC) + timedelta(minutes=5)).isoformat()}

        idempotency_key = f"api-reservation-{uuid4().hex}"
        assert client.get("/api/v1/auth/me", headers=headers).json()["id"] == str(user.id)
        created = client.post("/api/v1/reservations", headers={**headers, "Idempotency-Key": idempotency_key}, json=payload)
        assert created.status_code == 200
        reservation_id = created.json()["id"]
        first = client.post(f"/api/v1/reservations/{reservation_id}/release", headers=headers, json={})
        second = client.post(f"/api/v1/reservations/{reservation_id}/release", headers=headers, json={})
        assert first.status_code == 200, first.text
        assert second.status_code == 200, second.text
        assert first.json()["status"] == second.json()["status"] == "RELEASED"


def test_mission_stale_transition_is_rejected_by_api(client, test_settings):
    with get_session(test_settings.database_url)() as session:
        user, headers = make_user(session, test_settings, "DISPATCHER")
        incident = Incident(incident_code=f"INC-{uuid4().hex[:8]}", incident_type="TRAUMA", severity="CRITICAL", location=WKTElement("POINT(1 1)", srid=4326), latitude=1, longitude=1, patient_count=1, data_mode="SIMULATED", status="CREATED", created_by=user.id)
        ambulance = Ambulance(ambulance_code=f"AMB-{uuid4().hex[:8]}", vehicle_type="ALS", status="DISPATCHED", data_mode="SIMULATED", version=1)
        session.add_all([incident, ambulance])
        session.flush()
        mission = Mission(mission_code=f"MSN-{uuid4().hex[:8]}", incident_id=incident.id, ambulance_id=ambulance.id, status=MissionStatus.ASSIGNED, state_version=4)
        session.add(mission)
        session.commit()

        response = client.patch(f"/api/v1/missions/{mission.id}", headers=headers, json={"status": "EN_ROUTE_TO_PATIENT", "state_version": 3})
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "MISSION_STATE_CONFLICT"
