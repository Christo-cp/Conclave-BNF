from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import AcceptanceStatus, ReservationStatus
from app.core.errors import ApiError, ErrorCode
from app.db.models import AcceptanceRequest, AuditLog, Reservation
from app.reservation_service import ReservationService


def get_request(session: Session, request_id: UUID) -> AcceptanceRequest:
    request = session.get(AcceptanceRequest, request_id)
    if request is None:
        raise ApiError(404, ErrorCode.NOT_FOUND, "Acceptance request not found.")
    return request


def reject_request(session: Session, actor_id: UUID, request_id: UUID, reason: str) -> AcceptanceRequest:
    request = session.scalar(select(AcceptanceRequest).where(AcceptanceRequest.id == request_id).with_for_update())
    if request is None:
        raise ApiError(404, ErrorCode.NOT_FOUND, "Acceptance request not found.")
    if request.status != AcceptanceStatus.PENDING:
        return request
    request.status = AcceptanceStatus.REJECTED
    request.responded_by = actor_id
    for reservation in session.scalars(select(Reservation).where(Reservation.acceptance_request_id == request.id, Reservation.status == ReservationStatus.HELD).with_for_update()):
        ReservationService(session).cancel(reservation.id)
    session.add(AuditLog(actor_id=actor_id, action="HOSPITAL_REJECTED", entity_type="acceptance_request", entity_id=str(request.id), payload={"reason": reason}))
    session.commit()
    return request
