"""Tests for core exceptions."""

import pytest

from app.core.exceptions import (
    BaseAPIException,
    NotFoundError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    DatabaseError,
    ConflictError,
    RateLimitError,
    ExternalServiceError
)


class TestBaseAPIException:
    """Test BaseAPIException class."""

    def test_base_exception_default_values(self):
        """Test BaseAPIException with default values."""
        exception = BaseAPIException("Test message")
        
        assert exception.message == "Test message"
        assert exception.status_code == 500
        assert exception.error_code == "INTERNAL_ERROR"
        assert exception.details == {}
        assert str(exception) == "Test message"

    def test_base_exception_custom_values(self):
        """Test BaseAPIException with custom values."""
        details = {"field": "value", "extra": "info"}
        exception = BaseAPIException(
            message="Custom message",
            status_code=400,
            error_code="CUSTOM_ERROR",
            details=details
        )
        
        assert exception.message == "Custom message"
        assert exception.status_code == 400
        assert exception.error_code == "CUSTOM_ERROR"
        assert exception.details == details
        assert str(exception) == "Custom message"

    def test_base_exception_none_details(self):
        """Test BaseAPIException with None details."""
        exception = BaseAPIException(
            message="Test message",
            details=None
        )
        
        assert exception.details == {}

    def test_base_exception_inherits_from_exception(self):
        """Test that BaseAPIException inherits from Exception."""
        exception = BaseAPIException("Test message")
        assert isinstance(exception, Exception)

    def test_base_exception_can_be_raised(self):
        """Test that BaseAPIException can be raised and caught."""
        with pytest.raises(BaseAPIException) as exc_info:
            raise BaseAPIException("Test message")
        
        assert exc_info.value.message == "Test message"


class TestNotFoundError:
    """Test NotFoundError class."""

    def test_not_found_error_default_values(self):
        """Test NotFoundError with default values."""
        exception = NotFoundError()
        
        assert exception.message == "Resource not found"
        assert exception.status_code == 404
        assert exception.error_code == "NOT_FOUND"
        assert exception.details == {}

    def test_not_found_error_with_resource(self):
        """Test NotFoundError with resource specified."""
        exception = NotFoundError(resource="Sample")
        
        assert exception.message == "Sample not found"
        assert exception.status_code == 404
        assert exception.error_code == "NOT_FOUND"

    def test_not_found_error_with_resource_and_id(self):
        """Test NotFoundError with resource and ID."""
        exception = NotFoundError(resource="Sample", resource_id="123")
        
        assert exception.message == "Sample with ID '123' not found"
        assert exception.status_code == 404
        assert exception.error_code == "NOT_FOUND"

    def test_not_found_error_with_details(self):
        """Test NotFoundError with details."""
        details = {"table": "samples", "query": "id=123"}
        exception = NotFoundError(resource="Sample", details=details)
        
        assert exception.details == details

    def test_not_found_error_inherits_from_base(self):
        """Test that NotFoundError inherits from BaseAPIException."""
        exception = NotFoundError()
        assert isinstance(exception, BaseAPIException)


class TestValidationError:
    """Test ValidationError class."""

    def test_validation_error_default_values(self):
        """Test ValidationError with default values."""
        exception = ValidationError()
        
        assert exception.message == "Validation failed"
        assert exception.status_code == 400
        assert exception.error_code == "VALIDATION_ERROR"
        assert exception.details == {}

    def test_validation_error_with_custom_message(self):
        """Test ValidationError with custom message."""
        exception = ValidationError(message="Invalid input")
        
        assert exception.message == "Invalid input"
        assert exception.status_code == 400
        assert exception.error_code == "VALIDATION_ERROR"

    def test_validation_error_with_field(self):
        """Test ValidationError with field specified."""
        exception = ValidationError(message="Invalid email", field="email")
        
        assert exception.message == "Invalid email"
        assert exception.details == {"field": "email"}

    def test_validation_error_with_field_and_details(self):
        """Test ValidationError with field and additional details."""
        details = {"constraint": "format", "expected": "email"}
        exception = ValidationError(
            message="Invalid email",
            field="email",
            details=details
        )
        
        expected_details = {"field": "email", "constraint": "format", "expected": "email"}
        assert exception.details == expected_details

    def test_validation_error_inherits_from_base(self):
        """Test that ValidationError inherits from BaseAPIException."""
        exception = ValidationError()
        assert isinstance(exception, BaseAPIException)


