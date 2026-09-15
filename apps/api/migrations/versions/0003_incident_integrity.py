"""Add incident and requirement integrity checks and lookup indexes."""

from alembic import op

revision = "0003_incident_integrity"
down_revision = "0002_s7_s12_backend"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE INDEX IF NOT EXISTS ix_incidents_status_created_at ON incidents (status, created_at)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_patient_requirements_incident ON patient_requirement_items (incident_id)")
    op.execute("ALTER TABLE incidents DROP CONSTRAINT IF EXISTS ck_incidents_patient_count_positive")
    op.execute("ALTER TABLE incidents ADD CONSTRAINT ck_incidents_patient_count_positive CHECK (patient_count > 0)")
    op.execute("ALTER TABLE patient_requirement_items DROP CONSTRAINT IF EXISTS ck_patient_requirements_level")
    op.execute("ALTER TABLE patient_requirement_items ADD CONSTRAINT ck_patient_requirements_level CHECK (level IN ('REQUIRED', 'PREFERRED', 'UNKNOWN'))")


def downgrade() -> None:
    op.execute("ALTER TABLE patient_requirement_items DROP CONSTRAINT IF EXISTS ck_patient_requirements_level")
    op.execute("ALTER TABLE incidents DROP CONSTRAINT IF EXISTS ck_incidents_patient_count_positive")
    op.execute("DROP INDEX IF EXISTS ix_patient_requirements_incident")
    op.execute("DROP INDEX IF EXISTS ix_incidents_status_created_at")
