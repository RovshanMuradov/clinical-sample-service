from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ..core.exceptions import AuthenticationError, ConflictError
from ..core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
    verify_token,
)
from ..models.user import User
from ..repositories.user_repository import UserRepository
from ..schemas.auth import Token, UserCreate, UserLogin


class AuthService:
    """Service for authentication-related operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repository = UserRepository(db)

    async def register_user(self, user_data: UserCreate) -> User:
        """
        Register a new user.

        Args:
            user_data: User registration data

        Returns:
            User: Created user

        Raises:
            HTTPException: If email or username already exists
        """
        # Check if email already exists
        if await self.user_repository.email_exists(user_data.email):
            raise ConflictError(
                message="Email already registered",
                resource="email",
                details={"email": user_data.email},
            )

        # Check if username already exists
        if await self.user_repository.username_exists(user_data.username):
            raise ConflictError(
                message="Username already taken",
                resource="username",
                details={"username": user_data.username},
            )

        # Hash password
        hashed_password = get_password_hash(user_data.password)

        # Create user data
        user_dict = {
            "username": user_data.username,
            "email": user_data.email,
            "hashed_password": hashed_password,
            "is_active": True,
        }

        # Create user
        user = await self.user_repository.create_user(user_dict)
        return user

    async def authenticate_user(self, login_data: UserLogin) -> Optional[User]:
        """
        Authenticate user with email and password.

        Args:
            login_data: User login credentials

        Returns:
            Optional[User]: User if authentication successful, None otherwise
        """
        # Get user by email
        user = await self.user_repository.get_user_by_email(login_data.email)
        if not user:
            return None

        # Verify password
        if not verify_password(login_data.password, user.hashed_password):
            return None

        # Check if user is active
        if not user.is_active:
            return None

        return user

    async def create_access_token_for_user(self, user: User) -> Token:
        """
        Create access token for user.

        Args:
            user: User to create token for

        Returns:
            Token: Access token
        """
        # Create token data
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "username": user.username,
            "is_active": user.is_active,
        }

        # Create access token
        access_token = create_access_token(token_data)

        return Token(access_token=access_token, token_type="bearer")

    async def get_current_user_by_token(self, token: str) -> Optional[User]:
        """
        Get current user from JWT token.

        Args:
            token: JWT token

        Returns:
            Optional[User]: User if token is valid, None otherwise
        """
        try:
            # Verify token
            payload = verify_token(token)
            user_id_str = payload.get("sub")

            if not user_id_str:
                return None

            # Convert string to UUID
            user_id = UUID(user_id_str)

            # Get user from database
            user = await self.user_repository.get_user_by_id(user_id)

            # Check if user is active
            if not user or not user.is_active:
                return None

            return user

        except (AuthenticationError, ConflictError):
            return None

    async def login_user(self, login_data: UserLogin) -> Token:
        """
        Login user and return access token.

        Args:
            login_data: User login credentials

        Returns:
            Token: Access token

        Raises:
            HTTPException: If authentication fails
        """
        # Authenticate user
        user = await self.authenticate_user(login_data)

        if not user:
            raise AuthenticationError(
                message="Incorrect email or password",
                details={"email": login_data.email},
            )

        # Create access token
        return await self.create_access_token_for_user(user)

    async def refresh_access_token(self, current_user: User) -> Token:
        """
        Refresh access token for current user.

        Args:
            current_user: Current authenticated user

        Returns:
            Token: New access token

        Raises:
            HTTPException: If user is not active
        """
        # Check if user is still active
        if not current_user.is_active:
            raise AuthenticationError(
                message="User account is inactive",
                details={"user_id": str(current_user.id)},
            )

        # Get fresh user data from database to ensure it's up to date
        fresh_user = await self.user_repository.get_user_by_id(current_user.id)
        if not fresh_user or not fresh_user.is_active:
            raise AuthenticationError(
                message="User account is inactive or not found",
                details={"user_id": str(current_user.id)},
            )

        # Create new access token
        return await self.create_access_token_for_user(fresh_user)
