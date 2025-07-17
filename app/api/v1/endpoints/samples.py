from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ...deps import get_current_user, get_database
from app.models.user import User
from app.models.sample import SampleStatus, SampleType
from app.schemas.sample import (
    SampleCreate,
    SampleFilter,
    SampleListResponse,
    SampleResponse,
    SampleUpdate,
)
from app.services.sample_service import SampleService

# Create router for sample endpoints
router = APIRouter()


@router.post("/", response_model=SampleResponse, summary="Create a new sample")
async def create_sample(
    sample_data: SampleCreate,
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new clinical sample.
    """
    sample_service = SampleService(db)
    return await sample_service.create_sample(sample_data, current_user)


@router.get("/", response_model=SampleListResponse, summary="Get all samples")
async def get_samples(
    skip: int = Query(0, ge=0, description="Number of samples to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of samples to return"),
    sample_type: Optional[SampleType] = Query(None, description="Filter by sample type"),
    sample_status: Optional[SampleStatus] = Query(None, description="Filter by sample status"),
    subject_id: Optional[str] = Query(None, description="Filter by subject ID"),
    collection_date_from: Optional[str] = Query(None, description="Filter by collection date from (YYYY-MM-DD)"),
    collection_date_to: Optional[str] = Query(None, description="Filter by collection date to (YYYY-MM-DD)"),
    storage_location: Optional[str] = Query(None, description="Filter by storage location"),
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(get_current_user),
):
    """
    Get all clinical samples with optional filtering and pagination.
    """
    from datetime import datetime
    
    # Build filter object
    filters = SampleFilter(
        sample_type=sample_type,
        status=sample_status,
        subject_id=subject_id,
        collection_date_from=datetime.strptime(collection_date_from, "%Y-%m-%d").date() if collection_date_from else None,
        collection_date_to=datetime.strptime(collection_date_to, "%Y-%m-%d").date() if collection_date_to else None,
        storage_location=storage_location,
    )
    
    sample_service = SampleService(db)
    return await sample_service.get_samples(filters, skip, limit, current_user)


@router.get("/{sample_id}", response_model=SampleResponse, summary="Get a specific sample")
async def get_sample(
    sample_id: UUID,
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific clinical sample by ID.
    """
    sample_service = SampleService(db)
    return await sample_service.get_sample_by_id(sample_id, current_user)


@router.put("/{sample_id}", response_model=SampleResponse, summary="Update a sample")
async def update_sample(
    sample_id: UUID,
    sample_data: SampleUpdate,
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(get_current_user),
):
    """
    Update a clinical sample.
    """
    sample_service = SampleService(db)
    return await sample_service.update_sample(sample_id, sample_data, current_user)


@router.delete("/{sample_id}", summary="Delete a sample")
async def delete_sample(
    sample_id: UUID,
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a clinical sample.
    """
    sample_service = SampleService(db)
    return await sample_service.delete_sample(sample_id, current_user)


@router.get("/subject/{subject_id}", response_model=List[SampleResponse], summary="Get samples by subject ID")
async def get_samples_by_subject(
    subject_id: str,
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(get_current_user),
):
    """
    Get all samples for a specific subject/patient.
    """
    sample_service = SampleService(db)
    return await sample_service.get_samples_by_subject_id(subject_id, current_user)


@router.get("/stats/overview", summary="Get sample statistics")
async def get_sample_statistics(
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(get_current_user),
):
    """
    Get overview statistics of samples.
    """
    sample_service = SampleService(db)
    return await sample_service.get_sample_statistics(current_user)
