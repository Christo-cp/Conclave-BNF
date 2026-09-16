from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
from argon2 import PasswordHasher
from geoalchemy2.elements import WKTElement
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.enums import IncidentStatus, MissionStatus
from app.core.errors import ApiError, ErrorCode
from app.db.models import (
    AcceptanceRequest,
    Ambulance,
    AmbulanceAssignment,
    AmbulanceEquipment,
    AuditLog,
    Capability,
    Equipment,
    Hospital,
    HospitalCapability,
    HospitalResource,
    Incident,
    Mission,
    MissionEvent,
    Notification,
    PatientRequirement,
    Reservation,
    Route,
    SimulationScenario,
    User,
)
from app.decision_engine.ambulance import AmbulanceCandidate, evaluate_ambulances
from app.decision_engine.hospital import HospitalCandidate, evaluate_hospitals
from app.decision_service import persist_decision
from app.realtime.broker import queue_event
from app.reservation_service import ReservationService
from app.routing.service import RoutingService

ph = PasswordHasher()


def ambulance_equipment_requirements(requirements: set[str]) -> set[str]:
    mapping = {
        "VENTILATOR": "VENTILATOR",
        "TRAUMA": "TRAUMA_KIT",
        "OXYGEN": "OXYGEN",
    }
    return {mapping[requirement] for requirement in requirements if requirement in mapping}


def golden_scenario(session: Session) -> dict:
    scenario = session.scalar(select(SimulationScenario).where(SimulationScenario.status == "READY").order_by(SimulationScenario.scenario_code))
    if scenario is None:
        raise ApiError(409, ErrorCode.ROUTING_PROVIDER_ERROR, "No simulated scenario is available.")
    return scenario.configuration


def incident_json(incident: Incident) -> dict:
    return {
        "id": str(incident.id),
        "incident_code": incident.incident_code,
        "incident_type": incident.incident_type,
        "severity": incident.severity,
        "status": incident.status,
        "latitude": float(incident.latitude),
        "longitude": float(incident.longitude),
        "address_text": incident.address_text,
        "patient_count": incident.patient_count,
        "notes": incident.notes,
        "data_mode": incident.data_mode,
    }


