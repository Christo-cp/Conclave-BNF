from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from app.core.enums import MissionStatus, ReservationStatus
from app.core.errors import ApiError, ErrorCode
from app.db.models import (
    AcceptanceRequest,
    Ambulance,
    Hospital,
    HospitalResource,
    Incident,
    Mission,
    Reservation,
    User,
)
from app.db.session import get_session
from app.mission_service import assign_destination, transition_mission
from app.reservation_service import ReservationService


@pytest.fixture
def db_session(test_settings):
    with get_session(test_settings.database_url)() as session:
        yield session


def test_invalid_mission_transition_is_rejected(db_session):
    user = User(name="Test User", email=f"{uuid4().hex}@example.com", password_hash="x", status="ACTIVE")
    db_session.add(user)
    db_session.flush()
    incident = Incident(incident_code=f"INC-{uuid4().hex[:6]}", incident_type="TRAUMA", severity="CRITICAL", latitude=1, longitude=1, location="SRID=4326;POINT(1 1)", patient_count=1, data_mode="SIMULATED", status="CREATED", created_by=user.id)
    ambulance = Ambulance(ambulance_code=f"AMB-{uuid4().hex[:3]}", vehicle_type="ALS", status="AVAILABLE", data_mode="SIMULATED", version=1)
    db_session.add_all([incident, ambulance])
    db_session.flush()
    mission = Mission(
        id=uuid4(),
        mission_code=f"MSN-{uuid4().hex[:8]}",
        incident_id=incident.id,
        ambulance_id=ambulance.id,
        status=MissionStatus.CREATED,
        state_version=1,
    )
    db_session.add(mission)
    db_session.flush()

    with pytest.raises(ApiError) as error:
        transition_mission(db_session, uuid4(), mission.id, MissionStatus.COMPLETED, 1)

    assert error.value.code == ErrorCode.CONFLICT


def test_destination_assignment_requires_reservation_and_writes_audit_event(db_session):
    user = User(name="Test User", email=f"{uuid4().hex}@example.com", password_hash="x", status="ACTIVE")
    db_session.add(user)
    db_session.flush()
    incident = Incident(incident_code=f"INC-{uuid4().hex[:6]}", incident_type="TRAUMA", severity="CRITICAL", latitude=1, longitude=1, location="SRID=4326;POINT(1 1)", patient_count=1, data_mode="SIMULATED", status="CREATED", created_by=user.id)
    ambulance = Ambulance(ambulance_code=f"AMB-{uuid4().hex[:3]}", vehicle_type="ALS", status="AVAILABLE", data_mode="SIMULATED", version=1)
    db_session.add_all([incident, ambulance])
    db_session.flush()
    mission = Mission(
        mission_code="MSN-000002",
        incident_id=incident.id,
        ambulance_id=ambulance.id,
        status=MissionStatus.ASSIGNED,
        state_version=1,
    )
    db_session.add(mission)
    db_session.flush()

    with pytest.raises(ApiError) as error:
        assign_destination(db_session, uuid4(), mission.id, uuid4(), None)

    assert error.value.code == ErrorCode.RESOURCE_UNAVAILABLE


def test_reservation_expiry_restores_capacity_once(db_session):
    user = User(name="Test User", email=f"{uuid4().hex}@example.com", password_hash="x", status="ACTIVE")
    db_session.add(user)
    db_session.flush()
    incident = Incident(incident_code=f"INC-{uuid4().hex[:6]}", incident_type="TRAUMA", severity="CRITICAL", latitude=1, longitude=1, location="SRID=4326;POINT(1 1)", patient_count=1, data_mode="SIMULATED", status="CREATED", created_by=user.id)
    hospital = Hospital(hospital_code=f"H-{uuid4().hex[:3]}", name="Test Hospital", location="SRID=4326;POINT(1 1)", latitude=1, longitude=1, status="ACTIVE", emergency_capable=True, data_mode="SIMULATED")
    db_session.add_all([incident, hospital])
    db_session.flush()
    request = AcceptanceRequest(incident_id=incident.id, hospital_id=hospital.id, status="PENDING", idempotency_key=uuid4().hex, expires_at=datetime.now(UTC) - timedelta(seconds=1))
    db_session.add(request)
    db_session.flush()
    resource = HospitalResource(
        hospital_id=hospital.id,
        resource_type="ICU",
        total_capacity=1,
        available_capacity=0,
        reserved_capacity=1,
        occupied_capacity=0,
        status="ACTIVE",
        last_updated_at=datetime.now(UTC),
        version=2,
    )
    db_session.add(resource)
    db_session.flush()
    reservation = Reservation(
        reservation_code=f"RES-{uuid4().hex[:12]}",
        acceptance_request_id=request.id,
        incident_id=incident.id,
        hospital_id=resource.hospital_id,
        hospital_resource_id=resource.id,
        status=ReservationStatus.HELD,
        expires_at=datetime.now(UTC) - timedelta(seconds=1),
    )
    db_session.add(reservation)
    db_session.flush()

    service = ReservationService(db_session)
    service.expire(reservation.id)
    service.expire(reservation.id)
    db_session.refresh(resource)

    assert resource.available_capacity == 1
    assert resource.reserved_capacity == 0
    assert db_session.get(Reservation, reservation.id).status == ReservationStatus.EXPIRED
