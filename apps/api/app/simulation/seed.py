from datetime import UTC, datetime, timedelta
from pathlib import Path

from alembic import command
from alembic.config import Config
from argon2 import PasswordHasher
from geoalchemy2.elements import WKTElement
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.models import (
    Ambulance,
    AmbulanceAssignment,
    AmbulanceEquipment,
    Capability,
    Equipment,
    Hospital,
    HospitalCapability,
    HospitalResource,
    Incident,
    Mission,
    Notification,
    PatientRequirement,
    Role,
    SimulationScenario,
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
            "audit_logs, notifications, mission_events, simulation_events, simulation_scenarios, reservations, "
            "acceptance_requests, routes, missions, ambulance_assignments, "
            "patient_requirement_items, incidents, ambulance_equipment, "
            "hospital_resources, hospital_capabilities, equipment, capabilities, "
            "ambulances, user_roles, users, hospitals, roles "
            "RESTART IDENTITY CASCADE"
        )
    )
    roles = [Role(code=code, name=code.replace("_", " ").title()) for code in ["DISPATCHER", "AMBULANCE_CREW", "HOSPITAL_STAFF", "HOSPITAL_ADMIN", "SYSTEM_ADMIN", "DEMO_CONTROLLER"]]
    session.add_all(roles)
    seed_now = datetime(2026, 9, 12, 12, 30, tzinfo=UTC)
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
        ambulance = Ambulance(ambulance_code=f"AMB-{number:03d}", vehicle_type="ALS", status="AVAILABLE" if number != 3 else "DISPATCHED", current_location=WKTElement(f"POINT({76.94 + number / 1000} {10.01 + number / 1000})", srid=4326), latitude=10.01 + number / 1000, longitude=76.94 + number / 1000, gps_updated_at=seed_now - timedelta(seconds=120 if number == 5 else 5), crew_summary={"level": "ALS"}, data_mode="SIMULATED", version=1)
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
            session.add(HospitalResource(hospital_id=hospital.id, resource_type="ICU", total_capacity=1, available_capacity=1, reserved_capacity=0, occupied_capacity=0, status="ACTIVE", last_updated_at=seed_now, version=1))
            session.add(HospitalResource(hospital_id=hospital.id, resource_type="VENTILATOR", total_capacity=1, available_capacity=1, reserved_capacity=0, occupied_capacity=0, status="ACTIVE", last_updated_at=seed_now, version=1))
        if hospital.hospital_code == "H-006":
            session.add(HospitalResource(hospital_id=hospital.id, resource_type="ICU", total_capacity=1, available_capacity=0, reserved_capacity=0, occupied_capacity=1, status="ACTIVE", last_updated_at=seed_now, version=1))
        if hospital.hospital_code == "H-007":
            session.add(HospitalResource(hospital_id=hospital.id, resource_type="ICU", total_capacity=1, available_capacity=None, reserved_capacity=0, occupied_capacity=0, status="ACTIVE", last_updated_at=seed_now, version=1))
            session.add(HospitalResource(hospital_id=hospital.id, resource_type="VENTILATOR", total_capacity=1, available_capacity=1, reserved_capacity=0, occupied_capacity=0, status="ACTIVE", last_updated_at=seed_now, version=1))
        if hospital.hospital_code == "H-008":
            session.add(HospitalResource(hospital_id=hospital.id, resource_type="ICU", total_capacity=1, available_capacity=1, reserved_capacity=0, occupied_capacity=0, status="ACTIVE", last_updated_at=seed_now - timedelta(seconds=900), version=1))
            session.add(HospitalResource(hospital_id=hospital.id, resource_type="VENTILATOR", total_capacity=1, available_capacity=1, reserved_capacity=0, occupied_capacity=0, status="ACTIVE", last_updated_at=seed_now, version=1))

    dispatcher = users[0]
    golden_incident = Incident(
        incident_code="INC-000001",
        incident_type="TRAUMA",
        severity="CRITICAL",
        location=WKTElement("POINT(76.95 10.0)", srid=4326),
        latitude=10.0,
        longitude=76.95,
        address_text="Simulated Golden Incident",
        patient_count=1,
        notes="Deterministic A6 golden scenario.",
        data_mode="SIMULATED",
        status="CREATED",
        created_by=dispatcher.id,
    )
    session.add(golden_incident)
    session.flush()
    session.add_all([
        PatientRequirement(incident_id=golden_incident.id, requirement_code=code, level="REQUIRED")
        for code in ("ICU", "TRAUMA", "VENTILATOR", "EMERGENCY_SURGERY")
    ])
    seeded_ambulance = session.scalar(select(Ambulance).where(Ambulance.ambulance_code == "AMB-003"))
    if seeded_ambulance is None:
        raise RuntimeError("Golden seed ambulance AMB-003 was not created.")
    seeded_assignment = AmbulanceAssignment(incident_id=golden_incident.id, ambulance_id=seeded_ambulance.id, status="ASSIGNED", idempotency_key="seed-assignment-000001", assigned_by=dispatcher.id)
    seeded_mission = Mission(mission_code="MSN-000001", incident_id=golden_incident.id, ambulance_id=seeded_ambulance.id, status="ASSIGNED", state_version=1)
    session.add_all([seeded_assignment, seeded_mission])
    crew = users[1]
    crew.ambulance_id = seeded_ambulance.id
    session.add(SimulationScenario(
        scenario_code="GOLDEN_2026",
        name="A6 golden scenario",
        description="Deterministic synthetic ambulance and hospital routing inputs.",
        initial_state={"incident_code": "INC-000001"},
        configuration={
            "default_ambulance_eta_s": 900,
            "default_hospital_eta_s": 1800,
            "ambulance_etas": {"AMB-001": 240, "AMB-002": 420, "AMB-003": 360, "AMB-004": 540, "AMB-005": 600},
            "hospital_etas": {"H-001": 300, "H-002": 480, "H-003": 600, "H-004": 780, "H-005": 960, "H-006": 1080, "H-007": 1140, "H-008": 1200},
            "routes": {
                "default": {
                    "distance_m": 10000, "duration_seconds": 1200, "traffic_duration_seconds": 1200, "confidence": 0.95,
                    "alternatives": {"alternative": {"distance_m": 11800, "duration_seconds": 1080, "traffic_duration_seconds": 1080, "confidence": 0.9}},
                },
                "AMB-003:INC-000001": {
                    "distance_m": 2800, "duration_seconds": 360, "traffic_duration_seconds": 360, "confidence": 0.95,
                    "alternatives": {"alternative": {"distance_m": 3400, "duration_seconds": 300, "traffic_duration_seconds": 300, "confidence": 0.9}},
                },
                "INC-000001:H-003": {
                    "distance_m": 4200, "duration_seconds": 600, "traffic_duration_seconds": 600, "confidence": 0.95,
                    "alternatives": {"alternative": {"distance_m": 5100, "duration_seconds": 540, "traffic_duration_seconds": 540, "confidence": 0.9}},
                },
                "INC-000001:H-004": {
                    "distance_m": 5200, "duration_seconds": 780, "traffic_duration_seconds": 780, "confidence": 0.95,
                    "alternatives": {"alternative": {"distance_m": 6000, "duration_seconds": 720, "traffic_duration_seconds": 720, "confidence": 0.9}},
                },
                "INC-000001:H-005": {
                    "distance_m": 6400, "duration_seconds": 960, "traffic_duration_seconds": 960, "confidence": 0.95,
                    "alternatives": {"alternative": {"distance_m": 7300, "duration_seconds": 900, "traffic_duration_seconds": 900, "confidence": 0.9}},
                },
            },
        },
        seed=2026,
        status="READY",
        created_at=seed_now,
    ))
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
