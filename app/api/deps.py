import logging
from typing import AsyncGenerator

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.exceptions import AuthenticationError, ValidationError
from ..db.base import get_db

logger = logging.getLogger(__name__)

# Security scheme for JWT tokens
security = HTTPBearer()


async def get_database() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session.

    Yields:
        AsyncSession: Database session
    """
    async for session in get_db():
        yield session


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_database),
):
    """
    Dependency to get current authenticated user.

    Args:
        credentials: JWT token from Authorization header
        db: Database session

    Returns:
        User: Current authenticated user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    from app.services.auth_service import AuthService

    if not credentials or not credentials.credentials:
        raise AuthenticationError(
            message="No authorization token provided",
            details={"reason": "missing_token"}
        )

    token = credentials.credentials

    # Get user from token using AuthService
    auth_service = AuthService(db)
    user = await auth_service.get_current_user_by_token(token)

    if not user:
        raise AuthenticationError(
            message="Could not validate credentials",
            details={"reason": "invalid_token"}
        )

    logger.info(f"Authentication successful for user: {user.username}")
    return user


async def get_current_active_user(current_user=Depends(get_current_user)):
    """
    Dependency to get current active user.

    Args:
        current_user: Current user from get_current_user dependency

    Returns:
        User: Active user information

    Raises:
        HTTPException: If user is not active
    """
    if not current_user.is_active:
        raise ValidationError(
            message="User account is inactive",
            details={"user_id": str(current_user.id)}
        )

    return current_user


# Optional dependency for endpoints that can work with or without authentication
async def get_optional_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_database),
):
    """
    Optional dependency that returns user if authenticated, None otherwise.

    Args:
        credentials: JWT token from Authorization header (optional)
        db: Database session

    Returns:
        User | None: User information if authenticated, None otherwise
    """
    if not credentials or not credentials.credentials:
        return None

    try:
        return await get_current_user(credentials, db)
    except (AuthenticationError, ValidationError):
        return None
