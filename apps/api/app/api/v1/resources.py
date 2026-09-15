from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends
from geoalchemy2.elements import WKTElement
from sqlalchemy import select

from app.core.enums import AmbulanceStatus, HospitalStatus, Role
from app.core.errors import ApiError, ErrorCode
from app.db.models import (
    Ambulance,
    Capability,
    Hospital,
    HospitalCapability,
    HospitalResource,
    User,
)
from app.dependencies import Db, require_roles
from app.schemas import (
    AmbulanceCreate,
    AmbulanceStatusUpdate,
    AmbulanceUpdate,
    HospitalCreate,
    HospitalStatusUpdate,
    HospitalUpdate,
    LocationUpdate,
    ResourceCreate,
    ResourceStatusUpdate,
    ResourceUpdate,
)

router = APIRouter(tags=["resources"])
admin_user = require_roles(Role.SYSTEM_ADMIN, Role.HOSPITAL_ADMIN)
AdminUser = Annotated[User, Depends(admin_user)]
resource_viewer = require_roles(Role.DISPATCHER, Role.SYSTEM_ADMIN, Role.HOSPITAL_STAFF, Role.HOSPITAL_ADMIN)
ResourceViewer = Annotated[User, Depends(resource_viewer)]
ambulance_viewer = require_roles(Role.DISPATCHER, Role.SYSTEM_ADMIN, Role.AMBULANCE_CREW)
AmbulanceViewer = Annotated[User, Depends(ambulance_viewer)]


def scoped_hospital(user: User, hospital_id: UUID) -> None:
    if "SYSTEM_ADMIN" not in {role.code for role in user.roles} and user.hospital_id != hospital_id:
        raise ApiError(403, ErrorCode.AUTHORIZATION_ERROR, "Hospital scope denied.")


def role_codes(user: User) -> set[str]:
    return {role.code for role in user.roles}


def can_view_hospital(user: User, hospital_id: UUID) -> None:
    if {"SYSTEM_ADMIN", "DISPATCHER"} & role_codes(user):
        return
    scoped_hospital(user, hospital_id)


def ambulance_json(item: Ambulance) -> dict:
    return {"id": str(item.id), "ambulance_code": item.ambulance_code, "vehicle_type": item.vehicle_type, "status": item.status, "latitude": float(item.latitude) if item.latitude is not None else None, "longitude": float(item.longitude) if item.longitude is not None else None, "gps_updated_at": item.gps_updated_at, "crew_summary": item.crew_summary, "data_mode": item.data_mode, "version": item.version}


def hospital_json(item: Hospital) -> dict:
    return {"id": str(item.id), "hospital_code": item.hospital_code, "name": item.name, "latitude": float(item.latitude), "longitude": float(item.longitude), "status": item.status, "emergency_capable": item.emergency_capable, "data_mode": item.data_mode}


def resource_json(item: HospitalResource) -> dict:
    return {"id": str(item.id), "hospital_id": str(item.hospital_id), "resource_type": item.resource_type, "total_capacity": item.total_capacity, "available_capacity": item.available_capacity, "reserved_capacity": item.reserved_capacity, "occupied_capacity": item.occupied_capacity, "status": item.status, "last_updated_at": item.last_updated_at, "version": item.version}


def hospital_detail_json(session, item: Hospital) -> dict:
    payload = hospital_json(item)
    payload["capabilities"] = [
        {"code": code, "status": status}
        for code, status in session.execute(
            select(Capability.code, HospitalCapability.status)
            .join(HospitalCapability, HospitalCapability.capability_id == Capability.id)
            .where(HospitalCapability.hospital_id == item.id)
            .order_by(Capability.code)
        )
    ]
    payload["resources"] = [
        resource_json(resource)
        for resource in session.scalars(
            select(HospitalResource)
            .where(HospitalResource.hospital_id == item.id)
            .order_by(HospitalResource.resource_type)
        )
    ]
    return payload


