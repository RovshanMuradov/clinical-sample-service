import pytest

from app.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    NotFoundError,
    ValidationError,
)


def test_validation_error_to_dict():
    exc = ValidationError(field="email", message="bad")
    data = exc.to_dict()
    assert data["error_code"] == "VALIDATION_ERROR"
    assert data["details"]["field"] == "email"
    assert data["message"] == "bad"


def test_authentication_error_details():
    exc = AuthenticationError(details={"hint": "login"})
    data = exc.to_dict()
    assert exc.status_code == 401
    assert data["details"]["hint"] == "login"


def test_authorization_error_resource():
    exc = AuthorizationError(resource="sample")
    assert "sample" in exc.message
    assert exc.status_code == 403


def test_not_found_error_message():
    exc = NotFoundError(resource="Sample", resource_id="123")
    assert "Sample" in exc.message and "123" in exc.message
    assert exc.status_code == 404


def test_conflict_error():
    exc = ConflictError(resource="User")
    assert "User" in exc.message
    assert exc.status_code == 409
