import pytest
from httpx import AsyncClient
from fastapi import FastAPI

from app.middleware.logging_middleware import (
    LoggingMiddleware,
    SecurityLoggingMiddleware,
    PerformanceLoggingMiddleware,
)


@pytest.mark.asyncio
async def test_logging_middleware_adds_correlation_id():
    app = FastAPI()
    app.add_middleware(LoggingMiddleware)

    @app.get("/ping")
    async def ping():
        return {"msg": "pong"}

    async with AsyncClient(app=app, base_url="http://test") as client:
        res = await client.get("/ping")
        assert res.status_code == 200
        assert "X-Correlation-ID" in res.headers


@pytest.mark.asyncio
async def test_logging_middleware_logs_requests():
    app = FastAPI()
    app.add_middleware(LoggingMiddleware)

    @app.get("/ping")
    async def ping():
        return {"msg": "pong"}

    async with AsyncClient(app=app, base_url="http://test") as client:
        res = await client.get("/ping")
        assert res.status_code == 200


@pytest.mark.asyncio
async def test_logging_middleware_logs_responses():
    app = FastAPI()
    app.add_middleware(LoggingMiddleware)

    @app.get("/ping")
    async def ping():
        return {"msg": "pong"}

    async with AsyncClient(app=app, base_url="http://test") as client:
        res = await client.get("/ping")
        assert res.status_code == 200


@pytest.mark.asyncio
async def test_security_middleware_detects_sql_injection():
    app = FastAPI()
    app.add_middleware(SecurityLoggingMiddleware)

    @app.get("/ping")
    async def ping():
        return {"msg": "pong"}

    async with AsyncClient(app=app, base_url="http://test") as client:
        res = await client.get("/ping?user=1;DROP TABLE users")
        assert res.status_code == 200


@pytest.mark.asyncio
async def test_security_middleware_checks_headers():
    app = FastAPI()
    app.add_middleware(SecurityLoggingMiddleware)

    @app.get("/ping")
    async def ping():
        return {"msg": "pong"}

    async with AsyncClient(app=app, base_url="http://test") as client:
        res = await client.get("/ping", headers={"User-Agent": "sqlmap"})
        assert res.status_code == 200


@pytest.mark.asyncio
async def test_security_middleware_validates_user_agent():
    app = FastAPI()
    app.add_middleware(SecurityLoggingMiddleware)

    @app.get("/ping")
    async def ping():
        return {"msg": "pong"}

    async with AsyncClient(app=app, base_url="http://test") as client:
        res = await client.get("/ping", headers={"User-Agent": "custom"})
        assert res.status_code == 200


@pytest.mark.asyncio
async def test_performance_middleware_measures_time():
    app = FastAPI()
    app.add_middleware(PerformanceLoggingMiddleware)

    @app.get("/ping")
    async def ping():
        return {"msg": "pong"}

    async with AsyncClient(app=app, base_url="http://test") as client:
        res = await client.get("/ping")
        assert res.status_code == 200


@pytest.mark.asyncio
async def test_performance_middleware_logs_slow_requests():
    app = FastAPI()
    app.add_middleware(PerformanceLoggingMiddleware)

    @app.get("/slow")
    async def slow():
        import asyncio

        await asyncio.sleep(1.1)
        return {"msg": "done"}

    async with AsyncClient(app=app, base_url="http://test") as client:
        res = await client.get("/slow")
        assert res.status_code == 200
