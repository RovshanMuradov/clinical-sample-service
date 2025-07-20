import pytest
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.repositories.user_repository import UserRepository
from tests.helpers import build_user_data


class TestUserRepository:
    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self, user_repository: UserRepository):
        user = await user_repository.get_user_by_email("missing@test.com")
        assert user is None

    @pytest.mark.asyncio
    async def test_get_user_by_username_not_found(self, user_repository: UserRepository):
        user = await user_repository.get_user_by_username("missing")
        assert user is None

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, user_repository: UserRepository):
        data = build_user_data()
        await user_repository.create_user({
            "username": data["username"],
            "email": data["email"],
            "hashed_password": "x",
            "is_active": True,
        })
        with pytest.raises(IntegrityError):
            await user_repository.create_user({
                "username": data["username"] + "a",
                "email": data["email"],
                "hashed_password": "y",
                "is_active": True,
            })

    @pytest.mark.asyncio
    async def test_update_user_not_found(self, user_repository: UserRepository):
        import uuid
        user = await user_repository.update_user(uuid.UUID("00000000-0000-0000-0000-000000000000"), {"username": "none"})
        assert user is None
