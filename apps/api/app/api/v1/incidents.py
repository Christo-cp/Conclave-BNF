from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.core.enums import Role
from app.core.errors import ApiError, ErrorCode
from app.db.models import Incident, PatientRequirement, User
from app.dependencies import CurrentUser, Db, require_roles
from app.schemas import IncidentCreate, RequirementCreate
from app.services import add_requirement, create_incident, incident_json

router = APIRouter(prefix="/incidents", tags=["incidents"])


dispatcher_user = require_roles(Role.DISPATCHER, Role.SYSTEM_ADMIN)
DispatcherUser = Annotated[User, Depends(dispatcher_user)]


@router.post("")
def create(payload: IncidentCreate, session: Db, user: DispatcherUser):
    return incident_json(create_incident(session, user, payload))


@router.get("/{incident_id}")
def get_incident(incident_id: UUID, session: Db, _: CurrentUser):
    incident = session.get(Incident, incident_id)
    if incident is None:
        raise ApiError(404, ErrorCode.NOT_FOUND, "Incident not found.")
    return incident_json(incident)


@router.post("/{incident_id}/requirements")
def requirements(incident_id: UUID, payload: RequirementCreate, session: Db, user: CurrentUser):
    return add_requirement(session, user, incident_id, payload)


@router.get("/{incident_id}/requirements")
def list_requirements(incident_id: UUID, session: Db, _: CurrentUser):
    return list(session.scalars(select(PatientRequirement).where(PatientRequirement.incident_id == incident_id)))
