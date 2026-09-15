"""Index audit history for incident and entity investigations."""

from alembic import op

revision = "0012_audit_indexes"
down_revision = "0011_decision_trace_context"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE INDEX IF NOT EXISTS ix_audit_logs_entity_created ON audit_logs (entity_type, entity_id, created_at)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_audit_logs_action_created ON audit_logs (action, created_at)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_audit_logs_action_created")
    op.execute("DROP INDEX IF EXISTS ix_audit_logs_entity_created")