@router.get("/ambulances")
@router.get("/resources/ambulances", include_in_schema=False)
def list_ambulances(session: Db, user: AmbulanceViewer):
    return [ambulance_json(item) for item in session.scalars(select(Ambulance).order_by(Ambulance.ambulance_code))]


@router.get("/ambulances/{ambulance_id}")
@router.get("/resources/ambulances/{ambulance_id}", include_in_schema=False)
def get_ambulance(ambulance_id: UUID, session: Db, _: AmbulanceViewer):
    item = session.get(Ambulance, ambulance_id)
    if item is None:
        raise ApiError(404, ErrorCode.NOT_FOUND, "Ambulance not found.")
    return ambulance_json(item)


@router.patch("/ambulances/{ambulance_id}")
@router.patch("/resources/ambulances/{ambulance_id}", include_in_schema=False)
def update_ambulance(ambulance_id: UUID, payload: AmbulanceUpdate, session: Db, _: AdminUser):
    item = session.get(Ambulance, ambulance_id)
    if item is None:
        raise ApiError(404, ErrorCode.NOT_FOUND, "Ambulance not found.")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    item.version += 1
    session.commit()
    return ambulance_json(item)


@router.delete("/ambulances/{ambulance_id}")
@router.delete("/resources/ambulances/{ambulance_id}", include_in_schema=False)
def delete_ambulance(ambulance_id: UUID, session: Db, _: AdminUser):
    item = session.get(Ambulance, ambulance_id)
    if item is None:
        raise ApiError(404, ErrorCode.NOT_FOUND, "Ambulance not found.")
    session.delete(item)
    session.commit()
    return {"deleted": True, "id": str(ambulance_id)}


@router.post("/ambulances/{ambulance_id}/location")
@router.post("/resources/ambulances/{ambulance_id}/location", include_in_schema=False)
def update_ambulance_location(ambulance_id: UUID, payload: LocationUpdate, session: Db, user: AmbulanceViewer):
    item = session.get(Ambulance, ambulance_id)
    if item is None:
        raise ApiError(404, ErrorCode.NOT_FOUND, "Ambulance not found.")
    if "AMBULANCE_CREW" in role_codes(user) and item.status not in {AmbulanceStatus.DISPATCHED, AmbulanceStatus.RESERVED}:
        raise ApiError(403, ErrorCode.AUTHORIZATION_ERROR, "Crew cannot update this ambulance.")
    if payload.version is not None and payload.version != item.version:
        raise ApiError(409, ErrorCode.CONFLICT, "Ambulance state is newer than this client.")
    item.latitude, item.longitude = payload.latitude, payload.longitude
    item.current_location = WKTElement(f"POINT({payload.longitude} {payload.latitude})", srid=4326)
    item.gps_updated_at = datetime.now(UTC)
    item.version += 1
    session.commit()
    return ambulance_json(item)


@router.post("/ambulances/{ambulance_id}/status")
@router.post("/resources/ambulances/{ambulance_id}/status", include_in_schema=False)
def update_ambulance_status(ambulance_id: UUID, payload: AmbulanceStatusUpdate, session: Db, _: AdminUser):
    item = session.get(Ambulance, ambulance_id)
    if item is None:
        raise ApiError(404, ErrorCode.NOT_FOUND, "Ambulance not found.")
    try:
        item.status = AmbulanceStatus(payload.status)
    except ValueError as exc:
        raise ApiError(422, ErrorCode.VALIDATION_ERROR, "Invalid ambulance status.") from exc
    item.version += 1
    session.commit()
    return ambulance_json(item)


@router.post("/hospitals")
@router.post("/resources/hospitals", include_in_schema=False)
def create_hospital(payload: HospitalCreate, session: Db, _: AdminUser):
    hospital = Hospital(id=uuid4(), hospital_code=payload.hospital_code, name=payload.name, location=WKTElement(f"POINT({payload.longitude} {payload.latitude})", srid=4326), latitude=payload.latitude, longitude=payload.longitude, status="ACTIVE", emergency_capable=True, data_mode="SIMULATED")
    session.add(hospital)
    session.commit()
    return hospital_json(hospital)


