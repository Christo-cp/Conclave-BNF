from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.core.errors import ApiError, ErrorCode
from app.db.models import Hospital, HospitalResource, Incident, PatientRequirement, User
from app.db.session import get_session
from app.services import hold_acceptance


@pytest.fixture
def db_session(test_settings):
    with get_session(test_settings.database_url)() as session:
        yield session


def test_hold_refuses_null_capacity(db_session, test_settings):
    user = User(name="Hold User", email=f"{uuid4().hex}@hold.invalid", password_hash="x", status="ACTIVE")
    hospital = Hospital(hospital_code=f"H-{uuid4().hex[:8]}", name="Hold Hospital", location="SRID=4326;POINT(1 1)", latitude=1, longitude=1, status="ACTIVE", emergency_capable=True, data_mode="SIMULATED")
    incident = Incident(incident_code=f"INC-{uuid4().hex[:8]}", incident_type="TRAUMA", severity="CRITICAL", location="SRID=4326;POINT(1 1)", latitude=1, longitude=1, patient_count=1, data_mode="SIMULATED", status="CREATED", created_by=user.id)
    db_session.add_all([user, hospital, incident])
    db_session.flush()
    db_session.add(PatientRequirement(incident_id=incident.id, requirement_code="ICU", level="REQUIRED"))
    db_session.add(HospitalResource(hospital_id=hospital.id, resource_type="ICU", total_capacity=1, available_capacity=None, reserved_capacity=0, occupied_capacity=0, status="ACTIVE", last_updated_at=datetime.now(UTC), version=1))
    db_session.commit()

    with pytest.raises(ApiError) as error:
        hold_acceptance(db_session, user, incident.id, hospital.id, uuid4().hex, test_settings)
    assert error.value.code == ErrorCode.RESOURCE_UNAVAILABLE
