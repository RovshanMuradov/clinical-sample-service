import re
from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator

from ..models.sample import SampleStatus, SampleType


class SampleBase(BaseModel):
    sample_type: SampleType = Field(..., description="Type of clinical sample")
    subject_id: str = Field(
        ..., min_length=1, max_length=50, description="Subject/patient identifier"
    )
    collection_date: date = Field(..., description="Date when sample was collected")
    storage_location: Optional[str] = Field(
        None, max_length=255, description="Physical storage location identifier"
    )

    @validator("subject_id")
    def validate_subject_id(cls, v):
        # Subject ID must follow pattern: Letter + numbers (e.g., P001, S123)
        if not re.match(r"^[A-Za-z]\d{3,}$", v):
            raise ValueError(
                "Subject ID must start with a letter followed by at least 3 digits (e.g., P001, S123)"
            )
        return v.upper()

    @validator("collection_date")
    def validate_collection_date(cls, v):
        if v > date.today():
            raise ValueError("Collection date cannot be in the future")
        # Check if date is too old (more than 10 years ago)
        from datetime import timedelta

        ten_years_ago = date.today() - timedelta(days=365 * 10)
        if v < ten_years_ago:
            raise ValueError("Collection date cannot be more than 10 years ago")
        return v

    @validator("storage_location")
    def validate_storage_location(cls, v):
        if v is not None:
            # Storage location must follow format: freezer-X-rowY or room-X-shelfY
            if not re.match(r"^(freezer|room)-\d+-\w+$", v.lower()):
                raise ValueError(
                    "Storage location must follow format: 'freezer-X-rowY' or 'room-X-shelfY'"
                )
        return v

    @validator("storage_location")
    def validate_storage_by_sample_type(cls, v, values):
        # Business rule: tissue samples must be stored in freezer
        if "sample_type" in values and values["sample_type"] == SampleType.TISSUE:
            if v is None:
                raise ValueError(
                    "Tissue samples must have a storage location specified"
                )
            if not v.lower().startswith("freezer"):
                raise ValueError("Tissue samples must be stored in freezer")
        return v


class SampleCreate(SampleBase):
    status: SampleStatus = Field(
        default=SampleStatus.COLLECTED,
        description="Current processing status of sample",
    )


class SampleUpdate(BaseModel):
    sample_type: Optional[SampleType] = Field(
        None, description="Type of clinical sample"
    )
    subject_id: Optional[str] = Field(
        None, min_length=1, max_length=50, description="Subject/patient identifier"
    )
    collection_date: Optional[date] = Field(
        None, description="Date when sample was collected"
    )
    status: Optional[SampleStatus] = Field(
        None, description="Current processing status of sample"
    )
    storage_location: Optional[str] = Field(
        None, max_length=255, description="Physical storage location identifier"
    )

    @validator("subject_id")
    def validate_subject_id(cls, v):
        if v is not None:
            # Subject ID must follow pattern: Letter + numbers (e.g., P001, S123)
            if not re.match(r"^[A-Za-z]\d{3,}$", v):
                raise ValueError(
                    "Subject ID must start with a letter followed by at least 3 digits (e.g., P001, S123)"
                )
            return v.upper()
        return v

    @validator("collection_date")
    def validate_collection_date(cls, v):
        if v is not None:
            if v > date.today():
                raise ValueError("Collection date cannot be in the future")
            # Check if date is too old (more than 10 years ago)
            from datetime import timedelta

            ten_years_ago = date.today() - timedelta(days=365 * 10)
            if v < ten_years_ago:
                raise ValueError("Collection date cannot be more than 10 years ago")
        return v

    @validator("storage_location")
    def validate_storage_location(cls, v):
        if v is not None:
            # Storage location must follow format: freezer-X-rowY or room-X-shelfY
            if not re.match(r"^(freezer|room)-\d+-\w+$", v.lower()):
                raise ValueError(
                    "Storage location must follow format: 'freezer-X-rowY' or 'room-X-shelfY'"
                )
        return v

    @validator("status")
    def validate_status_transition(cls, v, values):
        # Business rule: can't go from archived back to processing
        if v == SampleStatus.PROCESSING and "status" in values:
            # This would need to be enhanced with current status from database
            # For now, we'll add a basic check
            pass
        return v


class SampleResponse(SampleBase):
    id: UUID = Field(..., description="Unique sample record identifier")
    sample_id: UUID = Field(..., description="Unique sample identifier for tracking")
    status: SampleStatus = Field(..., description="Current processing status of sample")
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class SampleFilter(BaseModel):
    sample_type: Optional[SampleType] = Field(None, description="Filter by sample type")
    subject_id: Optional[str] = Field(None, description="Filter by subject ID")
    status: Optional[SampleStatus] = Field(None, description="Filter by sample status")
    collection_date_from: Optional[date] = Field(
        None, description="Filter by collection date from"
    )
    collection_date_to: Optional[date] = Field(
        None, description="Filter by collection date to"
    )
    storage_location: Optional[str] = Field(
        None, description="Filter by storage location"
    )

    @validator("subject_id")
    def validate_subject_id(cls, v):
        if v is not None:
            # Allow partial matching for filtering (e.g., "P" to find all P* subjects)
            if not re.match(r"^[A-Za-z]\d*$", v):
                raise ValueError(
                    "Subject ID filter must start with a letter and contain only letters and digits"
                )
            return v.upper()
        return v

    @validator("collection_date_from")
    def validate_collection_date_from(cls, v):
        if v is not None:
            # Don't allow dates in the future
            if v > date.today():
                raise ValueError("Collection date from cannot be in the future")
            # Don't allow dates more than 20 years ago (reasonable limit for filtering)
            from datetime import timedelta

            twenty_years_ago = date.today() - timedelta(days=365 * 20)
            if v < twenty_years_ago:
                raise ValueError(
                    "Collection date from cannot be more than 20 years ago"
                )
        return v

    @validator("collection_date_to")
    def validate_collection_date_to(cls, v, values):
        if v is not None:
            # Don't allow dates in the future
            if v > date.today():
                raise ValueError("Collection date to cannot be in the future")

            # Check date range consistency
            if (
                "collection_date_from" in values
                and values["collection_date_from"] is not None
            ):
                if v < values["collection_date_from"]:
                    raise ValueError(
                        "Collection date to must be after collection date from"
                    )
                # Don't allow date ranges longer than 5 years
                from datetime import timedelta

                if (v - values["collection_date_from"]) > timedelta(days=365 * 5):
                    raise ValueError("Date range cannot be longer than 5 years")
        return v

    @validator("storage_location")
    def validate_storage_location(cls, v):
        if v is not None:
            # Allow partial matching for filtering (e.g., "freezer-1" to find all freezer-1-*)
            if not re.match(r"^(freezer|room)-\d+(-\w+)?$", v.lower()):
                raise ValueError(
                    "Storage location filter must follow format: 'freezer-X' or 'room-X' (optionally with '-rowY')"
                )
        return v


class SampleListResponse(BaseModel):
    samples: list[SampleResponse] = Field(..., description="List of samples")
    total: int = Field(..., description="Total number of samples matching filter")
    skip: int = Field(..., description="Number of skipped samples")
    limit: int = Field(..., description="Maximum number of samples returned")