@router.get("/hospitals")
@router.get("/resources/hospitals", include_in_schema=False)
def list_hospitals(session: Db, user: ResourceViewer):
    query = select(Hospital).order_by(Hospital.hospital_code)
    if not {"SYSTEM_ADMIN", "DISPATCHER"} & role_codes(user):
        query = query.where(Hospital.id == user.hospital_id)
    return [hospital_json(item) for item in session.scalars(query)]


@router.get("/hospitals/{hospital_id}")
@router.get("/resources/hospitals/{hospital_id}", include_in_schema=False)
def get_hospital(hospital_id: UUID, session: Db, user: ResourceViewer):
    item = session.get(Hospital, hospital_id)
    if item is None:
        raise ApiError(404, ErrorCode.NOT_FOUND, "Hospital not found.")
    can_view_hospital(user, hospital_id)
    return hospital_detail_json(session, item)


@router.patch("/hospitals/{hospital_id}")
@router.patch("/resources/hospitals/{hospital_id}", include_in_schema=False)
def update_hospital(hospital_id: UUID, payload: HospitalUpdate, session: Db, user: AdminUser):
    scoped_hospital(user, hospital_id)
    item = session.get(Hospital, hospital_id)
    if item is None:
        raise ApiError(404, ErrorCode.NOT_FOUND, "Hospital not found.")
    values = payload.model_dump(exclude_unset=True)
    latitude, longitude = values.pop("latitude", item.latitude), values.pop("longitude", item.longitude)
    for field, value in values.items():
        setattr(item, field, value)
    if "latitude" in payload.model_fields_set or "longitude" in payload.model_fields_set:
        item.latitude, item.longitude = latitude, longitude
        item.location = WKTElement(f"POINT({longitude} {latitude})", srid=4326)
    session.commit()
    return hospital_json(item)


@router.delete("/hospitals/{hospital_id}")
@router.delete("/resources/hospitals/{hospital_id}", include_in_schema=False)
def delete_hospital(hospital_id: UUID, session: Db, user: AdminUser):
    scoped_hospital(user, hospital_id)
    item = session.get(Hospital, hospital_id)
    if item is None:
        raise ApiError(404, ErrorCode.NOT_FOUND, "Hospital not found.")
    session.delete(item)
    session.commit()
    return {"deleted": True, "id": str(hospital_id)}


@router.post("/hospitals/{hospital_id}/status")
@router.post("/resources/hospitals/{hospital_id}/status", include_in_schema=False)
def update_hospital_status(hospital_id: UUID, payload: HospitalStatusUpdate, session: Db, user: AdminUser):
    scoped_hospital(user, hospital_id)
    item = session.get(Hospital, hospital_id)
    if item is None:
        raise ApiError(404, ErrorCode.NOT_FOUND, "Hospital not found.")
    try:
        item.status = HospitalStatus(payload.status)
    except ValueError as exc:
        raise ApiError(422, ErrorCode.VALIDATION_ERROR, "Invalid hospital status.") from exc
    session.commit()
    return hospital_json(item)


@router.get("/hospitals/{hospital_id}/resources")
@router.get("/resources/hospitals/{hospital_id}/resources", include_in_schema=False)
def list_hospital_resources(hospital_id: UUID, session: Db, user: ResourceViewer):
    if session.get(Hospital, hospital_id) is None:
        raise ApiError(404, ErrorCode.NOT_FOUND, "Hospital not found.")
    can_view_hospital(user, hospital_id)
    return [resource_json(item) for item in session.scalars(select(HospitalResource).where(HospitalResource.hospital_id == hospital_id).order_by(HospitalResource.resource_type))]


