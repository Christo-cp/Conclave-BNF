"""FastAPI application (plan S0)."""

from fastapi import FastAPI

from app.api.v1 import health
from app.core.errors import ApiError, api_error_handler
from app.core.log import configure_logging
from app.core.middleware import RequestContextMiddleware

API_PREFIX = "/api/v1"


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title="Smart Ambulance API", openapi_url=f"{API_PREFIX}/openapi.json")
    app.add_middleware(RequestContextMiddleware)
    app.add_exception_handler(ApiError, api_error_handler)
    app.include_router(health.router, prefix=API_PREFIX)
    return app


app = create_app()
