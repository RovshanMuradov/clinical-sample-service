"""
API routes for Lambda deployment.
"""

import os
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

import bcrypt
import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from config import settings
from exceptions import AuthenticationError, NotFoundError, ValidationError
from models import Sample, SampleStatus, SampleType, User, get_db

# Security
security = HTTPBearer()

# Create API router
api_router = APIRouter()

# Pydantic schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class SampleCreate(BaseModel):
    sample_type: SampleType
    subject_id: str
    collection_date: datetime
    status: SampleStatus = SampleStatus.COLLECTED
    storage_location: Optional[str] = None
    notes: Optional[str] = None

class SampleResponse(BaseModel):
    id: UUID
    sample_type: SampleType
    subject_id: str
    collection_date: datetime
    status: SampleStatus
    storage_location: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Auth utilities
def hash_password(password: str) -> str:
    """Hash a password."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(user_id: str) -> str:
    """Create JWT token."""
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user."""
    try:
        payload = jwt.decode(
            credentials.credentials, 
            settings.jwt_secret, 
            algorithms=[settings.jwt_algorithm]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise AuthenticationError("Invalid token")
        
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise AuthenticationError("User not found")
        
        return user
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token expired")
    except jwt.JWTError:
        raise AuthenticationError("Invalid token")

# Auth routes
@api_router.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise ValidationError("Email already registered")
    
    # Create user
    hashed_password = hash_password(user_data.password)
    user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create token
    access_token = create_access_token(str(user.id))
    return {"access_token": access_token, "token_type": "bearer"}

@api_router.post("/auth/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login user."""
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise AuthenticationError("Invalid credentials")
    
    access_token = create_access_token(str(user.id))
    return {"access_token": access_token, "token_type": "bearer"}

# Sample routes
@api_router.post("/samples", response_model=SampleResponse)
async def create_sample(
    sample_data: SampleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new sample."""
    sample = Sample(
        sample_type=sample_data.sample_type,
        subject_id=sample_data.subject_id,
        collection_date=sample_data.collection_date,
        status=sample_data.status,
        storage_location=sample_data.storage_location,
        notes=sample_data.notes,
        user_id=current_user.id,
    )
    db.add(sample)
    db.commit()
    db.refresh(sample)
    return sample

@api_router.get("/samples", response_model=List[SampleResponse])
async def list_samples(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    sample_type: Optional[SampleType] = None,
    status: Optional[SampleStatus] = None,
    subject_id: Optional[str] = None,
):
    """List user's samples with optional filters."""
    query = db.query(Sample).filter(Sample.user_id == current_user.id)
    
    if sample_type:
        query = query.filter(Sample.sample_type == sample_type)
    if status:
        query = query.filter(Sample.status == status)
    if subject_id:
        query = query.filter(Sample.subject_id.ilike(f"%{subject_id}%"))
    
    return query.all()

@api_router.get("/samples/{sample_id}", response_model=SampleResponse)
async def get_sample(
    sample_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific sample."""
    sample = db.query(Sample).filter(
        Sample.id == sample_id,
        Sample.user_id == current_user.id
    ).first()
    
    if not sample:
        raise NotFoundError("Sample not found")
    
    return sample

@api_router.put("/samples/{sample_id}", response_model=SampleResponse)
async def update_sample(
    sample_id: UUID,
    sample_data: SampleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a sample."""
    sample = db.query(Sample).filter(
        Sample.id == sample_id,
        Sample.user_id == current_user.id
    ).first()
    
    if not sample:
        raise NotFoundError("Sample not found")
    
    # Update fields
    sample.sample_type = sample_data.sample_type
    sample.subject_id = sample_data.subject_id
    sample.collection_date = sample_data.collection_date
    sample.status = sample_data.status
    sample.storage_location = sample_data.storage_location
    sample.notes = sample_data.notes
    sample.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(sample)
    return sample

@api_router.delete("/samples/{sample_id}")
async def delete_sample(
    sample_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a sample."""
    sample = db.query(Sample).filter(
        Sample.id == sample_id,
        Sample.user_id == current_user.id
    ).first()
    
    if not sample:
        raise NotFoundError("Sample not found")
    
    db.delete(sample)
    db.commit()
    return {"message": "Sample deleted successfully"}