@router.patch("/hospitals/{hospital_id}/resources")
@router.patch("/resources/hospitals/{hospital_id}/resources", include_in_schema=False)
def update_hospital_resource(hospital_id: UUID, payload: ResourceUpdate, session: Db, user: AdminUser):
    scoped_hospital(user, hospital_id)
    resource = session.get(HospitalResource, payload.resource_id) if payload.resource_id else session.scalar(select(HospitalResource).where(HospitalResource.hospital_id == hospital_id, HospitalResource.resource_type == payload.resource_type)) if payload.resource_type else None
    if resource is None:
        raise ApiError(404, ErrorCode.NOT_FOUND, "Hospital resource not found.")
    if resource.hospital_id != hospital_id:
        raise ApiError(403, ErrorCode.AUTHORIZATION_ERROR, "Hospital scope denied.")
    values = payload.model_dump(exclude_unset=True)
    values.pop("resource_id", None)
    for field, value in values.items():
        setattr(resource, field, value)
    resource.version += 1
    session.commit()
    return resource_json(resource)


@router.post("/ambulances")
@router.post("/resources/ambulances", include_in_schema=False)
def create_ambulance(payload: AmbulanceCreate, session: Db, _: AdminUser):
    ambulance = Ambulance(ambulance_code=payload.ambulance_code, vehicle_type=payload.vehicle_type, status="AVAILABLE", data_mode="SIMULATED", version=1)
    session.add(ambulance)
    session.commit()
    return ambulance_json(ambulance)


@router.post("/hospitals/{hospital_id}/resources")
@router.post("/resources/hospitals/{hospital_id}/resources", include_in_schema=False)
def create_resource(hospital_id: UUID, payload: ResourceCreate, session: Db, user: AdminUser):
    scoped_hospital(user, hospital_id)
    if payload.hospital_id != hospital_id:
        raise ApiError(422, ErrorCode.VALIDATION_ERROR, "Hospital ids do not match.")
    resource = HospitalResource(hospital_id=hospital_id, resource_type=payload.resource_type, total_capacity=payload.total_capacity, available_capacity=payload.available_capacity if payload.available_capacity is not None else payload.total_capacity, reserved_capacity=0, occupied_capacity=0, status="ACTIVE", version=1)
    session.add(resource)
    session.commit()
    return resource_json(resource)


@router.get("/resources/{resource_id}")
def get_resource(resource_id: UUID, session: Db, user: ResourceViewer):
    resource = session.get(HospitalResource, resource_id)
    if resource is None:
        raise ApiError(404, ErrorCode.NOT_FOUND, "Hospital resource not found.")
    can_view_hospital(user, resource.hospital_id)
    return resource_json(resource)


@router.patch("/resources/{resource_id}")
def patch_resource(resource_id: UUID, payload: ResourceUpdate, session: Db, user: AdminUser):
    resource = session.get(HospitalResource, resource_id)
    if resource is None:
        raise ApiError(404, ErrorCode.NOT_FOUND, "Hospital resource not found.")
    scoped_hospital(user, resource.hospital_id)
    values = payload.model_dump(exclude_unset=True)
    values.pop("resource_id", None)
    for field, value in values.items():
        setattr(resource, field, value)
    resource.version += 1
    session.commit()
    return resource_json(resource)


@router.delete("/resources/{resource_id}")
def delete_resource(resource_id: UUID, session: Db, user: AdminUser):
    resource = session.get(HospitalResource, resource_id)
    if resource is None:
        raise ApiError(404, ErrorCode.NOT_FOUND, "Hospital resource not found.")
    scoped_hospital(user, resource.hospital_id)
    session.delete(resource)
    session.commit()
    return {"deleted": True, "id": str(resource_id)}


@router.post("/resources/{resource_id}/status")
def update_resource_status(resource_id: UUID, payload: ResourceStatusUpdate, session: Db, user: AdminUser):
    resource = session.get(HospitalResource, resource_id)
    if resource is None:
        raise ApiError(404, ErrorCode.NOT_FOUND, "Hospital resource not found.")
    scoped_hospital(user, resource.hospital_id)
    if payload.status not in {"ACTIVE", "INACTIVE"}:
        raise ApiError(422, ErrorCode.VALIDATION_ERROR, "Invalid resource status.")
    resource.status = payload.status
    resource.version += 1
    session.commit()
    return resource_json(resource)