class TestAuthenticationError:
    """Test AuthenticationError class."""

    def test_authentication_error_default_values(self):
        """Test AuthenticationError with default values."""
        exception = AuthenticationError()
        
        assert exception.message == "Authentication failed"
        assert exception.status_code == 401
        assert exception.error_code == "AUTHENTICATION_ERROR"
        assert exception.details == {}

    def test_authentication_error_with_custom_message(self):
        """Test AuthenticationError with custom message."""
        exception = AuthenticationError(message="Invalid credentials")
        
        assert exception.message == "Invalid credentials"
        assert exception.status_code == 401
        assert exception.error_code == "AUTHENTICATION_ERROR"

    def test_authentication_error_with_details(self):
        """Test AuthenticationError with details."""
        details = {"reason": "token_expired", "expires_at": "2023-12-01"}
        exception = AuthenticationError(details=details)
        
        assert exception.details == details

    def test_authentication_error_inherits_from_base(self):
        """Test that AuthenticationError inherits from BaseAPIException."""
        exception = AuthenticationError()
        assert isinstance(exception, BaseAPIException)


class TestAuthorizationError:
    """Test AuthorizationError class."""

    def test_authorization_error_default_values(self):
        """Test AuthorizationError with default values."""
        exception = AuthorizationError()
        
        assert exception.message == "Access denied"
        assert exception.status_code == 403
        assert exception.error_code == "AUTHORIZATION_ERROR"
        assert exception.details == {}

    def test_authorization_error_with_resource(self):
        """Test AuthorizationError with resource specified."""
        exception = AuthorizationError(resource="admin panel")
        
        assert exception.message == "Access denied to admin panel"
        assert exception.status_code == 403
        assert exception.error_code == "AUTHORIZATION_ERROR"

    def test_authorization_error_with_custom_message(self):
        """Test AuthorizationError with custom message."""
        exception = AuthorizationError(message="Insufficient permissions")
        
        assert exception.message == "Insufficient permissions"

    def test_authorization_error_with_details(self):
        """Test AuthorizationError with details."""
        details = {"required_role": "admin", "user_role": "user"}
        exception = AuthorizationError(details=details)
        
        assert exception.details == details

    def test_authorization_error_inherits_from_base(self):
        """Test that AuthorizationError inherits from BaseAPIException."""
        exception = AuthorizationError()
        assert isinstance(exception, BaseAPIException)


class TestDatabaseError:
    """Test DatabaseError class."""

    def test_database_error_default_values(self):
        """Test DatabaseError with default values."""
        exception = DatabaseError()
        
        assert exception.message == "Database operation failed"
        assert exception.status_code == 500
        assert exception.error_code == "DATABASE_ERROR"
        assert exception.details == {}

    def test_database_error_with_operation(self):
        """Test DatabaseError with operation specified."""
        exception = DatabaseError(operation="insert")
        
        assert exception.message == "Database insert operation failed"
        assert exception.details == {"operation": "insert"}

    def test_database_error_with_custom_message(self):
        """Test DatabaseError with custom message."""
        exception = DatabaseError(message="Connection timeout")
        
        assert exception.message == "Connection timeout"

    def test_database_error_with_operation_and_details(self):
        """Test DatabaseError with operation and additional details."""
        details = {"table": "samples", "constraint": "unique"}
        exception = DatabaseError(operation="insert", details=details)
        
        expected_details = {"operation": "insert", "table": "samples", "constraint": "unique"}
        assert exception.details == expected_details

    def test_database_error_inherits_from_base(self):
        """Test that DatabaseError inherits from BaseAPIException."""
        exception = DatabaseError()
        assert isinstance(exception, BaseAPIException)


class TestConflictError:
    """Test ConflictError class."""

    def test_conflict_error_default_values(self):
        """Test ConflictError with default values."""
        exception = ConflictError()
        
        assert exception.message == "Resource conflict"
        assert exception.status_code == 409
        assert exception.error_code == "CONFLICT_ERROR"
        assert exception.details == {}

    def test_conflict_error_with_resource(self):
        """Test ConflictError with resource specified."""
        exception = ConflictError(resource="Sample")
        
        assert exception.message == "Sample already exists or conflicts with existing data"
        assert exception.status_code == 409
        assert exception.error_code == "CONFLICT_ERROR"

    def test_conflict_error_with_custom_message(self):
        """Test ConflictError with custom message."""
        exception = ConflictError(message="Duplicate entry")
        
        assert exception.message == "Duplicate entry"

    def test_conflict_error_with_details(self):
        """Test ConflictError with details."""
        details = {"field": "email", "value": "test@example.com"}
        exception = ConflictError(details=details)
        
        assert exception.details == details

    def test_conflict_error_inherits_from_base(self):
        """Test that ConflictError inherits from BaseAPIException."""
        exception = ConflictError()
        assert isinstance(exception, BaseAPIException)


