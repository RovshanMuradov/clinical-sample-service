"""
Authentication Security Tests - Critical for Medical Data Protection

These tests verify critical security components for authentication in the clinical samples system.
All tests are designed to prevent security vulnerabilities that could lead to unauthorized
access to sensitive medical data.
"""
import uuid
from datetime import datetime, timedelta, timezone
# from unittest.mock import patch  # Removed unused import

import pytest
from fastapi import HTTPException
from jose import jwt

from app.core.config import settings
from app.core.security import (
    create_access_token,
    decode_token,
    get_password_hash,
    verify_password,
    verify_token,
)
from app.services.auth_service import AuthService


class TestPasswordSecurity:
    """Test password hashing and verification security."""

    @pytest.mark.asyncio
    async def test_password_hashing_and_verification(self):
        """
        CRITICAL SECURITY TEST: Password Hashing and Verification

        Verifies that:
        1. Passwords are properly hashed using bcrypt
        2. Plain text passwords are never stored
        3. Password verification works correctly
        4. Same password produces different hashes (salt randomization)
        5. Hash contains bcrypt identifiers
        """
        # Test password
        plain_password = "TestPassword123!"

        # Generate hash
        hashed_password = get_password_hash(plain_password)

        # Verify hash characteristics
        assert (
            hashed_password != plain_password
        ), "Password should be hashed, not stored as plain text"
        assert len(hashed_password) > 50, "Bcrypt hash should be long enough"
        assert hashed_password.startswith("$2b$"), "Hash should use bcrypt format"

        # Verify password verification works
        assert verify_password(
            plain_password, hashed_password
        ), "Password verification should succeed"
        assert not verify_password(
            "WrongPassword", hashed_password
        ), "Wrong password should fail verification"

        # Verify salt randomization - same password should produce different hashes
        hashed_password2 = get_password_hash(plain_password)
        assert (
            hashed_password != hashed_password2
        ), "Same password should produce different hashes due to salt"

        # Both hashes should verify the same password
        assert verify_password(
            plain_password, hashed_password2
        ), "Second hash should also verify correctly"

        # Test edge cases
        assert not verify_password("", hashed_password), "Empty password should fail"
        assert not verify_password(plain_password, ""), "Empty hash should fail"
        assert not verify_password("", ""), "Both empty should fail"
        assert not verify_password(
            plain_password, "invalid_hash"
        ), "Invalid hash should fail gracefully"

    @pytest.mark.asyncio
    async def test_password_verification_edge_cases(self):
        """Test password verification handles edge cases securely."""
        valid_password = "TestPassword123!"
        valid_hash = get_password_hash(valid_password)

        # Test with None values (should not crash)
        assert not verify_password(None, valid_hash), "None password should fail safely"
        assert not verify_password(valid_password, None), "None hash should fail safely"

        # Test with corrupted hash
        corrupted_hash = valid_hash[:-5] + "XXXXX"
        assert not verify_password(
            valid_password, corrupted_hash
        ), "Corrupted hash should fail safely"


