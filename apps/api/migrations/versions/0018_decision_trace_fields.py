"""Expose decision trace fields already present in the S11 schema."""

from alembic import op

revision = "0018_decision_trace_fields"
down_revision = "0017_crew_scope"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE decision_runs ADD COLUMN IF NOT EXISTS trigger VARCHAR(60)")
    op.execute("ALTER TABLE decision_runs ADD COLUMN IF NOT EXISTS input_snapshot JSONB")
    op.execute("ALTER TABLE decision_runs ADD COLUMN IF NOT EXISTS duration_ms INTEGER")


def downgrade() -> None:
    op.execute("ALTER TABLE decision_runs DROP COLUMN IF EXISTS duration_ms")
    op.execute("ALTER TABLE decision_runs DROP COLUMN IF EXISTS input_snapshot")
    op.execute("ALTER TABLE decision_runs DROP COLUMN IF EXISTS trigger")
