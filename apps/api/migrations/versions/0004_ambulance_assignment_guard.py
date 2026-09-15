"""Prevent an ambulance from having multiple active assignments."""

from alembic import op

revision = "0004_ambulance_assignment_guard"
down_revision = "0003_incident_integrity"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS uq_active_ambulance_assignment
        ON ambulance_assignments (ambulance_id)
        WHERE status IN ('ASSIGNED', 'ACCEPTED', 'IN_PROGRESS')
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_ambulances_status ON ambulances (status)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_ambulances_gps_updated_at ON ambulances (gps_updated_at)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_ambulances_gps_updated_at")
    op.execute("DROP INDEX IF EXISTS ix_ambulances_status")
    op.execute("DROP INDEX IF EXISTS uq_active_ambulance_assignment")
