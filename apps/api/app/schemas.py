from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    email: str
    password: str


class IncidentCreate(BaseModel):
    incident_type: str = "TRAUMA"
    severity: str = "CRITICAL"
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    address_text: str | None = None
    patient_count: int = Field(default=1, ge=1)
    notes: str | None = None


class RequirementCreate(BaseModel):
    code: str = Field(min_length=1, max_length=80)
    level: str
    notes: str | None = None


class LocationUpdate(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    version: int | None = None


class AmbulanceUpdate(BaseModel):
    vehicle_type: str | None = Field(default=None, min_length=1, max_length=50)
    status: str | None = None
    version: int


class AmbulanceStatusUpdate(BaseModel):
    status: str
    version: int


class HospitalUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    emergency_capable: bool | None = None
    status: str | None = None


class HospitalStatusUpdate(BaseModel):
    status: str


class ResourceUpdate(BaseModel):
    resource_id: UUID | None = None
    resource_type: str | None = Field(default=None, min_length=1, max_length=60)
    total_capacity: int | None = Field(default=None, ge=0)
    available_capacity: int | None = Field(default=None, ge=0)
    status: str | None = None
    version: int


class ResourceStatusUpdate(BaseModel):
    status: str
    version: int


class ReservationCreate(BaseModel):
    acceptance_request_id: UUID
    incident_id: UUID
    hospital_id: UUID
    hospital_resource_id: UUID
    expires_at: datetime


class ReservationAction(BaseModel):
    reason: str | None = Field(default=None, max_length=80)


class MatchRequest(BaseModel):
    incident_id: UUID


class ConfirmAmbulanceRequest(BaseModel):
    incident_id: UUID
    override_reason: str | None = None


class AssignmentResponse(BaseModel):
    accepted: bool


class RouteRequest(BaseModel):
    incident_id: UUID
    hospital_id: UUID | None = None


class AcceptanceCreate(BaseModel):
    incident_id: UUID
    hospital_id: UUID


class AcceptanceReject(BaseModel):
    reason: str = Field(min_length=1, max_length=500)


class DestinationAssign(BaseModel):
    hospital_id: UUID
    reservation_id: UUID


class ResourceCreate(BaseModel):
    hospital_id: UUID
    resource_type: str = Field(min_length=1, max_length=60)
    total_capacity: int = Field(ge=0)
    available_capacity: int | None = Field(default=None, ge=0)


class HospitalCreate(BaseModel):
    hospital_code: str = Field(min_length=1, max_length=40)
    name: str = Field(min_length=1, max_length=255)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class AmbulanceCreate(BaseModel):
    ambulance_code: str = Field(min_length=1, max_length=40)
    vehicle_type: str = "ALS"


class MissionPatch(BaseModel):
    status: str
    state_version: int


class RerouteApply(BaseModel):
    variant: str
    state_version: int


class AssignmentReject(BaseModel):
    reason: str = Field(min_length=1, max_length=500)


class JsonResponse(BaseModel):
    id: UUID


class SimulationControl(BaseModel):
    target_id: UUID | None = None
    value: int | None = None
