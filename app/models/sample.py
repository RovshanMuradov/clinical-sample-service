from datetime import datetime, date
from enum import Enum as PyEnum
from uuid import uuid4

from sqlalchemy import String, DateTime, Date, Index, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from ..db.base import Base


class SampleType(PyEnum):
    BLOOD = "blood"
    SALIVA = "saliva"
    TISSUE = "tissue"


class SampleStatus(PyEnum):
    COLLECTED = "collected"
    PROCESSING = "processing"
    ARCHIVED = "archived"


class Sample(Base):
    __tablename__ = "samples"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), 
        primary_key=True, 
        default=lambda: str(uuid4()),
        comment="Unique sample record identifier"
    )
    sample_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), 
        unique=True,
        nullable=False,
        default=lambda: str(uuid4()),
        comment="Unique sample identifier for tracking"
    )
    sample_type: Mapped[SampleType] = mapped_column(
        Enum(SampleType, native_enum=False),
        nullable=False,
        comment="Type of clinical sample"
    )
    subject_id: Mapped[str] = mapped_column(
        String(50), 
        nullable=False,
        comment="Subject/patient identifier"
    )
    collection_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        comment="Date when sample was collected"
    )
    status: Mapped[SampleStatus] = mapped_column(
        Enum(SampleStatus, native_enum=False),
        default=SampleStatus.COLLECTED,
        nullable=False,
        comment="Current processing status of sample"
    )
    storage_location: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
        comment="Physical storage location identifier"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False,
        comment="Record creation timestamp"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Last update timestamp"
    )

    __table_args__ = (
        Index("ix_samples_sample_id", "sample_id"),
        Index("ix_samples_subject_id", "subject_id"),
        Index("ix_samples_sample_type", "sample_type"),
        Index("ix_samples_status", "status"),
        Index("ix_samples_collection_date", "collection_date"),
        Index("ix_samples_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Sample(id={self.id}, sample_id={self.sample_id}, type={self.sample_type.value}, subject={self.subject_id})>"