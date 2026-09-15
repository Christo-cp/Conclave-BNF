"""S7-S12 acceptance, lifecycle, decisions and immutable event records."""

import sqlalchemy as sa
from alembic import op

revision = "0002_s7_s12_backend"
down_revision = "0001_mvp_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    uuid = sa.dialects.postgresql.UUID(as_uuid=True)
    created = sa.DateTime(timezone=True)
    op.add_column("acceptance_requests", sa.Column("rejection_reason", sa.Text()))
    op.add_column("reservations", sa.Column("idempotency_key", sa.String(255)))
    op.add_column("reservations", sa.Column("release_reason", sa.String(80)))
    op.create_unique_constraint("uq_reservations_idempotency_key", "reservations", ["idempotency_key"])
    op.create_table(
        "decision_runs",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("incident_id", uuid, sa.ForeignKey("incidents.id"), nullable=False),
        sa.Column("decision_type", sa.String(50), nullable=False),
        sa.Column("algorithm_version", sa.String(50), nullable=False),
        sa.Column("config_version", sa.String(50), nullable=False),
        sa.Column("data_freshness", sa.JSON, nullable=False),
        sa.Column("created_at", created, nullable=False),
    )
    op.create_table(
        "decision_candidates",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("decision_run_id", uuid, sa.ForeignKey("decision_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("candidate_id", sa.String(80), nullable=False),
        sa.Column("eligible", sa.Boolean, nullable=False),
        sa.Column("score", sa.Numeric(8, 4)),
        sa.Column("rank", sa.Integer),
    )
    op.create_table(
        "decision_reasons",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("decision_candidate_id", uuid, sa.ForeignKey("decision_candidates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("code", sa.String(80), nullable=False),
        sa.Column("detail", sa.Text, nullable=False),
    )
    op.execute("""
        CREATE OR REPLACE FUNCTION reject_immutable_row_change() RETURNS trigger AS $$
        BEGIN RAISE EXCEPTION 'append-only record cannot be changed'; END;
        $$ LANGUAGE plpgsql;
    """)
    for table_name in ("audit_logs", "mission_events", "notifications"):
        op.execute(f"CREATE TRIGGER {table_name}_append_only BEFORE UPDATE OR DELETE ON {table_name} FOR EACH ROW EXECUTE FUNCTION reject_immutable_row_change()")


def downgrade() -> None:
    for table_name in ("notifications", "mission_events", "audit_logs"):
        op.execute(f"DROP TRIGGER IF EXISTS {table_name}_append_only ON {table_name}")
    op.execute("DROP FUNCTION IF EXISTS reject_immutable_row_change()")
    op.drop_table("decision_reasons")
    op.drop_table("decision_candidates")
    op.drop_table("decision_runs")
    op.drop_constraint("uq_reservations_idempotency_key", "reservations", type_="unique")
    op.drop_column("reservations", "release_reason")
    op.drop_column("reservations", "idempotency_key")
    op.drop_column("acceptance_requests", "rejection_reason")
