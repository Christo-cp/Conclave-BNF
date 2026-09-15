"""Add hospital capability and spatial lookup indexes."""

from alembic import op

revision = "0005_hospital_capability_indexes"
down_revision = "0004_ambulance_assignment_guard"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE INDEX IF NOT EXISTS ix_hospitals_status_emergency ON hospitals (status, emergency_capable)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_hospital_capabilities_capability ON hospital_capabilities (capability_id, status)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_hospital_resources_hospital_type ON hospital_resources (hospital_id, resource_type)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_hospital_resources_freshness ON hospital_resources (last_updated_at)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_hospital_resources_freshness")
    op.execute("DROP INDEX IF EXISTS ix_hospital_resources_hospital_type")
    op.execute("DROP INDEX IF EXISTS ix_hospital_capabilities_capability")
    op.execute("DROP INDEX IF EXISTS ix_hospitals_status_emergency")
