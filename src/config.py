"""
Configuration settings for Lambda deployment.
"""

import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings optimized for Lambda."""
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "")
    
    # JWT
    jwt_secret: str = os.getenv("JWT_SECRET", "")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Application
    app_name: str = "Clinical Sample Service"
    app_version: str = "1.0.0"
    debug: bool = False  # Always False in Lambda
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Lambda-specific settings
    environment: str = "lambda"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create settings instance
settings = Settings()