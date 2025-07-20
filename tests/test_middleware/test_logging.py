import json
import pytest
from fastapi import Body, Response, Request
from fastapi.responses import StreamingResponse


class TestLoggingMiddleware:
    """Tests for LoggingMiddleware behavior."""

    @pytest.mark.asyncio
    async def test_correlation_id_generation(self, client, monkeypatch):
        monkeypatch.setattr(
            "app.middleware.logging_middleware.generate_correlation_id",
            lambda: "test-corr-id",
        )
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.headers["X-Correlation-ID"] == "test-corr-id"

    @pytest.mark.asyncio
    async def test_request_and_response_logging(self, client, test_user1, monkeypatch):
        captured = {}

        from app.middleware import logging_middleware as lm
        orig_log_request = lm.log_request
        orig_log_response = lm.log_response

        def fake_log_request(method, url, headers, body=None):
            captured["request"] = {
                "method": method,
                "url": url,
                "headers": headers,
                "body": body,
            }
            orig_log_request(method, url, headers, body)

        def fake_log_response(status_code, response_time, response_size=0):
            captured["response"] = {
                "status_code": status_code,
                "response_time": response_time,
                "response_size": response_size,
            }
            orig_log_response(status_code, response_time, response_size)

        monkeypatch.setattr(
            "app.middleware.logging_middleware.log_request", fake_log_request
        )
        monkeypatch.setattr(
            "app.middleware.logging_middleware.log_response", fake_log_response
        )

        login_data = {"email": test_user1.email, "password": "testpass123"}
        resp = await client.post("/api/v1/auth/login?foo=bar", json=login_data)
        assert resp.status_code in {200, 401}
        assert captured["request"]["method"] == "POST"
        assert "/api/v1/auth/login" in captured["request"]["url"]
        assert "host" in {k.lower() for k in captured["request"]["headers"].keys()}
        assert captured["request"]["body"].get("email") == test_user1.email
        assert captured["response"]["status_code"] == resp.status_code
        assert captured["response"]["response_size"] >= 0
        assert captured["response"]["response_time"] >= 0

    @pytest.mark.asyncio
    async def test_error_logging(self, app_with_overrides, monkeypatch):
        async def err_route():
            raise RuntimeError("boom")

        app_with_overrides.add_api_route("/err", err_route, methods=["GET"])

        captured = {}

        def fake_log_error(error, context):
            captured["error"] = {
                "type": type(error).__name__,
                "context": context,
            }

        monkeypatch.setattr(
            "app.middleware.logging_middleware.log_error", fake_log_error
        )

        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app_with_overrides, raise_app_exceptions=False)
        async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
            resp = await ac.get("/err")
        assert resp.status_code == 500
        assert captured["error"]["type"] == "RuntimeError"
        assert captured["error"]["context"]["request_method"] == "GET"

    @pytest.mark.asyncio
    async def test_edge_cases(self, app_with_overrides, monkeypatch):
        async def echo_bytes(request: Request):
            data = await request.body()
            return Response(content=data, media_type="application/octet-stream")

        async def stream():
            async def generator():
                for i in range(3):
                    yield f"{i}\n"
            return StreamingResponse(generator(), media_type="text/plain")

        app_with_overrides.add_api_route("/binary", echo_bytes, methods=["POST"])
        app_with_overrides.add_api_route("/stream", stream, methods=["GET"])

        records = []

        def fake_log_request(method, url, headers, body=None):
            records.append(body)

        def fake_log_response(status_code, response_time, response_size=0):
            records.append(response_size)

        monkeypatch.setattr(
            "app.middleware.logging_middleware.log_request", fake_log_request
        )
        monkeypatch.setattr(
            "app.middleware.logging_middleware.log_response", fake_log_response
        )

        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app_with_overrides, raise_app_exceptions=False)
        async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
            big_data = "x" * 5000
            resp1 = await ac.post(
                "/binary",
                content=big_data.encode(),
                headers={"Content-Type": "application/json"},
            )
            assert resp1.status_code == 200
            resp2 = await ac.get("/stream")
            assert resp2.status_code == 200

        assert records[0] == {"raw_body_size": len(big_data.encode())}
        # response size for streaming should be 0
        assert records[-1] == 0
