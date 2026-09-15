"""Store comparable route candidates without changing the selected route."""

from alembic import op

revision = "0010_route_alternatives"
down_revision = "0009_mission_history_indexes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS route_alternatives (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            route_id UUID NOT NULL REFERENCES routes(id) ON DELETE CASCADE,
            provider VARCHAR(50) NOT NULL,
            distance_m INTEGER NOT NULL,
            duration_seconds INTEGER NOT NULL,
            traffic_duration_seconds INTEGER NOT NULL,
            confidence NUMERIC(4, 3) NOT NULL,
            selected BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMPTZ NOT NULL
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_route_alternatives_route ON route_alternatives (route_id, selected)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_route_alternatives_route")
    op.execute("DROP TABLE IF EXISTS route_alternatives")
