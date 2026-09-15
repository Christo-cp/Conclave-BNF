from app.simulation.seed import reset_and_seed


def test_reset_can_run_twice_without_foreign_key_failures(migrated_test_settings, test_settings):
    from app.db.session import get_session

    with get_session(test_settings.database_url)() as session:
        reset_and_seed(session, test_settings)
    with get_session(test_settings.database_url)() as session:
        reset_and_seed(session, test_settings)
