from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import AcceptanceStatus, ReservationStatus
from app.db.models import AcceptanceRequest, Reservation
from app.reservation_service import ReservationService


def expire_holds(session: Session, now: datetime | None = None) -> int:
    clock = now or datetime.now(UTC)
    expired = 0
    reservations = list(session.scalars(select(Reservation).where(Reservation.status == ReservationStatus.HELD, Reservation.expires_at <= clock).with_for_update()))
    service = ReservationService(session)
    for reservation in reservations:
        service.expire_in_transaction(reservation.id)
        expired += 1
    requests = list(session.scalars(select(AcceptanceRequest).where(AcceptanceRequest.status == AcceptanceStatus.PENDING, AcceptanceRequest.expires_at <= clock).with_for_update()))
    for request in requests:
        request.status = AcceptanceStatus.EXPIRED
    if reservations or requests:
        session.commit()
    return expired
