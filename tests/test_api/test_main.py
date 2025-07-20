import pytest


class TestMainEndpoints:
    """Tests for root and health endpoints."""

    @pytest.mark.asyncio
    async def test_root_endpoint(self, client):
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Clinical Sample Service API"
        assert "version" in data

    @pytest.mark.asyncio
    async def test_health_endpoint(self, client):
        response = await client.get("/health")
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "healthy"
        assert "service" in payload

    @pytest.mark.asyncio
    async def test_openapi_has_security_scheme(self, client):
        response = await client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "bearerAuth" in schema["components"]["securitySchemes"]

class TestMainAppConfiguration:
    """Tests for FastAPI application configuration."""

    def test_app_metadata(self, app_with_overrides):
        assert app_with_overrides.title == "Clinical Sample Service"
        assert app_with_overrides.version == "1.0.0"
        assert app_with_overrides.docs_url == "/docs"
        assert app_with_overrides.openapi_url == "/openapi.json"

    def test_cors_middleware_configuration(self, app_with_overrides):
        from fastapi.middleware.cors import CORSMiddleware

        cors = next((m for m in app_with_overrides.user_middleware if m.cls is CORSMiddleware), None)
        assert cors is not None
        opts = cors.kwargs
        assert opts["allow_credentials"] is True
        assert "X-Correlation-ID" in opts["expose_headers"]

    def test_custom_middlewares_registered(self, app_with_overrides):
        from app.middleware import LoggingMiddleware, SecurityLoggingMiddleware, PerformanceLoggingMiddleware

        classes = [m.cls for m in app_with_overrides.user_middleware]
        assert LoggingMiddleware in classes
        assert SecurityLoggingMiddleware in classes
        assert PerformanceLoggingMiddleware in classes

    def test_router_included(self, app_with_overrides):
        paths = [route.path for route in app_with_overrides.router.routes]
        assert "/api/v1/auth/login" in paths
        assert "/api/v1/samples/" in paths or any(p.startswith("/api/v1/samples") for p in paths)

    def test_exception_handlers_registered(self, app_with_overrides):
        from app.core.exceptions import NotFoundError, ValidationError, AuthenticationError

        handlers = app_with_overrides.exception_handlers
        assert NotFoundError in handlers
        assert ValidationError in handlers
        assert AuthenticationError in handlers
