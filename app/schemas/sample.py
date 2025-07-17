from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel, Field, validator

from ..models.sample import SampleType, SampleStatus


class SampleBase(BaseModel):
    sample_type: SampleType = Field(..., description="Type of clinical sample")
    subject_id: str = Field(..., min_length=1, max_length=50, description="Subject/patient identifier")
    collection_date: date = Field(..., description="Date when sample was collected")
    storage_location: Optional[str] = Field(None, max_length=255, description="Physical storage location identifier")
    
    @validator("collection_date")
    def validate_collection_date(cls, v):
        if v > date.today():
            raise ValueError("Collection date cannot be in the future")
        return v


class SampleCreate(SampleBase):
    status: SampleStatus = Field(default=SampleStatus.COLLECTED, description="Current processing status of sample")


class SampleUpdate(BaseModel):
    sample_type: Optional[SampleType] = Field(None, description="Type of clinical sample")
    subject_id: Optional[str] = Field(None, min_length=1, max_length=50, description="Subject/patient identifier")
    collection_date: Optional[date] = Field(None, description="Date when sample was collected")
    status: Optional[SampleStatus] = Field(None, description="Current processing status of sample")
    storage_location: Optional[str] = Field(None, max_length=255, description="Physical storage location identifier")
    
    @validator("collection_date")
    def validate_collection_date(cls, v):
        if v is not None and v > date.today():
            raise ValueError("Collection date cannot be in the future")
        return v


class SampleResponse(SampleBase):
    id: str = Field(..., description="Unique sample record identifier")
    sample_id: str = Field(..., description="Unique sample identifier for tracking")
    status: SampleStatus = Field(..., description="Current processing status of sample")
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class SampleFilter(BaseModel):
    sample_type: Optional[SampleType] = Field(None, description="Filter by sample type")
    subject_id: Optional[str] = Field(None, description="Filter by subject ID")
    status: Optional[SampleStatus] = Field(None, description="Filter by sample status")
    collection_date_from: Optional[date] = Field(None, description="Filter by collection date from")
    collection_date_to: Optional[date] = Field(None, description="Filter by collection date to")
    storage_location: Optional[str] = Field(None, description="Filter by storage location")
    
    @validator("collection_date_to")
    def validate_date_range(cls, v, values):
        if v is not None and "collection_date_from" in values and values["collection_date_from"] is not None:
            if v < values["collection_date_from"]:
                raise ValueError("collection_date_to must be after collection_date_from")
        return v


class SampleListResponse(BaseModel):
    samples: list[SampleResponse] = Field(..., description="List of samples")
    total: int = Field(..., description="Total number of samples matching filter")
    skip: int = Field(..., description="Number of skipped samples")
    limit: int = Field(..., description="Maximum number of samples returned")