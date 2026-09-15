from uuid import UUID

from fastapi import APIRouter
from sqlalchemy import select

from app.core.errors import ApiError, ErrorCode
from app.db.models import Mission
from app.dependencies import CurrentUser, Db
from app.mission_service import assign_destination
from app.schemas import DestinationAssign, MissionPatch
from app.services import patch_mission

router = APIRouter(prefix="/missions", tags=["missions"])


def mission_json(item: Mission) -> dict:
    return {"id": str(item.id), "mission_code": item.mission_code, "incident_id": str(item.incident_id), "ambulance_id": str(item.ambulance_id), "selected_hospital_id": str(item.selected_hospital_id) if item.selected_hospital_id else None, "selected_route_id": str(item.selected_route_id) if item.selected_route_id else None, "status": item.status, "state_version": item.state_version}


@router.get("")
def list_missions(session: Db, _: CurrentUser):
    return [mission_json(item) for item in session.scalars(select(Mission).order_by(Mission.created_at.desc()))]


@router.get("/{mission_id}")
def get_mission(mission_id: UUID, session: Db, _: CurrentUser):
    item = session.get(Mission, mission_id)
    if item is None:
        raise ApiError(404, ErrorCode.NOT_FOUND, "Mission not found.")
    return mission_json(item)


@router.patch("/{mission_id}")
def patch(mission_id: UUID, payload: MissionPatch, session: Db, user: CurrentUser):
    return patch_mission(session, user, mission_id, payload.status, payload.state_version)


@router.post("/{mission_id}/destination")
def destination(mission_id: UUID, payload: DestinationAssign, session: Db, user: CurrentUser):
    return assign_destination(session, user.id, mission_id, payload.hospital_id, payload.reservation_id)
