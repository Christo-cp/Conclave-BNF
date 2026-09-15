"""Add deterministic, explicitly simulated scenario definitions."""

from alembic import op

revision = "0013_simulation_scenarios"
down_revision = "0012_audit_indexes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS simulation_scenarios (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            scenario_code VARCHAR(50) NOT NULL UNIQUE,
            name VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            initial_state JSONB NOT NULL,
            configuration JSONB NOT NULL,
            seed BIGINT NOT NULL,
            status VARCHAR(30) NOT NULL,
            created_at TIMESTAMPTZ NOT NULL
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_simulation_scenarios_status ON simulation_scenarios (status)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_simulation_scenarios_status")
    op.execute("DROP TABLE IF EXISTS simulation_scenarios")
