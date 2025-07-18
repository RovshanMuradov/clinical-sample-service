"""
Authentication Business Logic Tests

These tests verify core authentication business logic for the clinical samples system.
They ensure proper validation of user registration, duplicate prevention, and login security.
"""
import pytest

from app.core.exceptions import AuthenticationError, ConflictError
from app.schemas.auth import UserCreate, UserLogin
from app.services.auth_service import AuthService


class TestAuthenticationBusinessLogic:
    """Test authentication business logic and validation."""

    @pytest.mark.asyncio
    async def test_duplicate_email_registration_blocked(self, auth_service: AuthService):
        """
        Test that attempting to register with an existing email is blocked.
        
        Business Rule: Email addresses must be unique across all users.
        Expected: ConflictError should be raised when trying to register 
                 with an already existing email address.
        """
        # Create first user with email
        user_data_1 = UserCreate(
            username="user1",
            email="test@test.com",
            password="TestPass456$"
        )
        
        # Register first user successfully
        first_user = await auth_service.register_user(user_data_1)
        assert first_user is not None
        assert first_user.email == "test@test.com"
        assert first_user.username == "user1"
        
        # Attempt to register second user with same email but different username
        user_data_2 = UserCreate(
            username="user2",  # Different username
            email="test@test.com",  # Same email - should conflict
            password="AnotherPass789#"
        )
        
        # Should raise ConflictError due to duplicate email
        with pytest.raises(ConflictError) as exc_info:
            await auth_service.register_user(user_data_2)
        
        # Verify error details
        assert exc_info.value.status_code == 409
        assert "email already exists or conflicts with existing data" in exc_info.value.message
        assert exc_info.value.details["email"] == "test@test.com"

    @pytest.mark.asyncio
    async def test_duplicate_username_registration_blocked(self, auth_service: AuthService):
        """
        Test that attempting to register with an existing username is blocked.
        
        Business Rule: Usernames must be unique across all users.
        Expected: ConflictError should be raised when trying to register 
                 with an already existing username.
        """
        # Create first user with username
        user_data_1 = UserCreate(
            username="testuser",
            email="user1@test.com",
            password="TestPass456$"
        )
        
        # Register first user successfully
        first_user = await auth_service.register_user(user_data_1)
        assert first_user is not None
        assert first_user.username == "testuser"
        assert first_user.email == "user1@test.com"
        
        # Attempt to register second user with same username but different email
        user_data_2 = UserCreate(
            username="testuser",  # Same username - should conflict
            email="user2@test.com",  # Different email
            password="AnotherPass789#"
        )
        
        # Should raise ConflictError due to duplicate username
        with pytest.raises(ConflictError) as exc_info:
            await auth_service.register_user(user_data_2)
        
        # Verify error details
        assert exc_info.value.status_code == 409
        assert "username already exists or conflicts with existing data" in exc_info.value.message
        assert exc_info.value.details["username"] == "testuser"

    @pytest.mark.asyncio
    async def test_login_with_wrong_password_fails(self, auth_service: AuthService):
        """
        Test that login fails when using wrong password.
        
        Business Rule: Users can only authenticate with correct credentials.
        Expected: AuthenticationError should be raised when attempting 
                 to login with incorrect password.
        """
        # Create and register user
        user_data = UserCreate(
            username="logintest",
            email="login@test.com",
            password="CorrectPass456$"
        )
        
        registered_user = await auth_service.register_user(user_data)
        assert registered_user is not None
        assert registered_user.email == "login@test.com"
        
        # Attempt to login with wrong password
        login_data = UserLogin(
            email="login@test.com",
            password="WrongPassword789#"  # Incorrect password
        )
        
        # Should raise AuthenticationError due to wrong password
        with pytest.raises(AuthenticationError) as exc_info:
            await auth_service.login_user(login_data)
        
        # Verify error details
        assert exc_info.value.status_code == 401
        assert "Incorrect email or password" in exc_info.value.message
        assert exc_info.value.details["email"] == "login@test.com"
        
        # Verify that authenticate_user returns None for wrong password
        authenticated_user = await auth_service.authenticate_user(login_data)
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_inactive_user_cannot_login(self, auth_service: AuthService, user_repository):
        """
        Test that inactive users cannot login even with correct credentials.
        
        Business Rule: Only active users should be able to authenticate.
        Expected: AuthenticationError should be raised when inactive user 
                 attempts to login, even with correct credentials.
        """
        # Create inactive user directly in repository (bypassing service validation)
        from app.core.security import get_password_hash
        
        user_data = {
            "username": "inactiveuser",
            "email": "inactive@test.com",
            "hashed_password": get_password_hash("TestPass456$"),
            "is_active": False  # User is inactive
        }
        
        # Create inactive user in repository
        inactive_user = await user_repository.create_user(user_data)
        assert inactive_user is not None
        assert inactive_user.is_active is False
        
        # Attempt to login with correct credentials but inactive account
        login_data = UserLogin(
            email="inactive@test.com",
            password="TestPass456$"  # Correct password
        )
        
        # Should raise AuthenticationError due to inactive account
        with pytest.raises(AuthenticationError) as exc_info:
            await auth_service.login_user(login_data)
        
        # Verify error details
        assert exc_info.value.status_code == 401
        assert "Incorrect email or password" in exc_info.value.message
        assert exc_info.value.details["email"] == "inactive@test.com"
        
        # Verify that authenticate_user returns None for inactive user
        authenticated_user = await auth_service.authenticate_user(login_data)
        assert authenticated_user is None
        
        # Verify that password itself would be valid (if user was active)
        from app.core.security import verify_password
        assert verify_password("TestPass456$", inactive_user.hashed_password) is True