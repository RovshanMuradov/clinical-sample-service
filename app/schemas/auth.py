import re
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, validator


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="User email address")

    @validator("username")
    def validate_username(cls, v):
        # Username must be alphanumeric with underscores/hyphens, start with letter
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", v):
            raise ValueError(
                "Username must start with a letter and contain only letters, numbers, underscores, and hyphens"
            )

        # Prevent common reserved words
        reserved_words = {"admin", "root", "user", "test", "guest", "api", "system"}
        if v.lower() in reserved_words:
            raise ValueError(f"Username '{v}' is reserved and cannot be used")

        return v.lower()

    @validator("email")
    def validate_email_domain(cls, v):
        # For clinical applications, we might want to restrict to certain domains
        # This is a business rule example
        allowed_domains = {
            "hospital.com",
            "clinic.org",
            "research.edu",
            "medical.gov",
            "example.com",
            "test.com",  # For testing
        }
        domain = v.split("@")[1].lower()
        if domain not in allowed_domains:
            raise ValueError(
                f"Email domain '{domain}' is not authorized for clinical data access"
            )
        return v.lower()


class UserCreate(UserBase):
    password: str = Field(
        ..., min_length=8, max_length=100, description="User password"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "username": "researcher_john",
                "email": "john.doe@research.edu",
                "password": "SecurePass123!",
            }
        }

    @validator("password")
    def validate_password(cls, v):
        # Enhanced password validation for clinical system
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")

        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")

        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")

        # Require at least one special character
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in v):
            raise ValueError("Password must contain at least one special character")

        # Check for common weak passwords
        weak_passwords = {
            "password",
            "password123",
            "12345678",
            "qwerty123",
            "admin123",
            "welcome123",
            "changeme",
        }
        if v.lower() in weak_passwords:
            raise ValueError(
                "Password is too common and weak. Please choose a stronger password"
            )

        # Check for sequential characters (basic check)
        if "123" in v or "abc" in v.lower() or "qwerty" in v.lower():
            raise ValueError("Password should not contain sequential characters")

        return v

    @validator("password")
    def validate_password_username_similarity(cls, v, values):
        # Ensure password is not too similar to username
        if "username" in values and values["username"]:
            username = values["username"].lower()
            if username in v.lower() or v.lower() in username:
                raise ValueError("Password should not be similar to username")
        return v


class UserUpdate(BaseModel):
    username: Optional[str] = Field(
        None, min_length=3, max_length=50, description="Username"
    )
    email: Optional[EmailStr] = Field(None, description="User email address")
    is_active: Optional[bool] = Field(
        None, description="Whether user account is active"
    )

    @validator("username")
    def validate_username(cls, v):
        if v is not None:
            # Username must be alphanumeric with underscores/hyphens, start with letter
            if not re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", v):
                raise ValueError(
                    "Username must start with a letter and contain only letters, numbers, underscores, and hyphens"
                )

            # Prevent common reserved words
            reserved_words = {"admin", "root", "user", "test", "guest", "api", "system"}
            if v.lower() in reserved_words:
                raise ValueError(f"Username '{v}' is reserved and cannot be used")

            return v.lower()
        return v

    @validator("email")
    def validate_email_domain(cls, v):
        if v is not None:
            # For clinical applications, we might want to restrict to certain domains
            allowed_domains = {
                "hospital.com",
                "clinic.org",
                "research.edu",
                "medical.gov",
                "example.com",
                "test.com",  # For testing
            }
            domain = v.split("@")[1].lower()
            if domain not in allowed_domains:
                raise ValueError(
                    f"Email domain '{domain}' is not authorized for clinical data access"
                )
            return v.lower()
        return v


class UserResponse(UserBase):
    id: UUID = Field(..., description="User unique identifier")
    is_active: bool = Field(..., description="Whether user account is active")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=1, description="User password")

    class Config:
        json_schema_extra = {
            "example": {"email": "john.doe@research.edu", "password": "SecurePass123!"}
        }

    @validator("email")
    def validate_email_format(cls, v):
        # Additional validation for login email
        if not v or len(v.strip()) == 0:
            raise ValueError("Email cannot be empty")
        return v.lower().strip()

    @validator("password")
    def validate_password_format(cls, v):
        # Basic validation for login password
        if not v or len(v.strip()) == 0:
            raise ValueError("Password cannot be empty")
        if len(v) > 100:  # Prevent extremely long passwords that might cause DoS
            raise ValueError("Password is too long")
        return v


class Token(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJqb2huLmRvZUByZXNlYXJjaC5lZHUiLCJleHAiOjE2NzAzMjgwMDB9.signature",
                "token_type": "bearer",
            }
        }


class TokenData(BaseModel):
    user_id: Optional[UUID] = Field(None, description="User ID from token")
    email: Optional[str] = Field(None, description="User email from token")


class UserInToken(BaseModel):
    id: UUID = Field(..., description="User unique identifier")
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., description="Username")
    is_active: bool = Field(..., description="Whether user account is active")

    class Config:
        from_attributes = True
