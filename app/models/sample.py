from datetime import date, datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING
from uuid import UUID as UUIDType
from uuid import uuid4

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from ..db.base import Base

if TYPE_CHECKING:
    from .user import User


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

    id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        comment="Unique sample record identifier",
    )
    sample_id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        unique=True,
        nullable=False,
        default=uuid4,
        comment="Unique sample identifier for tracking",
    )
    sample_type: Mapped[SampleType] = mapped_column(
        Enum(SampleType, native_enum=False),
        nullable=False,
        comment="Type of clinical sample",
    )
    subject_id: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="Subject/patient identifier"
    )
    collection_date: Mapped[date] = mapped_column(
        Date, nullable=False, comment="Date when sample was collected"
    )
    status: Mapped[SampleStatus] = mapped_column(
        Enum(SampleStatus, native_enum=False),
        default=SampleStatus.COLLECTED,
        nullable=False,
        comment="Current processing status of sample",
    )
    storage_location: Mapped[str] = mapped_column(
        String(255), nullable=True, comment="Physical storage location identifier"
    )
    user_id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="ID of user who created this sample",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Record creation timestamp",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Last update timestamp",
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="samples")

    __table_args__ = (
        Index("ix_samples_sample_id", "sample_id"),
        Index("ix_samples_subject_id", "subject_id"),
        Index("ix_samples_sample_type", "sample_type"),
        Index("ix_samples_status", "status"),
        Index("ix_samples_collection_date", "collection_date"),
        Index("ix_samples_created_at", "created_at"),
        Index("ix_samples_user_id", "user_id"),
    )

    def __repr__(self) -> str:
        return (
            f"<Sample(id={self.id}, sample_id={self.sample_id}, "
            f"type={self.sample_type.value}, subject={self.subject_id})>"
        )
