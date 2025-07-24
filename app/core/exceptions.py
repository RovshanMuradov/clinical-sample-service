from typing import Any, Dict, Optional


class BaseAPIException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Return a serializable representation of the exception."""
        return {
            "error": True,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details,
        }


class NotFoundError(BaseAPIException):
    def __init__(
        self,
        resource: str = "Resource",
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        if resource_id:
            message = f"{resource} with ID '{resource_id}' not found"
        else:
            message = f"{resource} not found"

        super().__init__(
            message=message, status_code=404, error_code="NOT_FOUND", details=details
        )


class ValidationError(BaseAPIException):
    def __init__(
        self,
        message: str = "Validation failed",
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        error_details = details or {}
        if field:
            error_details["field"] = field

        super().__init__(
            message=message,
            status_code=400,
            error_code="VALIDATION_ERROR",
            details=error_details,
        )


class AuthenticationError(BaseAPIException):
    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR",
            details=details,
        )


class AuthorizationError(BaseAPIException):
    def __init__(
        self,
        message: str = "Access denied",
        resource: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        if resource:
            message = f"Access denied to {resource}"

        super().__init__(
            message=message,
            status_code=403,
            error_code="AUTHORIZATION_ERROR",
            details=details,
        )


class DatabaseError(BaseAPIException):
    def __init__(
        self,
        message: str = "Database operation failed",
        operation: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        error_details = details or {}
        if operation:
            error_details["operation"] = operation
            message = f"Database {operation} operation failed"

        super().__init__(
            message=message,
            status_code=500,
            error_code="DATABASE_ERROR",
            details=error_details,
        )


class ConflictError(BaseAPIException):
    def __init__(
        self,
        message: str = "Resource conflict",
        resource: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        if resource:
            message = f"{resource} already exists or conflicts with existing data"

        super().__init__(
            message=message,
            status_code=409,
            error_code="CONFLICT_ERROR",
            details=details,
        )


class RateLimitError(BaseAPIException):
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        error_details = details or {}
        if retry_after:
            error_details["retry_after"] = retry_after

        super().__init__(
            message=message,
            status_code=429,
            error_code="RATE_LIMIT_ERROR",
            details=error_details,
        )


class ExternalServiceError(BaseAPIException):
    def __init__(
        self,
        service_name: str,
        message: str = "External service error",
        details: Optional[Dict[str, Any]] = None,
    ):
        error_details = details or {}
        error_details["service"] = service_name

        super().__init__(
            message=f"{service_name}: {message}",
            status_code=502,
            error_code="EXTERNAL_SERVICE_ERROR",
            details=error_details,
        )
