from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.main import app
from app.core.exceptions import NotFoundError


def test_fastapi_app_creation():
    assert isinstance(app, FastAPI)
    assert app.title


def test_cors_middleware_configured():
    assert any(mw.cls == CORSMiddleware for mw in app.user_middleware)


def test_exception_handlers_registered():
    assert NotFoundError in app.exception_handlers


def test_api_router_included():
    paths = [route.path for route in app.router.routes]
    assert "/api/v1/auth/login" in paths


def test_startup_event_handlers():
    assert app.router.lifespan_context is not None
