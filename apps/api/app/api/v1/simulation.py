from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.core.enums import Role
from app.db.models import User
from app.dependencies import Db, require_roles
from app.schemas import SimulationControl
from app.simulation.controls import run_control

router = APIRouter(prefix="/admin/simulation", tags=["simulation"])
SimulationUser = Annotated[User, Depends(require_roles(Role.SYSTEM_ADMIN, Role.DEMO_CONTROLLER))]


@router.post("/{action:path}")
def control(action: str, payload: SimulationControl, session: Db, _: SimulationUser, settings: Annotated[Settings, Depends(get_settings)]):
    return run_control(session, settings, action, payload.target_id, payload.value)
