import uuid
from time import perf_counter
from typing import Optional, Any

import structlog
from starlette.types import Scope, Receive, Send, Message


class FlaskRequestContextMiddleware:
    """Middleware for Flask to add request context to structlog."""

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        """Middleware logic executed for every HTTP request."""

        request_id = environ.get("HTTP_X_REQUEST_ID", str(uuid.uuid4()))
        request_method = environ.get("REQUEST_METHOD", "UNKNOWN")
        request_path = environ.get("PATH_INFO", "")

        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            request_method=request_method,
            request_path=request_path,
        )

        return self.app(environ, start_response)


# --- ASGI Request Logging Middleware (FastAPI/Starlette) ---
SENSITIVE_HEADERS = {"authorization", "cookie", "set-cookie", "x-api-key"}


def _headers_to_dict(raw_headers: list[tuple[bytes, bytes]]) -> dict[str, str]:
    return {k.decode("latin-1").lower(): v.decode("latin-1") for k, v in (raw_headers or [])}


def _sanitize_headers(headers: dict[str, str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for k, v in (headers or {}).items():
        lk = k.lower()
        if lk == "authorization":
            # Preserve scheme (e.g., "Bearer ***" or "Basic ***")
            parts = v.split(" ", 1)
            if len(parts) == 2:
                out[k] = f"{parts[0]} ***"
            else:
                out[k] = "***"
        elif lk in SENSITIVE_HEADERS:
            out[k] = "<redacted>"
        else:
            out[k] = v
    return out


def _client_ip(scope: Scope, headers: dict[str, str]) -> Optional[str]:
    xff = headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    client = scope.get("client")
    return client[0] if client else None


def _safe_int(value: Optional[str], default: int = 0) -> int:
    try:
        if value is None:
            return default
        v = int(value)
        return v if v >= 0 else default
    except Exception:
        return default


class RequestLoggingMiddleware:
    """Lightweight ASGI middleware that logs each HTTP request/response.

    - Uses structured logging with structlog
    - Avoids reading request/response bodies (logs sizes instead)
    - Distinguishes 2xx/3xx (info) vs 4xx (warning) vs 5xx (error)
    - For errors, includes sanitized headers and traceback when exceptions occur
    - Optionally propagates request_id to response headers
    """

    def __init__(
        self,
        app,
        logger: Optional[structlog.BoundLoggerBase] = None,
        slow_request_threshold_ms: Optional[int] = None,
        propagate_request_id: bool = True,
        skip_paths: Optional[set[str]] = None,
        skip_prefixes: Optional[tuple[str, ...]] = None,
        sample_2xx_rate: Optional[float] = None,
    ) -> None:
        self.app = app
        self.logger = logger or structlog.get_logger("http")
        self.slow_request_threshold_ms = slow_request_threshold_ms
        self.propagate_request_id = propagate_request_id
        self.skip_paths = skip_paths or {"/healthz", "/metrics"}
        self.skip_prefixes = skip_prefixes or ("/metrics",)
        self.sample_2xx_rate = sample_2xx_rate

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        headers_raw: list[tuple[bytes, bytes]] = scope.get("headers") or []
        req_headers = _headers_to_dict(headers_raw)

        orig_traceparent = req_headers.get("traceparent")
        request_id = (
            orig_traceparent
            or req_headers.get("x-request-id")
            or req_headers.get("x-amzn-trace-id")
            or str(uuid.uuid4())
        )
        method = scope.get("method", "UNKNOWN")
        path = scope.get("path", "")
        query_string = (scope.get("query_string") or b"").decode("latin-1")

        # Bind core request context for correlation
        structlog.contextvars.bind_contextvars(request_id=request_id, request_method=method, request_path=path)

        client_ip = _client_ip(scope, req_headers)
        user_agent = req_headers.get("user-agent")
        req_content_length = _safe_int(req_headers.get("content-length"))
        req_content_type = req_headers.get("content-type")

        start = perf_counter()
        resp: dict[str, Any] = {"status": None, "headers": [], "size": 0, "content_type": None}

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                resp["status"] = message.get("status")
                hdrs = list(message.get("headers") or [])
                resp["headers"] = hdrs
                rh = _headers_to_dict(hdrs)
                resp["content_type"] = rh.get("content-type")
                if self.propagate_request_id:
                    names = {k.lower() for k, _ in hdrs}
                    if b"x-request-id" not in names:
                        hdrs.append((b"x-request-id", request_id.encode("latin-1")))
                        message["headers"] = hdrs
                    if orig_traceparent and b"traceparent" not in names:
                        hdrs.append((b"traceparent", orig_traceparent.encode("latin-1")))
                        message["headers"] = hdrs
            elif message["type"] == "http.response.body":
                body = message.get("body") or b""
                resp["size"] += len(body)
            await send(message)

        log = self.logger.bind()

        # Skip noisy paths entirely (health/metrics) and OPTIONS requests; also skip configured prefixes
        skip_logging = (
            method == "OPTIONS" or (path in self.skip_paths) or any(path.startswith(p) for p in self.skip_prefixes)
        )
        if not skip_logging:
            log.info(
                "request.start",
                request_id=request_id,
                method=method,
                path=path,
                query=query_string,
                client_ip=client_ip,
                user_agent=user_agent,
                req_content_length=req_content_length,
                req_content_type=req_content_type,
            )

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception:
            duration_ms = int((perf_counter() - start) * 1000)
            # Log with traceback for unexpected exceptions
            log.error(
                "request.exception",
                request_id=request_id,
                method=method,
                path=path,
                query=query_string,
                client_ip=client_ip,
                user_agent=user_agent,
                duration_ms=duration_ms,
                req_content_length=req_content_length,
                req_content_type=req_content_type,
                status_code=500,
                response_size=resp["size"],
                exc_info=True,
                request_headers=_sanitize_headers(req_headers),
            )
            # Ensure context is cleared even when exceptions occur
            structlog.contextvars.clear_contextvars()
            raise

        duration_ms = int((perf_counter() - start) * 1000)
        status = int(resp["status"] or 200)

        # Sampling for successful responses
        sampled_ok = True
        if status < 400 and self.sample_2xx_rate is not None:
            try:
                import random

                sampled_ok = random.random() < max(0.0, min(1.0, float(self.sample_2xx_rate)))
            except Exception:
                sampled_ok = True

        is_slow = self.slow_request_threshold_ms is not None and duration_ms >= self.slow_request_threshold_ms

        level = "info"
        if status >= 500:
            level = "error"
        elif status >= 400:
            level = "warning"
        elif self.slow_request_threshold_ms is not None and duration_ms >= self.slow_request_threshold_ms:
            level = "warning"

        log_kwargs: dict[str, Any] = dict(
            request_id=request_id,
            method=method,
            path=path,
            query=query_string,
            client_ip=client_ip,
            user_agent=user_agent,
            status_code=status,
            duration_ms=duration_ms,
            response_size=int(resp["size"]),
            response_content_type=resp["content_type"],
            req_content_length=req_content_length,
            req_content_type=req_content_type,
            slow_request=is_slow,
            slow_threshold_ms=self.slow_request_threshold_ms,
        )
        if status >= 400:
            log_kwargs["request_headers"] = _sanitize_headers(req_headers)
            log_kwargs["response_headers"] = _sanitize_headers(_headers_to_dict(resp["headers"]))

        if not skip_logging:
            if level == "error":
                log.error("request.end", **log_kwargs)
            elif level == "warning":
                log.warning("request.end", **log_kwargs)
            else:
                if sampled_ok:
                    log.info("request.end", **log_kwargs)

        structlog.contextvars.clear_contextvars()
