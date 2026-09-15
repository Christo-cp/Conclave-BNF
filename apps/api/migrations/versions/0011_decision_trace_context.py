"""Preserve decision inputs, trigger context and measurable duration."""

from alembic import op

revision = "0011_decision_trace_context"
down_revision = "0010_route_alternatives"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE decision_runs ADD COLUMN IF NOT EXISTS trigger VARCHAR(60)")
    op.execute("ALTER TABLE decision_runs ADD COLUMN IF NOT EXISTS input_snapshot JSONB")
    op.execute("ALTER TABLE decision_runs ADD COLUMN IF NOT EXISTS duration_ms INTEGER")
    op.execute("CREATE INDEX IF NOT EXISTS ix_decision_runs_incident_created ON decision_runs (incident_id, created_at)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_decision_candidates_run_rank ON decision_candidates (decision_run_id, rank)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_decision_candidates_run_rank")
    op.execute("DROP INDEX IF EXISTS ix_decision_runs_incident_created")
    op.execute("ALTER TABLE decision_runs DROP COLUMN IF EXISTS duration_ms")
    op.execute("ALTER TABLE decision_runs DROP COLUMN IF EXISTS input_snapshot")
    op.execute("ALTER TABLE decision_runs DROP COLUMN IF EXISTS trigger")
