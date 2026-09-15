"""Add acceptance timestamps and decision trace linkage."""

from alembic import op

revision = "0007_acceptance_history"
down_revision = "0006_resource_events"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE acceptance_requests ADD COLUMN IF NOT EXISTS requested_at TIMESTAMPTZ")
    op.execute("ALTER TABLE acceptance_requests ADD COLUMN IF NOT EXISTS responded_at TIMESTAMPTZ")
    op.execute("ALTER TABLE acceptance_requests ADD COLUMN IF NOT EXISTS decision_run_id UUID REFERENCES decision_runs(id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_acceptance_requests_incident_status ON acceptance_requests (incident_id, status)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_acceptance_requests_expiry ON acceptance_requests (expires_at) WHERE status = 'PENDING'")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_acceptance_requests_expiry")
    op.execute("DROP INDEX IF EXISTS ix_acceptance_requests_incident_status")
    op.execute("ALTER TABLE acceptance_requests DROP COLUMN IF EXISTS decision_run_id")
    op.execute("ALTER TABLE acceptance_requests DROP COLUMN IF EXISTS responded_at")
    op.execute("ALTER TABLE acceptance_requests DROP COLUMN IF EXISTS requested_at")
