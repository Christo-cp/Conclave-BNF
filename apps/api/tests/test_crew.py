from uuid import uuid4

import pytest

from app.assignment_service import respond_to_assignment
from app.db.models import (
    Ambulance,
    AmbulanceAssignment,
    Incident,
    Mission,
    MissionEvent,
    User,
)
from app.db.session import get_session


@pytest.fixture
def db_session(test_settings):
    with get_session(test_settings.database_url)() as session:
        yield session


def test_crew_reject_assignment_writes_mission_event(db_session):
    user = User(name="Crew", email=f"{uuid4().hex}@crew.invalid", password_hash="x", status="ACTIVE")
    incident = Incident(incident_code=f"INC-{uuid4().hex[:8]}", incident_type="TRAUMA", severity="CRITICAL", location="SRID=4326;POINT(1 1)", latitude=1, longitude=1, patient_count=1, data_mode="SIMULATED", status="DISPATCHED", created_by=user.id)
    ambulance = Ambulance(ambulance_code=f"AMB-{uuid4().hex[:8]}", vehicle_type="ALS", status="DISPATCHED", data_mode="SIMULATED", version=1)
    db_session.add_all([user, incident, ambulance])
    db_session.flush()
    assignment = AmbulanceAssignment(incident_id=incident.id, ambulance_id=ambulance.id, status="ASSIGNED", idempotency_key=uuid4().hex, assigned_by=user.id)
    mission = Mission(mission_code=f"MSN-{uuid4().hex[:8]}", incident_id=incident.id, ambulance_id=ambulance.id, status="ASSIGNED", state_version=1)
    db_session.add_all([assignment, mission])
    db_session.commit()

    result = respond_to_assignment(db_session, user.id, assignment.id, False)
    assert result.status == "REJECTED"
    assert db_session.query(MissionEvent).filter_by(event_type="AMBULANCE_ASSIGNMENT_REJECTED").count() == 1
