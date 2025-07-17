from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, validator


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="User email address")


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100, description="User password")
    
    @validator("password")
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter") 
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Username")
    email: Optional[EmailStr] = Field(None, description="User email address")
    is_active: Optional[bool] = Field(None, description="Whether user account is active")


class UserResponse(UserBase):
    id: str = Field(..., description="User unique identifier")
    is_active: bool = Field(..., description="Whether user account is active")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=1, description="User password")


class Token(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


class TokenData(BaseModel):
    user_id: Optional[str] = Field(None, description="User ID from token")
    email: Optional[str] = Field(None, description="User email from token")


class UserInToken(BaseModel):
    id: str = Field(..., description="User unique identifier")
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., description="Username")
    is_active: bool = Field(..., description="Whether user account is active")
    
    class Config:
        from_attributes = True