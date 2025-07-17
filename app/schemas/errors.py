from typing import Any, Dict, Optional
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    error: bool = True
    message: str
    error_code: str
    details: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "error": True,
                "message": "Sample not found",
                "error_code": "NOT_FOUND",
                "details": {
                    "resource": "Sample",
                    "resource_id": "123e4567-e89b-12d3-a456-426614174000",
                },
                "timestamp": "2024-01-01T12:00:00Z",
            }
        }


class ValidationErrorResponse(BaseModel):
    error: bool = True
    message: str = "Validation failed"
    error_code: str = "VALIDATION_ERROR"
    details: Dict[str, Any]
    timestamp: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "error": True,
                "message": "Validation failed",
                "error_code": "VALIDATION_ERROR",
                "details": {"field": "email", "issue": "Invalid email format"},
                "timestamp": "2024-01-01T12:00:00Z",
            }
        }


class AuthenticationErrorResponse(BaseModel):
    error: bool = True
    message: str = "Authentication failed"
    error_code: str = "AUTHENTICATION_ERROR"
    details: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "error": True,
                "message": "Invalid credentials",
                "error_code": "AUTHENTICATION_ERROR",
                "details": {"reason": "invalid_password"},
                "timestamp": "2024-01-01T12:00:00Z",
            }
        }


class AuthorizationErrorResponse(BaseModel):
    error: bool = True
    message: str = "Access denied"
    error_code: str = "AUTHORIZATION_ERROR"
    details: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "error": True,
                "message": "Access denied to resource",
                "error_code": "AUTHORIZATION_ERROR",
                "details": {"resource": "sample", "required_permission": "read"},
                "timestamp": "2024-01-01T12:00:00Z",
            }
        }
