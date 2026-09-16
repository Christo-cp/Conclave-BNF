from datetime import UTC, datetime
from uuid import UUID, uuid4

from geoalchemy2 import Geography
from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def now() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(160))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE")
    hospital_id: Mapped[UUID | None] = mapped_column(ForeignKey("hospitals.id"), nullable=True)
    ambulance_id: Mapped[UUID | None] = mapped_column(ForeignKey("ambulances.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)
    roles: Mapped[list["Role"]] = relationship(back_populates="users", secondary="user_roles")


class Role(Base):
    __tablename__ = "roles"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    users: Mapped[list[User]] = relationship(back_populates="roles", secondary="user_roles")


class UserRole(Base):
    __tablename__ = "user_roles"
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    role_id: Mapped[UUID] = mapped_column(ForeignKey("roles.id"), primary_key=True)


class Incident(Base):
    __tablename__ = "incidents"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    incident_code: Mapped[str] = mapped_column(String(40), unique=True)
    incident_type: Mapped[str] = mapped_column(String(50))
    severity: Mapped[str] = mapped_column(String(20))
    location = mapped_column(Geography(geometry_type="POINT", srid=4326), nullable=False)
    latitude: Mapped[float] = mapped_column(Numeric(10, 7))
    longitude: Mapped[float] = mapped_column(Numeric(10, 7))
    address_text: Mapped[str | None] = mapped_column(Text)
    patient_count: Mapped[int] = mapped_column(Integer, default=1)
    notes: Mapped[str | None] = mapped_column(Text)
    data_mode: Mapped[str] = mapped_column(String(20), default="SIMULATED")
    status: Mapped[str] = mapped_column(String(40), default="CREATED")
    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)


class PatientRequirement(Base):
    __tablename__ = "patient_requirement_items"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    incident_id: Mapped[UUID] = mapped_column(ForeignKey("incidents.id", ondelete="CASCADE"))
    requirement_code: Mapped[str] = mapped_column(String(80))
    level: Mapped[str] = mapped_column(String(20))
    notes: Mapped[str | None] = mapped_column(Text)
    __table_args__ = (UniqueConstraint("incident_id", "requirement_code"),)


class Ambulance(Base):
    __tablename__ = "ambulances"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    ambulance_code: Mapped[str] = mapped_column(String(40), unique=True)
    vehicle_type: Mapped[str] = mapped_column(String(50), default="ALS")
    status: Mapped[str] = mapped_column(String(50), default="AVAILABLE")
    current_location = mapped_column(Geography(geometry_type="POINT", srid=4326))
    latitude: Mapped[float | None] = mapped_column(Numeric(10, 7))
    longitude: Mapped[float | None] = mapped_column(Numeric(10, 7))
    gps_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    crew_summary: Mapped[dict | None] = mapped_column(JSON)
    data_mode: Mapped[str] = mapped_column(String(20), default="SIMULATED")
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)


class Equipment(Base):
    __tablename__ = "equipment"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(String(80), unique=True)


class AmbulanceEquipment(Base):
    __tablename__ = "ambulance_equipment"
    ambulance_id: Mapped[UUID] = mapped_column(ForeignKey("ambulances.id"), primary_key=True)
    equipment_id: Mapped[UUID] = mapped_column(ForeignKey("equipment.id"), primary_key=True)
    quantity: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE")


class Hospital(Base):
    __tablename__ = "hospitals"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    hospital_code: Mapped[str] = mapped_column(String(40), unique=True)
    name: Mapped[str] = mapped_column(String(255))
    location = mapped_column(Geography(geometry_type="POINT", srid=4326), nullable=False)
    latitude: Mapped[float] = mapped_column(Numeric(10, 7))
    longitude: Mapped[float] = mapped_column(Numeric(10, 7))
    status: Mapped[str] = mapped_column(String(40), default="ACTIVE")
    emergency_capable: Mapped[bool] = mapped_column(Boolean, default=True)
    data_mode: Mapped[str] = mapped_column(String(20), default="SIMULATED")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Capability(Base):
    __tablename__ = "capabilities"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(String(80), unique=True)


class HospitalCapability(Base):
    __tablename__ = "hospital_capabilities"
    hospital_id: Mapped[UUID] = mapped_column(ForeignKey("hospitals.id"), primary_key=True)
    capability_id: Mapped[UUID] = mapped_column(ForeignKey("capabilities.id"), primary_key=True)
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE")


class HospitalResource(Base):
    __tablename__ = "hospital_resources"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    hospital_id: Mapped[UUID] = mapped_column(ForeignKey("hospitals.id"))
    resource_type: Mapped[str] = mapped_column(String(60))
    total_capacity: Mapped[int] = mapped_column(Integer)
    available_capacity: Mapped[int | None] = mapped_column(Integer)
    reserved_capacity: Mapped[int] = mapped_column(Integer, default=0)
    occupied_capacity: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE")
    last_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=now)
    version: Mapped[int] = mapped_column(Integer, default=1)


