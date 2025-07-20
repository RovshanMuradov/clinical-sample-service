import asyncio
import json
import time
from collections import defaultdict
from datetime import datetime
from typing import Awaitable, Callable, Dict, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from ..core.exceptions import RateLimitError, ValidationError
from ..core.logging import get_logger, log_security_event


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware for API endpoints."""

    def __init__(
        self,
        app: ASGIApp,
        requests_per_minute: int = 60,
        burst_limit: int = 10,
        window_size: int = 60,
        whitelist: Optional[set[str]] = None,
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.burst_limit = burst_limit
        self.window_size = window_size
        self.whitelist = whitelist or set()

        # In-memory storage for rate limiting
        # In production, use Redis or similar
        self.requests: Dict[str, list] = defaultdict(list)
        self.cleanup_interval = 300  # 5 minutes
        self.last_cleanup = time.time()

        self.logger = get_logger(__name__)

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # Perform cleanup if needed
        await self._cleanup_old_requests()

        # Get client identifier (IP address)
        client_ip = self._get_client_ip(request)

        # Check rate limits
        await self._check_rate_limit(client_ip, request)

        # Process request
        response = await call_next(request)

        return response

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address."""
        # Check for forwarded headers first
        if forwarded_for := request.headers.get("X-Forwarded-For"):
            return forwarded_for.split(",")[0].strip()

        if real_ip := request.headers.get("X-Real-IP"):
            return real_ip.strip()

        # Fallback to client host
        return request.client.host if request.client else "unknown"

    async def _check_rate_limit(self, client_ip: str, request: Request) -> None:
        """Check if request exceeds rate limits."""
        current_time = time.time()

        if client_ip in self.whitelist:
            return

        # Get requests for this client
        client_requests = self.requests[client_ip]

        # Remove old requests outside the window
        cutoff_time = current_time - self.window_size
        client_requests[:] = [
            req_time for req_time in client_requests if req_time > cutoff_time
        ]

        # Check burst limit (requests in last 60 seconds)
        if len(client_requests) >= self.requests_per_minute:
            retry_after = int(self.window_size - (current_time - client_requests[0]))

            log_security_event(
                event_type="rate_limit_exceeded",
                details={
                    "client_ip": client_ip,
                    "endpoint": request.url.path,
                    "method": request.method,
                    "requests_count": len(client_requests),
                    "limit": self.requests_per_minute,
                    "retry_after": retry_after,
                },
            )

            raise RateLimitError(
                message=f"Rate limit exceeded. Too many requests from {client_ip}",
                retry_after=retry_after,
                details={
                    "limit": self.requests_per_minute,
                    "window_seconds": self.window_size,
                    "requests_count": len(client_requests),
                },
            )

        # Check burst limit (requests in last 10 seconds)
        recent_cutoff = current_time - 10
        recent_requests = [
            req_time for req_time in client_requests if req_time > recent_cutoff
        ]

        if len(recent_requests) >= self.burst_limit:
            log_security_event(
                event_type="burst_limit_exceeded",
                details={
                    "client_ip": client_ip,
                    "endpoint": request.url.path,
                    "method": request.method,
                    "recent_requests": len(recent_requests),
                    "burst_limit": self.burst_limit,
                },
            )

            raise RateLimitError(
                message=f"Burst limit exceeded. Too many requests in short period from {client_ip}",
                retry_after=10,
                details={
                    "burst_limit": self.burst_limit,
                    "window_seconds": 10,
                    "recent_requests": len(recent_requests),
                },
            )

        # Add current request
        client_requests.append(current_time)

    async def _cleanup_old_requests(self) -> None:
        """Clean up old request records."""
        current_time = time.time()

        if current_time - self.last_cleanup < self.cleanup_interval:
            return

        cutoff_time = current_time - self.window_size

        # Clean up old requests
        for client_ip in list(self.requests.keys()):
            client_requests = self.requests[client_ip]
            client_requests[:] = [
                req_time for req_time in client_requests if req_time > cutoff_time
            ]

            # Remove empty client records
            if not client_requests:
                del self.requests[client_ip]

        self.last_cleanup = current_time
        self.logger.debug(
            f"Cleaned up rate limit records. Active clients: {len(self.requests)}"
        )


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers."""

    def __init__(self, app: ASGIApp, enable_hsts: bool = False):
        super().__init__(app)
        self.enable_hsts = enable_hsts

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response = await call_next(request)

        # Add security headers
        self._add_security_headers(response)

        return response

    def _add_security_headers(self, response: Response) -> None:
        """Add security headers to response."""

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Content Security Policy (более гибкая для Swagger UI)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://unpkg.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com https://fonts.googleapis.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://cdn.jsdelivr.net https://unpkg.com; "
            "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net https://unpkg.com; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )

        # Permissions Policy (formerly Feature Policy)
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), "
            "payment=(), usb=(), accelerometer=(), "
            "gyroscope=(), magnetometer=()"
        )

        # HSTS (only for HTTPS)
        if self.enable_hsts:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )


class RequestTimeoutMiddleware(BaseHTTPMiddleware):
    """Middleware to handle request timeouts."""

    def __init__(self, app: ASGIApp, timeout_seconds: int = 30):
        super().__init__(app)
        self.timeout_seconds = timeout_seconds
        self.logger = get_logger(__name__)

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        try:
            # Use asyncio.wait_for to implement timeout
            response = await asyncio.wait_for(
                call_next(request), timeout=self.timeout_seconds
            )
            return response

        except asyncio.TimeoutError:
            self.logger.warning(
                f"Request timeout after {self.timeout_seconds}s",
                extra={
                    "event": "request_timeout",
                    "method": request.method,
                    "url": str(request.url),
                    "timeout_seconds": self.timeout_seconds,
                },
            )

            log_security_event(
                event_type="request_timeout",
                details={
                    "endpoint": request.url.path,
                    "method": request.method,
                    "timeout_seconds": self.timeout_seconds,
                    "client_ip": request.client.host if request.client else "unknown",
                },
            )

            return Response(
                content=json.dumps(
                    {
                        "error": True,
                        "message": "Request timeout",
                        "error_code": "REQUEST_TIMEOUT",
                        "details": {"timeout_seconds": self.timeout_seconds},
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                    }
                ),
                status_code=408,
                media_type="application/json",
            )


class ContentTypeValidationMiddleware(BaseHTTPMiddleware):
    """Middleware to validate Content-Type headers."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = get_logger(__name__)

        # Allowed content types for different methods
        self.allowed_content_types = {
            "POST": {
                "application/json",
                "application/x-www-form-urlencoded",
                "multipart/form-data",
            },
            "PUT": {
                "application/json",
                "application/x-www-form-urlencoded",
                "multipart/form-data",
            },
            "PATCH": {
                "application/json",
                "application/x-www-form-urlencoded",
                "multipart/form-data",
            },
        }

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # Skip validation for certain paths
        if self._should_skip_validation(request):
            return await call_next(request)

        # Validate content type for requests with body
        if request.method in self.allowed_content_types:
            await self._validate_content_type(request)

        return await call_next(request)

    def _should_skip_validation(self, request: Request) -> bool:
        """Check if content type validation should be skipped."""
        skip_paths = {"/health", "/", "/docs", "/redoc", "/openapi.json"}
        return request.url.path in skip_paths

    async def _validate_content_type(self, request: Request) -> None:
        """Validate the Content-Type header."""
        content_type = request.headers.get("content-type", "").lower()

        # Extract base content type (remove charset, boundary, etc.)
        base_content_type = content_type.split(";")[0].strip()

        # Check if request has a body
        has_body = False
        try:
            body = await request.body()
            has_body = bool(body)
        except Exception:
            has_body = False

        # If request has body, validate content type
        if has_body and base_content_type not in self.allowed_content_types.get(
            request.method, set()
        ):
            self.logger.warning(
                f"Invalid content type: {content_type}",
                extra={
                    "event": "invalid_content_type",
                    "method": request.method,
                    "url": str(request.url),
                    "content_type": content_type,
                    "allowed_types": list(
                        self.allowed_content_types.get(request.method, set())
                    ),
                },
            )

            log_security_event(
                event_type="invalid_content_type",
                details={
                    "endpoint": request.url.path,
                    "method": request.method,
                    "content_type": content_type,
                    "allowed_types": list(
                        self.allowed_content_types.get(request.method, set())
                    ),
                    "client_ip": request.client.host if request.client else "unknown",
                },
            )

            raise ValidationError(
                message=f"Invalid Content-Type: {content_type}",
                details={
                    "content_type": content_type,
                    "allowed_types": list(
                        self.allowed_content_types.get(request.method, set())
                    ),
                },
            )


