"""Harden simulation metadata and historical records before the demo milestone."""

from alembic import op

revision = "0015_simulation_integrity"
down_revision = "0014_simulation_events"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE simulation_scenarios DROP CONSTRAINT IF EXISTS ck_simulation_scenario_status")
    op.execute("ALTER TABLE simulation_scenarios ADD CONSTRAINT ck_simulation_scenario_status CHECK (status IN ('READY', 'RUNNING', 'COMPLETED', 'DISABLED'))")
    op.execute("ALTER TABLE simulation_events DROP CONSTRAINT IF EXISTS ck_simulation_event_type")
    op.execute("ALTER TABLE simulation_events ADD CONSTRAINT ck_simulation_event_type CHECK (event_type <> '')")
    op.execute("""
        CREATE OR REPLACE FUNCTION reject_simulation_event_change() RETURNS trigger AS $$
        BEGIN
            IF OLD.executed_at IS NOT NULL THEN
                RAISE EXCEPTION 'executed simulation event cannot be changed';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql
    """)
    op.execute("DROP TRIGGER IF EXISTS simulation_event_execution_guard ON simulation_events")
    op.execute("CREATE TRIGGER simulation_event_execution_guard BEFORE UPDATE ON simulation_events FOR EACH ROW EXECUTE FUNCTION reject_simulation_event_change()")


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS simulation_event_execution_guard ON simulation_events")
    op.execute("DROP FUNCTION IF EXISTS reject_simulation_event_change()")
    op.execute("ALTER TABLE simulation_events DROP CONSTRAINT IF EXISTS ck_simulation_event_type")
    op.execute("ALTER TABLE simulation_scenarios DROP CONSTRAINT IF EXISTS ck_simulation_scenario_status")