class ResourceEvent(Base):
    __tablename__ = "resource_events"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    hospital_resource_id: Mapped[UUID] = mapped_column(ForeignKey("hospital_resources.id"))
    event_type: Mapped[str] = mapped_column(String(50))
    old_available: Mapped[int | None] = mapped_column(Integer)
    new_available: Mapped[int | None] = mapped_column(Integer)
    old_reserved: Mapped[int | None] = mapped_column(Integer)
    new_reserved: Mapped[int | None] = mapped_column(Integer)
    source: Mapped[str] = mapped_column(String(50))
    actor_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class AmbulanceAssignment(Base):
    __tablename__ = "ambulance_assignments"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    incident_id: Mapped[UUID] = mapped_column(ForeignKey("incidents.id"))
    ambulance_id: Mapped[UUID] = mapped_column(ForeignKey("ambulances.id"))
    status: Mapped[str] = mapped_column(String(40), default="ASSIGNED")
    idempotency_key: Mapped[str | None] = mapped_column(String(255), unique=True)
    assigned_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Mission(Base):
    __tablename__ = "missions"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    mission_code: Mapped[str] = mapped_column(String(50), unique=True)
    incident_id: Mapped[UUID] = mapped_column(ForeignKey("incidents.id"))
    ambulance_id: Mapped[UUID] = mapped_column(ForeignKey("ambulances.id"))
    selected_hospital_id: Mapped[UUID | None] = mapped_column(ForeignKey("hospitals.id"))
    selected_route_id: Mapped[UUID | None] = mapped_column(ForeignKey("routes.id"))
    status: Mapped[str] = mapped_column(String(50), default="CREATED")
    state_version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)


class Route(Base):
    __tablename__ = "routes"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    incident_id: Mapped[UUID] = mapped_column(ForeignKey("incidents.id"))
    mission_id: Mapped[UUID | None] = mapped_column(ForeignKey("missions.id"))
    provider: Mapped[str] = mapped_column(String(50))
    origin = mapped_column(Geography(geometry_type="POINT", srid=4326))
    destination = mapped_column(Geography(geometry_type="POINT", srid=4326))
    distance_m: Mapped[int] = mapped_column(Integer)
    duration_seconds: Mapped[int] = mapped_column(Integer)
    traffic_duration_seconds: Mapped[int] = mapped_column(Integer)
    confidence: Mapped[float] = mapped_column(Numeric(4, 3), default=0.9)
    fallback_used: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class AcceptanceRequest(Base):
    __tablename__ = "acceptance_requests"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    incident_id: Mapped[UUID] = mapped_column(ForeignKey("incidents.id"))
    hospital_id: Mapped[UUID] = mapped_column(ForeignKey("hospitals.id"))
    status: Mapped[str] = mapped_column(String(30), default="PENDING")
    idempotency_key: Mapped[str] = mapped_column(String(255), unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    responded_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    rejection_reason: Mapped[str | None] = mapped_column(Text)


class Reservation(Base):
    __tablename__ = "reservations"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    reservation_code: Mapped[str] = mapped_column(String(50), unique=True)
    acceptance_request_id: Mapped[UUID] = mapped_column(ForeignKey("acceptance_requests.id"))
    incident_id: Mapped[UUID] = mapped_column(ForeignKey("incidents.id"))
    hospital_id: Mapped[UUID] = mapped_column(ForeignKey("hospitals.id"))
    hospital_resource_id: Mapped[UUID] = mapped_column(ForeignKey("hospital_resources.id"))
    status: Mapped[str] = mapped_column(String(30), default="HELD")
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    idempotency_key: Mapped[str | None] = mapped_column(String(255), unique=True)
    release_reason: Mapped[str | None] = mapped_column(String(80))


class DecisionRun(Base):
    __tablename__ = "decision_runs"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    incident_id: Mapped[UUID] = mapped_column(ForeignKey("incidents.id"))
    decision_type: Mapped[str] = mapped_column(String(50))
    algorithm_version: Mapped[str] = mapped_column(String(50))
    config_version: Mapped[str] = mapped_column(String(50))
    data_freshness: Mapped[dict] = mapped_column(JSON, default=dict)
    trigger: Mapped[str | None] = mapped_column(String(60))
    input_snapshot: Mapped[dict | None] = mapped_column(JSON)
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class DecisionCandidate(Base):
    __tablename__ = "decision_candidates"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    decision_run_id: Mapped[UUID] = mapped_column(ForeignKey("decision_runs.id", ondelete="CASCADE"))
    candidate_id: Mapped[str] = mapped_column(String(80))
    eligible: Mapped[bool] = mapped_column(Boolean)
    score: Mapped[float | None] = mapped_column(Numeric(8, 4))
    rank: Mapped[int | None] = mapped_column(Integer)


class DecisionReason(Base):
    __tablename__ = "decision_reasons"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    decision_candidate_id: Mapped[UUID] = mapped_column(ForeignKey("decision_candidates.id", ondelete="CASCADE"))
    code: Mapped[str] = mapped_column(String(80))
    detail: Mapped[str] = mapped_column(Text)


class MissionEvent(Base):
    __tablename__ = "mission_events"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    mission_id: Mapped[UUID] = mapped_column(ForeignKey("missions.id"))
    incident_id: Mapped[UUID] = mapped_column(ForeignKey("incidents.id"))
    event_type: Mapped[str] = mapped_column(String(60))
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    actor_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Notification(Base):
    __tablename__ = "notifications"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    incident_id: Mapped[UUID] = mapped_column(ForeignKey("incidents.id"))
    event_type: Mapped[str] = mapped_column(String(60))
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class SimulationScenario(Base):
    __tablename__ = "simulation_scenarios"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    scenario_code: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    initial_state: Mapped[dict] = mapped_column(JSON, default=dict)
    configuration: Mapped[dict] = mapped_column(JSON, default=dict)
    seed: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(30))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    actor_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(80))
    entity_type: Mapped[str] = mapped_column(String(80))
    entity_id: Mapped[str] = mapped_column(String(80))
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