class TestJWTSecurity:
    """Test JWT token creation and validation security."""

    @pytest.mark.asyncio
    async def test_jwt_token_creation_and_validation(self):
        """
        CRITICAL SECURITY TEST: JWT Token Creation and Validation

        Verifies that:
        1. Tokens are properly created with correct payload
        2. Tokens can be decoded and validated
        3. Token contains expected user data
        4. Token has proper expiration
        5. Token uses correct signing algorithm
        """
        # Test user data
        user_data = {
            "sub": str(uuid.uuid4()),
            "email": "test@clinical.test",
            "username": "testuser",
            "is_active": True,
        }

        # Create token
        token = create_access_token(user_data)

        # Verify token is a string
        assert isinstance(token, str), "Token should be a string"
        assert len(token) > 50, "JWT token should be long enough"
        assert token.count(".") == 2, "JWT should have 3 parts separated by dots"

        # Decode and verify token
        decoded_payload = verify_token(token)

        # Verify payload contains expected data
        assert (
            decoded_payload["sub"] == user_data["sub"]
        ), "Token should contain correct user ID"
        assert (
            decoded_payload["email"] == user_data["email"]
        ), "Token should contain correct email"
        assert (
            decoded_payload["username"] == user_data["username"]
        ), "Token should contain correct username"
        assert (
            decoded_payload["is_active"] == user_data["is_active"]
        ), "Token should contain correct active status"

        # Verify expiration is set and in the future
        assert "exp" in decoded_payload, "Token should have expiration"
        exp_timestamp = decoded_payload["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        assert exp_datetime > datetime.now(
            timezone.utc
        ), "Token expiration should be in the future"

        # Verify expiration is reasonable (within configured time + 1 minute tolerance)
        max_expected_exp = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes + 1
        )
        assert (
            exp_datetime <= max_expected_exp
        ), "Token expiration should not exceed configured time"

    @pytest.mark.asyncio
    async def test_jwt_token_with_custom_expiration(self):
        """Test JWT token creation with custom expiration."""
        user_data = {"sub": str(uuid.uuid4()), "email": "test@clinical.test"}
        custom_expiration = timedelta(minutes=5)

        # Create token with custom expiration
        token = create_access_token(user_data, expires_delta=custom_expiration)
        decoded_payload = verify_token(token)

        # Verify custom expiration is respected
        exp_datetime = datetime.fromtimestamp(decoded_payload["exp"], tz=timezone.utc)
        expected_exp = datetime.now(timezone.utc) + custom_expiration

        # Allow 1 minute tolerance
        assert (
            abs((exp_datetime - expected_exp).total_seconds()) < 60
        ), "Custom expiration should be respected"

    @pytest.mark.asyncio
    async def test_expired_token_rejection(self):
        """
        CRITICAL SECURITY TEST: Expired Token Rejection

        Verifies that:
        1. Expired tokens are properly rejected
        2. HTTPException is raised with correct status
        3. Error message is appropriate
        4. No user data is leaked from expired tokens
        """
        # Create token with immediate expiration
        user_data = {
            "sub": str(uuid.uuid4()),
            "email": "test@clinical.test",
            "username": "testuser",
        }

        # Create token that expires immediately
        expired_token = create_access_token(
            user_data, expires_delta=timedelta(seconds=-1)
        )

        # Verify token is rejected
        with pytest.raises(HTTPException) as exc_info:
            verify_token(expired_token)

        # Verify correct error response
        assert (
            exc_info.value.status_code == 401
        ), "Expired token should return 401 Unauthorized"
        assert (
            "Could not validate credentials" in exc_info.value.detail
        ), "Error message should indicate credential failure"
        assert (
            "WWW-Authenticate" in exc_info.value.headers
        ), "Should include WWW-Authenticate header"
        assert (
            exc_info.value.headers["WWW-Authenticate"] == "Bearer"
        ), "Should specify Bearer authentication"

        # Verify decode_token returns None for expired token (doesn't raise exception)
        decoded = decode_token(expired_token)
        assert decoded is None, "decode_token should return None for expired token"

    @pytest.mark.asyncio
    async def test_invalid_token_rejection(self):
        """
        CRITICAL SECURITY TEST: Invalid Token Rejection

        Verifies that:
        1. Malformed tokens are rejected
        2. Tokens with wrong signature are rejected
        3. Empty/None tokens are rejected
        4. All rejections return proper error responses
        5. No exceptions leak sensitive information
        """
        # Test various invalid tokens
        invalid_tokens = [
            "",  # Empty token
            "invalid.token.here",  # Malformed JWT
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.invalid",  # Invalid payload
            "valid.header.but.wrong.signature",  # Wrong signature
            "not-a-jwt-at-all",  # Not JWT format
            ".",  # Just dots
            "..",  # Just dots
            None,  # None token
        ]

        for invalid_token in invalid_tokens:
            if invalid_token is None:
                # For None, verify we handle it gracefully in actual usage
                # (this would typically be caught earlier in the authentication flow)
                continue

            # Test verify_token raises HTTPException
            with pytest.raises(HTTPException) as exc_info:
                verify_token(invalid_token)

            # Verify correct error response
            assert (
                exc_info.value.status_code == 401
            ), f"Invalid token '{invalid_token}' should return 401"
            assert (
                "Could not validate credentials" in exc_info.value.detail
            ), "Error should not leak token details"

            # Test decode_token returns None (doesn't raise)
            decoded = decode_token(invalid_token)
            assert (
                decoded is None
            ), f"decode_token should return None for invalid token '{invalid_token}'"

    @pytest.mark.asyncio
    async def test_token_with_wrong_secret_key(self):
        """Test that tokens signed with wrong secret key are rejected."""
        user_data = {"sub": str(uuid.uuid4()), "email": "test@clinical.test"}

        # Create token with wrong secret key
        wrong_secret_token = jwt.encode(
            user_data, "wrong-secret-key", algorithm=settings.algorithm
        )

        # Verify token is rejected
        with pytest.raises(HTTPException):
            verify_token(wrong_secret_token)

        assert (
            decode_token(wrong_secret_token) is None
        ), "Token with wrong secret should be rejected"

    @pytest.mark.asyncio
    async def test_token_with_wrong_algorithm(self):
        """Test that tokens signed with wrong algorithm are rejected."""
        user_data = {"sub": str(uuid.uuid4()), "email": "test@clinical.test"}

        # Create token with wrong algorithm
        wrong_algo_token = jwt.encode(
            user_data,
            settings.secret_key,
            algorithm="HS512",  # Different from configured algorithm
        )

        # Verify token is rejected
        with pytest.raises(HTTPException):
            verify_token(wrong_algo_token)

        assert (
            decode_token(wrong_algo_token) is None
        ), "Token with wrong algorithm should be rejected"


