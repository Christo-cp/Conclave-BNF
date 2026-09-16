from uuid import UUID

from fastapi import APIRouter
from sqlalchemy import select

from app.core.enums import Role
from app.core.errors import ApiError, ErrorCode
from app.crew_service import apply_reroute, compare_routes, load_mission, mission_view
from app.db.models import Mission, User
from app.dependencies import CurrentUser, Db
from app.mission_service import assign_destination
from app.schemas import DestinationAssign, MissionPatch, RerouteApply
from app.services import patch_mission

router = APIRouter(prefix="/missions", tags=["missions"])


def can_access_mission(user: User, mission: Mission) -> bool:
    roles = {role.code for role in user.roles}
    return bool(
        roles & {Role.DISPATCHER.value, Role.SYSTEM_ADMIN.value}
        or (Role.AMBULANCE_CREW.value in roles and user.ambulance_id == mission.ambulance_id)
    )


def mission_json(item: Mission) -> dict:
    return {"id": str(item.id), "mission_code": item.mission_code, "incident_id": str(item.incident_id), "ambulance_id": str(item.ambulance_id), "selected_hospital_id": str(item.selected_hospital_id) if item.selected_hospital_id else None, "selected_route_id": str(item.selected_route_id) if item.selected_route_id else None, "status": item.status, "state_version": item.state_version}


@router.get("")
def list_missions(session: Db, user: CurrentUser):
    return [mission_json(item) for item in session.scalars(select(Mission).order_by(Mission.created_at.desc())) if can_access_mission(user, item)]


@router.get("/{mission_id}")
def get_mission(mission_id: UUID, session: Db, _: CurrentUser):
    item = session.get(Mission, mission_id)
    if item is None:
        raise ApiError(404, ErrorCode.NOT_FOUND, "Mission not found.")
    if not can_access_mission(_, item):
        raise ApiError(403, ErrorCode.AUTHORIZATION_ERROR, "Mission scope denied.")
    return mission_json(item)


@router.patch("/{mission_id}")
def patch(mission_id: UUID, payload: MissionPatch, session: Db, user: CurrentUser):
    mission = session.get(Mission, mission_id)
    if mission is None:
        raise ApiError(404, ErrorCode.NOT_FOUND, "Mission not found.")
    if not can_access_mission(user, mission):
        raise ApiError(403, ErrorCode.AUTHORIZATION_ERROR, "Mission scope denied.")
    return mission_json(patch_mission(session, user, mission_id, payload.status, payload.state_version))


def scoped_mission(session, user: User, mission_id: UUID) -> Mission:
    mission = load_mission(session, mission_id)
    if not can_access_mission(user, mission):
        raise ApiError(403, ErrorCode.AUTHORIZATION_ERROR, "Mission scope denied.")
    return mission


@router.get("/{mission_id}/crew-view")
def crew_view(mission_id: UUID, session: Db, user: CurrentUser):
    return mission_view(session, scoped_mission(session, user, mission_id))


@router.get("/{mission_id}/route-options")
def route_options(mission_id: UUID, session: Db, user: CurrentUser):
    return compare_routes(session, scoped_mission(session, user, mission_id))


@router.post("/{mission_id}/reroute")
def reroute(mission_id: UUID, payload: RerouteApply, session: Db, user: CurrentUser):
    return apply_reroute(session, user, scoped_mission(session, user, mission_id), payload.variant, payload.state_version)


@router.post("/{mission_id}/destination")
def destination(mission_id: UUID, payload: DestinationAssign, session: Db, user: CurrentUser):
    return mission_json(assign_destination(session, user.id, mission_id, payload.hospital_id, payload.reservation_id))
