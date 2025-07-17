"""Tests for security utilities."""

import pytest
from unittest.mock import patch, Mock
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException

from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    verify_token,
    decode_token,
    get_user_id_from_token
)


class TestPasswordFunctions:
    """Test password hashing and verification functions."""

    def test_get_password_hash_returns_string(self):
        """Test that password hashing returns a string."""
        password = "test_password"
        
        result = get_password_hash(password)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert result != password  # Should be hashed, not plain text

    def test_get_password_hash_different_passwords_different_hashes(self):
        """Test that different passwords produce different hashes."""
        password1 = "password1"
        password2 = "password2"
        
        hash1 = get_password_hash(password1)
        hash2 = get_password_hash(password2)
        
        assert hash1 != hash2

    def test_get_password_hash_same_password_different_hashes(self):
        """Test that same password produces different hashes (due to salt)."""
        password = "test_password"
        
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # bcrypt uses salt, so same password should produce different hashes
        assert hash1 != hash2

    def test_verify_password_correct_password(self):
        """Test password verification with correct password."""
        password = "test_password"
        hashed_password = get_password_hash(password)
        
        result = verify_password(password, hashed_password)
        
        assert result is True

    def test_verify_password_incorrect_password(self):
        """Test password verification with incorrect password."""
        correct_password = "test_password"
        incorrect_password = "wrong_password"
        hashed_password = get_password_hash(correct_password)
        
        result = verify_password(incorrect_password, hashed_password)
        
        assert result is False

    def test_verify_password_empty_password(self):
        """Test password verification with empty password."""
        password = "test_password"
        hashed_password = get_password_hash(password)
        
        result = verify_password("", hashed_password)
        
        assert result is False

    def test_verify_password_empty_hash(self):
        """Test password verification with empty hash."""
        password = "test_password"
        
        result = verify_password(password, "")
        
        assert result is False

    def test_verify_password_none_hash(self):
        """Test password verification with None hash."""
        password = "test_password"
        
        result = verify_password(password, None)
        
        assert result is False

    def test_verify_password_invalid_hash_format(self):
        """Test password verification with invalid hash format."""
        password = "test_password"
        invalid_hash = "invalid_hash_format"
        
        result = verify_password(password, invalid_hash)
        
        assert result is False

    def test_password_hash_bcrypt_format(self):
        """Test that password hash follows bcrypt format."""
        password = "test_password"
        
        hashed = get_password_hash(password)
        
        # bcrypt hashes start with $2b$
        assert hashed.startswith("$2b$")
        assert len(hashed) == 60  # bcrypt hashes are 60 characters long

    @patch('app.core.security.pwd_context.hash')
    def test_get_password_hash_calls_bcrypt(self, mock_hash):
        """Test that get_password_hash calls bcrypt hash function."""
        password = "test_password"
        mock_hash.return_value = "mocked_hash"
        
        result = get_password_hash(password)
        
        mock_hash.assert_called_once_with(password)
        assert result == "mocked_hash"

    @patch('app.core.security.pwd_context.verify')
    def test_verify_password_calls_bcrypt(self, mock_verify):
        """Test that verify_password calls bcrypt verify function."""
        password = "test_password"
        hashed = "hashed_password"
        mock_verify.return_value = True
        
        result = verify_password(password, hashed)
        
        mock_verify.assert_called_once_with(password, hashed)
        assert result is True


