from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import MissionStatus, ReservationStatus
from app.core.errors import ApiError, ErrorCode
from app.db.models import AuditLog, Mission, MissionEvent, Notification, Reservation
from app.realtime.broker import queue_event

MISSION_TRANSITIONS = {
    MissionStatus.ASSIGNED: {MissionStatus.EN_ROUTE_TO_PATIENT},
    MissionStatus.EN_ROUTE_TO_PATIENT: {MissionStatus.ON_SCENE},
    MissionStatus.ON_SCENE: {MissionStatus.PATIENT_ON_BOARD},
    MissionStatus.PATIENT_ON_BOARD: {MissionStatus.EN_ROUTE_TO_HOSPITAL},
    MissionStatus.EN_ROUTE_TO_HOSPITAL: {MissionStatus.ARRIVED},
    MissionStatus.ARRIVED: {MissionStatus.HANDOVER},
    MissionStatus.HANDOVER: {MissionStatus.COMPLETED},
}


def assign_destination(session: Session, actor_id: UUID, mission_id: UUID, hospital_id: UUID, reservation_id: UUID | None) -> Mission:
    mission = session.scalar(select(Mission).where(Mission.id == mission_id).with_for_update())
    if mission is None:
        raise ApiError(404, ErrorCode.NOT_FOUND, "Mission not found.")
    if reservation_id is None:
        raise ApiError(409, ErrorCode.RESOURCE_UNAVAILABLE, "A committed reservation is required.")
    reservation = session.scalar(select(Reservation).where(Reservation.id == reservation_id).with_for_update())
    if reservation is None or reservation.hospital_id != hospital_id or reservation.status != ReservationStatus.CONFIRMED:
        raise ApiError(409, ErrorCode.RESOURCE_UNAVAILABLE, "A confirmed reservation for this hospital is required.")
    old = mission.selected_hospital_id
    mission.selected_hospital_id = hospital_id
    mission.state_version += 1
    payload = {"from_hospital_id": str(old) if old else None, "to_hospital_id": str(hospital_id)}
    session.add(MissionEvent(mission_id=mission.id, incident_id=mission.incident_id, event_type="DESTINATION_CHANGED", payload=payload, actor_id=actor_id))
    session.add(Notification(incident_id=mission.incident_id, event_type="DESTINATION_CHANGED", payload={"mission_id": str(mission.id), **payload}))
    session.add(AuditLog(actor_id=actor_id, action="DESTINATION_CHANGED", entity_type="mission", entity_id=str(mission.id), payload=payload))
    queue_event(session, "mission.destination.changed", mission.id, mission.state_version, {"mission_id": str(mission.id), "ambulance_id": str(mission.ambulance_id), "incident_id": str(mission.incident_id), "hospital_id": str(hospital_id)})
    session.commit()
    return mission


def transition_mission(session: Session, actor_id: UUID, mission_id: UUID, target: MissionStatus | str, state_version: int) -> Mission:
    mission = session.scalar(select(Mission).where(Mission.id == mission_id).with_for_update())
    if mission is None:
        raise ApiError(404, ErrorCode.NOT_FOUND, "Mission not found.")
    if mission.state_version != state_version:
        raise ApiError(409, ErrorCode.MISSION_STATE_CONFLICT, "Mission state is newer than this client.")
    current = MissionStatus(mission.status)
    target_status = MissionStatus(target)
    if target_status not in MISSION_TRANSITIONS.get(current, set()):
        raise ApiError(409, ErrorCode.CONFLICT, "Invalid mission state transition.")
    if target_status == MissionStatus.EN_ROUTE_TO_HOSPITAL and mission.selected_hospital_id is None:
        raise ApiError(409, ErrorCode.CONFLICT, "A confirmed destination is required.")
    mission.status = target_status
    mission.state_version += 1
    session.add(MissionEvent(mission_id=mission.id, incident_id=mission.incident_id, event_type=target_status.value, payload={"from": current.value, "to": target_status.value}, actor_id=actor_id))
    session.add(Notification(incident_id=mission.incident_id, event_type=target_status.value, payload={"mission_id": str(mission.id)}))
    session.add(AuditLog(actor_id=actor_id, action="MISSION_STATE_CHANGED", entity_type="mission", entity_id=str(mission.id), payload={"to": target_status.value}))
    session.commit()
    return mission
