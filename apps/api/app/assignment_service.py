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
from app.realtime.broker import queue_event


def respond_to_assignment(session: Session, actor_id: UUID, assignment_id: UUID, accepted: bool, reason: str | None = None) -> AmbulanceAssignment:
    assignment = session.scalar(select(AmbulanceAssignment).where(AmbulanceAssignment.id == assignment_id).with_for_update())
    if assignment is None:
        raise ApiError(404, ErrorCode.NOT_FOUND, "Ambulance assignment not found.")
    if assignment.status != "ASSIGNED":
        raise ApiError(409, ErrorCode.CONFLICT, "Ambulance assignment is already closed.")
    if not accepted and not (reason or "").strip():
        raise ApiError(422, ErrorCode.VALIDATION_ERROR, "A rejection reason is required.")
    target = "ACCEPTED" if accepted else "REJECTED"
    assignment.status = target
    detail = {"assignment_id": str(assignment.id), **({} if accepted else {"reason": reason})}
    mission = session.scalar(select(Mission).where(Mission.incident_id == assignment.incident_id, Mission.ambulance_id == assignment.ambulance_id).with_for_update())
    if mission:
        event_type = "AMBULANCE_ASSIGNMENT_ACCEPTED" if accepted else "AMBULANCE_ASSIGNMENT_REJECTED"
        session.add(MissionEvent(mission_id=mission.id, incident_id=mission.incident_id, event_type=event_type, payload=detail, actor_id=actor_id))
        session.add(Notification(incident_id=mission.incident_id, event_type=event_type, payload={"mission_id": str(mission.id), **detail}))
    session.add(AuditLog(actor_id=actor_id, action=target, entity_type="ambulance_assignment", entity_id=str(assignment.id), payload={"accepted": accepted, **detail}))
    queue_event(session, f"ambulance.assignment.{target.lower()}", assignment.id, 1, {
        "assignment_id": str(assignment.id),
        "ambulance_id": str(assignment.ambulance_id),
        "incident_id": str(assignment.incident_id),
        "status": target,
        **({"mission_id": str(mission.id)} if mission else {}),
        **({} if accepted else {"reason": reason}),
    })
    session.commit()
    return assignment
