"""Correlation ID and Request Tracking Middleware for CampusGPT (WP11).

Accepts or generates an X-Request-ID header, validates it, binds it to
the logging contextvar, and attaches it to all HTTP responses.
"""

import re
import uuid
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import request_id_var

# Valid request ID: 8 to 64 alphanumeric chars and hyphens
VALID_REQUEST_ID_REGEX = re.compile(r"^[A-Za-z0-9\-]{8,64}$")


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Middleware ensuring every HTTP request has a validated correlation ID."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        incoming_id = request.headers.get("X-Request-ID", "").strip()

        # Validate incoming ID or generate a new UUID4
        if incoming_id and VALID_REQUEST_ID_REGEX.match(incoming_id):
            correlation_id = incoming_id
        else:
            correlation_id = str(uuid.uuid4())

        # Bind to contextvar for the duration of this request
        token = request_id_var.set(correlation_id)
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = correlation_id
            return response
        finally:
            request_id_var.reset(token)

