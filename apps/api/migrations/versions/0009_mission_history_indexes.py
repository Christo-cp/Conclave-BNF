"""Index mission history for ordered state and destination updates."""

from alembic import op

revision = "0009_mission_history_indexes"
down_revision = "0008_reservation_invariants"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE INDEX IF NOT EXISTS ix_missions_incident_status ON missions (incident_id, status)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_mission_events_mission_created ON mission_events (mission_id, created_at)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_notifications_incident_created ON notifications (incident_id, created_at)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_notifications_incident_created")
    op.execute("DROP INDEX IF EXISTS ix_mission_events_mission_created")
    op.execute("DROP INDEX IF EXISTS ix_missions_incident_status")
