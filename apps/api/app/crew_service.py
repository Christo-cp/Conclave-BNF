from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from geoalchemy2.elements import WKTElement
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.enums import MissionStatus
from app.core.errors import ApiError, ErrorCode
from app.db.models import (
    AcceptanceRequest,
    Ambulance,
    AmbulanceAssignment,
    Hospital,
    Incident,
    Mission,
    PatientRequirement,
    Reservation,
    Route,
    User,
)
from app.realtime.broker import queue_event
from app.routing.geometry import as_json, simulated_path
from app.routing.service import RoutingService
from app.services import MISSION_TRANSITIONS, audit, golden_scenario

TO_PATIENT_STATES = {MissionStatus.CREATED, MissionStatus.ASSIGNED, MissionStatus.EN_ROUTE_TO_PATIENT, MissionStatus.ON_SCENE}


def active_leg(mission: Mission) -> str:
    return "TO_PATIENT" if MissionStatus(mission.status) in TO_PATIENT_STATES else "TO_HOSPITAL"


def point_json(latitude, longitude) -> dict | None:
    if latitude is None or longitude is None:
        return None
    return {"lat": float(latitude), "lng": float(longitude)}


def gps_state(ambulance: Ambulance) -> dict:
    if ambulance.gps_updated_at is None:
        return {"gps_age_s": None, "gps_stale": None, "gps_state": "UNKNOWN"}
    age = (datetime.now(UTC) - ambulance.gps_updated_at).total_seconds()
    stale = age > get_settings().gps_stale_after_s
    return {"gps_age_s": age, "gps_stale": stale, "gps_state": "STALE" if stale else "FRESH"}


def load_mission(session: Session, mission_id: UUID) -> Mission:
    mission = session.get(Mission, mission_id)
    if mission is None:
        raise ApiError(404, ErrorCode.NOT_FOUND, "Mission not found.")
    return mission


def leg_endpoints(session: Session, mission: Mission) -> tuple[str, str, tuple[float, float] | None, tuple[float, float] | None]:
    incident = session.get(Incident, mission.incident_id)
    ambulance = session.get(Ambulance, mission.ambulance_id)
    if incident is None or ambulance is None:
        raise ApiError(404, ErrorCode.NOT_FOUND, "Mission incident or ambulance is missing.")
    if active_leg(mission) == "TO_PATIENT":
        origin = point_json(ambulance.latitude, ambulance.longitude)
        destination = point_json(incident.latitude, incident.longitude)
        return ambulance.ambulance_code, incident.incident_code, _pair(origin), _pair(destination)
    hospital = session.get(Hospital, mission.selected_hospital_id) if mission.selected_hospital_id else None
    if hospital is None:
        raise ApiError(409, ErrorCode.CONFLICT, "A confirmed destination is required before the hospital leg is routed.")
    origin = point_json(ambulance.latitude, ambulance.longitude) or point_json(incident.latitude, incident.longitude)
    return incident.incident_code, hospital.hospital_code, _pair(origin), _pair(point_json(hospital.latitude, hospital.longitude))


def _pair(value: dict | None) -> tuple[float, float] | None:
    return None if value is None else (value["lat"], value["lng"])


def _wkt(point: tuple[float, float] | None) -> WKTElement | None:
    return None if point is None else WKTElement(f"POINT({point[1]} {point[0]})", srid=4326)


def current_route(session: Session, mission: Mission) -> Route | None:
    return session.scalar(select(Route).where(Route.mission_id == mission.id).order_by(Route.created_at.desc()))


def route_variant_for_leg(scenario: dict, origin_code: str, destination_code: str, route: Route) -> str | None:
    """Which declared variant a persisted route is, or None when it belongs to the other leg.

    The Route row records no variant, so it is recovered by matching the scenario's
    declared options. Free-flow duration is compared rather than traffic duration
    because the traffic-change control mutates the latter on the persisted row.
    """
    routing = RoutingService()
    for variant in routing.variants(scenario, origin_code, destination_code):
        estimate = routing.calculate(scenario, origin_code, destination_code, variant)
        if estimate.distance_m == route.distance_m and estimate.duration_seconds == route.duration_seconds:
            return variant
    return None


