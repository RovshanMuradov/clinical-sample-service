import asyncio
import pytest
import pytest_asyncio
from starlette.requests import Request
from starlette.responses import Response

from app.middleware.security_middleware import (
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
    PayloadSizeValidationMiddleware,
    ContentTypeValidationMiddleware,
)
from app.middleware.logging_middleware import SecurityLoggingMiddleware
from app.core.exceptions import RateLimitError, ValidationError


def make_request(method: str = "GET", path: str = "/", headers=None, body: bytes = b""):
    if headers is None:
        headers = {}

    async def receive():
        return {"type": "http.request", "body": body, "more_body": False}

    scope = {
        "type": "http",
        "method": method,
        "path": path,
        "headers": [(k.encode(), v.encode()) for k, v in headers.items()],
        "query_string": b"",
        "client": ("test", 0),
    }
    return Request(scope, receive)


@pytest.mark.asyncio
async def test_rate_limit_counting():
    async def endpoint(request):
        return Response("ok")

    middleware = RateLimitMiddleware(
        endpoint, requests_per_minute=2, burst_limit=2, window_size=1
    )
    middleware._get_client_ip = lambda req: "1.1.1.1"

    await middleware.dispatch(make_request(), endpoint)
    await middleware.dispatch(make_request(), endpoint)

    assert len(middleware.requests["1.1.1.1"]) == 2


@pytest.mark.asyncio
async def test_rate_limit_exceeded():
    async def endpoint(request):
        return Response("ok")

    middleware = RateLimitMiddleware(
        endpoint, requests_per_minute=2, burst_limit=2, window_size=1
    )
    middleware._get_client_ip = lambda req: "2.2.2.2"

    await middleware.dispatch(make_request(), endpoint)
    await middleware.dispatch(make_request(), endpoint)
    with pytest.raises(RateLimitError):
        await middleware.dispatch(make_request(), endpoint)


@pytest.mark.asyncio
async def test_rate_limit_whitelist():
    async def endpoint(request):
        return Response("ok")

    middleware = RateLimitMiddleware(
        endpoint,
        requests_per_minute=1,
        burst_limit=1,
        window_size=1,
        whitelist={"3.3.3.3"},
    )
    middleware._get_client_ip = lambda req: "3.3.3.3"

    await middleware.dispatch(make_request(), endpoint)
    await middleware.dispatch(make_request(), endpoint)


@pytest.mark.asyncio
async def test_rate_limit_resets_after_window():
    async def endpoint(request):
        return Response("ok")

    middleware = RateLimitMiddleware(
        endpoint, requests_per_minute=1, burst_limit=1, window_size=1
    )
    middleware._get_client_ip = lambda req: "4.4.4.4"

    await middleware.dispatch(make_request(), endpoint)
    await asyncio.sleep(1.1)
    await middleware.dispatch(make_request(), endpoint)


@pytest.mark.asyncio
async def test_security_headers_added():
    called = False

    async def endpoint(request):
        nonlocal called
        called = True
        return Response("ok")

    middleware = SecurityHeadersMiddleware(endpoint)
    response = await middleware.dispatch(make_request(), endpoint)

    assert called
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-XSS-Protection"] == "1; mode=block"
    assert "default-src" in response.headers["Content-Security-Policy"]


@pytest.mark.asyncio
async def test_attack_detection(monkeypatch):
    events = []

    def recorder(event_type, details):
        events.append(event_type)

    monkeypatch.setattr(
        "app.middleware.logging_middleware.log_security_event",
        recorder,
    )
    middleware = SecurityLoggingMiddleware(lambda r: Response("ok"))

    async def endpoint(request):
        return Response("ok")

    req = make_request(path="/health?q=select")
    await middleware.dispatch(req, endpoint)
    assert "suspicious_request" in events


@pytest.mark.asyncio
async def test_payload_size_validation():
    async def endpoint(request):
        return Response("ok")

    middleware = PayloadSizeValidationMiddleware(endpoint, max_size_mb=0)
    req = make_request(
        method="POST",
        path="/",
        headers={"content-type": "application/json"},
        body=b"x" * 1024,
    )
    with pytest.raises(ValidationError):
        await middleware.dispatch(req, endpoint)


@pytest.mark.asyncio
async def test_content_type_validation():
    async def endpoint2(request):
        return Response("ok")

    middleware = ContentTypeValidationMiddleware(endpoint2)
    req = make_request(
        method="POST",
        path="/submit",
        headers={"content-type": "text/plain"},
        body=b"hello",
    )
    with pytest.raises(ValidationError):
        await middleware.dispatch(req, endpoint2)
