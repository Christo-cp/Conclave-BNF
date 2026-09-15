from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.core.enums import Role
from app.db.models import Notification, User
from app.dependencies import Db, require_roles

router = APIRouter(prefix="/alerts", tags=["alerts"])
AlertViewer = Annotated[User, Depends(require_roles(Role.DISPATCHER, Role.SYSTEM_ADMIN, Role.DEMO_CONTROLLER))]


def alert_json(item: Notification) -> dict:
    payload = item.payload or {}
    return {
        "id": str(item.id),
        "incident_id": str(item.incident_id) if item.incident_id else None,
        "type": item.event_type,
        "severity": payload.get("severity", "WARNING"),
        "message": payload.get("message", item.event_type.replace("_", " ").title()),
        "payload": payload,
        "created_at": item.created_at,
        "status": "ACTIVE",
        "data_mode": "SIMULATED",
    }


@router.get("/active")
def list_active_alerts(session: Db, _: AlertViewer):
    return [
        alert_json(item)
        for item in session.scalars(
            select(Notification).order_by(Notification.created_at.desc())
        )
    ]
