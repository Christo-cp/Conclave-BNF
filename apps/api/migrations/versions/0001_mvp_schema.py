"""Smart Ambulance MVP schema."""

import sqlalchemy as sa
from alembic import op
from geoalchemy2 import Geography

revision = "0001_mvp_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    uuid = sa.dialects.postgresql.UUID(as_uuid=True)
    created = sa.DateTime(timezone=True)
    def table(name, *columns):
        op.create_table(name, sa.Column("id", uuid, primary_key=True, default=sa.text("gen_random_uuid()")), *columns)
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    table("hospitals", sa.Column("hospital_code", sa.String(40), unique=True, nullable=False), sa.Column("name", sa.String(255), nullable=False), sa.Column("location", Geography("POINT", srid=4326), nullable=False), sa.Column("latitude", sa.Numeric(10, 7), nullable=False), sa.Column("longitude", sa.Numeric(10, 7), nullable=False), sa.Column("status", sa.String(40), nullable=False), sa.Column("emergency_capable", sa.Boolean, nullable=False), sa.Column("data_mode", sa.String(20), nullable=False), sa.Column("created_at", created, nullable=False))
    table("users", sa.Column("name", sa.String(160), nullable=False), sa.Column("email", sa.String(255), unique=True, nullable=False), sa.Column("password_hash", sa.Text, nullable=False), sa.Column("status", sa.String(30), nullable=False), sa.Column("hospital_id", uuid, sa.ForeignKey("hospitals.id")), sa.Column("created_at", created, nullable=False), sa.Column("updated_at", created, nullable=False))
    table("roles", sa.Column("code", sa.String(50), unique=True, nullable=False), sa.Column("name", sa.String(100), nullable=False))
    op.create_table("user_roles", sa.Column("user_id", uuid, sa.ForeignKey("users.id"), primary_key=True), sa.Column("role_id", uuid, sa.ForeignKey("roles.id"), primary_key=True))
    table("incidents", sa.Column("incident_code", sa.String(40), unique=True, nullable=False), sa.Column("incident_type", sa.String(50), nullable=False), sa.Column("severity", sa.String(20), nullable=False), sa.Column("location", Geography("POINT", srid=4326), nullable=False), sa.Column("latitude", sa.Numeric(10, 7), nullable=False), sa.Column("longitude", sa.Numeric(10, 7), nullable=False), sa.Column("address_text", sa.Text), sa.Column("patient_count", sa.Integer, nullable=False), sa.Column("notes", sa.Text), sa.Column("data_mode", sa.String(20), nullable=False), sa.Column("status", sa.String(40), nullable=False), sa.Column("created_by", uuid, sa.ForeignKey("users.id")), sa.Column("created_at", created, nullable=False), sa.Column("updated_at", created, nullable=False))
    op.create_table("patient_requirement_items", sa.Column("id", uuid, primary_key=True), sa.Column("incident_id", uuid, sa.ForeignKey("incidents.id", ondelete="CASCADE")), sa.Column("requirement_code", sa.String(80), nullable=False), sa.Column("level", sa.String(20), nullable=False), sa.Column("notes", sa.Text), sa.UniqueConstraint("incident_id", "requirement_code"))
    table("ambulances", sa.Column("ambulance_code", sa.String(40), unique=True, nullable=False), sa.Column("vehicle_type", sa.String(50), nullable=False), sa.Column("status", sa.String(50), nullable=False), sa.Column("current_location", Geography("POINT", srid=4326)), sa.Column("latitude", sa.Numeric(10, 7)), sa.Column("longitude", sa.Numeric(10, 7)), sa.Column("gps_updated_at", created), sa.Column("crew_summary", sa.JSON), sa.Column("data_mode", sa.String(20), nullable=False), sa.Column("version", sa.Integer, nullable=False), sa.Column("created_at", created, nullable=False), sa.Column("updated_at", created, nullable=False))
    table("equipment", sa.Column("code", sa.String(80), unique=True, nullable=False))
    op.create_table("ambulance_equipment", sa.Column("ambulance_id", uuid, sa.ForeignKey("ambulances.id"), primary_key=True), sa.Column("equipment_id", uuid, sa.ForeignKey("equipment.id"), primary_key=True), sa.Column("quantity", sa.Integer), sa.Column("status", sa.String(30), nullable=False))
    table("capabilities", sa.Column("code", sa.String(80), unique=True, nullable=False))
    op.create_table("hospital_capabilities", sa.Column("hospital_id", uuid, sa.ForeignKey("hospitals.id"), primary_key=True), sa.Column("capability_id", uuid, sa.ForeignKey("capabilities.id"), primary_key=True), sa.Column("status", sa.String(30), nullable=False))
    table("hospital_resources", sa.Column("hospital_id", uuid, sa.ForeignKey("hospitals.id")), sa.Column("resource_type", sa.String(60), nullable=False), sa.Column("total_capacity", sa.Integer, nullable=False), sa.Column("available_capacity", sa.Integer), sa.Column("reserved_capacity", sa.Integer, nullable=False), sa.Column("occupied_capacity", sa.Integer, nullable=False), sa.Column("status", sa.String(30), nullable=False), sa.Column("last_updated_at", created), sa.Column("version", sa.Integer, nullable=False), sa.CheckConstraint("total_capacity >= 0 AND available_capacity >= 0 AND reserved_capacity >= 0 AND occupied_capacity >= 0 AND occupied_capacity + reserved_capacity + COALESCE(available_capacity, 0) <= total_capacity", name="capacity_nonnegative"))
    table("ambulance_assignments", sa.Column("incident_id", uuid, sa.ForeignKey("incidents.id")), sa.Column("ambulance_id", uuid, sa.ForeignKey("ambulances.id")), sa.Column("status", sa.String(40), nullable=False), sa.Column("idempotency_key", sa.String(255), unique=True), sa.Column("assigned_by", uuid, sa.ForeignKey("users.id")), sa.Column("created_at", created, nullable=False))
    table("routes", sa.Column("incident_id", uuid, sa.ForeignKey("incidents.id")), sa.Column("mission_id", uuid), sa.Column("provider", sa.String(50), nullable=False), sa.Column("origin", Geography("POINT", srid=4326)), sa.Column("destination", Geography("POINT", srid=4326)), sa.Column("distance_m", sa.Integer, nullable=False), sa.Column("duration_seconds", sa.Integer, nullable=False), sa.Column("traffic_duration_seconds", sa.Integer, nullable=False), sa.Column("confidence", sa.Numeric(4, 3), nullable=False), sa.Column("fallback_used", sa.Boolean, nullable=False), sa.Column("created_at", created, nullable=False))
    table("missions", sa.Column("mission_code", sa.String(50), unique=True, nullable=False), sa.Column("incident_id", uuid, sa.ForeignKey("incidents.id")), sa.Column("ambulance_id", uuid, sa.ForeignKey("ambulances.id")), sa.Column("selected_hospital_id", uuid, sa.ForeignKey("hospitals.id")), sa.Column("selected_route_id", uuid, sa.ForeignKey("routes.id")), sa.Column("status", sa.String(50), nullable=False), sa.Column("state_version", sa.Integer, nullable=False), sa.Column("created_at", created, nullable=False), sa.Column("updated_at", created, nullable=False))
    op.create_foreign_key("routes_mission_fk", "routes", "missions", ["mission_id"], ["id"])
    table("acceptance_requests", sa.Column("incident_id", uuid, sa.ForeignKey("incidents.id")), sa.Column("hospital_id", uuid, sa.ForeignKey("hospitals.id")), sa.Column("status", sa.String(30), nullable=False), sa.Column("idempotency_key", sa.String(255), unique=True, nullable=False), sa.Column("expires_at", created, nullable=False), sa.Column("responded_by", uuid, sa.ForeignKey("users.id")))
    table("reservations", sa.Column("reservation_code", sa.String(50), unique=True, nullable=False), sa.Column("acceptance_request_id", uuid, sa.ForeignKey("acceptance_requests.id")), sa.Column("incident_id", uuid, sa.ForeignKey("incidents.id")), sa.Column("hospital_id", uuid, sa.ForeignKey("hospitals.id")), sa.Column("hospital_resource_id", uuid, sa.ForeignKey("hospital_resources.id")), sa.Column("status", sa.String(30), nullable=False), sa.Column("expires_at", created, nullable=False))
    table("mission_events", sa.Column("mission_id", uuid, sa.ForeignKey("missions.id")), sa.Column("incident_id", uuid, sa.ForeignKey("incidents.id")), sa.Column("event_type", sa.String(60), nullable=False), sa.Column("payload", sa.JSON, nullable=False), sa.Column("actor_id", uuid, sa.ForeignKey("users.id")), sa.Column("created_at", created, nullable=False))
    table("notifications", sa.Column("incident_id", uuid, sa.ForeignKey("incidents.id")), sa.Column("event_type", sa.String(60), nullable=False), sa.Column("payload", sa.JSON, nullable=False), sa.Column("created_at", created, nullable=False))
    table("audit_logs", sa.Column("actor_id", uuid, sa.ForeignKey("users.id")), sa.Column("action", sa.String(80), nullable=False), sa.Column("entity_type", sa.String(80), nullable=False), sa.Column("entity_id", sa.String(80), nullable=False), sa.Column("payload", sa.JSON, nullable=False), sa.Column("created_at", created, nullable=False))
    for table_name, col in [("ambulances", "current_location"), ("hospitals", "location"), ("incidents", "location")]:
        op.create_index(f"ix_{table_name}_{col}", table_name, [col], postgresql_using="gist")


def downgrade() -> None:
    for name in ["audit_logs", "notifications", "mission_events", "reservations", "acceptance_requests", "missions", "routes", "ambulance_assignments", "hospital_resources", "hospital_capabilities", "capabilities", "ambulance_equipment", "equipment", "ambulances", "patient_requirement_items", "incidents", "user_roles", "roles", "users", "hospitals"]:
        op.drop_table(name)
