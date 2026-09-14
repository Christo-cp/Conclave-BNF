"""X-Request-ID correlation and one structured log line per request.

tech:6247-6263 (X-Request-ID), tech:4776-4784 (request_id, user_id, route, duration,
status). `duration` is in milliseconds. A client-supplied X-Request-ID is echoed;
otherwise one is generated with the `req_` prefix of the tech:4510 example.
"""

import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.log import get_logger

REQUEST_ID_HEADER = "X-Request-ID"

logger = get_logger("http")


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER) or f"req_{uuid.uuid4().hex}"
        request.state.request_id = request_id
        started = time.perf_counter()
        status = 500
        try:
            response = await call_next(request)
            status = response.status_code
        finally:
            route = request.scope.get("route")
            logger.info(
                "request",
                extra={
                    "fields": {
                        "request_id": request_id,
                        "user_id": getattr(request.state, "user_id", None),
                        "route": getattr(route, "path", request.url.path),
                        "duration": round((time.perf_counter() - started) * 1000, 1),
                        "status": status,
                    }
                },
            )
        response.headers[REQUEST_ID_HEADER] = request_id
        return response
