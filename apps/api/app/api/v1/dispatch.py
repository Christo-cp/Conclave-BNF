from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header
from sqlalchemy import select

from app.acceptance_service import get_request, reject_request
from app.assignment_service import respond_to_assignment
from app.core.config import Settings, get_settings
from app.core.enums import Role
from app.core.errors import ApiError, ErrorCode
from app.db.models import AcceptanceRequest, AmbulanceAssignment, Reservation, User
from app.dependencies import CurrentUser, Db, require_roles
from app.reservation_service import ReservationService
from app.schemas import (
    AcceptanceCreate,
    AcceptanceReject,
    ConfirmAmbulanceRequest,
    MatchRequest,
    ReservationAction,
    ReservationCreate,
    RouteRequest,
)
from app.services import (
    accept_request,
    calculate_route,
    confirm_ambulance,
    hold_acceptance,
    match_ambulances,
    match_hospitals,
    route_json,
)

router = APIRouter(tags=["dispatch"])
Dispatcher = Annotated[User, Depends(require_roles(Role.DISPATCHER, Role.SYSTEM_ADMIN))]
HospitalResponder = Annotated[User, Depends(require_roles(Role.HOSPITAL_STAFF, Role.HOSPITAL_ADMIN, Role.SYSTEM_ADMIN))]
ReservationUser = Annotated[User, Depends(require_roles(Role.HOSPITAL_STAFF, Role.HOSPITAL_ADMIN, Role.SYSTEM_ADMIN))]


def reservation_json(item: Reservation) -> dict:
    return {"id": str(item.id), "reservation_code": item.reservation_code, "acceptance_request_id": str(item.acceptance_request_id), "incident_id": str(item.incident_id), "hospital_id": str(item.hospital_id), "hospital_resource_id": str(item.hospital_resource_id), "status": item.status, "expires_at": item.expires_at, "release_reason": item.release_reason}


def acceptance_json(item: AcceptanceRequest) -> dict:
    return {"id": str(item.id), "incident_id": str(item.incident_id), "hospital_id": str(item.hospital_id), "status": item.status, "idempotency_key": item.idempotency_key, "expires_at": item.expires_at, "responded_by": str(item.responded_by) if item.responded_by else None, "rejection_reason": item.rejection_reason}


def assert_hospital_scope(user, hospital_id: UUID) -> None:
    roles = {role.code for role in user.roles}
    if roles & {"SYSTEM_ADMIN", "DISPATCHER"}:
        return
    if user.hospital_id != hospital_id:
        raise ApiError(403, ErrorCode.AUTHORIZATION_ERROR, "Hospital scope denied.")


def assert_hospital_response_role(user) -> None:
    if not {"SYSTEM_ADMIN", "HOSPITAL_STAFF", "HOSPITAL_ADMIN"} & {role.code for role in user.roles}:
        raise ApiError(403, ErrorCode.AUTHORIZATION_ERROR, "Only hospital staff may respond to an acceptance request.")


@router.post("/dispatch/ambulances/match")
def ambulance_match(payload: MatchRequest, session: Db, _: Dispatcher, settings: Annotated[Settings, Depends(get_settings)]):
    return match_ambulances(session, payload.incident_id, settings)


@router.post("/dispatch/ambulances/{ambulance_id}/confirm")
def ambulance_confirm(ambulance_id: UUID, payload: ConfirmAmbulanceRequest, session: Db, user: Dispatcher, idempotency_key: Annotated[str, Header(alias="Idempotency-Key")]):
    return confirm_ambulance(session, user, ambulance_id, payload.incident_id, idempotency_key, payload.override_reason)


@router.post("/ambulance-assignments/{assignment_id}/accept")
def accept_assignment(assignment_id: UUID, session: Db, user: Annotated[User, Depends(require_roles(Role.AMBULANCE_CREW, Role.SYSTEM_ADMIN))]):
    assignment = session.get(AmbulanceAssignment, assignment_id)
    if assignment is None or (Role.AMBULANCE_CREW.value in {role.code for role in user.roles} and user.ambulance_id != assignment.ambulance_id):
        raise ApiError(403, ErrorCode.AUTHORIZATION_ERROR, "Ambulance assignment scope denied.")
    return respond_to_assignment(session, user.id, assignment_id, True)


