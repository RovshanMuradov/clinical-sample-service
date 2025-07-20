import json
import time
from typing import Any, Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ..core.logging import (
    generate_correlation_id,
    get_logger,
    log_error,
    log_request,
    log_response,
    log_security_event,
    set_correlation_id,
)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging with correlation ID."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # Generate correlation ID
        correlation_id = (
            request.headers.get("X-Correlation-ID") or generate_correlation_id()
        )
        set_correlation_id(correlation_id)
        start_time = time.time()

        # Log request
        await self._log_request(request)

        # Process request
        try:
            response = await call_next(request)
            response_time = time.time() - start_time

            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id

            # Log response
            self._log_response(request, response, response_time)

            return response

        except Exception as e:
            response_time = time.time() - start_time
            self._log_error(request, e, response_time, correlation_id)
            raise

    async def _log_request(self, request: Request) -> None:
        """Log request details."""
        try:
            body = await self._get_request_body(request)
            log_request(
                method=request.method,
                url=str(request.url),
                headers=dict(request.headers),
                body=body,
            )
            self._log_auth_attempt(request)
        except Exception as e:
            logger = get_logger(__name__)
            logger.error(f"Error logging request: {e}")

    async def _get_request_body(self, request: Request) -> Any:
        """Get request body safely."""
        if request.method == "GET":
            return None

        try:
            body_bytes = await request.body()
            if not body_bytes:
                return None

            try:
                parsed_body = json.loads(body_bytes.decode("utf-8"))
                return (
                    parsed_body
                    if isinstance(parsed_body, dict)
                    else {"parsed_body": parsed_body}
                )
            except (json.JSONDecodeError, UnicodeDecodeError):
                return {"raw_body_size": len(body_bytes)}
        except Exception:
            return {"error": "Could not read request body"}

    def _log_auth_attempt(self, request: Request) -> None:
        """Log authentication attempt."""
        if request.url.path.startswith("/api/v1/auth/"):
            log_security_event(
                event_type="auth_attempt",
                details={
                    "endpoint": request.url.path,
                    "method": request.method,
                    "user_agent": request.headers.get("user-agent", "unknown"),
                    "remote_addr": request.client.host if request.client else "unknown",
                },
            )

    def _log_response(
        self, request: Request, response: Response, response_time: float
    ) -> None:
        """Log response details."""
        response_size = 0
        if hasattr(response, "body") and response.body:
            response_size = len(response.body)

        log_response(
            status_code=response.status_code,
            response_time=response_time,
            response_size=response_size,
        )

        # Log security events for auth endpoints
        if request.url.path.startswith("/api/v1/auth/"):
            log_security_event(
                event_type="auth_response",
                details={
                    "endpoint": request.url.path,
                    "status_code": response.status_code,
                    "response_time_ms": round(response_time * 1000, 2),
                    "success": 200 <= response.status_code < 300,
                },
            )

    def _log_error(
        self,
        request: Request,
        error: Exception,
        response_time: float,
        correlation_id: str,
    ) -> None:
        """Log error details."""
        log_error(
            error=error,
            context={
                "request_method": request.method,
                "request_url": str(request.url),
                "response_time": response_time,
                "correlation_id": correlation_id,
            },
        )

        log_security_event(
            event_type="request_failed",
            details={
                "endpoint": request.url.path,
                "method": request.method,
                "error": str(error),
                "response_time_ms": round(response_time * 1000, 2),
            },
        )


class SecurityLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for security event logging."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # Check for suspicious patterns
        self._check_suspicious_patterns(request)

        # Process request
        response = await call_next(request)

        # Log failed authentication attempts
        if request.url.path.startswith("/api/v1/auth/") and response.status_code in [
            401,
            403,
        ]:
            log_security_event(
                event_type="auth_failed",
                details={
                    "endpoint": request.url.path,
                    "method": request.method,
                    "status_code": response.status_code,
                    "user_agent": request.headers.get("user-agent", "unknown"),
                    "remote_addr": request.client.host if request.client else "unknown",
                },
            )

        return response

    def _check_suspicious_patterns(self, request: Request) -> None:
        """Check for suspicious request patterns."""

        # Check for SQL injection patterns
        url_str = str(request.url).lower()
        suspicious_sql_patterns = [
            "union",
            "select",
            "insert",
            "update",
            "delete",
            "drop",
            "exec",
            "execute",
            "script",
            "javascript",
            "onload",
            "onerror",
        ]

        for pattern in suspicious_sql_patterns:
            if pattern in url_str:
                log_security_event(
                    event_type="suspicious_request",
                    details={
                        "pattern": pattern,
                        "url": str(request.url),
                        "method": request.method,
                        "user_agent": request.headers.get("user-agent", "unknown"),
                        "remote_addr": (
                            request.client.host if request.client else "unknown"
                        ),
                    },
                )
                break

        # Check for excessive header size (possible DoS)
        total_header_size = sum(len(k) + len(v) for k, v in request.headers.items())
        if total_header_size > 8192:  # 8KB limit
            log_security_event(
                event_type="large_headers",
                details={
                    "header_size": total_header_size,
                    "url": str(request.url),
                    "method": request.method,
                    "remote_addr": request.client.host if request.client else "unknown",
                },
            )

        # Check for suspicious user agents
        user_agent = request.headers.get("user-agent", "").lower()
        suspicious_agents = ["sqlmap", "nmap", "nikto", "dirb", "gobuster", "wfuzz"]

        for agent in suspicious_agents:
            if agent in user_agent:
                log_security_event(
                    event_type="suspicious_user_agent",
                    details={
                        "user_agent": user_agent,
                        "url": str(request.url),
                        "method": request.method,
                        "remote_addr": (
                            request.client.host if request.client else "unknown"
                        ),
                    },
                )
                break


class PerformanceLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for performance monitoring."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        start_time = time.time()

        response = await call_next(request)

        response_time = time.time() - start_time

        # Log slow requests (>1 second)
        if response_time > 1.0:
            logger = get_logger("app.performance")
            logger.warning(
                "Slow request detected",
                extra={
                    "event": "slow_request",
                    "method": request.method,
                    "url": str(request.url),
                    "response_time_ms": round(response_time * 1000, 2),
                    "status_code": response.status_code,
                },
            )

        return response
