from uuid import UUID

import jwt
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.models import User


def websocket_user(session: Session, settings: Settings, token: str | None) -> User | None:
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id = UUID(str(payload["sub"]))
    except (jwt.InvalidTokenError, KeyError, ValueError):
        return None
    user = session.get(User, user_id)
    return user if user and user.status == "ACTIVE" else None


def can_subscribe(user: User, channel: str) -> bool:
    kind, _, identifier = channel.partition(":")
    roles = {role.code for role in user.roles}
    if not identifier:
        return False
    if kind in {"dispatcher", "incident", "mission"}:
        return bool(roles.intersection({"DISPATCHER", "SYSTEM_ADMIN", "DEMO_CONTROLLER"}))
    if kind == "hospital":
        return bool(user.hospital_id and str(user.hospital_id) == identifier) or "SYSTEM_ADMIN" in roles
    if kind == "ambulance":
        return bool(roles.intersection({"AMBULANCE_CREW", "DISPATCHER", "SYSTEM_ADMIN", "DEMO_CONTROLLER"}))
    return False
