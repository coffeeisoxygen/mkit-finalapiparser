import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.mlogg import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):  # noqa: ANN001
        start_time = time.time()
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        headers = dict(request.headers)
        log = logger.bind(
            client_ip=client_ip,
            user_agent=user_agent,
            headers=headers,
            method=request.method,
            url=str(request.url),
        )
        log.info(f"Incoming Request: {request.method} {request.url.path}")

        response = await call_next(request)

        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        log.info(
            f"Outgoing Response: {request.method} {request.url.path} - Status: {response.status_code} - Process Time: {process_time:.4f}s"
        )
        return response
