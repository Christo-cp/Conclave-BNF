"""Record every hospital resource capacity change as append-only history."""

from alembic import op

revision = "0006_resource_events"
down_revision = "0005_hospital_capability_indexes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS resource_events (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            hospital_resource_id UUID NOT NULL REFERENCES hospital_resources(id),
            event_type VARCHAR(50) NOT NULL,
            old_available INTEGER,
            new_available INTEGER,
            old_reserved INTEGER,
            new_reserved INTEGER,
            source VARCHAR(50) NOT NULL,
            actor_id UUID REFERENCES users(id),
            created_at TIMESTAMPTZ NOT NULL
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_resource_events_resource_created ON resource_events (hospital_resource_id, created_at)")
    op.execute("""
        CREATE OR REPLACE FUNCTION reject_resource_event_change() RETURNS trigger AS $$
        BEGIN RAISE EXCEPTION 'append-only record cannot be changed'; END;
        $$ LANGUAGE plpgsql
    """)
    op.execute("DROP TRIGGER IF EXISTS resource_events_append_only ON resource_events")
    op.execute("CREATE TRIGGER resource_events_append_only BEFORE UPDATE OR DELETE ON resource_events FOR EACH ROW EXECUTE FUNCTION reject_resource_event_change()")


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS resource_events_append_only ON resource_events")
    op.execute("DROP FUNCTION IF EXISTS reject_resource_event_change()")
    op.execute("DROP INDEX IF EXISTS ix_resource_events_resource_created")
    op.execute("DROP TABLE IF EXISTS resource_events")
