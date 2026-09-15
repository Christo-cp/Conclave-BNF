from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import MissionStatus
from app.core.errors import ApiError, ErrorCode
from app.db.models import Ambulance, AuditLog, Mission, MissionEvent, Notification


def resource_loss(session: Session, actor_id: UUID, mission_id: UUID, reason: str = "RESOURCE_LOST") -> Mission:
    mission = session.scalar(select(Mission).where(Mission.id == mission_id).with_for_update())
    if mission is None:
        raise ApiError(404, ErrorCode.NOT_FOUND, "Mission not found.")
    mission.status = MissionStatus.REASSESSMENT
    mission.state_version += 1
    payload = {"reason": reason}
    session.add(MissionEvent(mission_id=mission.id, incident_id=mission.incident_id, event_type="RESOURCE_LOST", payload=payload, actor_id=actor_id))
    session.add(Notification(incident_id=mission.incident_id, event_type="RESOURCE_LOST", payload={"mission_id": str(mission.id)}))
    session.add(AuditLog(actor_id=actor_id, action="RESOURCE_LOST", entity_type="mission", entity_id=str(mission.id), payload=payload))
    session.commit()
    return mission


def traffic_change(session: Session, actor_id: UUID, mission_id: UUID, traffic_duration_seconds: int) -> Mission:
    return resource_loss(session, actor_id, mission_id, f"TRAFFIC_CHANGED:{traffic_duration_seconds}")


def ambulance_failure(session: Session, actor_id: UUID, mission_id: UUID) -> Mission:
    mission = resource_loss(session, actor_id, mission_id, "AMBULANCE_FAILURE")
    ambulance = session.get(Ambulance, mission.ambulance_id)
    if ambulance:
        ambulance.status = "UNAVAILABLE"
        session.commit()
    return mission


def gps_loss(session: Session, actor_id: UUID, mission_id: UUID) -> Mission:
    return resource_loss(session, actor_id, mission_id, "GPS_STALE")