@router.post("/ambulance-assignments/{assignment_id}/reject")
def reject_assignment(assignment_id: UUID, session: Db, user: Annotated[User, Depends(require_roles(Role.AMBULANCE_CREW, Role.SYSTEM_ADMIN))]):
    assignment = session.get(AmbulanceAssignment, assignment_id)
    if assignment is None or (Role.AMBULANCE_CREW.value in {role.code for role in user.roles} and user.ambulance_id != assignment.ambulance_id):
        raise ApiError(403, ErrorCode.AUTHORIZATION_ERROR, "Ambulance assignment scope denied.")
    return respond_to_assignment(session, user.id, assignment_id, False)


@router.post("/routes/calculate")
def route(payload: RouteRequest, session: Db, _: Dispatcher):
    return route_json(calculate_route(session, payload.incident_id, payload.hospital_id))


@router.post("/dispatch/hospitals/match")
def hospital_match(payload: MatchRequest, session: Db, _: Dispatcher):
    return match_hospitals(session, payload.incident_id)


@router.post("/acceptance-requests")
def acceptance(payload: AcceptanceCreate, session: Db, user: Dispatcher, settings: Annotated[Settings, Depends(get_settings)], idempotency_key: Annotated[str, Header(alias="Idempotency-Key")]):
    return hold_acceptance(session, user, payload.incident_id, payload.hospital_id, idempotency_key, settings)


@router.post("/acceptance-requests/{request_id}/accept")
def accept(request_id: UUID, session: Db, user: HospitalResponder, idempotency_key: Annotated[str, Header(alias="Idempotency-Key")]):
    return accept_request(session, user, request_id, idempotency_key)


@router.get("/acceptance-requests/{request_id}")
def acceptance_get(request_id: UUID, session: Db, _: HospitalResponder):
    request = get_request(session, request_id)
    assert_hospital_scope(_, request.hospital_id)
    return acceptance_json(request)


@router.post("/acceptance-requests/{request_id}/reject")
def reject(request_id: UUID, payload: AcceptanceReject, session: Db, user: HospitalResponder):
    request = get_request(session, request_id)
    assert_hospital_response_role(user)
    assert_hospital_scope(user, request.hospital_id)
    return acceptance_json(reject_request(session, user.id, request_id, payload.reason))


@router.post("/reservations")
def create_reservation(payload: ReservationCreate, session: Db, user: ReservationUser, idempotency_key: Annotated[str, Header(alias="Idempotency-Key")]):
    assert_hospital_scope(user, payload.hospital_id)
    existing = session.scalar(select(Reservation).where(Reservation.idempotency_key == idempotency_key))
    if existing:
        return reservation_json(existing)
    reservation = Reservation(reservation_code=f"RES-{session.query(Reservation).count() + 1:06d}", acceptance_request_id=payload.acceptance_request_id, incident_id=payload.incident_id, hospital_id=payload.hospital_id, hospital_resource_id=payload.hospital_resource_id, expires_at=payload.expires_at, idempotency_key=idempotency_key)
    return reservation_json(ReservationService(session).reserve(reservation))


@router.get("/reservations/{reservation_id}")
def get_reservation(reservation_id: UUID, session: Db, user: CurrentUser):
    reservation = session.get(Reservation, reservation_id)
    if reservation is None:
        raise ApiError(404, ErrorCode.NOT_FOUND, "Reservation not found.")
    assert_hospital_scope(user, reservation.hospital_id)
    return reservation_json(reservation)


def transition_reservation(reservation_id: UUID, session, user, action: str, payload: ReservationAction):
    reservation = session.get(Reservation, reservation_id)
    if reservation is None:
        raise ApiError(404, ErrorCode.NOT_FOUND, "Reservation not found.")
    assert_hospital_scope(user, reservation.hospital_id)
    if payload.reason:
        reservation.release_reason = payload.reason
    result = getattr(ReservationService(session), action)(reservation_id)
    return reservation_json(result)


@router.post("/reservations/{reservation_id}/release")
def release_reservation(reservation_id: UUID, payload: ReservationAction, session: Db, user: CurrentUser):
    return transition_reservation(reservation_id, session, user, "release", payload)


@router.post("/reservations/{reservation_id}/expire")
def expire_reservation(reservation_id: UUID, payload: ReservationAction, session: Db, user: CurrentUser):
    return transition_reservation(reservation_id, session, user, "expire", payload)


@router.post("/reservations/{reservation_id}/consume")
def consume_reservation(reservation_id: UUID, payload: ReservationAction, session: Db, user: CurrentUser):
    return transition_reservation(reservation_id, session, user, "consume", payload)


@router.post("/reservations/{reservation_id}/cancel")
def cancel_reservation(reservation_id: UUID, payload: ReservationAction, session: Db, user: CurrentUser):
    return transition_reservation(reservation_id, session, user, "cancel", payload)
