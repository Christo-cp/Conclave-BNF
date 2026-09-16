from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy import select

from app.db.models import (
    Hospital,
    HospitalResource,
    Incident,
    PatientRequirement,
    Role,
    User,
)
from app.db.session import get_session
from app.services import accept_request, hold_acceptance


@pytest.fixture
def db_session(test_settings):
    with get_session(test_settings.database_url)() as session:
        yield session


def test_acceptance_retry_uses_creation_key_and_updates_destination(db_session, test_settings):
    hospital = Hospital(hospital_code=f"H-{uuid4().hex[:8]}", name="Acceptance Hospital", location="SRID=4326;POINT(1 1)", latitude=1, longitude=1, status="ACTIVE", emergency_capable=True, data_mode="SIMULATED")
    db_session.add(hospital)
    db_session.flush()
    role = db_session.scalar(select(Role).where(Role.code == "HOSPITAL_STAFF"))
    assert role is not None
    user = User(name="Acceptance", email=f"{uuid4().hex}@accept.invalid", password_hash="x", status="ACTIVE", hospital_id=hospital.id, roles=[role])
    incident = Incident(incident_code=f"INC-{uuid4().hex[:8]}", incident_type="TRAUMA", severity="CRITICAL", location="SRID=4326;POINT(1 1)", latitude=1, longitude=1, patient_count=1, data_mode="SIMULATED", status="CREATED", created_by=user.id)
    db_session.add_all([user, incident])
    db_session.flush()
    db_session.add(PatientRequirement(incident_id=incident.id, requirement_code="ICU", level="REQUIRED"))
    db_session.add(HospitalResource(hospital_id=hospital.id, resource_type="ICU", total_capacity=1, available_capacity=1, reserved_capacity=0, occupied_capacity=0, status="ACTIVE", last_updated_at=datetime.now(UTC), version=1))
    db_session.commit()

    key = uuid4().hex
    request = hold_acceptance(db_session, user, incident.id, hospital.id, key, test_settings)
    accepted = accept_request(db_session, user, request.id, uuid4().hex)
    retried = accept_request(db_session, user, request.id, uuid4().hex)
    assert accepted.status == retried.status == "ACCEPTED"