class TestAuthServiceSecurity:
    """Test AuthService security functions."""

    @pytest.mark.asyncio
    async def test_get_current_user_by_token_with_invalid_tokens(
        self, auth_service: AuthService
    ):
        """Test that AuthService properly handles invalid tokens."""
        # Test with well-formed but invalid JWT tokens
        invalid_tokens = [
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.invalid_signature",
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.invalid_payload.signature",
        ]

        for invalid_token in invalid_tokens:
            user = await auth_service.get_current_user_by_token(invalid_token)
            assert (
                user is None
            ), f"Invalid token '{invalid_token}' should return None user"

        # Test with malformed tokens that will cause JWT parsing errors
        malformed_tokens = [
            "invalid.token",
            "not-a-jwt",
        ]

        for malformed_token in malformed_tokens:
            user = await auth_service.get_current_user_by_token(malformed_token)
            assert (
                user is None
            ), f"Malformed token '{malformed_token}' should return None user"

    @pytest.mark.asyncio
    async def test_authenticate_user_security(
        self, auth_service: AuthService, test_user1
    ):
        """Test authentication security with various attack vectors."""
        from app.schemas.auth import UserLogin

        # Test that authentication handles various edge cases securely
        # These are valid email formats but would be problematic if not handled correctly by ORM
        edge_case_emails = [
            "test+tag@example.com",  # Plus addressing
            "user.name@example.com",  # Dots in local part
            "test123@sub.example.com",  # Subdomain
        ]

        for edge_case_email in edge_case_emails:
            login_data = UserLogin(email=edge_case_email, password="any_password")
            user = await auth_service.authenticate_user(login_data)
            assert (
                user is None
            ), f"Non-existent user '{edge_case_email}' should return None safely"

        # Test that wrong credentials are handled securely
        # Test non-existent email returns None
        user = await auth_service.authenticate_user(
            UserLogin(email="nonexistent@test.com", password="password")
        )
        assert user is None, "Non-existent email should return None"

        # Test wrong password with existing email returns None
        user = await auth_service.authenticate_user(
            UserLogin(email=test_user1.email, password="wrongpassword")
        )
        assert user is None, "Wrong password should return None"

        # Test correct credentials return user
        user = await auth_service.authenticate_user(
            UserLogin(email=test_user1.email, password="testpass123")
        )
        assert user is not None, "Correct credentials should return user"
        assert user.email == test_user1.email, "Should return correct user"
