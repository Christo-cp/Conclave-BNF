from sqlalchemy import select

from app.db.models import (
    Ambulance,
    Hospital,
    Incident,
    Mission,
    PatientRequirement,
    User,
)
from app.simulation.seed import reset_and_seed


def test_reset_can_run_twice_without_foreign_key_failures(migrated_test_settings, test_settings):
    from app.db.session import get_session

    with get_session(test_settings.database_url)() as session:
        reset_and_seed(session, test_settings)


def test_reset_seeds_demo_controller_user(migrated_test_settings, test_settings):
    from app.db.session import get_session

    with get_session(test_settings.database_url)() as session:
        reset_and_seed(session, test_settings)
        controller = session.scalar(select(User).where(User.email == "demo.controller@demo.invalid"))
        assert controller is not None
        assert {role.code for role in controller.roles} == {"DEMO_CONTROLLER"}


def test_reset_seeds_a6_golden_fixtures(migrated_test_settings, test_settings):
    from app.db.session import get_session

    with get_session(test_settings.database_url)() as session:
        reset_and_seed(session, test_settings)
        assert session.scalar(select(Incident).where(Incident.incident_code == "INC-000001")) is not None
        assert session.scalar(select(Mission).where(Mission.mission_code == "MSN-000001")) is not None
        assert session.scalar(select(Ambulance).where(Ambulance.ambulance_code == "AMB-004")) is not None
        assert session.scalar(select(Hospital).where(Hospital.hospital_code == "H-007")) is not None
        assert session.scalar(select(Hospital).where(Hospital.hospital_code == "H-008")) is not None
        assert session.scalar(select(PatientRequirement).where(PatientRequirement.requirement_code == "EMERGENCY_SURGERY")) is not None
    with get_session(test_settings.database_url)() as session:
        reset_and_seed(session, test_settings)
