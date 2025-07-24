from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.auth import Token, UserCreate, UserLogin, UserResponse
from app.services.auth_service import AuthService

from ...deps import get_current_active_user, get_current_user, get_database

# Create router for authentication endpoints
router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    summary="Register a new user",
    description="Create a new user account for accessing the clinical sample management system.",
    response_description="Successfully created user account information",
    responses={
        201: {
            "description": "User successfully registered",
            "content": {
                "application/json": {
                    "example": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "username": "researcher_john",
                        "email": "john.doe@research.edu",
                        "is_active": True,
                        "created_at": "2023-12-01T10:00:00Z",
                        "updated_at": "2023-12-01T10:00:00Z",
                    }
                }
            },
        },
        400: {
            "description": "Validation error - invalid input data",
            "content": {
                "application/json": {
                    "example": {
                        "error": True,
                        "message": "Password must contain at least one uppercase letter",
                        "error_code": "VALIDATION_ERROR",
                        "details": {"field": "password", "issue": "missing_uppercase"},
                        "timestamp": "2023-12-01T10:00:00Z",
                    }
                }
            },
        },
        409: {
            "description": "User already exists - email or username taken",
            "content": {
                "application/json": {
                    "example": {
                        "error": True,
                        "message": "Email already registered",
                        "error_code": "CONFLICT_ERROR",
                        "details": {"field": "email", "value": "john.doe@research.edu"},
                        "timestamp": "2023-12-01T10:00:00Z",
                    }
                }
            },
        },
    },
)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_database)):
    """
    Register a new user account in the clinical sample management system.

    This endpoint allows new users to create an account with the following requirements:
    - **Username**: Must be unique, 3-50 characters, start with letter, alphanumeric with underscores/hyphens
    - **Email**: Must be unique and from an authorized domain (hospital.com, clinic.org, research.edu, medical.gov)
    - **Password**: Must be at least 8 characters with uppercase, lowercase, digit, and special character

    **Business Rules:**
    - Only users with authorized email domains can register
    - Username cannot be a reserved word (admin, root, user, etc.)
    - Password cannot be similar to username or contain common weak patterns
    - All new accounts are active by default

    **Example Request:**
    ```json
    {
        "username": "researcher_john",
        "email": "john.doe@research.edu",
        "password": "SecurePass123!"
    }
    ```
    """
    auth_service = AuthService(db)
    user = await auth_service.register_user(user_data)
    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=Token,
    summary="User login",
    description="Authenticate user credentials and return a JWT access token for API access.",
    response_description="JWT access token for authenticated API requests",
    responses={
        200: {
            "description": "Successfully authenticated",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJqb2huLmRvZUByZXNlYXJjaC5lZHUiLCJleHAiOjE2NzAzMjgwMDB9.signature",
                        "token_type": "bearer",
                    }
                }
            },
        },
        400: {
            "description": "Invalid request data",
            "content": {
                "application/json": {
                    "example": {
                        "error": True,
                        "message": "Email cannot be empty",
                        "error_code": "VALIDATION_ERROR",
                        "details": {"field": "email"},
                        "timestamp": "2023-12-01T10:00:00Z",
                    }
                }
            },
        },
        401: {
            "description": "Invalid credentials or inactive account",
            "content": {
                "application/json": {
                    "example": {
                        "error": True,
                        "message": "Invalid email or password",
                        "error_code": "AUTHENTICATION_ERROR",
                        "details": {},
                        "timestamp": "2023-12-01T10:00:00Z",
                    }
                }
            },
        },
        429: {
            "description": "Too many login attempts",
            "content": {
                "application/json": {
                    "example": {
                        "error": True,
                        "message": "Too many requests",
                        "error_code": "RATE_LIMIT_ERROR",
                        "details": {"retry_after": 60},
                        "timestamp": "2023-12-01T10:00:00Z",
                    }
                }
            },
        },
    },
)
async def login(login_data: UserLogin, db: AsyncSession = Depends(get_database)):
    """
    Authenticate a user and return a JWT access token for API access.

    This endpoint validates user credentials and returns a JWT token that must be included
    in the Authorization header for all protected API requests.

    **Token Usage:**
    - Include the token in the Authorization header: `Authorization: Bearer <token>`
    - Token expires in 30 minutes (configurable)
    - Use the `/refresh` endpoint to get a new token before expiration

    **Authentication Flow:**
    1. User provides email and password
    2. System validates credentials against database
    3. If valid, returns JWT token containing user information
    4. Token is used for subsequent API requests

    **Example Request:**
    ```json
    {
        "email": "john.doe@research.edu",
        "password": "SecurePass123!"
    }
    ```

    **Example Response:**
    ```json
    {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "token_type": "bearer"
    }
    ```
    """
    auth_service = AuthService(db)
    token = await auth_service.login_user(login_data)
    return token


@router.post(
    "/refresh",
    response_model=Token,
    summary="Refresh access token",
    description="Generate a new JWT access token using a valid existing token.",
    response_description="New JWT access token with extended expiration",
    responses={
        200: {
            "description": "Token successfully refreshed",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJqb2huLmRvZUByZXNlYXJjaC5lZHUiLCJleHAiOjE2NzAzMzAwMDB9.signature",
                        "token_type": "bearer",
                    }
                }
            },
        },
        401: {
            "description": "Invalid or expired token",
            "content": {
                "application/json": {
                    "example": {
                        "error": True,
                        "message": "Token has expired",
                        "error_code": "AUTHENTICATION_ERROR",
                        "details": {},
                        "timestamp": "2023-12-01T10:00:00Z",
                    }
                }
            },
        },
        403: {
            "description": "User account is inactive",
            "content": {
                "application/json": {
                    "example": {
                        "error": True,
                        "message": "User account is inactive",
                        "error_code": "AUTHORIZATION_ERROR",
                        "details": {},
                        "timestamp": "2023-12-01T10:00:00Z",
                    }
                }
            },
        },
    },
)
async def refresh_token(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database),
):
    """
    Refresh an existing JWT access token to extend the session.

    This endpoint allows users to obtain a new access token using their current valid token,
    extending their session without requiring re-authentication.

    **Authentication Required:**
    - Must provide a valid Bearer token in the Authorization header
    - Token must not be expired
    - Associated user account must be active

    **Usage:**
    - Call this endpoint before your current token expires
    - Use the new token for subsequent API requests
    - The old token becomes invalid after refresh

    **Headers Required:**
    ```
    Authorization: Bearer <your-current-token>
    ```

    **Example Response:**
    ```json
    {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "token_type": "bearer"
    }
    ```

    **Best Practices:**
    - Refresh tokens proactively before expiration
    - Store the new token securely
    - Handle token refresh failures gracefully by redirecting to login
    """
    auth_service = AuthService(db)
    return await auth_service.refresh_access_token(current_user)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user information",
    description="Return information about the currently authenticated user.",
)
async def get_me(current_user: User = Depends(get_current_active_user)):
    """Retrieve the active user making the request."""
    return UserResponse.model_validate(current_user)