def estimate_json(estimate, origin, destination, *, label: str) -> dict:
    return {
        "variant": estimate.variant,
        "label": label,
        "distance_m": estimate.distance_m,
        "duration_seconds": estimate.duration_seconds,
        "traffic_duration_seconds": estimate.traffic_duration_seconds,
        "confidence": float(estimate.confidence),
        "provider": estimate.provider,
        "data_mode": estimate.data_mode,
        "geometry": as_json(simulated_path(origin, destination, variant=estimate.variant)) if origin and destination else [],
    }


def mission_view(session: Session, mission: Mission) -> dict:
    incident = session.get(Incident, mission.incident_id)
    ambulance = session.get(Ambulance, mission.ambulance_id)
    hospital = session.get(Hospital, mission.selected_hospital_id) if mission.selected_hospital_id else None
    requirements = list(session.scalars(select(PatientRequirement).where(PatientRequirement.incident_id == mission.incident_id)))
    acceptance = session.scalar(select(AcceptanceRequest).where(AcceptanceRequest.incident_id == mission.incident_id).order_by(AcceptanceRequest.created_at.desc()))
    reservations = list(session.scalars(select(Reservation).where(Reservation.incident_id == mission.incident_id))) if hospital else []
    assignment = session.scalar(select(AmbulanceAssignment).where(AmbulanceAssignment.incident_id == mission.incident_id, AmbulanceAssignment.ambulance_id == mission.ambulance_id).order_by(AmbulanceAssignment.created_at.desc()))
    leg = active_leg(mission)
    route = current_route(session, mission)
    geometry: list[dict] = []
    origin_code, destination_code, origin, destination = _safe_endpoints(session, mission)
    if route is not None:
        # A route calculated for the other leg must not be reported against this one.
        variant = route_variant_for_leg(golden_scenario(session), origin_code, destination_code, route) if origin_code else None
        if variant is None:
            route = None
        elif origin and destination:
            geometry = as_json(simulated_path(origin, destination, variant=variant))
    return {
        "mission": {
            "id": str(mission.id),
            "mission_code": mission.mission_code,
            "status": mission.status,
            "state_version": mission.state_version,
            "active_leg": leg,
            "next_states": sorted(state.value for state in MISSION_TRANSITIONS.get(MissionStatus(mission.status), set())),
            "data_mode": "SIMULATED",
        },
        "assignment": None if assignment is None else {"id": str(assignment.id), "status": assignment.status},
        "incident": None if incident is None else {
            "id": str(incident.id),
            "incident_code": incident.incident_code,
            "incident_type": incident.incident_type,
            "severity": incident.severity,
            "address_text": incident.address_text,
            "patient_count": incident.patient_count,
            "point": point_json(incident.latitude, incident.longitude),
            "requirements": [{"code": item.requirement_code, "level": item.level} for item in requirements],
        },
        "ambulance": None if ambulance is None else {
            "id": str(ambulance.id),
            "ambulance_code": ambulance.ambulance_code,
            "status": ambulance.status,
            "point": point_json(ambulance.latitude, ambulance.longitude),
            **gps_state(ambulance),
        },
        "destination": None if hospital is None else {
            "id": str(hospital.id),
            "hospital_code": hospital.hospital_code,
            "name": hospital.name,
            "point": point_json(hospital.latitude, hospital.longitude),
        },
        "acceptance": None if acceptance is None else {"id": str(acceptance.id), "status": acceptance.status},
        "reservations": [{"id": str(item.id), "status": item.status, "resource_type": _resource_type(session, item)} for item in reservations],
        "route": None if route is None else {
            "id": str(route.id),
            "distance_m": route.distance_m,
            "duration_seconds": route.duration_seconds,
            "traffic_duration_seconds": route.traffic_duration_seconds,
            "confidence": float(route.confidence),
            "provider": route.provider,
            "geometry": geometry,
            "data_mode": "SIMULATED",
        },
    }


