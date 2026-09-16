from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import ApiError, ErrorCode
from app.db.models import (
    AmbulanceAssignment,
    AuditLog,
    Mission,
    MissionEvent,
    Notification,
)


def respond_to_assignment(session: Session, actor_id: UUID, assignment_id: UUID, accepted: bool) -> AmbulanceAssignment:
    assignment = session.scalar(select(AmbulanceAssignment).where(AmbulanceAssignment.id == assignment_id).with_for_update())
    if assignment is None:
        raise ApiError(404, ErrorCode.NOT_FOUND, "Ambulance assignment not found.")
    if assignment.status != "ASSIGNED":
        raise ApiError(409, ErrorCode.CONFLICT, "Ambulance assignment is already closed.")
    target = "ACCEPTED" if accepted else "REJECTED"
    assignment.status = target
    mission = session.scalar(select(Mission).where(Mission.incident_id == assignment.incident_id, Mission.ambulance_id == assignment.ambulance_id).with_for_update())
    if mission:
        event_type = "AMBULANCE_ASSIGNMENT_ACCEPTED" if accepted else "AMBULANCE_ASSIGNMENT_REJECTED"
        session.add(MissionEvent(mission_id=mission.id, incident_id=mission.incident_id, event_type=event_type, payload={"assignment_id": str(assignment.id)}, actor_id=actor_id))
        session.add(Notification(incident_id=mission.incident_id, event_type=event_type, payload={"mission_id": str(mission.id)}))
    session.add(AuditLog(actor_id=actor_id, action=target, entity_type="ambulance_assignment", entity_id=str(assignment.id), payload={"accepted": accepted}))
    session.commit()
    return assignment
