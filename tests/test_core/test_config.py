"""Tests for config utilities."""

import pytest
import os
from unittest.mock import patch, Mock
from pydantic import ValidationError

from app.core.config import Settings, get_settings


class TestSettings:
    """Test Settings class."""

    def test_settings_with_required_fields(self):
        """Test settings with required fields provided."""
        env_vars = {
            'DATABASE_URL': 'postgresql+asyncpg://user:pass@localhost/test',
            'SECRET_KEY': 'test-secret-key'
        }
        
        with patch.dict('os.environ', env_vars, clear=True):
            settings = Settings(_env_file=None)
            
            assert settings.database_url == 'postgresql+asyncpg://user:pass@localhost/test'
            assert settings.secret_key == 'test-secret-key'
            assert settings.app_name == "Clinical Sample Service"
            assert settings.app_version == "1.0.0"
            assert settings.debug is False
            assert settings.log_level == "INFO"
            assert settings.algorithm == "HS256"
            assert settings.access_token_expire_minutes == 30

    def test_validate_log_level_valid(self):
        """Test log level validation with valid values."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        for level in valid_levels:
            env_vars = {
                'DATABASE_URL': 'postgresql+asyncpg://user:pass@localhost/test',
                'SECRET_KEY': 'test-secret-key',
                'LOG_LEVEL': level
            }
            
            with patch.dict('os.environ', env_vars, clear=True):
                settings = Settings(_env_file=None)
                assert settings.log_level == level.upper()

    def test_validate_log_level_invalid(self):
        """Test log level validation with invalid values."""
        env_vars = {
            'DATABASE_URL': 'postgresql+asyncpg://user:pass@localhost/test',
            'SECRET_KEY': 'test-secret-key',
            'LOG_LEVEL': 'INVALID'
        }
        
        with patch.dict('os.environ', env_vars, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings(_env_file=None)
            
            assert "Log level must be one of" in str(exc_info.value)

    def test_validate_log_level_case_insensitive(self):
        """Test log level validation is case insensitive."""
        env_vars = {
            'DATABASE_URL': 'postgresql+asyncpg://user:pass@localhost/test',
            'SECRET_KEY': 'test-secret-key',
            'LOG_LEVEL': 'debug'
        }
        
        with patch.dict('os.environ', env_vars, clear=True):
            settings = Settings(_env_file=None)
            assert settings.log_level == 'DEBUG'

    def test_parse_cors_origins_from_list(self):
        """Test parsing CORS origins from list."""
        # Test the validator directly
        from app.core.config import Settings
        origins = ['http://localhost:3000', 'http://localhost:8080']
        parsed = Settings.parse_cors_origins(origins)
        assert parsed == origins

    def test_parse_cors_origins_from_string(self):
        """Test parsing CORS origins from comma-separated string."""
        from app.core.config import Settings
        origins_string = 'http://localhost:3000, http://localhost:8080, https://example.com'
        parsed = Settings.parse_cors_origins(origins_string)
        expected = ['http://localhost:3000', 'http://localhost:8080', 'https://example.com']
        assert parsed == expected

    def test_validate_database_url_valid(self):
        """Test database URL validation with valid asyncpg URL."""
        env_vars = {
            'DATABASE_URL': 'postgresql+asyncpg://user:pass@localhost:5432/testdb',
            'SECRET_KEY': 'test-secret-key'
        }
        
        with patch.dict('os.environ', env_vars, clear=True):
            settings = Settings(_env_file=None)
            assert settings.database_url == 'postgresql+asyncpg://user:pass@localhost:5432/testdb'

    def test_validate_database_url_invalid(self):
        """Test database URL validation with invalid URL."""
        env_vars = {
            'DATABASE_URL': 'postgresql://user:pass@localhost:5432/testdb',  # Missing asyncpg
            'SECRET_KEY': 'test-secret-key'
        }
        
        with patch.dict('os.environ', env_vars, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings(_env_file=None)
            
            assert "Database URL must use asyncpg driver" in str(exc_info.value)

    def test_validate_database_url_wrong_scheme(self):
        """Test database URL validation with wrong scheme."""
        env_vars = {
            'DATABASE_URL': 'mysql://user:pass@localhost:5432/testdb',
            'SECRET_KEY': 'test-secret-key'
        }
        
        with patch.dict('os.environ', env_vars, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings(_env_file=None)
            
            assert "Database URL must use asyncpg driver" in str(exc_info.value)

    def test_postgres_settings_optional(self):
        """Test that PostgreSQL settings are optional."""
        env_vars = {
            'DATABASE_URL': 'postgresql+asyncpg://user:pass@localhost/test',
            'SECRET_KEY': 'test-secret-key',
            'POSTGRES_USER': 'postgres',
            'POSTGRES_PASSWORD': 'password',
            'POSTGRES_DB': 'testdb'
        }
        
        with patch.dict('os.environ', env_vars, clear=True):
            settings = Settings(_env_file=None)
            assert settings.postgres_user == 'postgres'
            assert settings.postgres_password == 'password'
            assert settings.postgres_db == 'testdb'

    def test_numeric_settings_conversion(self):
        """Test that numeric settings are properly converted."""
        env_vars = {
            'DATABASE_URL': 'postgresql+asyncpg://user:pass@localhost/test',
            'SECRET_KEY': 'test-secret-key',
            'ACCESS_TOKEN_EXPIRE_MINUTES': '120',
            'RATE_LIMIT_PER_MINUTE': '200',
            'RATE_LIMIT_BURST': '30',
            'REQUEST_TIMEOUT_SECONDS': '60',
            'MAX_PAYLOAD_SIZE_MB': '50'
        }
        
        with patch.dict('os.environ', env_vars, clear=True):
            settings = Settings(_env_file=None)
            assert settings.access_token_expire_minutes == 120
            assert settings.rate_limit_per_minute == 200
            assert settings.rate_limit_burst == 30
            assert settings.request_timeout_seconds == 60
            assert settings.max_payload_size_mb == 50

    def test_boolean_settings_conversion(self):
        """Test that boolean settings are properly converted."""
        env_vars = {
            'DATABASE_URL': 'postgresql+asyncpg://user:pass@localhost/test',
            'SECRET_KEY': 'test-secret-key',
            'DEBUG': 'true',
            'ENABLE_HSTS': 'false'
        }
        
        with patch.dict('os.environ', env_vars, clear=True):
            settings = Settings(_env_file=None)
            assert settings.debug is True
            assert settings.enable_hsts is False


class TestGetSettings:
    """Test get_settings function."""

    def test_get_settings_returns_settings_instance(self):
        """Test that get_settings returns a Settings instance."""
        settings = get_settings()
        assert isinstance(settings, Settings)

    def test_get_settings_caching(self):
        """Test that get_settings returns consistent instances."""
        settings1 = get_settings()
        settings2 = get_settings()
        
        # They should be the same type
        assert type(settings1) == type(settings2)

    def test_settings_module_level_instance(self):
        """Test that the module-level settings instance is created."""
        from app.core.config import settings
        
        # The settings instance should exist
        assert settings is not None
        assert isinstance(settings, Settings)


class TestSettingsValidation:
    """Test settings validation edge cases."""

    def test_whitespace_cors_origins(self):
        """Test parsing CORS origins with whitespace."""
        from app.core.config import Settings
        origins_string = '  http://localhost:3000  ,  http://localhost:8080  '
        parsed = Settings.parse_cors_origins(origins_string)
        expected = ['http://localhost:3000', 'http://localhost:8080']
        assert parsed == expected

    def test_single_cors_origin(self):
        """Test parsing single CORS origin."""
        from app.core.config import Settings
        origins_string = 'http://localhost:3000'
        parsed = Settings.parse_cors_origins(origins_string)
        expected = ['http://localhost:3000']
        assert parsed == expected

    def test_case_sensitive_false(self):
        """Test that case sensitivity is disabled."""
        env_vars = {
            'database_url': 'postgresql+asyncpg://user:pass@localhost/test',  # lowercase
            'secret_key': 'test-secret-key',  # lowercase
            'app_name': 'Test App'  # lowercase
        }
        
        with patch.dict('os.environ', env_vars, clear=True):
            settings = Settings(_env_file=None)
            assert settings.database_url == 'postgresql+asyncpg://user:pass@localhost/test'
            assert settings.secret_key == 'test-secret-key'
            assert settings.app_name == 'Test App'