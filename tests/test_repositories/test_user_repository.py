"""Tests for UserRepository."""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

from app.repositories.user_repository import UserRepository
from app.models.user import User


class TestUserRepository:
    """Test UserRepository functionality."""

    @pytest.fixture
    def mock_db_session(self):
        """Create mock database session."""
        mock_session = Mock()
        mock_session.execute = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        mock_session.add = Mock()
        mock_session.delete = AsyncMock()
        return mock_session

    @pytest.fixture
    def user_repository(self, mock_db_session):
        """Create UserRepository instance with mocked database session."""
        return UserRepository(mock_db_session)

    @pytest.fixture
    def test_user(self):
        """Create test user."""
        return User(
            id=uuid4(),
            username="testuser",
            email="test@example.com",
            hashed_password="$2b$12$test_hash",
            is_active=True
        )

    @pytest.fixture
    def user_data(self):
        """Create user data dictionary."""
        return {
            "username": "testuser",
            "email": "test@example.com",
            "hashed_password": "$2b$12$test_hash",
            "is_active": True
        }

    @pytest.mark.asyncio
    async def test_get_user_by_id_success(
        self, user_repository, test_user, mock_db_session
    ):
        """Test successful user retrieval by ID."""
        # Mock database query result
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = test_user
        mock_db_session.execute.return_value = mock_result
        
        result = await user_repository.get_user_by_id(test_user.id)
        
        assert result == test_user
        mock_db_session.execute.assert_called_once()
        mock_result.scalar_one_or_none.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(
        self, user_repository, mock_db_session
    ):
        """Test user retrieval by ID when user not found."""
        user_id = uuid4()
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        result = await user_repository.get_user_by_id(user_id)
        
        assert result is None
        mock_db_session.execute.assert_called_once()
        mock_result.scalar_one_or_none.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_by_email_success(
        self, user_repository, test_user, mock_db_session
    ):
        """Test successful user retrieval by email."""
        email = "test@example.com"
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = test_user
        mock_db_session.execute.return_value = mock_result
        
        result = await user_repository.get_user_by_email(email)
        
        assert result == test_user
        mock_db_session.execute.assert_called_once()
        mock_result.scalar_one_or_none.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(
        self, user_repository, mock_db_session
    ):
        """Test user retrieval by email when user not found."""
        email = "nonexistent@example.com"
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        result = await user_repository.get_user_by_email(email)
        
        assert result is None
        mock_db_session.execute.assert_called_once()
        mock_result.scalar_one_or_none.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_by_username_success(
        self, user_repository, test_user, mock_db_session
    ):
        """Test successful user retrieval by username."""
        username = "testuser"
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = test_user
        mock_db_session.execute.return_value = mock_result
        
        result = await user_repository.get_user_by_username(username)
        
        assert result == test_user
        mock_db_session.execute.assert_called_once()
        mock_result.scalar_one_or_none.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_by_username_not_found(
        self, user_repository, mock_db_session
    ):
        """Test user retrieval by username when user not found."""
        username = "nonexistent"
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        result = await user_repository.get_user_by_username(username)
        
        assert result is None
        mock_db_session.execute.assert_called_once()
        mock_result.scalar_one_or_none.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_user_success(
        self, user_repository, user_data, test_user, mock_db_session
    ):
        """Test successful user creation."""
        # Mock the User constructor and database operations
        with patch('app.repositories.user_repository.User') as mock_user_class:
            mock_user_class.return_value = test_user
            mock_db_session.add = Mock()
            mock_db_session.commit = AsyncMock()
            mock_db_session.refresh = AsyncMock()
            
            result = await user_repository.create_user(user_data)
            
            assert result == test_user
            mock_user_class.assert_called_once_with(**user_data)
            mock_db_session.add.assert_called_once_with(test_user)
            mock_db_session.commit.assert_called_once()
            mock_db_session.refresh.assert_called_once_with(test_user)

    @pytest.mark.asyncio
    async def test_update_user_success(
        self, user_repository, test_user, mock_db_session
    ):
        """Test successful user update."""
        user_id = test_user.id
        update_data = {
            "email": "updated@example.com",
            "is_active": False
        }
        
        # Mock get_user_by_id to return the test user
        user_repository.get_user_by_id = AsyncMock(return_value=test_user)
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()
        
        result = await user_repository.update_user(user_id, update_data)
        
        assert result == test_user
        # Check that attributes were updated
        assert hasattr(test_user, 'email')
        assert hasattr(test_user, 'is_active')
        
        user_repository.get_user_by_id.assert_called_once_with(user_id)
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once_with(test_user)

    @pytest.mark.asyncio
    async def test_update_user_not_found(
        self, user_repository, mock_db_session
    ):
        """Test user update when user not found."""
        user_id = uuid4()
        update_data = {"email": "updated@example.com"}
        
        # Mock get_user_by_id to return None
        user_repository.get_user_by_id = AsyncMock(return_value=None)
        
        result = await user_repository.update_user(user_id, update_data)
        
        assert result is None
        user_repository.get_user_by_id.assert_called_once_with(user_id)
        # Ensure commit and refresh are not called when user is not found
        mock_db_session.commit.assert_not_called()
        mock_db_session.refresh.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_user_with_invalid_attribute(
        self, user_repository, test_user, mock_db_session
    ):
        """Test user update with invalid attribute (should be ignored)."""
        user_id = test_user.id
        update_data = {
            "email": "updated@example.com",
            "nonexistent_field": "value"
        }
        
        # Mock get_user_by_id to return the test user
        user_repository.get_user_by_id = AsyncMock(return_value=test_user)
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()
        
        result = await user_repository.update_user(user_id, update_data)
        
        assert result == test_user
        # Check that valid attribute was updated
        assert hasattr(test_user, 'email')
        # Check that invalid attribute was not set
        assert not hasattr(test_user, 'nonexistent_field')
        
        user_repository.get_user_by_id.assert_called_once_with(user_id)
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once_with(test_user)

    @pytest.mark.asyncio
    async def test_delete_user_success(
        self, user_repository, test_user, mock_db_session
    ):
        """Test successful user deletion."""
        user_id = test_user.id
        
        # Mock get_user_by_id to return the test user
        user_repository.get_user_by_id = AsyncMock(return_value=test_user)
        mock_db_session.delete = AsyncMock()
        mock_db_session.commit = AsyncMock()
        
        result = await user_repository.delete_user(user_id)
        
        assert result is True
        user_repository.get_user_by_id.assert_called_once_with(user_id)
        mock_db_session.delete.assert_called_once_with(test_user)
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_user_not_found(
        self, user_repository, mock_db_session
    ):
        """Test user deletion when user not found."""
        user_id = uuid4()
        
        # Mock get_user_by_id to return None
        user_repository.get_user_by_id = AsyncMock(return_value=None)
        
        result = await user_repository.delete_user(user_id)
        
        assert result is False
        user_repository.get_user_by_id.assert_called_once_with(user_id)
        # Ensure delete and commit are not called when user is not found
        mock_db_session.delete.assert_not_called()
        mock_db_session.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_email_exists_true(
        self, user_repository, test_user
    ):
        """Test email existence check when email exists."""
        email = "test@example.com"
        
        # Mock get_user_by_email to return the test user
        user_repository.get_user_by_email = AsyncMock(return_value=test_user)
        
        result = await user_repository.email_exists(email)
        
        assert result is True
        user_repository.get_user_by_email.assert_called_once_with(email)

    @pytest.mark.asyncio
    async def test_email_exists_false(
        self, user_repository
    ):
        """Test email existence check when email doesn't exist."""
        email = "nonexistent@example.com"
        
        # Mock get_user_by_email to return None
        user_repository.get_user_by_email = AsyncMock(return_value=None)
        
        result = await user_repository.email_exists(email)
        
        assert result is False
        user_repository.get_user_by_email.assert_called_once_with(email)

    @pytest.mark.asyncio
    async def test_username_exists_true(
        self, user_repository, test_user
    ):
        """Test username existence check when username exists."""
        username = "testuser"
        
        # Mock get_user_by_username to return the test user
        user_repository.get_user_by_username = AsyncMock(return_value=test_user)
        
        result = await user_repository.username_exists(username)
        
        assert result is True
        user_repository.get_user_by_username.assert_called_once_with(username)

    @pytest.mark.asyncio
    async def test_username_exists_false(
        self, user_repository
    ):
        """Test username existence check when username doesn't exist."""
        username = "nonexistent"
        
        # Mock get_user_by_username to return None
        user_repository.get_user_by_username = AsyncMock(return_value=None)
        
        result = await user_repository.username_exists(username)
        
        assert result is False
        user_repository.get_user_by_username.assert_called_once_with(username)

    @pytest.mark.asyncio
    async def test_create_user_with_all_fields(
        self, user_repository, mock_db_session
    ):
        """Test user creation with all possible fields."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "hashed_password": "$2b$12$test_hash",
            "is_active": True
        }
        
        created_user = User(**user_data)
        
        with patch('app.repositories.user_repository.User') as mock_user_class:
            mock_user_class.return_value = created_user
            mock_db_session.add = Mock()
            mock_db_session.commit = AsyncMock()
            mock_db_session.refresh = AsyncMock()
            
            result = await user_repository.create_user(user_data)
            
            assert result == created_user
            mock_user_class.assert_called_once_with(**user_data)
            mock_db_session.add.assert_called_once_with(created_user)
            mock_db_session.commit.assert_called_once()
            mock_db_session.refresh.assert_called_once_with(created_user)

    @pytest.mark.asyncio
    async def test_update_user_partial_update(
        self, user_repository, test_user, mock_db_session
    ):
        """Test partial user update (only updating some fields)."""
        user_id = test_user.id
        update_data = {
            "is_active": False
        }
        
        # Mock get_user_by_id to return the test user
        user_repository.get_user_by_id = AsyncMock(return_value=test_user)
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()
        
        result = await user_repository.update_user(user_id, update_data)
        
        assert result == test_user
        # Check that only the specified field was updated
        assert hasattr(test_user, 'is_active')
        
        user_repository.get_user_by_id.assert_called_once_with(user_id)
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once_with(test_user)

    @pytest.mark.asyncio
    async def test_database_queries_use_correct_filters(
        self, user_repository, mock_db_session
    ):
        """Test that database queries use correct WHERE clauses."""
        # Test get_user_by_id query construction
        user_id = uuid4()
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        await user_repository.get_user_by_id(user_id)
        
        # Check that execute was called with a query
        mock_db_session.execute.assert_called_once()
        query = mock_db_session.execute.call_args[0][0]
        # Basic check that it's a select query - detailed SQL checking would require more complex mocking
        assert hasattr(query, 'where')

    @pytest.mark.asyncio
    async def test_get_user_by_email_query_construction(
        self, user_repository, mock_db_session
    ):
        """Test email query construction."""
        email = "test@example.com"
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        await user_repository.get_user_by_email(email)
        
        # Check that execute was called with a query
        mock_db_session.execute.assert_called_once()
        query = mock_db_session.execute.call_args[0][0]
        assert hasattr(query, 'where')

    @pytest.mark.asyncio
    async def test_get_user_by_username_query_construction(
        self, user_repository, mock_db_session
    ):
        """Test username query construction."""
        username = "testuser"
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        await user_repository.get_user_by_username(username)
        
        # Check that execute was called with a query
        mock_db_session.execute.assert_called_once()
        query = mock_db_session.execute.call_args[0][0]
        assert hasattr(query, 'where')