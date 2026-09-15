from __future__ import annotations

from datetime import UTC, datetime, timedelta
from threading import Barrier, Thread
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, delete, select, text, update
from sqlalchemy.exc import DBAPIError, IntegrityError

from app.core.enums import ReservationStatus
from app.core.errors import ApiError, ErrorCode
from app.db.models import (
    AcceptanceRequest,
    AuditLog,
    Hospital,
    HospitalResource,
    Incident,
    Notification,
    Reservation,
    User,
)
from app.db.session import get_session
from app.reservation_service import ReservationService


def _reservation(
    incident: Incident,
    hospital: Hospital,
    resource: HospitalResource,
    request: AcceptanceRequest,
    *,
    code: str | None = None,
) -> Reservation:
    return Reservation(
        reservation_code=code or f"RES-{uuid4().hex[:12]}",
        acceptance_request_id=request.id,
        incident_id=incident.id,
        hospital_id=hospital.id,
        hospital_resource_id=resource.id,
        status=ReservationStatus.HELD,
        expires_at=datetime.now(UTC) + timedelta(minutes=5),
    )


@pytest.fixture
def capacity_unit(test_settings: object) -> tuple[object, object, object, object, object]:
    with get_session(test_settings.database_url)() as session:  # type: ignore[attr-defined]
        user = User(
            name="Concurrency Test User",
            email=f"{uuid4().hex}@example.com",
            password_hash="test",
            status="ACTIVE",
        )
        hospital = Hospital(
            hospital_code=f"H-{uuid4().hex[:8]}",
            name="Concurrency Hospital",
            location="SRID=4326;POINT(1 1)",
            latitude=1,
            longitude=1,
            status="ACTIVE",
            emergency_capable=True,
            data_mode="SIMULATED",
        )
        incident = Incident(
            incident_code=f"INC-{uuid4().hex[:8]}",
            incident_type="TRAUMA",
            severity="CRITICAL",
            location="SRID=4326;POINT(1 1)",
            latitude=1,
            longitude=1,
            patient_count=1,
            data_mode="SIMULATED",
            status="CREATED",
            created_by=user.id,
        )
        resource = HospitalResource(
            hospital_id=hospital.id,
            resource_type="ICU",
            total_capacity=1,
            available_capacity=1,
            reserved_capacity=0,
            occupied_capacity=0,
            status="ACTIVE",
            version=1,
        )
        session.add_all([user, hospital, incident, resource])
        session.flush()
        requests = [
            AcceptanceRequest(
                incident_id=incident.id,
                hospital_id=hospital.id,
                status="ACCEPTED",
                idempotency_key=uuid4().hex,
                expires_at=datetime.now(UTC) + timedelta(minutes=5),
            )
            for _ in range(2)
        ]
        session.add_all(requests)
        session.commit()
        return (
            test_settings,
            incident.id,
            hospital.id,
            resource.id,
            [request.id for request in requests],
        )


def test_two_concurrent_reservations_on_one_unit_have_one_winner(capacity_unit):
    settings, incident_id, hospital_id, resource_id, request_ids = capacity_unit
    ready = Barrier(2)
    results: list[str] = []
    errors: list[Exception] = []

    def attempt(request_id) -> None:
        try:
            with get_session(settings.database_url)() as session:
                reservation = _reservation(
                    Incident(id=incident_id),
                    Hospital(id=hospital_id),
                    HospitalResource(id=resource_id),
                    AcceptanceRequest(id=request_id),
                )
                ready.wait()
                ReservationService(session).reserve(reservation)
                results.append("succeeded")
        except ApiError as error:
            assert error.code == ErrorCode.RESOURCE_UNAVAILABLE
            results.append("failed")
        except (AssertionError, DBAPIError) as error:  # report unexpected thread failures
            errors.append(error)
            results.append("failed")

    threads = [Thread(target=attempt, args=(request_id,)) for request_id in request_ids]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=10)

    assert not errors
    assert results.count("succeeded") == 1
    assert results.count("failed") == 1

    with get_session(settings.database_url)() as session:
        resource = session.get(HospitalResource, resource_id)
        assert resource is not None
        assert resource.available_capacity == 0
        assert resource.reserved_capacity == 1
        assert session.scalar(
            select(Reservation).where(Reservation.hospital_resource_id == resource_id)
        ) is not None


