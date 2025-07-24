from unittest.mock import AsyncMock

import pytest
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.api.deps import get_current_active_user, get_current_user
from app.core.exceptions import AuthenticationError, ValidationError
from app.db.base import get_db
from app.services.auth_service import AuthService


class TestGetDb:
    @pytest.mark.asyncio
    async def test_session_lifecycle(self, async_engine, monkeypatch):
        sessionmaker = async_sessionmaker(
            bind=async_engine, class_=AsyncSession, expire_on_commit=False
        )
        monkeypatch.setattr("app.db.base.AsyncSessionLocal", sessionmaker)
        gen = get_db()
        session = await gen.__anext__()
        assert isinstance(session, AsyncSession)
        close_mock = AsyncMock()
        monkeypatch.setattr(session, "close", close_mock)
        await gen.aclose()
        assert close_mock.called

    @pytest.mark.asyncio
    async def test_rollback_on_exception(self, async_engine, monkeypatch):
        sessionmaker = async_sessionmaker(
            bind=async_engine, class_=AsyncSession, expire_on_commit=False
        )
        monkeypatch.setattr("app.db.base.AsyncSessionLocal", sessionmaker)
        gen = get_db()
        session = await gen.__anext__()
        rollback_mock = AsyncMock()
        close_mock = AsyncMock()
        monkeypatch.setattr(session, "rollback", rollback_mock)
        monkeypatch.setattr(session, "close", close_mock)
        with pytest.raises(RuntimeError):
            await gen.athrow(RuntimeError("boom"))
        rollback_mock.assert_called_once()
        assert close_mock.called


class TestGetCurrentUser:
    @pytest.mark.asyncio
    async def test_valid_token_returns_user(self, db_session, test_user1, monkeypatch):
        async def mock_get_current_user_by_token(self, token):
            return test_user1

        monkeypatch.setattr(
            AuthService, "get_current_user_by_token", mock_get_current_user_by_token
        )
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token")
        user = await get_current_user(creds, db_session)
        assert user.id == test_user1.id

    @pytest.mark.asyncio
    async def test_invalid_token_raises(self, db_session, monkeypatch):
        async def mock_get_current_user_by_token(self, token):
            return None

        monkeypatch.setattr(
            AuthService, "get_current_user_by_token", mock_get_current_user_by_token
        )
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="bad")
        with pytest.raises(AuthenticationError):
            await get_current_user(creds, db_session)

    @pytest.mark.asyncio
    async def test_user_not_found(self, db_session, monkeypatch):
        async def mock_get_current_user_by_token(self, token):
            return None

        monkeypatch.setattr(
            AuthService, "get_current_user_by_token", mock_get_current_user_by_token
        )
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid")
        with pytest.raises(AuthenticationError):
            await get_current_user(creds, db_session)

    @pytest.mark.asyncio
    async def test_inactive_user(self, db_session, inactive_user, monkeypatch):
        async def mock_get_current_user_by_token(self, token):
            return None

        monkeypatch.setattr(
            AuthService, "get_current_user_by_token", mock_get_current_user_by_token
        )
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token")
        with pytest.raises(AuthenticationError):
            await get_current_user(creds, db_session)

    @pytest.mark.asyncio
    async def test_missing_token(self, db_session):
        with pytest.raises(AuthenticationError):
            await get_current_user(None, db_session)  # type: ignore[arg-type]


class TestGetCurrentActiveUser:
    @pytest.mark.asyncio
    async def test_active_user_passes(self, test_user1):
        user = await get_current_active_user(test_user1)
        assert user is test_user1

    @pytest.mark.asyncio
    async def test_inactive_user_rejected(self, inactive_user):
        with pytest.raises(ValidationError):
            await get_current_active_user(inactive_user)
