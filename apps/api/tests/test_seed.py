from sqlalchemy import select

from app.db.models import User
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
    with get_session(test_settings.database_url)() as session:
        reset_and_seed(session, test_settings)