class TestRateLimitError:
    """Test RateLimitError class."""

    def test_rate_limit_error_default_values(self):
        """Test RateLimitError with default values."""
        exception = RateLimitError()
        
        assert exception.message == "Rate limit exceeded"
        assert exception.status_code == 429
        assert exception.error_code == "RATE_LIMIT_ERROR"
        assert exception.details == {}

    def test_rate_limit_error_with_retry_after(self):
        """Test RateLimitError with retry_after specified."""
        exception = RateLimitError(retry_after=60)
        
        assert exception.message == "Rate limit exceeded"
        assert exception.details == {"retry_after": 60}

    def test_rate_limit_error_with_custom_message(self):
        """Test RateLimitError with custom message."""
        exception = RateLimitError(message="Too many requests")
        
        assert exception.message == "Too many requests"

    def test_rate_limit_error_with_retry_after_and_details(self):
        """Test RateLimitError with retry_after and additional details."""
        details = {"limit": 100, "window": "1 minute"}
        exception = RateLimitError(retry_after=60, details=details)
        
        expected_details = {"retry_after": 60, "limit": 100, "window": "1 minute"}
        assert exception.details == expected_details

    def test_rate_limit_error_inherits_from_base(self):
        """Test that RateLimitError inherits from BaseAPIException."""
        exception = RateLimitError()
        assert isinstance(exception, BaseAPIException)


class TestExternalServiceError:
    """Test ExternalServiceError class."""

    def test_external_service_error_default_values(self):
        """Test ExternalServiceError with default values."""
        exception = ExternalServiceError(service_name="PaymentService")
        
        assert exception.message == "PaymentService: External service error"
        assert exception.status_code == 502
        assert exception.error_code == "EXTERNAL_SERVICE_ERROR"
        assert exception.details == {"service": "PaymentService"}

    def test_external_service_error_with_custom_message(self):
        """Test ExternalServiceError with custom message."""
        exception = ExternalServiceError(
            service_name="PaymentService",
            message="Service unavailable"
        )
        
        assert exception.message == "PaymentService: Service unavailable"
        assert exception.details == {"service": "PaymentService"}

    def test_external_service_error_with_details(self):
        """Test ExternalServiceError with details."""
        details = {"timeout": 30, "endpoint": "/api/v1/payment"}
        exception = ExternalServiceError(
            service_name="PaymentService",
            details=details
        )
        
        expected_details = {"service": "PaymentService", "timeout": 30, "endpoint": "/api/v1/payment"}
        assert exception.details == expected_details

    def test_external_service_error_inherits_from_base(self):
        """Test that ExternalServiceError inherits from BaseAPIException."""
        exception = ExternalServiceError(service_name="TestService")
        assert isinstance(exception, BaseAPIException)


class TestExceptionHierarchy:
    """Test exception hierarchy and inheritance."""

    def test_all_exceptions_inherit_from_base(self):
        """Test that all custom exceptions inherit from BaseAPIException."""
        exceptions = [
            NotFoundError(),
            ValidationError(),
            AuthenticationError(),
            AuthorizationError(),
            DatabaseError(),
            ConflictError(),
            RateLimitError(),
            ExternalServiceError("TestService")
        ]
        
        for exception in exceptions:
            assert isinstance(exception, BaseAPIException)
            assert isinstance(exception, Exception)

    def test_exception_status_codes(self):
        """Test that exceptions have correct status codes."""
        status_codes = {
            NotFoundError(): 404,
            ValidationError(): 400,
            AuthenticationError(): 401,
            AuthorizationError(): 403,
            DatabaseError(): 500,
            ConflictError(): 409,
            RateLimitError(): 429,
            ExternalServiceError("TestService"): 502
        }
        
        for exception, expected_code in status_codes.items():
            assert exception.status_code == expected_code

    def test_exception_error_codes(self):
        """Test that exceptions have correct error codes."""
        error_codes = {
            NotFoundError(): "NOT_FOUND",
            ValidationError(): "VALIDATION_ERROR",
            AuthenticationError(): "AUTHENTICATION_ERROR",
            AuthorizationError(): "AUTHORIZATION_ERROR",
            DatabaseError(): "DATABASE_ERROR",
            ConflictError(): "CONFLICT_ERROR",
            RateLimitError(): "RATE_LIMIT_ERROR",
            ExternalServiceError("TestService"): "EXTERNAL_SERVICE_ERROR"
        }
        
        for exception, expected_code in error_codes.items():
            assert exception.error_code == expected_code

    def test_exceptions_can_be_caught_as_base(self):
        """Test that specific exceptions can be caught as BaseAPIException."""
        exceptions = [
            NotFoundError(),
            ValidationError(),
            AuthenticationError(),
            AuthorizationError(),
            DatabaseError(),
            ConflictError(),
            RateLimitError(),
            ExternalServiceError("TestService")
        ]
        
        for exception in exceptions:
            with pytest.raises(BaseAPIException):
                raise exception

    def test_exceptions_preserve_original_type(self):
        """Test that exceptions preserve their original type when caught."""
        with pytest.raises(NotFoundError) as exc_info:
            raise NotFoundError("Sample", "123")
        
        assert isinstance(exc_info.value, NotFoundError)
        assert isinstance(exc_info.value, BaseAPIException)
        assert exc_info.value.message == "Sample with ID '123' not found"