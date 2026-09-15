"""FastAPI application (plan S0)."""

from fastapi import FastAPI

from app.api.v1 import (
    alerts,
    auth,
    dispatch,
    health,
    incidents,
    missions,
    resources,
    simulation,
)
from app.core.errors import ApiError, api_error_handler
from app.core.log import configure_logging
from app.core.middleware import RequestContextMiddleware
from app.realtime.websocket import router as websocket_router

API_PREFIX = "/api/v1"


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title="Smart Ambulance API", openapi_url=f"{API_PREFIX}/openapi.json")
    app.add_middleware(RequestContextMiddleware)
    app.add_exception_handler(ApiError, api_error_handler)

    @app.get("/", tags=["service"])
    def root() -> dict[str, str]:
        return {"name": "ResQFlow API", "status": "ok"}

    app.include_router(health.router, prefix=API_PREFIX)
    app.include_router(auth.router, prefix=API_PREFIX)
    app.include_router(alerts.router, prefix=API_PREFIX)
    app.include_router(incidents.router, prefix=API_PREFIX)
    app.include_router(dispatch.router, prefix=API_PREFIX)
    app.include_router(missions.router, prefix=API_PREFIX)
    app.include_router(resources.router, prefix=API_PREFIX)
    app.include_router(simulation.router, prefix=API_PREFIX)
    app.include_router(websocket_router, prefix=API_PREFIX)
    return app


app = create_app()