class PayloadSizeValidationMiddleware(BaseHTTPMiddleware):
    """Middleware to validate payload size."""

    def __init__(self, app: ASGIApp, max_size_mb: int = 10):
        super().__init__(app)
        self.max_size_bytes = max_size_mb * 1024 * 1024  # Convert to bytes
        self.logger = get_logger(__name__)

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # Check Content-Length header if present
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                if size > self.max_size_bytes:
                    self._log_oversized_request(request, size)
                    raise ValidationError(
                        message=f"Request payload too large: {size} bytes",
                        details={
                            "size_bytes": size,
                            "max_size_bytes": self.max_size_bytes,
                            "max_size_mb": self.max_size_bytes // (1024 * 1024),
                        },
                    )
            except ValueError:
                # Invalid Content-Length header
                self.logger.warning(f"Invalid Content-Length header: {content_length}")

        # For chunked requests, we need to read the body to check size
        if request.method in {"POST", "PUT", "PATCH"}:
            body = await request.body()
            if len(body) > self.max_size_bytes:
                self._log_oversized_request(request, len(body))
                raise ValidationError(
                    message=f"Request payload too large: {len(body)} bytes",
                    details={
                        "size_bytes": len(body),
                        "max_size_bytes": self.max_size_bytes,
                        "max_size_mb": self.max_size_bytes // (1024 * 1024),
                    },
                )

        return await call_next(request)

    def _log_oversized_request(self, request: Request, size: int) -> None:
        """Log oversized request attempt."""
        self.logger.warning(
            f"Oversized request blocked: {size} bytes",
            extra={
                "event": "oversized_request",
                "method": request.method,
                "url": str(request.url),
                "size_bytes": size,
                "max_size_bytes": self.max_size_bytes,
            },
        )

        log_security_event(
            event_type="oversized_request",
            details={
                "endpoint": request.url.path,
                "method": request.method,
                "size_bytes": size,
                "max_size_bytes": self.max_size_bytes,
                "client_ip": request.client.host if request.client else "unknown",
            },
        )
