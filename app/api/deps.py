import logging
from typing import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings
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

    This is a placeholder for future authentication implementation.
    For now, it validates the token format but doesn't verify the user.

    Args:
        credentials: JWT token from Authorization header
        db: Database session

    Returns:
        dict: User information (placeholder)

    Raises:
        HTTPException: If token is invalid
    """
    # TODO: Implement actual JWT token validation when User model is ready
    # For now, just validate that a token is present

    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authorization token provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    # Basic token format validation (placeholder)
    if len(token) < 10:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.info(f"Authentication check passed for token: {token[:10]}...")

    # Return placeholder user data
    # TODO: Replace with actual user lookup when User model is implemented
    return {
        "user_id": "placeholder_user_id",
        "username": "placeholder_user",
        "email": "user@example.com",
        "is_active": True,
    }


async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    """
    Dependency to get current active user.

    Args:
        current_user: Current user from get_current_user dependency

    Returns:
        dict: Active user information

    Raises:
        HTTPException: If user is not active
    """
    if not current_user.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
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
        dict | None: User information if authenticated, None otherwise
    """
    if not credentials or not credentials.credentials:
        return None

    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None
