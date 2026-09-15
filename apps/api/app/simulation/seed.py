from datetime import UTC, datetime, timedelta
from pathlib import Path

from alembic import command
from alembic.config import Config
from argon2 import PasswordHasher
from geoalchemy2.elements import WKTElement
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.models import (
    Ambulance,
    AmbulanceEquipment,
    Capability,
    Equipment,
    Hospital,
    HospitalCapability,
    HospitalResource,
    Notification,
    Role,
    User,
)

PASSWORD = "demo-password-change-me"
ph = PasswordHasher()


def migrate(database_url: str) -> None:
    config = Config(str(Path(__file__).resolve().parents[2] / "alembic.ini"))
    config.attributes["database_url"] = database_url
    command.upgrade(config, "head")


def reset_and_seed(session: Session, settings: Settings) -> None:
    if settings.app_env.lower() == "production":
        raise RuntimeError("Refusing to reset a production database.")
    session.execute(
        text(
            "TRUNCATE TABLE "
            "audit_logs, notifications, mission_events, reservations, "
            "acceptance_requests, routes, missions, ambulance_assignments, "
            "patient_requirement_items, incidents, ambulance_equipment, "
            "hospital_resources, hospital_capabilities, equipment, capabilities, "
            "ambulances, user_roles, users, hospitals, roles "
            "RESTART IDENTITY CASCADE"
        )
    )
    roles = [Role(code=code, name=code.replace("_", " ").title()) for code in ["DISPATCHER", "AMBULANCE_CREW", "HOSPITAL_STAFF", "HOSPITAL_ADMIN", "SYSTEM_ADMIN", "DEMO_CONTROLLER"]]
    session.add_all(roles)
    hospital_rows = []
    for number in range(1, 11):
        hospital_rows.append(Hospital(hospital_code=f"H-{number:03d}", name=f"Simulated Hospital {number:03d}", location=WKTElement(f"POINT({76.95 + number / 1000} {10.0 + number / 1000})", srid=4326), latitude=10.0 + number / 1000, longitude=76.95 + number / 1000, status="ACTIVE", emergency_capable=True, data_mode="SIMULATED"))
    session.add_all(hospital_rows)
    session.flush()
    users = []
    for role, name, hospital in [(roles[0], "Dispatcher Demo", None), (roles[1], "Crew Demo", None), (roles[2], "Hospital Staff Demo", hospital_rows[2]), (roles[4], "System Admin Demo", None), (roles[5], "Demo Controller", None)]:
        user = User(name=name, email=name.lower().replace(" ", ".") + "@demo.invalid", password_hash=ph.hash(PASSWORD), status="ACTIVE", hospital_id=hospital.id if hospital else None, roles=[role])
        users.append(user)
    session.add_all(users)
    equipment = [Equipment(code=code) for code in ["VENTILATOR", "TRAUMA_KIT", "OXYGEN"]]
    session.add_all(equipment)
    session.flush()
    for number in range(1, 11):
        ambulance = Ambulance(ambulance_code=f"AMB-{number:03d}", vehicle_type="ALS", status="AVAILABLE" if number != 3 else "DISPATCHED", current_location=WKTElement(f"POINT({76.94 + number / 1000} {10.01 + number / 1000})", srid=4326), latitude=10.01 + number / 1000, longitude=76.94 + number / 1000, gps_updated_at=datetime.now(UTC) - timedelta(seconds=120 if number == 5 else 5), crew_summary={"level": "ALS"}, data_mode="SIMULATED", version=1)
        session.add(ambulance)
        session.flush()
        for item in equipment[1:] if number == 1 else equipment:
            session.add(AmbulanceEquipment(ambulance_id=ambulance.id, equipment_id=item.id, quantity=1, status="ACTIVE"))
    capabilities = [Capability(code=code) for code in ["TRAUMA", "EMERGENCY_SURGERY", "ICU", "VENTILATOR"]]
    session.add_all(capabilities)
    session.flush()
    for hospital in hospital_rows:
        for capability in capabilities:
            if hospital.hospital_code == "H-001" and capability.code == "ICU":
                continue
            if hospital.hospital_code == "H-002" and capability.code == "TRAUMA":
                continue
            session.add(HospitalCapability(hospital_id=hospital.id, capability_id=capability.id, status="ACTIVE"))
        if hospital.hospital_code in {"H-003", "H-004", "H-005"}:
            session.add(HospitalResource(hospital_id=hospital.id, resource_type="ICU", total_capacity=1, available_capacity=1, reserved_capacity=0, occupied_capacity=0, status="ACTIVE", last_updated_at=datetime.now(UTC), version=1))
            session.add(HospitalResource(hospital_id=hospital.id, resource_type="VENTILATOR", total_capacity=1, available_capacity=1, reserved_capacity=0, occupied_capacity=0, status="ACTIVE", last_updated_at=datetime.now(UTC), version=1))
        if hospital.hospital_code == "H-006":
            session.add(HospitalResource(hospital_id=hospital.id, resource_type="ICU", total_capacity=1, available_capacity=0, reserved_capacity=0, occupied_capacity=1, status="ACTIVE", last_updated_at=datetime.now(UTC), version=1))
    session.add_all([
        Notification(
            event_type="AMBULANCE_UNAVAILABLE",
            payload={"severity": "WARNING", "message": "AMB-003 is dispatched and unavailable for new assignments.", "ambulance_code": "AMB-003"},
        ),
        Notification(
            event_type="HOSPITAL_CAPACITY_WARNING",
            payload={"severity": "CRITICAL", "message": "H-006 ICU capacity is full.", "hospital_code": "H-006", "resource_type": "ICU"},
        ),
    ])
    session.commit()