def test_failed_reservation_rolls_back_capacity(capacity_unit):
    settings, incident_id, hospital_id, resource_id, request_ids = capacity_unit
    with get_session(settings.database_url)() as session:
        resource = session.get(HospitalResource, resource_id)
        assert resource is not None
        before = (resource.available_capacity, resource.reserved_capacity, resource.version)
        duplicate_request = session.get(AcceptanceRequest, request_ids[0])
        assert duplicate_request is not None
        invalid = _reservation(
            Incident(id=incident_id),
            Hospital(id=hospital_id),
            HospitalResource(id=resource_id),
            AcceptanceRequest(id=duplicate_request.id),
        )
        invalid.reservation_code = None  # database NOT NULL constraint must roll back the update

        with pytest.raises(IntegrityError):
            ReservationService(session).reserve(invalid)
        session.rollback()

    with get_session(settings.database_url)() as session:
        resource = session.get(HospitalResource, resource_id)
        assert resource is not None
        assert (resource.available_capacity, resource.reserved_capacity, resource.version) == before
        assert session.scalar(select(Reservation).where(Reservation.hospital_resource_id == resource_id)) is None


def test_releasing_reservation_with_unknown_capacity_is_rejected(capacity_unit):
    settings, incident_id, hospital_id, resource_id, request_ids = capacity_unit
    with get_session(settings.database_url)() as session:
        resource = session.get(HospitalResource, resource_id)
        assert resource is not None
        resource.available_capacity = None
        reservation = _reservation(
            Incident(id=incident_id),
            Hospital(id=hospital_id),
            HospitalResource(id=resource_id),
            AcceptanceRequest(id=request_ids[0]),
        )
        session.add(reservation)
        session.commit()
        reservation_id = reservation.id

        with pytest.raises(ApiError) as error:
            ReservationService(session).release(reservation_id)
        assert error.value.code == ErrorCode.RESOURCE_UNAVAILABLE

        session.rollback()
        resource = session.get(HospitalResource, resource_id)
        assert resource is not None
        assert resource.available_capacity is None
        assert session.get(Reservation, reservation_id).status == ReservationStatus.HELD


@pytest.mark.parametrize("model, table_name, values", [
    (AuditLog, "audit_logs", {"action": "TEST", "entity_type": "TEST", "entity_id": "x"}),
    (Notification, "notifications", {"event_type": "TEST"}),
])
def test_append_only_records_reject_update_and_delete(test_settings, model, table_name, values):
    with get_session(test_settings.database_url)() as session:
        record = model(**values)
        session.add(record)
        session.commit()
        record_id = record.id

        with pytest.raises(DBAPIError, match="append-only record cannot be changed"):
            session.execute(update(model).where(model.id == record_id).values(**values))
        session.rollback()

        with pytest.raises(DBAPIError, match="append-only record cannot be changed"):
            session.execute(delete(model).where(model.id == record_id))
        session.rollback()
        assert session.scalar(select(model).where(model.id == record_id)) is not None

        trigger = session.execute(
            text("SELECT 1 FROM pg_trigger WHERE tgname = :name"),
            {"name": f"{table_name}_append_only"},
        ).scalar_one_or_none()
        assert trigger == 1


def test_mission_event_append_only_trigger_rejects_update_and_delete(test_settings):
    event_id = uuid4()
    with get_session(test_settings.database_url)() as session:
        session.execute(
            text("INSERT INTO mission_events (id, event_type, payload, created_at) VALUES (:id, 'TEST', '{}', now())"),
            {"id": event_id},
        )
        session.commit()

        with pytest.raises(DBAPIError, match="append-only record cannot be changed"):
            session.execute(
                text("UPDATE mission_events SET event_type = 'CHANGED' WHERE id = :id"),
                {"id": event_id},
            )
        session.rollback()
        with pytest.raises(DBAPIError, match="append-only record cannot be changed"):
            session.execute(text("DELETE FROM mission_events WHERE id = :id"), {"id": event_id})
        session.rollback()
        assert session.execute(
            text("SELECT 1 FROM mission_events WHERE id = :id"), {"id": event_id}
        ).scalar_one() == 1


def test_s7_s12_migration_roundtrip_in_isolated_database(test_settings):
    base_url = create_engine(test_settings.database_url).url
    database_name = f"smart_ambulance_migration_{uuid4().hex}"
    admin_url = base_url.set(database="postgres")
    database_url = base_url.set(database=database_name)
    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    database_engine = create_engine(database_url)
    alembic_ini = str(__import__("pathlib").Path(__file__).resolve().parents[1] / "alembic.ini")

    try:
        with admin_engine.connect() as connection:
            connection.execute(text(f'CREATE DATABASE "{database_name}"'))
        config = Config(alembic_ini)
        config.attributes["database_url"] = database_url.render_as_string(hide_password=False)
        command.upgrade(config, "head")
        command.downgrade(config, "0001_mvp_schema")
        command.upgrade(config, "head")
        with database_engine.connect() as connection:
            assert connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one() == "0015_simulation_integrity"
    finally:
        database_engine.dispose()
        with admin_engine.connect() as connection:
            connection.execute(text(f'DROP DATABASE IF EXISTS "{database_name}" WITH (FORCE)'))
        admin_engine.dispose()
