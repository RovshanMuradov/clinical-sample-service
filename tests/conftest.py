"""
Test configuration and fixtures.
"""

import os

os.environ["DATABASE_URL"] = "postgresql+asyncpg://user:pass@localhost:5432/testdb"
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("ALGORITHM", "HS256")

import asyncio
from datetime import date
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio

# from sqlalchemy import create_engine  # Removed unused import
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.security import get_password_hash
from app.db.base import Base
from app.models.sample import Sample, SampleStatus, SampleType
from app.models.user import User
from app.repositories.sample_repository import SampleRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.sample_service import SampleService

# from unittest.mock import AsyncMock  # Removed unused import


# Test database URL (SQLite in-memory for fast tests)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def async_engine():
    """Create async engine for testing."""
    engine = create_async_engine(
        SQLALCHEMY_TEST_DATABASE_URL,
        echo=False,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def async_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create async session for testing."""
    async_session_maker = async_sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session


@pytest_asyncio.fixture
async def sample_repository(async_session: AsyncSession) -> SampleRepository:
    """Create SampleRepository instance."""
    return SampleRepository(async_session)


@pytest_asyncio.fixture
async def user_repository(async_session: AsyncSession) -> UserRepository:
    """Create UserRepository instance."""
    return UserRepository(async_session)


@pytest_asyncio.fixture
async def auth_service(async_session: AsyncSession) -> AuthService:
    """Create AuthService instance."""
    return AuthService(async_session)


@pytest_asyncio.fixture
async def sample_service(async_session: AsyncSession) -> SampleService:
    """Create SampleService instance."""
    return SampleService(async_session)


@pytest_asyncio.fixture
async def test_user1(user_repository: UserRepository) -> User:
    """Create test user 1."""
    user_data = {
        "username": "testuser1",
        "email": "user1@example.com",
        "hashed_password": get_password_hash("testpass123"),
        "is_active": True,
    }
    return await user_repository.create_user(user_data)


@pytest_asyncio.fixture
async def test_user2(user_repository: UserRepository) -> User:
    """Create test user 2."""
    user_data = {
        "username": "testuser2",
        "email": "user2@example.com",
        "hashed_password": get_password_hash("testpass456"),
        "is_active": True,
    }
    return await user_repository.create_user(user_data)


@pytest_asyncio.fixture
async def inactive_user(user_repository: UserRepository) -> User:
    """Create an inactive test user."""
    user_data = {
        "username": "inactive",
        "email": "inactive@example.com",
        "hashed_password": get_password_hash("inactivePass1$"),
        "is_active": False,
    }
    return await user_repository.create_user(user_data)


@pytest_asyncio.fixture
async def test_samples_user1(
    sample_repository: SampleRepository, test_user1: User
) -> list[Sample]:
    """Create test samples for user1."""
    samples_data = [
        {
            "sample_type": SampleType.BLOOD,
            "subject_id": "P001",
            "collection_date": date(2024, 1, 15),
            "status": SampleStatus.COLLECTED,
            "storage_location": "freezer-1-rowA",
            "user_id": test_user1.id,
        },
        {
            "sample_type": SampleType.BLOOD,
            "subject_id": "P002",
            "collection_date": date(2024, 1, 16),
            "status": SampleStatus.PROCESSING,
            "storage_location": "freezer-1-rowB",
            "user_id": test_user1.id,
        },
        {
            "sample_type": SampleType.TISSUE,
            "subject_id": "P003",
            "collection_date": date(2024, 1, 17),
            "status": SampleStatus.ARCHIVED,
            "storage_location": "freezer-2-rowA",
            "user_id": test_user1.id,
        },
    ]

    samples = []
    for sample_data in samples_data:
        sample = await sample_repository.create_sample(sample_data)
        samples.append(sample)

    return samples


@pytest_asyncio.fixture
async def test_samples_user2(
    sample_repository: SampleRepository, test_user2: User
) -> list[Sample]:
    """Create test samples for user2."""
    samples_data = [
        {
            "sample_type": SampleType.BLOOD,
            "subject_id": "S001",
            "collection_date": date(2024, 2, 1),
            "status": SampleStatus.COLLECTED,
            "storage_location": "freezer-3-rowA",
            "user_id": test_user2.id,
        },
        {
            "sample_type": SampleType.SALIVA,
            "subject_id": "S002",
            "collection_date": date(2024, 2, 2),
            "status": SampleStatus.PROCESSING,
            "storage_location": "room-1-shelfA",
            "user_id": test_user2.id,
        },
        {
            "sample_type": SampleType.SALIVA,
            "subject_id": "S003",
            "collection_date": date(2024, 2, 3),
            "status": SampleStatus.COLLECTED,
            "storage_location": "room-1-shelfB",
            "user_id": test_user2.id,
        },
    ]

    samples = []
    for sample_data in samples_data:
        sample = await sample_repository.create_sample(sample_data)
        samples.append(sample)

    return samples


@pytest_asyncio.fixture
async def app_with_overrides(async_session, monkeypatch):
    """FastAPI app with test database overrides."""
    monkeypatch.setenv("DATABASE_URL", SQLALCHEMY_TEST_DATABASE_URL)
    monkeypatch.setenv("RATE_LIMIT_BURST", "1000")
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "1000")
    from app.main import app
    from app.middleware.security_middleware import RateLimitMiddleware
    from app.api.deps import get_database

    async def _get_db_override():
        yield async_session

    app.dependency_overrides[get_database] = _get_db_override
    # Disable rate limiting for tests
    app.user_middleware = [
        m for m in app.user_middleware if m.cls is not RateLimitMiddleware
    ]
    app.middleware_stack = app.build_middleware_stack()
    yield app
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(app_with_overrides):
    """HTTP client for API tests."""
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app_with_overrides)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


@pytest_asyncio.fixture
async def db_session(async_session: AsyncSession) -> AsyncGenerator[AsyncSession, None]:
    """Alias for async_session fixture used by tests."""
    yield async_session


@pytest_asyncio.fixture
async def authenticated_client(
    client, auth_service: AuthService, test_user1: User
) -> AsyncGenerator:
    """HTTP client with Authorization header for test_user1."""
    token = await auth_service.create_access_token_for_user(test_user1)
    client.headers.update({"Authorization": f"Bearer {token.access_token}"})
    yield client


@pytest.fixture
def test_data_builder():
    """Factory to build sample data dictionaries."""

    def _builder(**overrides):
        data = {
            "sample_type": "blood",
            "subject_id": "P001",
            "collection_date": str(date.today()),
            "status": "collected",
            "storage_location": "freezer-1-rowA",
        }
        data.update(overrides)
        return data

    return _builder
