"""
SQLAlchemy models for Lambda deployment.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Column,
    DateTime,
    Enum as SQLEnum,
    String,
    Text,
    create_engine,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import settings

# Convert asyncpg URL to psycopg2 URL for Lambda
database_url = settings.database_url.replace("postgresql+asyncpg://", "postgresql://")

# Create database engine (synchronous for Lambda)
engine = create_engine(
    database_url,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


class SampleType(str, Enum):
    """Sample type enumeration."""
    BLOOD = "blood"
    SALIVA = "saliva"
    TISSUE = "tissue"


class SampleStatus(str, Enum):
    """Sample status enumeration."""
    COLLECTED = "collected"
    PROCESSING = "processing"
    ARCHIVED = "archived"


class User(Base):
    """User model."""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(String(10), default="true")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Sample(Base):
    """Sample model."""
    __tablename__ = "samples"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sample_type = Column(SQLEnum(SampleType), nullable=False)
    subject_id = Column(String(50), nullable=False, index=True)
    collection_date = Column(DateTime, nullable=False)
    status = Column(SQLEnum(SampleStatus), nullable=False, default=SampleStatus.COLLECTED)
    storage_location = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Database dependency
def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()