"""Test configuration and fixtures for the clinical sample service."""

import os
import pytest
from typing import AsyncGenerator, Generator
from unittest.mock import Mock
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from httpx import AsyncClient
import tempfile

from app.main import app
from app.core.config import get_settings
from app.core.security import create_access_token, get_password_hash
from app.db.base import Base
from app.api.deps import get_db
from app.models.user import User
from app.models.sample import Sample
from app.schemas.auth import UserCreate
from app.schemas.sample import SampleCreate


# Test database configuration
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
TEST_SYNC_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_async_engine():
    """Create test async database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False}
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Drop tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def test_db_session(test_async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session = async_sessionmaker(
        test_async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture
def test_client():
    """Create test client with test database."""
    
    # Create a simple mock database session for sync tests
    def mock_get_db():
        yield Mock()
    
    app.dependency_overrides[get_db] = mock_get_db
    
    client = TestClient(app)
    yield client
    
    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
async def async_client():
    """Create async test client."""
    
    # Create a simple mock database session for async tests
    async def mock_get_db():
        yield Mock()
    
    app.dependency_overrides[get_db] = mock_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Test user data."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPassword123!"
    }


@pytest.fixture
def test_user_create(test_user_data):
    """Test user creation schema."""
    return UserCreate(**test_user_data)


@pytest.fixture
async def test_user(test_db_session: AsyncSession, test_user_data):
    """Create test user in database."""
    user = User(
        username=test_user_data["username"],
        email=test_user_data["email"],
        hashed_password=get_password_hash(test_user_data["password"]),
        is_active=True
    )
    
    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)
    
    return user


@pytest.fixture
async def test_user_token(test_user: User):
    """Create JWT token for test user."""
    return create_access_token(data={"sub": str(test_user.id)})


@pytest.fixture
def auth_headers(test_user_token: str):
    """Create authorization headers for test requests."""
    return {"Authorization": f"Bearer {test_user_token}"}


@pytest.fixture
def sample_data():
    """Test sample data."""
    return {
        "sample_type": "blood",
        "subject_id": "P001",
        "collection_date": "2023-12-01",
        "status": "collected",
        "storage_location": "freezer-1-rowA"
    }


@pytest.fixture
def sample_create(sample_data):
    """Test sample creation schema."""
    return SampleCreate(**sample_data)


@pytest.fixture
async def test_sample(test_db_session: AsyncSession, test_user: User, sample_data):
    """Create test sample in database."""
    sample = Sample(
        sample_type=sample_data["sample_type"],
        subject_id=sample_data["subject_id"],
        collection_date=sample_data["collection_date"],
        status=sample_data["status"],
        storage_location=sample_data["storage_location"],
        user_id=test_user.id
    )
    
    test_db_session.add(sample)
    await test_db_session.commit()
    await test_db_session.refresh(sample)
    
    return sample


@pytest.fixture
async def multiple_test_samples(test_db_session: AsyncSession, test_user: User):
    """Create multiple test samples for testing filtering."""
    samples = [
        Sample(
            sample_type="blood",
            subject_id="P001",
            collection_date="2023-12-01",
            status="collected",
            storage_location="freezer-1-rowA",
            user_id=test_user.id
        ),
        Sample(
            sample_type="saliva",
            subject_id="P002",
            collection_date="2023-12-02",
            status="processing",
            storage_location="shelf-1-rowB",
            user_id=test_user.id
        ),
        Sample(
            sample_type="tissue",
            subject_id="P003",
            collection_date="2023-12-03",
            status="archived",
            storage_location="freezer-2-rowC",
            user_id=test_user.id
        )
    ]
    
    for sample in samples:
        test_db_session.add(sample)
    
    await test_db_session.commit()
    
    for sample in samples:
        await test_db_session.refresh(sample)
    
    return samples


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    settings = Mock()
    settings.DATABASE_URL = TEST_DATABASE_URL
    settings.SECRET_KEY = "test-secret-key"
    settings.ALGORITHM = "HS256"
    settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30
    settings.DEBUG = True
    settings.LOG_LEVEL = "INFO"
    return settings


@pytest.fixture
def temp_file():
    """Create temporary file for testing."""
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
        yield f.name
    
    # Clean up
    try:
        os.unlink(f.name)
    except OSError:
        pass


@pytest.fixture
def mock_db_session():
    """Mock database session for unit tests."""
    return Mock(spec=AsyncSession)


# Test data generators for parameterized tests
@pytest.fixture
def invalid_sample_data():
    """Generate invalid sample data for testing validation."""
    return [
        # Invalid sample type
        {
            "sample_type": "invalid_type",
            "subject_id": "P001",
            "collection_date": "2023-12-01",
            "status": "collected",
            "storage_location": "freezer-1-rowA"
        },
        # Invalid subject_id format
        {
            "sample_type": "blood",
            "subject_id": "invalid_id",
            "collection_date": "2023-12-01",
            "status": "collected",
            "storage_location": "freezer-1-rowA"
        },
        # Future date
        {
            "sample_type": "blood",
            "subject_id": "P001",
            "collection_date": "2025-12-01",
            "status": "collected",
            "storage_location": "freezer-1-rowA"
        }
    ]


@pytest.fixture
def invalid_user_data():
    """Generate invalid user data for testing validation."""
    return [
        # Invalid email
        {
            "username": "testuser",
            "email": "invalid_email",
            "password": "TestPassword123!"
        },
        # Weak password
        {
            "username": "testuser",
            "email": "test@example.com",
            "password": "weak"
        },
        # Reserved username
        {
            "username": "admin",
            "email": "test@example.com",
            "password": "TestPassword123!"
        }
    ]


# Helper functions for tests
def assert_sample_equal(sample1, sample2, exclude_fields=None):
    """Assert two samples are equal excluding specified fields."""
    if exclude_fields is None:
        exclude_fields = ['id', 'created_at', 'updated_at']
    
    for field in ['sample_type', 'subject_id', 'collection_date', 'status', 'storage_location']:
        if field not in exclude_fields:
            assert getattr(sample1, field) == getattr(sample2, field)


def assert_user_equal(user1, user2, exclude_fields=None):
    """Assert two users are equal excluding specified fields."""
    if exclude_fields is None:
        exclude_fields = ['id', 'created_at', 'updated_at', 'hashed_password']
    
    for field in ['username', 'email', 'is_active']:
        if field not in exclude_fields:
            assert getattr(user1, field) == getattr(user2, field)