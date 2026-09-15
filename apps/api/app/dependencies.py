from collections.abc import Generator
from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.enums import Role
from app.core.errors import ApiError, ErrorCode
from app.db.models import User
from app.db.session import get_session


def db(settings: Annotated[Settings, Depends(get_settings)]) -> Generator[Session, None, None]:
    session = get_session(settings.database_url)()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


Db = Annotated[Session, Depends(db)]


def current_user(
    authorization: Annotated[str | None, Header()] = None,
    session: Db = None,  # type: ignore[assignment]
    settings: Annotated[Settings, Depends(get_settings)] = None,  # type: ignore[assignment]
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise ApiError(401, ErrorCode.AUTHENTICATION_ERROR, "Authentication required.")
    try:
        payload = jwt.decode(authorization[7:], settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id = UUID(str(payload["sub"]))
    except (jwt.InvalidTokenError, KeyError, ValueError) as exc:
        raise ApiError(401, ErrorCode.AUTHENTICATION_ERROR, "Invalid authentication token.") from exc
    user = session.get(User, user_id)
    if user is None or user.status != "ACTIVE":
        raise ApiError(401, ErrorCode.AUTHENTICATION_ERROR, "Authentication required.")
    return user


CurrentUser = Annotated[User, Depends(current_user)]


def require_roles(*roles: Role):
    def dependency(user: CurrentUser) -> User:
        if not any(role.code in roles for role in user.roles):
            raise ApiError(403, ErrorCode.AUTHORIZATION_ERROR, "You are not authorized for this action.")
        return user

    return dependency


def require_role(*roles: Role):
    return Depends(require_roles(*roles))
