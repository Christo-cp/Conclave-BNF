from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.dependencies import CurrentUser, Db
from app.schemas import LoginRequest
from app.services import issue_token, login

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login_endpoint(payload: LoginRequest, session: Db, settings: Annotated[Settings, Depends(get_settings)]):
    return {"access_token": login(session, settings, payload.email, payload.password), "token_type": "bearer"}


@router.post("/logout")
def logout(_: CurrentUser):
    return {"logged_out": True}


@router.get("/me")
def me(user: CurrentUser):
    return {"id": str(user.id), "name": user.name, "email": user.email, "roles": [role.code for role in user.roles]}


@router.post("/refresh")
def refresh(user: CurrentUser, settings: Annotated[Settings, Depends(get_settings)]):
    return {"access_token": issue_token(settings, user), "token_type": "bearer"}
