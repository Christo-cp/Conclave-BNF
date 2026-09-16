from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from app.db.models import (
    AcceptanceRequest,
    Hospital,
    HospitalResource,
    Incident,
    Reservation,
    User,
)
from app.db.session import get_session
from app.sweeper import expire_holds


@pytest.fixture
def db_session(test_settings):
    with get_session(test_settings.database_url)() as session:
        yield session


def test_sweeper_expires_hold_restores_capacity_once(db_session):
    user = User(name="Sweep User", email=f"{uuid4().hex}@sweep.invalid", password_hash="x", status="ACTIVE")
    hospital = Hospital(hospital_code=f"H-{uuid4().hex[:8]}", name="Sweep Hospital", location="SRID=4326;POINT(1 1)", latitude=1, longitude=1, status="ACTIVE", emergency_capable=True, data_mode="SIMULATED")
    incident = Incident(incident_code=f"INC-{uuid4().hex[:8]}", incident_type="TRAUMA", severity="CRITICAL", location="SRID=4326;POINT(1 1)", latitude=1, longitude=1, patient_count=1, data_mode="SIMULATED", status="CREATED", created_by=user.id)
    db_session.add_all([user, hospital, incident])
    db_session.flush()
    resource = HospitalResource(hospital_id=hospital.id, resource_type="ICU", total_capacity=1, available_capacity=0, reserved_capacity=1, occupied_capacity=0, status="ACTIVE", last_updated_at=datetime.now(UTC), version=2)
    request = AcceptanceRequest(incident_id=incident.id, hospital_id=hospital.id, status="PENDING", idempotency_key=uuid4().hex, expires_at=datetime.now(UTC) - timedelta(seconds=1))
    db_session.add_all([resource, request])
    db_session.flush()
    reservation = Reservation(reservation_code=f"RES-{uuid4().hex[:8]}", acceptance_request_id=request.id, incident_id=incident.id, hospital_id=hospital.id, hospital_resource_id=resource.id, status="HELD", expires_at=request.expires_at)
    db_session.add(reservation)
    db_session.commit()

    assert expire_holds(db_session) == 1
    assert expire_holds(db_session) == 0
    db_session.refresh(resource)
    assert resource.available_capacity == 1
    assert resource.reserved_capacity == 0
