"""GET /api/v1/health/db: connectivity, migration version, simple query (db:4684-4698).

Never exposes credentials or connection details. A database failure returns 503 with
the error envelope and INTERNAL_ERROR (user decision 2026-09-13, docs/spec-conflicts.md).
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import Settings, get_settings
from app.core.errors import ApiError, ErrorCode
from app.db.session import get_engine

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/db")
def health_db(
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict[str, object]:
    try:
        with get_engine(settings.database_url).connect() as conn:
            simple_query = conn.execute(text("SELECT 1")).scalar_one()
            has_version_table = (
                conn.execute(
                    text("SELECT to_regclass('public.alembic_version')")
                ).scalar_one()
                is not None
            )
            migration_version = (
                conn.execute(
                    text("SELECT version_num FROM alembic_version")
                ).scalar_one_or_none()
                if has_version_table
                else None
            )
    except SQLAlchemyError as exc:
        raise ApiError(
            503, ErrorCode.INTERNAL_ERROR, "Database health check failed."
        ) from exc
    return {
        "connectivity": "ok",
        "migration_version": migration_version,
        "simple_query": simple_query,
    }
