from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import ReservationStatus
from app.core.errors import ApiError, ErrorCode
from app.db.models import HospitalResource, Reservation

ACTIVE_RESERVATIONS = {ReservationStatus.HELD, ReservationStatus.CONFIRMED}


class ReservationService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def reserve(self, reservation: Reservation, quantity: int = 1) -> Reservation:
        if quantity < 1:
            raise ApiError(422, ErrorCode.VALIDATION_ERROR, "Reservation quantity must be positive.")
        resource = self.session.scalar(
            select(HospitalResource)
            .where(HospitalResource.id == reservation.hospital_resource_id)
            .with_for_update()
        )
        if resource is None or resource.status != "ACTIVE":
            raise ApiError(409, ErrorCode.RESOURCE_UNAVAILABLE, "Resource is unavailable.")
        if resource.available_capacity is None or resource.available_capacity < quantity:
            raise ApiError(409, ErrorCode.RESOURCE_UNAVAILABLE, "Resource capacity is unavailable.")
        resource.available_capacity -= quantity
        resource.reserved_capacity += quantity
        resource.version += 1
        self.session.add(reservation)
        self.session.commit()
        self.session.refresh(reservation)
        return reservation

    def _transition(self, reservation_id: UUID, target: ReservationStatus) -> Reservation:
        reservation = self.session.scalar(
            select(Reservation).where(Reservation.id == reservation_id).with_for_update()
        )
        if reservation is None:
            raise ApiError(404, ErrorCode.NOT_FOUND, "Reservation not found.")
        current = ReservationStatus(reservation.status)
        if current not in ACTIVE_RESERVATIONS:
            return reservation
        resource = self.session.scalar(
            select(HospitalResource)
            .where(HospitalResource.id == reservation.hospital_resource_id)
            .with_for_update()
        )
        if resource is None:
            raise ApiError(409, ErrorCode.RESOURCE_UNAVAILABLE, "Reservation resource is missing.")
        if current == ReservationStatus.HELD or target in {
            ReservationStatus.RELEASED,
            ReservationStatus.EXPIRED,
            ReservationStatus.CANCELLED,
        }:
            resource.available_capacity = (resource.available_capacity or 0) + 1
            resource.reserved_capacity -= 1
        reservation.status = target
        resource.version += 1
        self.session.commit()
        return reservation

    def release(self, reservation_id: UUID) -> Reservation:
        return self._transition(reservation_id, ReservationStatus.RELEASED)

    def expire(self, reservation_id: UUID) -> Reservation:
        reservation = self.session.get(Reservation, reservation_id)
        if reservation and reservation.expires_at > datetime.now(UTC):
            raise ApiError(409, ErrorCode.CONFLICT, "Reservation has not expired.")
        return self._transition(reservation_id, ReservationStatus.EXPIRED)

    def cancel(self, reservation_id: UUID) -> Reservation:
        return self._transition(reservation_id, ReservationStatus.CANCELLED)

    def consume(self, reservation_id: UUID) -> Reservation:
        reservation = self.session.scalar(
            select(Reservation).where(Reservation.id == reservation_id).with_for_update()
        )
        if reservation is None:
            raise ApiError(404, ErrorCode.NOT_FOUND, "Reservation not found.")
        if ReservationStatus(reservation.status) != ReservationStatus.CONFIRMED:
            raise ApiError(409, ErrorCode.CONFLICT, "Only a confirmed reservation can be consumed.")
        resource = self.session.scalar(
            select(HospitalResource)
            .where(HospitalResource.id == reservation.hospital_resource_id)
            .with_for_update()
        )
        if resource is None or resource.reserved_capacity < 1:
            raise ApiError(409, ErrorCode.RESOURCE_UNAVAILABLE, "Reserved resource is unavailable.")
        resource.reserved_capacity -= 1
        resource.occupied_capacity += 1
        resource.version += 1
        reservation.status = "IN_USE"
        self.session.commit()
        return reservation
