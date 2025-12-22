import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.metrics import SCAN_LATENCY_SECONDS


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id

        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000.0

        request.state.latency_ms = elapsed_ms
        response.headers["X-Request-ID"] = request_id

        # Record latency only for the scan endpoint
        if request.url.path == "/v1/scan":
            SCAN_LATENCY_SECONDS.observe(elapsed_ms / 1000.0)

        return response

