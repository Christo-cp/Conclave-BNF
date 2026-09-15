from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import ApiError, ErrorCode
from app.db.models import Ambulance, HospitalResource, Mission, Route
from app.realtime.broker import queue_event
from app.simulation.seed import reset_and_seed

SUPPORTED_ACTIONS = {
    "heartbeat", "traffic-change", "resource-lost", "hospital-reject",
    "ambulance-failure", "gps-lost", "route-blocked", "reset", "scenario/start",
}


def _mission(session: Session, mission_id: UUID | None) -> Mission:
    mission = session.get(Mission, mission_id) if mission_id else session.scalar(select(Mission).order_by(Mission.created_at))
    if not mission:
        raise ApiError(404, ErrorCode.NOT_FOUND, "Mission not found.")
    return mission


def run_control(session: Session, settings, action: str, target_id: UUID | None = None, value: int | None = None) -> dict:
    if action not in SUPPORTED_ACTIONS:
        raise ApiError(400, ErrorCode.VALIDATION_ERROR, "Unsupported simulation action.")
    if action == "reset":
        reset_and_seed(session, settings)
        queue_event(session, "simulation.reset", "simulation", payload={"action": action})
        session.commit()
        return {"action": action, "mode": "SIMULATED"}
    mission = _mission(session, target_id)
    if action == "scenario/start":
        queue_event(session, "simulation.started", mission.id, mission.state_version, {"mission_id": str(mission.id)})
    elif action == "heartbeat":
        ambulance = session.get(Ambulance, mission.ambulance_id)
        if ambulance:
            ambulance.gps_updated_at = datetime.now(UTC)
            ambulance.version += 1
            queue_event(session, "ambulance.location.updated", ambulance.id, ambulance.version, {"mission_id": str(mission.id), "ambulance_id": str(ambulance.id), "latitude": float(ambulance.latitude), "longitude": float(ambulance.longitude)})
    elif action == "traffic-change":
        route = session.scalar(select(Route).where(Route.mission_id == mission.id).order_by(Route.created_at.desc()))
        if route:
            route.traffic_duration_seconds = value or route.traffic_duration_seconds + 300
            queue_event(session, "mission.route.updated", mission.id, mission.state_version, {"mission_id": str(mission.id), "traffic_duration_seconds": route.traffic_duration_seconds})
    elif action == "resource-lost":
        resource = session.scalar(select(HospitalResource).order_by(HospitalResource.id))
        if resource:
            resource.available_capacity = None
            resource.version += 1
            queue_event(session, "hospital.readiness.changed", resource.hospital_id, resource.version, {"hospital_id": str(resource.hospital_id), "resource": resource.resource_type, "available_capacity": None})
    elif action == "hospital-reject":
        queue_event(session, "hospital.rejected", mission.id, mission.state_version, {"mission_id": str(mission.id), "reason": "SIMULATED_REJECTION"})
    elif action == "ambulance-failure":
        ambulance = session.get(Ambulance, mission.ambulance_id)
        if ambulance:
            ambulance.status = "UNAVAILABLE"
            ambulance.version += 1
            queue_event(session, "ambulance.status.changed", ambulance.id, ambulance.version, {"mission_id": str(mission.id), "ambulance_id": str(ambulance.id), "status": ambulance.status})
    elif action == "gps-lost":
        ambulance = session.get(Ambulance, mission.ambulance_id)
        if ambulance:
            ambulance.gps_updated_at = None
            ambulance.version += 1
            queue_event(session, "ambulance.status.changed", ambulance.id, ambulance.version, {"mission_id": str(mission.id), "ambulance_id": str(ambulance.id), "status": "GPS_LOST"})
    elif action == "route-blocked":
        queue_event(session, "mission.route.updated", mission.id, mission.state_version, {"mission_id": str(mission.id), "blocked": True})
    session.commit()
    return {"action": action, "mission_id": str(mission.id), "mode": "SIMULATED"}
