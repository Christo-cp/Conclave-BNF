"""Complete S1 database invariants and immutable decision history."""

from alembic import op

revision = "0016_s1_invariants"
down_revision = "0015_simulation_integrity"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS uq_active_ambulance_mission
        ON missions (ambulance_id)
        WHERE status NOT IN ('COMPLETED', 'CANCELLED', 'FAILED')
    """)
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS uq_active_assignment_per_ambulance
        ON ambulance_assignments (ambulance_id)
        WHERE status IN ('ASSIGNED', 'ACCEPTED', 'IN_PROGRESS')
    """)
    op.execute("ALTER TABLE ambulances DROP CONSTRAINT IF EXISTS ck_ambulance_status")
    op.execute("ALTER TABLE ambulances ADD CONSTRAINT ck_ambulance_status CHECK (status IN ('AVAILABLE', 'RESERVED', 'DISPATCHED', 'UNAVAILABLE', 'MAINTENANCE'))")
    op.execute("ALTER TABLE hospitals DROP CONSTRAINT IF EXISTS ck_hospital_status")
    op.execute("ALTER TABLE hospitals ADD CONSTRAINT ck_hospital_status CHECK (status IN ('ACTIVE', 'LIMITED', 'TEMPORARILY_UNAVAILABLE', 'CLOSED', 'UNKNOWN'))")
    op.execute("ALTER TABLE hospital_resources DROP CONSTRAINT IF EXISTS ck_resource_status")
    op.execute("ALTER TABLE hospital_resources ADD CONSTRAINT ck_resource_status CHECK (status IN ('ACTIVE', 'INACTIVE'))")
    op.execute("ALTER TABLE missions DROP CONSTRAINT IF EXISTS ck_mission_status")
    op.execute("ALTER TABLE missions ADD CONSTRAINT ck_mission_status CHECK (status IN ('CREATED', 'ASSIGNED', 'EN_ROUTE_TO_PATIENT', 'ON_SCENE', 'PATIENT_ON_BOARD', 'EN_ROUTE_TO_HOSPITAL', 'ARRIVED', 'HANDOVER', 'COMPLETED', 'CANCELLED', 'FAILED', 'REASSESSMENT'))")
    op.execute("""
        CREATE OR REPLACE FUNCTION reject_decision_history_change() RETURNS trigger AS $$
        BEGIN RAISE EXCEPTION 'append-only record cannot be changed'; END;
        $$ LANGUAGE plpgsql
    """)
    for table_name in ("decision_runs", "decision_candidates", "decision_reasons"):
        op.execute(f"DROP TRIGGER IF EXISTS {table_name}_append_only ON {table_name}")
        op.execute(f"CREATE TRIGGER {table_name}_append_only BEFORE UPDATE OR DELETE ON {table_name} FOR EACH ROW EXECUTE FUNCTION reject_decision_history_change()")


def downgrade() -> None:
    for table_name in ("decision_reasons", "decision_candidates", "decision_runs"):
        op.execute(f"DROP TRIGGER IF EXISTS {table_name}_append_only ON {table_name}")
    op.execute("DROP FUNCTION IF EXISTS reject_decision_history_change()")
    for table_name, constraint in (("missions", "ck_mission_status"), ("hospital_resources", "ck_resource_status"), ("hospitals", "ck_hospital_status"), ("ambulances", "ck_ambulance_status")):
        op.execute(f"ALTER TABLE {table_name} DROP CONSTRAINT IF EXISTS {constraint}")
    op.execute("DROP INDEX IF EXISTS uq_active_assignment_per_ambulance")
    op.execute("DROP INDEX IF EXISTS uq_active_ambulance_mission")