def _safe_endpoints(session: Session, mission: Mission):
    try:
        return leg_endpoints(session, mission)
    except ApiError:
        return None, None, None, None


def _resource_type(session: Session, reservation: Reservation) -> str | None:
    from app.db.models import HospitalResource

    resource = session.get(HospitalResource, reservation.hospital_resource_id)
    return resource.resource_type if resource else None


def compare_routes(session: Session, mission: Mission) -> dict:
    origin_code, destination_code, origin, destination = leg_endpoints(session, mission)
    scenario = golden_scenario(session)
    routing = RoutingService()
    active = current_route(session, mission)
    active_variant = route_variant_for_leg(scenario, origin_code, destination_code, active) if active is not None else None
    current_variant = active_variant or "primary"
    options: list[dict] = []
    for variant in routing.variants(scenario, origin_code, destination_code):
        estimate = routing.calculate(scenario, origin_code, destination_code, variant)
        is_current = variant == current_variant
        option = estimate_json(estimate, origin, destination, label="CURRENT ROUTE" if is_current else "ALTERNATIVE ROUTE")
        if is_current and active_variant is not None:
            option["traffic_duration_seconds"] = active.traffic_duration_seconds
            option["route_id"] = str(active.id)
        options.append(option)
    current = next((option for option in options if option["variant"] == current_variant), None)
    alternatives = [option for option in options if option["variant"] != current_variant]
    best = min(alternatives, key=lambda option: option["traffic_duration_seconds"], default=None)
    delta = None if not (current and best) else current["traffic_duration_seconds"] - best["traffic_duration_seconds"]
    threshold = get_settings().reroute_significant_delta_s
    return {
        "mission_id": str(mission.id),
        "active_leg": active_leg(mission),
        "current": current,
        "alternatives": alternatives,
        "recommended_variant": best["variant"] if (best and delta is not None and delta >= threshold) else None,
        "saving_seconds": delta,
        "significant": bool(delta is not None and delta >= threshold),
        "threshold_seconds": threshold,
        "data_mode": "SIMULATED",
    }


def apply_reroute(session: Session, actor: User, mission: Mission, variant: str, state_version: int) -> dict:
    if mission.state_version != state_version:
        raise ApiError(409, ErrorCode.MISSION_STATE_CONFLICT, "Mission state is newer than this client.")
    origin_code, destination_code, origin, destination = leg_endpoints(session, mission)
    scenario = golden_scenario(session)
    estimate = RoutingService().calculate(scenario, origin_code, destination_code, variant)
    incident = session.get(Incident, mission.incident_id)
    route = Route(
        incident_id=mission.incident_id,
        mission_id=mission.id,
        provider=estimate.provider,
        distance_m=estimate.distance_m,
        duration_seconds=estimate.duration_seconds,
        traffic_duration_seconds=estimate.traffic_duration_seconds,
        confidence=estimate.confidence,
        fallback_used=estimate.fallback_used,
        origin=_wkt(origin),
        destination=_wkt(destination),
    )
    session.add(route)
    session.flush()
    mission.selected_route_id = route.id
    mission.state_version += 1
    audit(session, actor.id, "MISSION_REROUTED", "mission", str(mission.id), {"variant": variant, "leg": active_leg(mission)})
    queue_event(session, "mission.route.updated", mission.id, mission.state_version, {
        "mission_id": str(mission.id),
        "ambulance_id": str(mission.ambulance_id),
        "incident_id": str(incident.id) if incident else None,
        "route_id": str(route.id),
        "variant": variant,
    })
    session.commit()
    return {
        "mission_id": str(mission.id),
        "state_version": mission.state_version,
        "applied": estimate_json(estimate, origin, destination, label="ACTIVE ROUTE"),
    }
