import logging
import time
from uuid import uuid4

from starlette.datastructures import MutableHeaders
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.context import request_id_var
from app.core.logging import log_event

logger = logging.getLogger(__name__)


class RequestContextMiddleware:

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = str(uuid4())
        token = request_id_var.set(request_id)
        start_time = time.perf_counter()
        status_code = 500
        response_started = False

        async def send_with_headers(message: Message) -> None:
            nonlocal status_code, response_started
            if message["type"] == "http.response.start":
                response_started = True
                status_code = message["status"]
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                headers = MutableHeaders(scope=message)
                headers["X-Request-ID"] = request_id
                headers["X-Process-Time-Ms"] = f"{elapsed_ms:.2f}"
            await send(message)

        try:
            await self.app(scope, receive, send_with_headers)
        except Exception:
            log_event(
                logger,
                logging.ERROR,
                "request_failed",
                exc_info=True,
                method=scope["method"],
                path=scope["path"],
            )
            if response_started:
                raise
            response = JSONResponse(
                status_code=500,
                content={"detail": "Erro interno do servidor."},
            )
            await response(scope, receive, send_with_headers)
        finally:
            log_event(
                logger,
                logging.INFO,
                "request_completed",
                method=scope["method"],
                path=scope["path"],
                status_code=status_code,
                total_latency_ms=round((time.perf_counter() - start_time) * 1000, 2),
            )
            request_id_var.reset(token)
