"""Add ordered simulation events for repeatable demo failures."""

from alembic import op

revision = "0014_simulation_events"
down_revision = "0013_simulation_scenarios"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS simulation_events (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            scenario_id UUID NOT NULL REFERENCES simulation_scenarios(id) ON DELETE CASCADE,
            sequence_number INTEGER NOT NULL,
            delay_ms INTEGER NOT NULL,
            event_type VARCHAR(60) NOT NULL,
            payload JSONB NOT NULL,
            executed_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL,
            CONSTRAINT uq_simulation_event_sequence UNIQUE (scenario_id, sequence_number),
            CONSTRAINT ck_simulation_event_delay_nonnegative CHECK (delay_ms >= 0)
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_simulation_events_pending ON simulation_events (scenario_id, sequence_number) WHERE executed_at IS NULL")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_simulation_events_pending")
    op.execute("DROP TABLE IF EXISTS simulation_events")
