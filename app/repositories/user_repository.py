from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.user import User


class UserRepository:
    """Repository for user-related database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID.

        Args:
            user_id: User ID to search for

        Returns:
            Optional[User]: User if found, None otherwise
        """
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.

        Args:
            email: Email address to search for

        Returns:
            Optional[User]: User if found, None otherwise
        """
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.

        Args:
            username: Username to search for

        Returns:
            Optional[User]: User if found, None otherwise
        """
        query = select(User).where(User.username == username)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_user(self, user_data: dict) -> User:
        """
        Create a new user.

        Args:
            user_data: Dictionary containing user data

        Returns:
            User: Created user
        """
        user = User(**user_data)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_user(self, user_id: str, user_data: dict) -> Optional[User]:
        """
        Update user information.

        Args:
            user_id: User ID to update
            user_data: Dictionary containing updated user data

        Returns:
            Optional[User]: Updated user if found, None otherwise
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        for key, value in user_data.items():
            if hasattr(user, key):
                setattr(user, key, value)

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete_user(self, user_id: str) -> bool:
        """
        Delete a user.

        Args:
            user_id: User ID to delete

        Returns:
            bool: True if user was deleted, False if not found
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return False

        await self.db.delete(user)
        await self.db.commit()
        return True

    async def email_exists(self, email: str) -> bool:
        """
        Check if email already exists in database.

        Args:
            email: Email to check

        Returns:
            bool: True if email exists, False otherwise
        """
        user = await self.get_user_by_email(email)
        return user is not None

    async def username_exists(self, username: str) -> bool:
        """
        Check if username already exists in database.

        Args:
            username: Username to check

        Returns:
            bool: True if username exists, False otherwise
        """
        user = await self.get_user_by_username(username)
        return user is not None
