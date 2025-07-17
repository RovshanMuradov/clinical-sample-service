"""Tests for AuthService."""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4, UUID

from app.services.auth_service import AuthService
from app.models.user import User
from app.schemas.auth import UserCreate, UserLogin, Token
from app.core.exceptions import AuthenticationError, ConflictError


class TestAuthService:
    """Test AuthService functionality."""

    @pytest.fixture
    def mock_db_session(self):
        """Create mock database session."""
        return Mock()

    @pytest.fixture
    def mock_user_repository(self):
        """Create mock user repository."""
        return Mock()

    @pytest.fixture
    def auth_service(self, mock_db_session, mock_user_repository):
        """Create AuthService instance with mocked dependencies."""
        service = AuthService(mock_db_session)
        service.user_repository = mock_user_repository
        return service

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
    def user_create_data(self):
        """Create UserCreate data."""
        return UserCreate(
            username="testuser",
            email="test@example.com",
            password="TestPassw0rd!"
        )

    @pytest.fixture
    def user_login_data(self):
        """Create UserLogin data."""
        return UserLogin(
            email="test@example.com",
            password="TestPassw0rd!"
        )

    @pytest.mark.asyncio
    async def test_register_user_success(
        self, auth_service, user_create_data, mock_user_repository
    ):
        """Test successful user registration."""
        # Mock repository methods
        mock_user_repository.email_exists = AsyncMock(return_value=False)
        mock_user_repository.username_exists = AsyncMock(return_value=False)
        
        test_user = User(
            id=uuid4(),
            username=user_create_data.username,
            email=user_create_data.email,
            hashed_password="$2b$12$test_hash",
            is_active=True
        )
        mock_user_repository.create_user = AsyncMock(return_value=test_user)

        # Mock password hashing
        with patch('app.services.auth_service.get_password_hash') as mock_hash:
            mock_hash.return_value = "$2b$12$test_hash"
            
            result = await auth_service.register_user(user_create_data)
            
            assert result == test_user
            assert mock_user_repository.email_exists.called
            assert mock_user_repository.username_exists.called
            assert mock_user_repository.create_user.called
            mock_hash.assert_called_once_with(user_create_data.password)

    @pytest.mark.asyncio
    async def test_register_user_email_exists(
        self, auth_service, user_create_data, mock_user_repository
    ):
        """Test user registration with existing email."""
        mock_user_repository.email_exists = AsyncMock(return_value=True)

        with pytest.raises(ConflictError) as exc_info:
            await auth_service.register_user(user_create_data)
        
        assert "email already exists or conflicts with existing data" in str(exc_info.value)
        mock_user_repository.create_user = AsyncMock()
        assert mock_user_repository.email_exists.called
        assert not mock_user_repository.create_user.called

    @pytest.mark.asyncio
    async def test_register_user_username_exists(
        self, auth_service, user_create_data, mock_user_repository
    ):
        """Test user registration with existing username."""
        mock_user_repository.email_exists = AsyncMock(return_value=False)
        mock_user_repository.username_exists = AsyncMock(return_value=True)

        with pytest.raises(ConflictError) as exc_info:
            await auth_service.register_user(user_create_data)
        
        assert "username already exists or conflicts with existing data" in str(exc_info.value)
        mock_user_repository.create_user = AsyncMock()
        assert mock_user_repository.email_exists.called
        assert mock_user_repository.username_exists.called
        assert not mock_user_repository.create_user.called

    @pytest.mark.asyncio
    async def test_authenticate_user_success(
        self, auth_service, user_login_data, test_user, mock_user_repository
    ):
        """Test successful user authentication."""
        mock_user_repository.get_user_by_email = AsyncMock(return_value=test_user)
        
        with patch('app.services.auth_service.verify_password') as mock_verify:
            mock_verify.return_value = True
            
            result = await auth_service.authenticate_user(user_login_data)
            
            assert result == test_user
            mock_user_repository.get_user_by_email.assert_called_once_with(user_login_data.email)
            mock_verify.assert_called_once_with(user_login_data.password, test_user.hashed_password)

    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(
        self, auth_service, user_login_data, mock_user_repository
    ):
        """Test authentication with non-existent user."""
        mock_user_repository.get_user_by_email = AsyncMock(return_value=None)
        
        result = await auth_service.authenticate_user(user_login_data)
        
        assert result is None
        mock_user_repository.get_user_by_email.assert_called_once_with(user_login_data.email)

    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(
        self, auth_service, user_login_data, test_user, mock_user_repository
    ):
        """Test authentication with wrong password."""
        mock_user_repository.get_user_by_email = AsyncMock(return_value=test_user)
        
        with patch('app.services.auth_service.verify_password') as mock_verify:
            mock_verify.return_value = False
            
            result = await auth_service.authenticate_user(user_login_data)
            
            assert result is None
            mock_user_repository.get_user_by_email.assert_called_once_with(user_login_data.email)
            mock_verify.assert_called_once_with(user_login_data.password, test_user.hashed_password)

    @pytest.mark.asyncio
    async def test_authenticate_user_inactive(
        self, auth_service, user_login_data, test_user, mock_user_repository
    ):
        """Test authentication with inactive user."""
        test_user.is_active = False
        mock_user_repository.get_user_by_email = AsyncMock(return_value=test_user)
        
        with patch('app.services.auth_service.verify_password') as mock_verify:
            mock_verify.return_value = True
            
            result = await auth_service.authenticate_user(user_login_data)
            
            assert result is None

    @pytest.mark.asyncio
    async def test_create_access_token_for_user(
        self, auth_service, test_user
    ):
        """Test access token creation for user."""
        with patch('app.services.auth_service.create_access_token') as mock_create_token:
            mock_create_token.return_value = "test_token"
            
            result = await auth_service.create_access_token_for_user(test_user)
            
            assert isinstance(result, Token)
            assert result.access_token == "test_token"
            assert result.token_type == "bearer"
            
            # Check that token data was created correctly
            mock_create_token.assert_called_once()
            call_args = mock_create_token.call_args[0][0]
            assert call_args["sub"] == str(test_user.id)
            assert call_args["email"] == test_user.email
            assert call_args["username"] == test_user.username
            assert call_args["is_active"] == test_user.is_active

    @pytest.mark.asyncio
    async def test_get_current_user_by_token_success(
        self, auth_service, test_user, mock_user_repository
    ):
        """Test getting current user by valid token."""
        token = "valid_token"
        mock_payload = {"sub": str(test_user.id)}
        mock_user_repository.get_user_by_id = AsyncMock(return_value=test_user)
        
        with patch('app.services.auth_service.verify_token') as mock_verify:
            mock_verify.return_value = mock_payload
            
            result = await auth_service.get_current_user_by_token(token)
            
            assert result == test_user
            mock_verify.assert_called_once_with(token)
            mock_user_repository.get_user_by_id.assert_called_once_with(test_user.id)

    @pytest.mark.asyncio
    async def test_get_current_user_by_token_invalid_token(
        self, auth_service, mock_user_repository
    ):
        """Test getting current user by invalid token."""
        token = "invalid_token"
        
        with patch('app.services.auth_service.verify_token') as mock_verify:
            mock_verify.side_effect = AuthenticationError("Invalid token")
            
            result = await auth_service.get_current_user_by_token(token)
            
            assert result is None
            mock_verify.assert_called_once_with(token)
            assert not mock_user_repository.get_user_by_id.called

    @pytest.mark.asyncio
    async def test_get_current_user_by_token_no_sub(
        self, auth_service, mock_user_repository
    ):
        """Test getting current user by token without sub."""
        token = "token_without_sub"
        mock_payload = {"email": "test@example.com"}
        
        with patch('app.services.auth_service.verify_token') as mock_verify:
            mock_verify.return_value = mock_payload
            
            result = await auth_service.get_current_user_by_token(token)
            
            assert result is None
            mock_verify.assert_called_once_with(token)
            assert not mock_user_repository.get_user_by_id.called

    @pytest.mark.asyncio
    async def test_get_current_user_by_token_user_not_found(
        self, auth_service, mock_user_repository
    ):
        """Test getting current user by token when user not found."""
        token = "valid_token"
        user_id = uuid4()
        mock_payload = {"sub": str(user_id)}
        mock_user_repository.get_user_by_id = AsyncMock(return_value=None)
        
        with patch('app.services.auth_service.verify_token') as mock_verify:
            mock_verify.return_value = mock_payload
            
            result = await auth_service.get_current_user_by_token(token)
            
            assert result is None
            mock_verify.assert_called_once_with(token)
            mock_user_repository.get_user_by_id.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_get_current_user_by_token_inactive_user(
        self, auth_service, test_user, mock_user_repository
    ):
        """Test getting current user by token when user is inactive."""
        token = "valid_token"
        test_user.is_active = False
        mock_payload = {"sub": str(test_user.id)}
        mock_user_repository.get_user_by_id = AsyncMock(return_value=test_user)
        
        with patch('app.services.auth_service.verify_token') as mock_verify:
            mock_verify.return_value = mock_payload
            
            result = await auth_service.get_current_user_by_token(token)
            
            assert result is None
            mock_verify.assert_called_once_with(token)
            mock_user_repository.get_user_by_id.assert_called_once_with(test_user.id)

    @pytest.mark.asyncio
    async def test_login_user_success(
        self, auth_service, user_login_data, test_user, mock_user_repository
    ):
        """Test successful user login."""
        mock_user_repository.get_user_by_email = AsyncMock(return_value=test_user)
        
        with patch('app.services.auth_service.verify_password') as mock_verify:
            mock_verify.return_value = True
            
            with patch('app.services.auth_service.create_access_token') as mock_create_token:
                mock_create_token.return_value = "test_token"
                
                result = await auth_service.login_user(user_login_data)
                
                assert isinstance(result, Token)
                assert result.access_token == "test_token"
                assert result.token_type == "bearer"

    @pytest.mark.asyncio
    async def test_login_user_invalid_credentials(
        self, auth_service, user_login_data, mock_user_repository
    ):
        """Test login with invalid credentials."""
        mock_user_repository.get_user_by_email = AsyncMock(return_value=None)
        
        with pytest.raises(AuthenticationError) as exc_info:
            await auth_service.login_user(user_login_data)
        
        assert "Incorrect email or password" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_refresh_access_token_success(
        self, auth_service, test_user, mock_user_repository
    ):
        """Test successful token refresh."""
        mock_user_repository.get_user_by_id = AsyncMock(return_value=test_user)
        
        with patch('app.services.auth_service.create_access_token') as mock_create_token:
            mock_create_token.return_value = "new_token"
            
            result = await auth_service.refresh_access_token(test_user)
            
            assert isinstance(result, Token)
            assert result.access_token == "new_token"
            assert result.token_type == "bearer"
            mock_user_repository.get_user_by_id.assert_called_once_with(test_user.id)

    @pytest.mark.asyncio
    async def test_refresh_access_token_inactive_user(
        self, auth_service, test_user, mock_user_repository
    ):
        """Test token refresh with inactive user."""
        test_user.is_active = False
        
        with pytest.raises(AuthenticationError) as exc_info:
            await auth_service.refresh_access_token(test_user)
        
        assert "User account is inactive" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_refresh_access_token_user_not_found(
        self, auth_service, test_user, mock_user_repository
    ):
        """Test token refresh when user not found in database."""
        mock_user_repository.get_user_by_id = AsyncMock(return_value=None)
        
        with pytest.raises(AuthenticationError) as exc_info:
            await auth_service.refresh_access_token(test_user)
        
        assert "User account is inactive or not found" in str(exc_info.value)
        mock_user_repository.get_user_by_id.assert_called_once_with(test_user.id)

    @pytest.mark.asyncio
    async def test_refresh_access_token_user_became_inactive(
        self, auth_service, test_user, mock_user_repository
    ):
        """Test token refresh when user became inactive."""
        inactive_user = User(
            id=test_user.id,
            username=test_user.username,
            email=test_user.email,
            hashed_password=test_user.hashed_password,
            is_active=False
        )
        mock_user_repository.get_user_by_id = AsyncMock(return_value=inactive_user)
        
        with pytest.raises(AuthenticationError) as exc_info:
            await auth_service.refresh_access_token(test_user)
        
        assert "User account is inactive or not found" in str(exc_info.value)
        mock_user_repository.get_user_by_id.assert_called_once_with(test_user.id)