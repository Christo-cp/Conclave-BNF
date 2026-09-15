"""Add reservation lifecycle indexes and capacity invariants."""

from alembic import op

revision = "0008_reservation_invariants"
down_revision = "0007_acceptance_history"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE hospital_resources DROP CONSTRAINT IF EXISTS capacity_nonnegative")
    op.execute("ALTER TABLE hospital_resources DROP CONSTRAINT IF EXISTS ck_hospital_resources_capacity")
    op.execute("ALTER TABLE hospital_resources ADD CONSTRAINT ck_hospital_resources_capacity CHECK (total_capacity >= 0 AND available_capacity >= 0 AND reserved_capacity >= 0 AND occupied_capacity >= 0 AND occupied_capacity + reserved_capacity + COALESCE(available_capacity, 0) <= total_capacity)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_reservations_resource_status ON reservations (hospital_resource_id, status)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_reservations_expiry ON reservations (expires_at) WHERE status = 'HELD'")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_reservations_expiry")
    op.execute("DROP INDEX IF EXISTS ix_reservations_resource_status")
    op.execute("ALTER TABLE hospital_resources DROP CONSTRAINT IF EXISTS ck_hospital_resources_capacity")
    op.execute("ALTER TABLE hospital_resources DROP CONSTRAINT IF EXISTS capacity_nonnegative")
    op.execute("ALTER TABLE hospital_resources ADD CONSTRAINT capacity_nonnegative CHECK (total_capacity >= 0 AND available_capacity >= 0 AND reserved_capacity >= 0 AND occupied_capacity >= 0 AND occupied_capacity + reserved_capacity + COALESCE(available_capacity, 0) <= total_capacity)")
