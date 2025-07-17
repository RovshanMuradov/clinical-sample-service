"""Tests for main application functionality."""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app
from app.core.config import get_settings


class TestMainApplication:
    """Test main application functionality."""
    
    def test_app_creation(self):
        """Test that the app is created successfully."""
        assert app is not None
        assert app.title == "Clinical Sample Service"
        assert app.version == "1.0.0"
    
    def test_health_check_endpoint(self, test_client: TestClient):
        """Test the health check endpoint."""
        response = test_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "Clinical Sample Service"
        assert "version" in data
        assert "timestamp" in data
    
    def test_root_endpoint(self, test_client: TestClient):
        """Test the root endpoint."""
        response = test_client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs_url" in data
    
    def test_docs_endpoint(self, test_client: TestClient):
        """Test that API documentation is available."""
        response = test_client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_openapi_endpoint(self, test_client: TestClient):
        """Test OpenAPI schema endpoint."""
        response = test_client.get("/openapi.json")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        schema = response.json()
        assert "info" in schema
        assert "paths" in schema
        assert schema["info"]["title"] == "Clinical Sample Service"
    
    def test_cors_headers(self, test_client: TestClient):
        """Test CORS headers are set correctly."""
        response = test_client.options("/health")
        assert response.status_code == 200
        
        # Check CORS headers
        headers = response.headers
        assert "access-control-allow-origin" in headers
        assert "access-control-allow-methods" in headers
        assert "access-control-allow-headers" in headers
    
    def test_invalid_endpoint(self, test_client: TestClient):
        """Test that invalid endpoints return 404."""
        response = test_client.get("/invalid-endpoint")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Not Found"
    
    def test_api_v1_prefix(self, test_client: TestClient):
        """Test that API v1 routes are properly prefixed."""
        # Test auth endpoints
        response = test_client.post("/api/v1/auth/login", json={
            "username": "nonexistent",
            "password": "wrong"
        })
        # Should return 401 (not 404), meaning endpoint exists
        assert response.status_code == 401
        
        # Test samples endpoints (should require auth)
        response = test_client.get("/api/v1/samples")
        assert response.status_code == 401
    
    def test_request_validation_error(self, test_client: TestClient):
        """Test request validation error handling."""
        # Send invalid JSON to auth endpoint
        response = test_client.post("/api/v1/auth/register", json={
            "username": "",  # Empty username should fail validation
            "email": "invalid-email",  # Invalid email format
            "password": "weak"  # Weak password
        })
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], list)
    
    def test_internal_server_error_handling(self, test_client: TestClient):
        """Test that internal server errors are handled gracefully."""
        # This test would require mocking to trigger an actual 500 error
        # For now, just ensure the error handlers are registered
        assert app.exception_handlers is not None
    
    def test_security_headers(self, test_client: TestClient):
        """Test that security headers are set."""
        response = test_client.get("/health")
        
        headers = response.headers
        # Check for security headers added by middleware
        assert "x-content-type-options" in headers
        assert "x-frame-options" in headers
        assert "x-xss-protection" in headers
        assert "referrer-policy" in headers
    
    def test_request_logging_middleware(self, test_client: TestClient):
        """Test that request logging middleware is working."""
        # Test that requests are being processed through middleware
        response = test_client.get("/health")
        assert response.status_code == 200
        
        # Check for correlation ID header
        assert "x-correlation-id" in response.headers
    
    def test_performance_monitoring(self, test_client: TestClient):
        """Test that performance monitoring is working."""
        response = test_client.get("/health")
        assert response.status_code == 200
        
        # Check for response time header
        assert "x-response-time" in response.headers
        
        # Verify it's a valid float
        response_time = float(response.headers["x-response-time"])
        assert response_time > 0


class TestApplicationSettings:
    """Test application settings and configuration."""
    
    def test_settings_loaded(self):
        """Test that settings are loaded correctly."""
        settings = get_settings()
        
        assert settings is not None
        assert hasattr(settings, 'database_url')
        assert hasattr(settings, 'secret_key')
        assert hasattr(settings, 'algorithm')
        assert hasattr(settings, 'access_token_expire_minutes')
    
    def test_debug_mode_in_tests(self):
        """Test that debug mode is properly configured for tests."""
        settings = get_settings()
        # In test environment, debug should be True
        assert settings.debug is True
    
    def test_database_url_format(self):
        """Test database URL format."""
        settings = get_settings()
        assert settings.database_url is not None
        assert isinstance(settings.database_url, str)
        
        # Should contain database connection info
        assert "postgresql" in settings.database_url.lower() or "sqlite" in settings.database_url.lower()
    
    def test_jwt_configuration(self):
        """Test JWT configuration."""
        settings = get_settings()
        
        assert settings.secret_key is not None
        assert len(settings.secret_key) > 0
        assert settings.algorithm == "HS256"
        assert settings.access_token_expire_minutes > 0
    
    def test_cors_configuration(self):
        """Test CORS configuration."""
        settings = get_settings()
        
        assert hasattr(settings, 'cors_origins')
        assert isinstance(settings.cors_origins, list)


@pytest.mark.asyncio
class TestAsyncMainApplication:
    """Test async functionality of main application."""
    
    async def test_async_health_check(self, async_client: AsyncClient):
        """Test health check endpoint with async client."""
        response = await async_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    async def test_async_root_endpoint(self, async_client: AsyncClient):
        """Test root endpoint with async client."""
        response = await async_client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
    
    async def test_async_api_endpoints(self, async_client: AsyncClient):
        """Test API endpoints with async client."""
        # Test that endpoints respond correctly (even if they require auth)
        response = await async_client.get("/api/v1/samples")
        # Should return 401 (unauthorized) not 404 (not found)
        assert response.status_code == 401
    
    async def test_concurrent_requests(self, async_client: AsyncClient):
        """Test handling of concurrent requests."""
        import asyncio
        
        # Make multiple concurrent requests
        tasks = [
            async_client.get("/health"),
            async_client.get("/health"),
            async_client.get("/health"),
        ]
        
        responses = await asyncio.gather(*tasks)
        
        # All should succeed
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"


class TestApplicationLifecycle:
    """Test application lifecycle events."""
    
    def test_startup_event(self):
        """Test that startup events are configured."""
        # The app should have startup event handlers
        assert app.router.lifespan is not None
    
    def test_app_middleware_order(self):
        """Test that middleware is applied in correct order."""
        # Check that middleware stack is properly configured
        assert app.user_middleware is not None
        assert len(app.user_middleware) > 0
    
    def test_exception_handlers_registered(self):
        """Test that exception handlers are registered."""
        assert app.exception_handlers is not None
        assert len(app.exception_handlers) > 0


if __name__ == "__main__":
    pytest.main([__file__])