def issue_token(settings: Settings, user: User) -> str:
    return jwt.encode(
        {"sub": str(user.id), "roles": [role.code for role in user.roles], "exp": datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


def audit(session: Session, actor: UUID | None, action: str, entity: str, entity_id: str, payload: dict | None = None) -> None:
    session.add(AuditLog(actor_id=actor, action=action, entity_type=entity, entity_id=entity_id, payload=payload or {}))


def login(session: Session, settings: Settings, email: str, password: str) -> str:
    user = session.scalar(select(User).where(User.email == email.lower()))
    if user is None:
        raise ApiError(401, ErrorCode.AUTHENTICATION_ERROR, "Invalid email or password.")
    try:
        ph.verify(user.password_hash, password)
    except Exception as exc:
        raise ApiError(401, ErrorCode.AUTHENTICATION_ERROR, "Invalid email or password.") from exc
    session.commit()
    return issue_token(settings, user)


def create_incident(session: Session, actor: User, payload) -> Incident:
    count = session.scalar(select(Incident).order_by(Incident.created_at.desc()))
    sequence = (int(count.incident_code[-6:]) + 1) if count else 1
    incident = Incident(incident_code=f"INC-{sequence:06d}", incident_type=payload.incident_type, severity=payload.severity, location=WKTElement(f"POINT({payload.longitude} {payload.latitude})", srid=4326), latitude=payload.latitude, longitude=payload.longitude, address_text=payload.address_text, patient_count=payload.patient_count, notes=payload.notes, status=IncidentStatus.CREATED, data_mode="SIMULATED", created_by=actor.id)
    session.add(incident)
    session.flush()
    audit(session, actor.id, "INCIDENT_CREATED", "incident", str(incident.id))
    session.commit()
    return incident


def add_requirement(session: Session, actor: User, incident_id: UUID, payload) -> PatientRequirement:
    if session.get(Incident, incident_id) is None:
        raise ApiError(404, ErrorCode.NOT_FOUND, "Incident not found.")
    if session.scalar(select(PatientRequirement).where(PatientRequirement.incident_id == incident_id, PatientRequirement.requirement_code == payload.code)):
        raise ApiError(409, ErrorCode.CONFLICT, "Requirement already exists.")
    requirement = PatientRequirement(incident_id=incident_id, requirement_code=payload.code, level=payload.level, notes=payload.notes)
    session.add(requirement)
    audit(session, actor.id, "REQUIREMENT_ADDED", "incident", str(incident_id))
    session.commit()
    return requirement


def match_ambulances(session: Session, incident_id: UUID, settings: Settings) -> list[dict]:
    incident = session.get(Incident, incident_id)
    if incident is None:
        raise ApiError(404, ErrorCode.NOT_FOUND, "Incident not found.")
    requirements = list(session.scalars(select(PatientRequirement).where(PatientRequirement.incident_id == incident_id)))
    required = ambulance_equipment_requirements(
        {item.requirement_code for item in requirements if item.level == "REQUIRED"}
    )
    preferred = ambulance_equipment_requirements(
        {item.requirement_code for item in requirements if item.level == "PREFERRED"}
    )
    ambulances = list(session.scalars(select(Ambulance).order_by(Ambulance.ambulance_code)))
    active_mission_ambulances = set(session.scalars(select(Mission.ambulance_id).where(Mission.status.not_in({MissionStatus.COMPLETED, MissionStatus.CANCELLED, MissionStatus.FAILED}))))
    routing = RoutingService()
    scenario = golden_scenario(session)
    candidates = []
    for ambulance in ambulances:
        equipment = {code for code, in session.execute(select(Equipment.code).join(AmbulanceEquipment, AmbulanceEquipment.equipment_id == Equipment.id).where(AmbulanceEquipment.ambulance_id == ambulance.id, AmbulanceEquipment.quantity > 0))}
        candidates.append(AmbulanceCandidate(ambulance.ambulance_code, routing.ambulance_eta(scenario, ambulance.ambulance_code), ambulance.status, ambulance.gps_updated_at, frozenset(equipment), ambulance.id in active_mission_ambulances))
    result = evaluate_ambulances(candidates, required, preferred, datetime.now(UTC), settings.gps_stale_after_s)
    persist_decision(session, incident.id, "AMBULANCE_MATCH", "ambulance-v1", settings.config_version, [{"candidate_id": item.code, "eligible": item.eligible, "score": item.score, "rank": item.rank, "reasons": list(item.reasons)} for item in result], {"gps": settings.gps_stale_after_s}, input_snapshot={"incident_id": str(incident.id), "required": sorted(required), "preferred": sorted(preferred)}, commit=False)
    if not any(item.eligible for item in result):
        incident.status = IncidentStatus.ESCALATED
        audit(session, None, "AMBULANCE_MATCH_ESCALATED", "incident", str(incident.id))
        session.commit()
    decisions = {item.code: item for item in result}
    return [
        {
            **item.__dict__,
            "ambulance_id": str(ambulance.id),
        }
        for ambulance in ambulances
        if (item := decisions[ambulance.ambulance_code]) is not None
    ]


def confirm_ambulance(session: Session, actor: User, ambulance_id: UUID, incident_id: UUID, key: str, override_reason: str | None) -> Mission:
    existing = session.scalar(select(AmbulanceAssignment).where(AmbulanceAssignment.idempotency_key == key))
    if existing:
        return session.get(Mission, session.scalar(select(Mission.id).where(Mission.incident_id == existing.incident_id, Mission.ambulance_id == existing.ambulance_id)))
    incident = session.get(Incident, incident_id)
    ambulance = session.get(Ambulance, ambulance_id)
    if not incident or not ambulance:
        raise ApiError(404, ErrorCode.NOT_FOUND, "Incident or ambulance not found.")
    recommendations = match_ambulances(session, incident_id, get_settings())
    selected = next((item for item in recommendations if item["ambulance_id"] == str(ambulance_id)), None)
    if selected is None or not selected["eligible"]:
        raise ApiError(409, ErrorCode.CONFLICT, "Ambulance is not eligible.")
    if selected["rank"] != 1 and not override_reason:
        raise ApiError(422, ErrorCode.VALIDATION_ERROR, "Override reason is required for a non-top recommendation.")
    sequence = session.query(Mission).count() + 1
    assignment = AmbulanceAssignment(incident_id=incident_id, ambulance_id=ambulance_id, status="ASSIGNED", idempotency_key=key, assigned_by=actor.id)
    mission = Mission(mission_code=f"MSN-{sequence:06d}", incident_id=incident_id, ambulance_id=ambulance_id, status=MissionStatus.ASSIGNED, state_version=1)
    session.add_all([assignment, mission])
    ambulance.status = "DISPATCHED"
    incident.status = IncidentStatus.DISPATCHED
    audit(session, actor.id, "AMBULANCE_CONFIRMED", "mission", mission.mission_code)
    if override_reason:
        audit(session, actor.id, "AMBULANCE_OVERRIDE", "mission", mission.mission_code, {"reason": override_reason})
    queue_event(session, "mission.assigned", mission.id, mission.state_version, {"mission_id": str(mission.id), "incident_id": str(incident_id), "ambulance_id": str(ambulance_id)})
    session.commit()
    return mission


def calculate_route(session: Session, incident_id: UUID, hospital_id: UUID | None) -> Route:
    incident = session.get(Incident, incident_id)
    hospital = session.get(Hospital, hospital_id) if hospital_id else None
    if not incident:
        raise ApiError(404, ErrorCode.NOT_FOUND, "Incident not found.")
    if hospital_id and not hospital:
        raise ApiError(404, ErrorCode.NOT_FOUND, "Hospital not found.")
    if hospital is None:
        raise ApiError(409, ErrorCode.ROUTING_PROVIDER_ERROR, "A hospital destination is required for route calculation.")
    estimate = RoutingService().calculate(golden_scenario(session), incident.incident_code, hospital.hospital_code)
    route = Route(incident_id=incident_id, provider=estimate.provider, distance_m=estimate.distance_m, duration_seconds=estimate.duration_seconds, traffic_duration_seconds=estimate.traffic_duration_seconds, confidence=estimate.confidence, fallback_used=estimate.fallback_used, origin=WKTElement(f"POINT({incident.longitude} {incident.latitude})", srid=4326), destination=WKTElement(f"POINT({hospital.longitude} {hospital.latitude})", srid=4326))
    session.add(route)
    queue_event(session, "mission.route.updated", route.id, 1, {"incident_id": str(incident_id), "route_id": str(route.id)})
    session.commit()
    return route


def route_json(route: Route) -> dict:
    return {
        "id": str(route.id),
        "incident_id": str(route.incident_id),
        "provider": route.provider,
        "distance_m": route.distance_m,
        "duration_seconds": route.duration_seconds,
        "traffic_duration_seconds": route.traffic_duration_seconds,
        "confidence": float(route.confidence),
        "fallback_used": route.fallback_used,
    }


def match_hospitals(session: Session, incident_id: UUID) -> list[dict]:
    incident = session.get(Incident, incident_id)
    if not incident:
        raise ApiError(404, ErrorCode.NOT_FOUND, "Incident not found.")
    requirements = list(session.scalars(select(PatientRequirement).where(PatientRequirement.incident_id == incident_id)))
    required = {item.requirement_code for item in requirements if item.level == "REQUIRED"}
    preferred = {item.requirement_code for item in requirements if item.level == "PREFERRED"}
    now = datetime.now(UTC)
    resource_codes = {resource.resource_type for resource in session.scalars(select(HospitalResource))}
    hospitals = list(session.scalars(select(Hospital).where(Hospital.status == "ACTIVE").order_by(Hospital.hospital_code)))
    decisions = []
    for hospital in hospitals:
        rejected = session.scalar(select(AcceptanceRequest).where(AcceptanceRequest.incident_id == incident_id, AcceptanceRequest.hospital_id == hospital.id, AcceptanceRequest.status == "REJECTED"))
        if rejected:
            continue
        capabilities = {code for code, in session.execute(select(Capability.code).join(HospitalCapability, HospitalCapability.capability_id == Capability.id).where(HospitalCapability.hospital_id == hospital.id, HospitalCapability.status == "ACTIVE"))}
        hospital_resources = list(session.scalars(select(HospitalResource).where(HospitalResource.hospital_id == hospital.id)))
        resources = {resource.resource_type: resource.available_capacity for resource in hospital_resources}
        stale_resources = frozenset(resource.resource_type for resource in hospital_resources if resource.last_updated_at is None or (now - resource.last_updated_at).total_seconds() > get_settings().resource_stale_after_s)
        decisions.append(HospitalCandidate(hospital.hospital_code, RoutingService().hospital_eta(golden_scenario(session), hospital.hospital_code), frozenset(capabilities), resources, stale_resources=stale_resources))
    result = evaluate_hospitals(decisions, required, preferred, required & resource_codes)
    persist_decision(session, incident.id, "HOSPITAL_MATCH", "hospital-v1", get_settings().config_version, [{"candidate_id": item.code, "eligible": item.eligible, "score": item.score, "rank": item.rank, "reasons": list(item.reasons)} for item in result], {"resource_stale_after_s": get_settings().resource_stale_after_s}, input_snapshot={"incident_id": str(incident.id), "required": sorted(required), "preferred": sorted(preferred)}, commit=False)
    if not any(item.eligible for item in result):
        incident.status = IncidentStatus.ESCALATED
        session.commit()
    decisions = {item.code: item for item in result}
    return [
        {
            **item.__dict__,
            "hospital_id": str(hospital.id),
        }
        for hospital in hospitals
        if (item := decisions[hospital.hospital_code]) is not None
    ]


def hold_acceptance(session: Session, actor: User, incident_id: UUID, hospital_id: UUID, key: str, settings: Settings) -> AcceptanceRequest:
    existing = session.scalar(select(AcceptanceRequest).where(AcceptanceRequest.idempotency_key == key))
    if existing:
        return existing
    resources = list(session.scalars(select(HospitalResource).where(HospitalResource.hospital_id == hospital_id).with_for_update()))
    requirements = list(session.scalars(select(PatientRequirement).where(PatientRequirement.incident_id == incident_id, PatientRequirement.level == "REQUIRED")))
    wanted = {item.requirement_code for item in requirements}
    capacity = [resource for resource in resources if resource.resource_type in wanted]
    if len(capacity) != len(wanted):
        raise ApiError(409, ErrorCode.MISSING_CAPABILITY, "A required resource is not available at this hospital.")
    if any(resource.status != "ACTIVE" or resource.available_capacity is None or resource.available_capacity < 1 or not resource.last_updated_at or (datetime.now(UTC) - resource.last_updated_at).total_seconds() > settings.resource_stale_after_s for resource in capacity):
        raise ApiError(409, ErrorCode.RESOURCE_UNAVAILABLE, "Required resource cannot be held.")
    expires = datetime.now(UTC) + timedelta(seconds=settings.reservation_hold_ttl_s)
    request = AcceptanceRequest(incident_id=incident_id, hospital_id=hospital_id, idempotency_key=key, expires_at=expires)
    session.add(request)
    session.flush()
    for resource in capacity:
        resource.available_capacity -= 1
        resource.reserved_capacity += 1
        resource.version += 1
        session.add(Reservation(reservation_code=f"RES-{session.query(Reservation).count()+1:06d}", acceptance_request_id=request.id, incident_id=incident_id, hospital_id=hospital_id, hospital_resource_id=resource.id, expires_at=expires))
    audit(session, actor.id, "RESOURCE_HELD", "acceptance_request", str(request.id))
    queue_event(session, "resource.reserved", request.id, 1, {"incident_id": str(incident_id), "hospital_id": str(hospital_id)})
    session.commit()
    return request


def accept_request(session: Session, actor: User, request_id: UUID, key: str) -> AcceptanceRequest:
    request = session.get(AcceptanceRequest, request_id, with_for_update=True)
    if not request:
        raise ApiError(404, ErrorCode.NOT_FOUND, "Acceptance request not found.")
    hospital = session.get(Hospital, request.hospital_id)
    if hospital is None:
        raise ApiError(404, ErrorCode.NOT_FOUND, "Hospital not found.")
    actor_roles = {role.code for role in actor.roles}
    hospital_roles = {"HOSPITAL_STAFF", "HOSPITAL_ADMIN", "SYSTEM_ADMIN"}
    if "SYSTEM_ADMIN" not in actor_roles and (
        not actor_roles.intersection(hospital_roles)
        or actor.hospital_id != hospital.id
    ):
        raise ApiError(403, ErrorCode.AUTHORIZATION_ERROR, "Only staff of the target hospital may accept.")
    if request.status != "PENDING":
        if request.status == "ACCEPTED":
            return request
        raise ApiError(409, ErrorCode.CONFLICT, "Acceptance request is closed.")
    if request.expires_at <= datetime.now(UTC):
        for reservation in session.scalars(select(Reservation).where(Reservation.acceptance_request_id == request.id, Reservation.status == "HELD").with_for_update()):
            ReservationService(session).expire_in_transaction(reservation.id)
        request.status = "EXPIRED"
        session.commit()
        raise ApiError(409, ErrorCode.RESOURCE_UNAVAILABLE, "Acceptance hold expired.")
    request.status = "ACCEPTED"
    request.responded_by = actor.id
    for reservation in session.scalars(select(Reservation).where(Reservation.acceptance_request_id == request.id).with_for_update()):
        reservation.status = "CONFIRMED"
    incident = session.get(Incident, request.incident_id)
    if incident:
        incident.status = IncidentStatus.RESOURCE_RESERVED
        mission = session.scalar(select(Mission).where(Mission.incident_id == incident.id).with_for_update())
        if mission:
            mission.selected_hospital_id = request.hospital_id
            mission.state_version += 1
            session.add(MissionEvent(mission_id=mission.id, incident_id=incident.id, event_type="DESTINATION_CHANGED", payload={"to_hospital_id": str(request.hospital_id)}, actor_id=actor.id))
            session.add(Notification(incident_id=incident.id, event_type="DESTINATION_CHANGED", payload={"mission_id": str(mission.id), "hospital_id": str(request.hospital_id)}))
    audit(session, actor.id, "HOSPITAL_ACCEPTED", "acceptance_request", str(request.id))
    queue_event(session, "hospital.accepted", request.id, 1, {"incident_id": str(request.incident_id), "hospital_id": str(request.hospital_id)})
    session.commit()
    return request


MISSION_TRANSITIONS = {
    MissionStatus.ASSIGNED: {MissionStatus.EN_ROUTE_TO_PATIENT},
    MissionStatus.EN_ROUTE_TO_PATIENT: {MissionStatus.ON_SCENE},
    MissionStatus.ON_SCENE: {MissionStatus.PATIENT_ON_BOARD},
    MissionStatus.PATIENT_ON_BOARD: {MissionStatus.EN_ROUTE_TO_HOSPITAL},
    MissionStatus.EN_ROUTE_TO_HOSPITAL: {MissionStatus.ARRIVED},
    MissionStatus.ARRIVED: {MissionStatus.HANDOVER},
    MissionStatus.HANDOVER: {MissionStatus.COMPLETED},
}


def patch_mission(session: Session, actor: User, mission_id: UUID, status: str, state_version: int) -> Mission:
    mission = session.get(Mission, mission_id, with_for_update=True)
    if not mission:
        raise ApiError(404, ErrorCode.NOT_FOUND, "Mission not found.")
    if mission.state_version != state_version:
        raise ApiError(409, ErrorCode.MISSION_STATE_CONFLICT, "Mission state is newer than this client.")
    current, target = MissionStatus(mission.status), MissionStatus(status)
    if target not in MISSION_TRANSITIONS.get(current, set()):
        raise ApiError(409, ErrorCode.CONFLICT, "Invalid mission state transition.")
    if target == MissionStatus.EN_ROUTE_TO_HOSPITAL and mission.selected_hospital_id is None:
        raise ApiError(409, ErrorCode.CONFLICT, "A confirmed destination is required.")
    mission.status = target
    mission.state_version += 1
    session.add(MissionEvent(mission_id=mission.id, incident_id=mission.incident_id, event_type=target.value, payload={"from": current.value, "to": target.value}, actor_id=actor.id))
    session.add(Notification(incident_id=mission.incident_id, event_type=target.value, payload={"mission_id": str(mission.id)}))
    audit(session, actor.id, "MISSION_STATE_CHANGED", "mission", str(mission.id), {"to": target.value})
    if target == MissionStatus.EN_ROUTE_TO_HOSPITAL:
        incident = session.get(Incident, mission.incident_id)
        if incident:
            incident.status = IncidentStatus.IN_TRANSIT
    queue_event(session, "mission.state.changed", mission.id, mission.state_version, {"mission_id": str(mission.id), "status": target.value})
    session.commit()
    return mission