class TestJWTFunctions:
    """Test JWT token functions."""

    @pytest.fixture
    def mock_settings(self):
        """Mock settings for testing."""
        with patch('app.core.security.settings') as mock_settings:
            mock_settings.secret_key = "test_secret_key"
            mock_settings.algorithm = "HS256"
            mock_settings.access_token_expire_minutes = 30
            yield mock_settings

    @pytest.fixture
    def test_token_data(self):
        """Test token data."""
        return {
            "sub": "test_user_id",
            "email": "test@example.com",
            "username": "testuser",
            "is_active": True
        }

    def test_create_access_token_with_default_expiration(self, mock_settings, test_token_data):
        """Test JWT token creation with default expiration."""
        with patch('app.core.security.jwt.encode') as mock_encode:
            mock_encode.return_value = "test_token"
            
            result = create_access_token(test_token_data)
            
            assert result == "test_token"
            mock_encode.assert_called_once()
            
            # Check the call arguments
            call_args = mock_encode.call_args
            encoded_data = call_args[0][0]
            secret_key = call_args[0][1]
            algorithm = call_args[1]['algorithm']
            
            assert encoded_data["sub"] == test_token_data["sub"]
            assert encoded_data["email"] == test_token_data["email"]
            assert encoded_data["username"] == test_token_data["username"]
            assert encoded_data["is_active"] == test_token_data["is_active"]
            assert "exp" in encoded_data
            assert secret_key == mock_settings.secret_key
            assert algorithm == mock_settings.algorithm

    def test_create_access_token_with_custom_expiration(self, mock_settings, test_token_data):
        """Test JWT token creation with custom expiration."""
        custom_expiration = timedelta(minutes=60)
        
        with patch('app.core.security.jwt.encode') as mock_encode:
            mock_encode.return_value = "test_token"
            
            result = create_access_token(test_token_data, custom_expiration)
            
            assert result == "test_token"
            mock_encode.assert_called_once()
            
            # Check that custom expiration was used
            call_args = mock_encode.call_args
            encoded_data = call_args[0][0]
            assert "exp" in encoded_data

    def test_create_access_token_preserves_original_data(self, mock_settings, test_token_data):
        """Test that token creation doesn't modify original data."""
        original_data = test_token_data.copy()
        
        with patch('app.core.security.jwt.encode') as mock_encode:
            mock_encode.return_value = "test_token"
            
            create_access_token(test_token_data)
            
            # Original data should be unchanged
            assert test_token_data == original_data

    def test_verify_token_valid_token(self, mock_settings):
        """Test token verification with valid token."""
        token = "valid_token"
        expected_payload = {"sub": "test_user_id", "exp": 1234567890}
        
        with patch('app.core.security.jwt.decode') as mock_decode:
            mock_decode.return_value = expected_payload
            
            result = verify_token(token)
            
            assert result == expected_payload
            mock_decode.assert_called_once_with(
                token, mock_settings.secret_key, algorithms=[mock_settings.algorithm]
            )

    def test_verify_token_invalid_token(self, mock_settings):
        """Test token verification with invalid token."""
        token = "invalid_token"
        
        with patch('app.core.security.jwt.decode') as mock_decode:
            from jose import JWTError
            mock_decode.side_effect = JWTError("Invalid token")
            
            with pytest.raises(HTTPException) as exc_info:
                verify_token(token)
            
            assert exc_info.value.status_code == 401
            assert "Could not validate credentials" in str(exc_info.value.detail)
            assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}

    def test_verify_token_expired_token(self, mock_settings):
        """Test token verification with expired token."""
        token = "expired_token"
        
        with patch('app.core.security.jwt.decode') as mock_decode:
            from jose import JWTError
            mock_decode.side_effect = JWTError("Token expired")
            
            with pytest.raises(HTTPException) as exc_info:
                verify_token(token)
            
            assert exc_info.value.status_code == 401

    def test_decode_token_valid_token(self, mock_settings):
        """Test token decoding with valid token."""
        token = "valid_token"
        expected_payload = {"sub": "test_user_id", "exp": 1234567890}
        
        with patch('app.core.security.jwt.decode') as mock_decode:
            mock_decode.return_value = expected_payload
            
            result = decode_token(token)
            
            assert result == expected_payload
            mock_decode.assert_called_once_with(
                token, mock_settings.secret_key, algorithms=[mock_settings.algorithm]
            )

    def test_decode_token_invalid_token(self, mock_settings):
        """Test token decoding with invalid token."""
        token = "invalid_token"
        
        with patch('app.core.security.jwt.decode') as mock_decode:
            from jose import JWTError
            mock_decode.side_effect = JWTError("Invalid token")
            
            result = decode_token(token)
            
            assert result is None

    def test_get_user_id_from_token_valid_token(self, mock_settings):
        """Test extracting user ID from valid token."""
        token = "valid_token"
        user_id = "test_user_id"
        payload = {"sub": user_id, "exp": 1234567890}
        
        with patch('app.core.security.decode_token') as mock_decode:
            mock_decode.return_value = payload
            
            result = get_user_id_from_token(token)
            
            assert result == user_id
            mock_decode.assert_called_once_with(token)

    def test_get_user_id_from_token_no_sub(self, mock_settings):
        """Test extracting user ID from token without sub claim."""
        token = "token_without_sub"
        payload = {"email": "test@example.com", "exp": 1234567890}
        
        with patch('app.core.security.decode_token') as mock_decode:
            mock_decode.return_value = payload
            
            result = get_user_id_from_token(token)
            
            assert result is None
            mock_decode.assert_called_once_with(token)

    def test_get_user_id_from_token_invalid_token(self, mock_settings):
        """Test extracting user ID from invalid token."""
        token = "invalid_token"
        
        with patch('app.core.security.decode_token') as mock_decode:
            mock_decode.return_value = None
            
            result = get_user_id_from_token(token)
            
            assert result is None
            mock_decode.assert_called_once_with(token)

    def test_create_access_token_expiration_calculation(self, mock_settings, test_token_data):
        """Test that token expiration is calculated correctly."""
        with patch('app.core.security.datetime') as mock_datetime:
            mock_now = datetime(2023, 12, 1, 12, 0, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = mock_now
            
            with patch('app.core.security.jwt.encode') as mock_encode:
                mock_encode.return_value = "test_token"
                
                create_access_token(test_token_data)
                
                # Check that the expiration was calculated correctly
                call_args = mock_encode.call_args
                encoded_data = call_args[0][0]
                expected_exp = mock_now + timedelta(minutes=mock_settings.access_token_expire_minutes)
                
                assert encoded_data["exp"] == expected_exp

    def test_create_access_token_with_custom_expiration_calculation(self, mock_settings, test_token_data):
        """Test that custom expiration is calculated correctly."""
        custom_delta = timedelta(minutes=120)
        
        with patch('app.core.security.datetime') as mock_datetime:
            mock_now = datetime(2023, 12, 1, 12, 0, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = mock_now
            
            with patch('app.core.security.jwt.encode') as mock_encode:
                mock_encode.return_value = "test_token"
                
                create_access_token(test_token_data, custom_delta)
                
                # Check that the custom expiration was used
                call_args = mock_encode.call_args
                encoded_data = call_args[0][0]
                expected_exp = mock_now + custom_delta
                
                assert encoded_data["exp"] == expected_exp

    def test_jwt_encode_decode_integration(self, mock_settings):
        """Test JWT encode/decode integration."""
        # This test uses actual JWT encoding/decoding without mocking
        test_data = {
            "sub": "test_user_id",
            "email": "test@example.com",
            "username": "testuser"
        }
        
        # Create token
        token = create_access_token(test_data)
        
        # Verify token
        decoded_payload = verify_token(token)
        
        # Check that essential data is preserved
        assert decoded_payload["sub"] == test_data["sub"]
        assert decoded_payload["email"] == test_data["email"]
        assert decoded_payload["username"] == test_data["username"]
        assert "exp" in decoded_payload

    def test_jwt_decode_without_exception_integration(self, mock_settings):
        """Test JWT decode without exception integration."""
        test_data = {
            "sub": "test_user_id",
            "email": "test@example.com"
        }
        
        # Create token
        token = create_access_token(test_data)
        
        # Decode token without exception
        decoded_payload = decode_token(token)
        
        # Check that data is preserved
        assert decoded_payload["sub"] == test_data["sub"]
        assert decoded_payload["email"] == test_data["email"]
        assert "exp" in decoded_payload

    def test_get_user_id_from_token_integration(self, mock_settings):
        """Test get_user_id_from_token integration."""
        user_id = "test_user_id_123"
        test_data = {
            "sub": user_id,
            "email": "test@example.com"
        }
        
        # Create token
        token = create_access_token(test_data)
        
        # Extract user ID
        extracted_user_id = get_user_id_from_token(token)
        
        assert extracted_user_id == user_id

    def test_token_algorithms_configuration(self, mock_settings):
        """Test that token algorithms are properly configured."""
        test_data = {"sub": "test_user"}
        
        with patch('app.core.security.jwt.encode') as mock_encode:
            mock_encode.return_value = "test_token"
            
            create_access_token(test_data)
            
            # Check that algorithm from settings is used
            call_args = mock_encode.call_args
            algorithm = call_args[1]['algorithm']
            assert algorithm == mock_settings.algorithm

    def test_token_secret_key_configuration(self, mock_settings):
        """Test that token secret key is properly configured."""
        test_data = {"sub": "test_user"}
        
        with patch('app.core.security.jwt.encode') as mock_encode:
            mock_encode.return_value = "test_token"
            
            create_access_token(test_data)
            
            # Check that secret key from settings is used
            call_args = mock_encode.call_args
            secret_key = call_args[0][1]
            assert secret_key == mock_settings.secret_key

    def test_verify_token_uses_correct_algorithm(self, mock_settings):
        """Test that token verification uses correct algorithm."""
        token = "test_token"
        
        with patch('app.core.security.jwt.decode') as mock_decode:
            mock_decode.return_value = {"sub": "test_user"}
            
            verify_token(token)
            
            # Check that correct algorithm is used
            call_args = mock_decode.call_args
            algorithms = call_args[1]['algorithms']
            assert algorithms == [mock_settings.algorithm]

    def test_decode_token_uses_correct_algorithm(self, mock_settings):
        """Test that token decoding uses correct algorithm."""
        token = "test_token"
        
        with patch('app.core.security.jwt.decode') as mock_decode:
            mock_decode.return_value = {"sub": "test_user"}
            
            decode_token(token)
            
            # Check that correct algorithm is used
            call_args = mock_decode.call_args
            algorithms = call_args[1]['algorithms']
            assert algorithms == [mock_settings.algorithm]