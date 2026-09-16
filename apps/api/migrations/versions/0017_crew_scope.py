"""Add the nullable ambulance scope used by crew authorization."""

from alembic import op

revision = "0017_crew_scope"
down_revision = "0016_s1_invariants"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS ambulance_id UUID REFERENCES ambulances(id)")


def downgrade() -> None:
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS ambulance_id")
