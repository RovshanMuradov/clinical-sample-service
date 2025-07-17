from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...deps import get_database
from app.schemas.auth import Token, UserCreate, UserLogin, UserResponse
from app.services.auth_service import AuthService

# Create router for authentication endpoints
router = APIRouter()


@router.post("/register", response_model=UserResponse, summary="User registration")
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_database)):
    """
    Register a new user.

    Args:
        user_data: User registration data
        db: Database session

    Returns:
        UserResponse: Created user information

    Raises:
        HTTPException: If email or username already exists
    """
    auth_service = AuthService(db)
    user = await auth_service.register_user(user_data)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=Token, summary="User login")
async def login(login_data: UserLogin, db: AsyncSession = Depends(get_database)):
    """
    Authenticate user and return access token.

    Args:
        login_data: User login credentials
        db: Database session

    Returns:
        Token: JWT access token

    Raises:
        HTTPException: If authentication fails
    """
    auth_service = AuthService(db)
    token = await auth_service.login_user(login_data)
    return token


@router.post("/refresh", response_model=Token, summary="Refresh access token")
async def refresh_token(db: AsyncSession = Depends(get_database)):
    """
    Refresh access token endpoint.

    TODO: Implement token refresh logic when authentication is ready.
    """
    # Placeholder implementation - would need current token verification
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Token refresh not implemented yet",
    )
