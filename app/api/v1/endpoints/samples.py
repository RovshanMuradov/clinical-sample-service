from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sample import SampleStatus, SampleType
from app.models.user import User
from app.schemas.sample import (
    SampleCreate,
    SampleFilter,
    SampleListResponse,
    SampleResponse,
    SampleUpdate,
)
from app.services.sample_service import SampleService

from ...deps import get_current_user, get_database

# Create router for sample endpoints
router = APIRouter()


@router.post(
    "/",
    response_model=SampleResponse,
    summary="Create a new clinical sample",
    description="Create a new clinical sample record with validation and automatic tracking ID generation.",
    response_description="Created sample with auto-generated tracking ID and metadata",
    responses={
        201: {
            "description": "Sample successfully created",
            "content": {
                "application/json": {
                    "example": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "sample_id": "650e8400-e29b-41d4-a716-446655440001",
                        "sample_type": "blood",
                        "subject_id": "P001",
                        "collection_date": "2023-12-01",
                        "status": "collected",
                        "storage_location": "freezer-1-rowA",
                        "created_at": "2023-12-01T10:00:00Z",
                        "updated_at": "2023-12-01T10:00:00Z"
                    }
                }
            }
        },
        400: {
            "description": "Validation error - invalid sample data",
            "content": {
                "application/json": {
                    "example": {
                        "error": True,
                        "message": "Tissue samples must be stored in freezer",
                        "error_code": "VALIDATION_ERROR",
                        "details": {"field": "storage_location", "value": "room-1-shelfA"},
                        "timestamp": "2023-12-01T10:00:00Z"
                    }
                }
            }
        },
        401: {
            "description": "Authentication required",
            "content": {
                "application/json": {
                    "example": {
                        "error": True,
                        "message": "Token has expired",
                        "error_code": "AUTHENTICATION_ERROR",
                        "details": {},
                        "timestamp": "2023-12-01T10:00:00Z"
                    }
                }
            }
        }
    }
)
async def create_sample(
    sample_data: SampleCreate,
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new clinical sample record in the system.

    This endpoint creates a new sample with automatic tracking ID generation and validation
    of business rules specific to clinical sample management.

    **Authentication Required:**
    - Must provide a valid Bearer token in the Authorization header
    - Sample will be automatically associated with the authenticated user

    **Business Rules:**
    - **Sample Type**: Must be one of: blood, saliva, tissue
    - **Subject ID**: Must follow format: Letter + 3+ digits (e.g., P001, S123)
    - **Collection Date**: Cannot be in the future or more than 10 years ago
    - **Storage Location**: Must follow format: freezer-X-rowY or room-X-shelfY
    - **Tissue Samples**: Must be stored in freezer (business rule)

    **Auto-Generated Fields:**
    - `id`: Database record ID (UUID)
    - `sample_id`: Unique tracking ID for the sample (UUID)
    - `created_at`: Timestamp when record was created
    - `updated_at`: Timestamp when record was last modified

    **Example Request:**
    ```json
    {
        "sample_type": "blood",
        "subject_id": "P001",
        "collection_date": "2023-12-01",
        "storage_location": "freezer-1-rowA",
        "status": "collected"
    }
    ```

    **Example Response:**
    ```json
    {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "sample_id": "650e8400-e29b-41d4-a716-446655440001",
        "sample_type": "blood",
        "subject_id": "P001",
        "collection_date": "2023-12-01",
        "status": "collected",
        "storage_location": "freezer-1-rowA",
        "created_at": "2023-12-01T10:00:00Z",
        "updated_at": "2023-12-01T10:00:00Z"
    }
    ```
    """
    sample_service = SampleService(db)
    return await sample_service.create_sample(sample_data, current_user)


@router.get(
    "/",
    response_model=SampleListResponse,
    summary="Get all samples with filtering and pagination",
    description="Retrieve clinical samples with advanced filtering options and pagination support.",
    response_description="Paginated list of samples with metadata",
    responses={
        200: {
            "description": "Successfully retrieved samples",
            "content": {
                "application/json": {
                    "example": {
                        "samples": [
                            {
                                "id": "550e8400-e29b-41d4-a716-446655440000",
                                "sample_id": "650e8400-e29b-41d4-a716-446655440001",
                                "sample_type": "blood",
                                "subject_id": "P001",
                                "collection_date": "2023-12-01",
                                "status": "collected",
                                "storage_location": "freezer-1-rowA",
                                "created_at": "2023-12-01T10:00:00Z",
                                "updated_at": "2023-12-01T10:00:00Z"
                            },
                            {
                                "id": "550e8400-e29b-41d4-a716-446655440002",
                                "sample_id": "650e8400-e29b-41d4-a716-446655440003",
                                "sample_type": "tissue",
                                "subject_id": "P002",
                                "collection_date": "2023-12-02",
                                "status": "processing",
                                "storage_location": "freezer-2-rowB",
                                "created_at": "2023-12-02T11:00:00Z",
                                "updated_at": "2023-12-02T11:00:00Z"
                            }
                        ],
                        "total": 2,
                        "skip": 0,
                        "limit": 100
                    }
                }
            }
        },
        400: {
            "description": "Invalid filter parameters",
            "content": {
                "application/json": {
                    "example": {
                        "error": True,
                        "message": "Collection date to must be after collection date from",
                        "error_code": "VALIDATION_ERROR",
                        "details": {"field": "collection_date_to"},
                        "timestamp": "2023-12-01T10:00:00Z"
                    }
                }
            }
        },
        401: {
            "description": "Authentication required",
            "content": {
                "application/json": {
                    "example": {
                        "error": True,
                        "message": "Token has expired",
                        "error_code": "AUTHENTICATION_ERROR",
                        "details": {},
                        "timestamp": "2023-12-01T10:00:00Z"
                    }
                }
            }
        }
    }
)
async def get_samples(
    skip: int = Query(0, ge=0, description="Number of samples to skip for pagination"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of samples to return (1-1000)"
    ),
    sample_type: Optional[SampleType] = Query(
        None, description="Filter by sample type: blood, saliva, or tissue"
    ),
    sample_status: Optional[SampleStatus] = Query(
        None, description="Filter by sample status: collected, processing, or archived"
    ),
    subject_id: Optional[str] = Query(None, description="Filter by subject ID (e.g., P001)"),
    collection_date_from: Optional[str] = Query(
        None, description="Filter by collection date from (YYYY-MM-DD format)"
    ),
    collection_date_to: Optional[str] = Query(
        None, description="Filter by collection date to (YYYY-MM-DD format)"
    ),
    storage_location: Optional[str] = Query(
        None, description="Filter by storage location (e.g., freezer-1-rowA)"
    ),
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve clinical samples with advanced filtering and pagination.

    This endpoint returns a paginated list of samples that belong to the authenticated user.
    Data isolation ensures users can only see their own samples.

    **Authentication Required:**
    - Must provide a valid Bearer token in the Authorization header
    - Only samples belonging to the authenticated user are returned

    **Filtering Options:**
    - **sample_type**: Filter by sample type (blood, saliva, tissue)
    - **sample_status**: Filter by processing status (collected, processing, archived)
    - **subject_id**: Filter by subject/patient ID (exact or partial match)
    - **collection_date_from/to**: Filter by collection date range (YYYY-MM-DD)
    - **storage_location**: Filter by storage location (exact or partial match)

    **Pagination:**
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return (1-1000)

    **Response Format:**
    - **samples**: Array of sample objects
    - **total**: Total number of samples matching the filter
    - **skip**: Number of samples skipped
    - **limit**: Maximum number of samples returned

    **Example Usage:**
    ```
    GET /api/v1/samples?sample_type=blood&limit=10&skip=0
    GET /api/v1/samples?subject_id=P001&collection_date_from=2023-01-01
    GET /api/v1/samples?storage_location=freezer-1&sample_status=collected
    ```

    **Data Isolation:**
    - Users can only access their own samples
    - Total count reflects only user's samples
    - Filtering is applied within user's data scope
    """
    from datetime import datetime

    # Build filter object
    filters = SampleFilter(
        sample_type=sample_type,
        status=sample_status,
        subject_id=subject_id,
        collection_date_from=datetime.strptime(collection_date_from, "%Y-%m-%d").date()
        if collection_date_from
        else None,
        collection_date_to=datetime.strptime(collection_date_to, "%Y-%m-%d").date()
        if collection_date_to
        else None,
        storage_location=storage_location,
    )

    sample_service = SampleService(db)
    return await sample_service.get_samples(filters, skip, limit, current_user)


@router.get(
    "/{sample_id}",
    response_model=SampleResponse,
    summary="Get a specific sample by ID",
    description="Retrieve a specific clinical sample by its unique identifier.",
    response_description="Sample details for the specified ID",
    responses={
        200: {
            "description": "Sample found and returned",
            "content": {
                "application/json": {
                    "example": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "sample_id": "650e8400-e29b-41d4-a716-446655440001",
                        "sample_type": "blood",
                        "subject_id": "P001",
                        "collection_date": "2023-12-01",
                        "status": "collected",
                        "storage_location": "freezer-1-rowA",
                        "created_at": "2023-12-01T10:00:00Z",
                        "updated_at": "2023-12-01T10:00:00Z"
                    }
                }
            }
        },
        404: {
            "description": "Sample not found",
            "content": {
                "application/json": {
                    "example": {
                        "error": True,
                        "message": "Sample not found",
                        "error_code": "NOT_FOUND_ERROR",
                        "details": {"sample_id": "550e8400-e29b-41d4-a716-446655440000"},
                        "timestamp": "2023-12-01T10:00:00Z"
                    }
                }
            }
        },
        401: {
            "description": "Authentication required",
            "content": {
                "application/json": {
                    "example": {
                        "error": True,
                        "message": "Token has expired",
                        "error_code": "AUTHENTICATION_ERROR",
                        "details": {},
                        "timestamp": "2023-12-01T10:00:00Z"
                    }
                }
            }
        }
    }
)
async def get_sample(
    sample_id: UUID,
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve a specific clinical sample by its unique identifier.

    This endpoint returns detailed information about a single sample identified by its UUID.
    Data isolation ensures users can only access their own samples.

    **Authentication Required:**
    - Must provide a valid Bearer token in the Authorization header
    - Can only access samples belonging to the authenticated user

    **Path Parameters:**
    - **sample_id**: UUID of the sample to retrieve

    **Data Isolation:**
    - Users can only access their own samples
    - Attempting to access another user's sample returns 404 (not found)
    - This prevents data leakage between users

    **Example Usage:**
    ```
    GET /api/v1/samples/550e8400-e29b-41d4-a716-446655440000
    ```

    **Response Fields:**
    - **id**: Database record ID
    - **sample_id**: Unique tracking ID for the sample
    - **sample_type**: Type of sample (blood, saliva, tissue)
    - **subject_id**: Subject/patient identifier
    - **collection_date**: Date when sample was collected
    - **status**: Current processing status
    - **storage_location**: Physical storage location
    - **created_at**: When the record was created
    - **updated_at**: When the record was last modified
    """
    sample_service = SampleService(db)
    return await sample_service.get_sample_by_id(sample_id, current_user)


@router.put(
    "/{sample_id}",
    response_model=SampleResponse,
    summary="Update a sample",
    description="Update an existing clinical sample with new information.",
    response_description="Updated sample information",
    responses={
        200: {
            "description": "Sample successfully updated",
            "content": {
                "application/json": {
                    "example": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "sample_id": "650e8400-e29b-41d4-a716-446655440001",
                        "sample_type": "blood",
                        "subject_id": "P001",
                        "collection_date": "2023-12-01",
                        "status": "processing",
                        "storage_location": "freezer-2-rowB",
                        "created_at": "2023-12-01T10:00:00Z",
                        "updated_at": "2023-12-01T15:30:00Z"
                    }
                }
            }
        },
        400: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "error": True,
                        "message": "Collection date cannot be in the future",
                        "error_code": "VALIDATION_ERROR",
                        "details": {"field": "collection_date"},
                        "timestamp": "2023-12-01T10:00:00Z"
                    }
                }
            }
        },
        404: {
            "description": "Sample not found",
            "content": {
                "application/json": {
                    "example": {
                        "error": True,
                        "message": "Sample not found",
                        "error_code": "NOT_FOUND_ERROR",
                        "details": {"sample_id": "550e8400-e29b-41d4-a716-446655440000"},
                        "timestamp": "2023-12-01T10:00:00Z"
                    }
                }
            }
        }
    }
)
async def update_sample(
    sample_id: UUID,
    sample_data: SampleUpdate,
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(get_current_user),
):
    """
    Update an existing clinical sample with new information.

    This endpoint allows updating specific fields of a sample while maintaining
    data integrity and business rules.

    **Authentication Required:**
    - Must provide a valid Bearer token in the Authorization header
    - Can only update samples belonging to the authenticated user

    **Path Parameters:**
    - **sample_id**: UUID of the sample to update

    **Updatable Fields:**
    - **sample_type**: Change sample type (blood, saliva, tissue)
    - **subject_id**: Update subject/patient identifier
    - **collection_date**: Modify collection date
    - **status**: Update processing status (collected, processing, archived)
    - **storage_location**: Change storage location

    **Business Rules:**
    - All validation rules apply as in sample creation
    - Tissue samples must be stored in freezer
    - Collection date cannot be in the future
    - Only provided fields are updated (partial updates supported)

    **Example Request:**
    ```json
    {
        "status": "processing",
        "storage_location": "freezer-2-rowB"
    }
    ```

    **Data Isolation:**
    - Users can only update their own samples
    - Attempting to update another user's sample returns 404
    - Updated timestamp is automatically set
    """
    sample_service = SampleService(db)
    return await sample_service.update_sample(sample_id, sample_data, current_user)


@router.delete(
    "/{sample_id}",
    summary="Delete a sample",
    description="Permanently delete a clinical sample from the system.",
    response_description="Confirmation of sample deletion",
    responses={
        200: {
            "description": "Sample successfully deleted",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Sample deleted successfully",
                        "sample_id": "550e8400-e29b-41d4-a716-446655440000"
                    }
                }
            }
        },
        404: {
            "description": "Sample not found",
            "content": {
                "application/json": {
                    "example": {
                        "error": True,
                        "message": "Sample not found",
                        "error_code": "NOT_FOUND_ERROR",
                        "details": {"sample_id": "550e8400-e29b-41d4-a716-446655440000"},
                        "timestamp": "2023-12-01T10:00:00Z"
                    }
                }
            }
        },
        401: {
            "description": "Authentication required",
            "content": {
                "application/json": {
                    "example": {
                        "error": True,
                        "message": "Token has expired",
                        "error_code": "AUTHENTICATION_ERROR",
                        "details": {},
                        "timestamp": "2023-12-01T10:00:00Z"
                    }
                }
            }
        }
    }
)
async def delete_sample(
    sample_id: UUID,
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(get_current_user),
):
    """
    Permanently delete a clinical sample from the system.

    This endpoint removes a sample record permanently. This action cannot be undone.
    Use with caution as it will permanently remove all sample data.

    **Authentication Required:**
    - Must provide a valid Bearer token in the Authorization header
    - Can only delete samples belonging to the authenticated user

    **Path Parameters:**
    - **sample_id**: UUID of the sample to delete

    **Data Isolation:**
    - Users can only delete their own samples
    - Attempting to delete another user's sample returns 404
    - This prevents unauthorized data deletion

    **Example Usage:**
    ```
    DELETE /api/v1/samples/550e8400-e29b-41d4-a716-446655440000
    ```

    **Warning:**
    - This action is permanent and cannot be undone
    - All sample data including tracking information will be lost
    - Consider updating status to 'archived' instead of deletion for audit purposes

    **Best Practices:**
    - Implement soft deletion in production systems
    - Log all deletion operations for audit trails
    - Require additional confirmation for critical samples
    """
    sample_service = SampleService(db)
    return await sample_service.delete_sample(sample_id, current_user)


@router.get(
    "/subject/{subject_id}",
    response_model=List[SampleResponse],
    summary="Get samples by subject ID",
    description="Retrieve all samples for a specific subject/patient identifier.",
    response_description="List of samples for the specified subject",
    responses={
        200: {
            "description": "List of samples for the subject",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "sample_id": "650e8400-e29b-41d4-a716-446655440001",
                            "sample_type": "blood",
                            "subject_id": "P001",
                            "collection_date": "2023-12-01",
                            "status": "collected",
                            "storage_location": "freezer-1-rowA",
                            "created_at": "2023-12-01T10:00:00Z",
                            "updated_at": "2023-12-01T10:00:00Z"
                        },
                        {
                            "id": "550e8400-e29b-41d4-a716-446655440002",
                            "sample_id": "650e8400-e29b-41d4-a716-446655440003",
                            "sample_type": "saliva",
                            "subject_id": "P001",
                            "collection_date": "2023-12-03",
                            "status": "processing",
                            "storage_location": "room-1-shelfB",
                            "created_at": "2023-12-03T14:00:00Z",
                            "updated_at": "2023-12-03T14:00:00Z"
                        }
                    ]
                }
            }
        },
        404: {
            "description": "Subject not found or no samples",
            "content": {
                "application/json": {
                    "example": {
                        "error": True,
                        "message": "No samples found for subject P001",
                        "error_code": "NOT_FOUND_ERROR",
                        "details": {"subject_id": "P001"},
                        "timestamp": "2023-12-01T10:00:00Z"
                    }
                }
            }
        },
        401: {
            "description": "Authentication required",
            "content": {
                "application/json": {
                    "example": {
                        "error": True,
                        "message": "Token has expired",
                        "error_code": "AUTHENTICATION_ERROR",
                        "details": {},
                        "timestamp": "2023-12-01T10:00:00Z"
                    }
                }
            }
        }
    }
)
async def get_samples_by_subject(
    subject_id: str,
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve all samples for a specific subject/patient identifier.

    This endpoint returns all samples that belong to a specific subject/patient,
    filtered by the authenticated user's data scope.

    **Authentication Required:**
    - Must provide a valid Bearer token in the Authorization header
    - Only samples belonging to the authenticated user are returned

    **Path Parameters:**
    - **subject_id**: Subject/patient identifier (e.g., P001, S123)

    **Use Cases:**
    - Track all samples for a specific patient
    - Clinical research requiring patient-specific sample analysis
    - Audit trail for individual subjects
    - Sample collection completeness verification

    **Example Usage:**
    ```
    GET /api/v1/samples/subject/P001
    GET /api/v1/samples/subject/S123
    ```

    **Data Isolation:**
    - Users can only access samples from their own subjects
    - Subject IDs are scoped to the authenticated user
    - Cross-user data leakage is prevented

    **Response:**
    - Returns an array of sample objects
    - Empty array if no samples found for the subject
    - Samples are ordered by collection date (newest first)

    **Clinical Workflow:**
    - Use this endpoint to review all samples collected from a patient
    - Verify sample collection protocols are followed
    - Track sample processing status across multiple collection dates
    """
    sample_service = SampleService(db)
    return await sample_service.get_samples_by_subject_id(subject_id, current_user)


@router.get(
    "/stats/overview",
    summary="Get sample statistics",
    description="Retrieve overview statistics and analytics for clinical samples.",
    response_description="Statistical overview of samples",
    responses={
        200: {
            "description": "Sample statistics successfully retrieved",
            "content": {
                "application/json": {
                    "example": {
                        "total_samples": 150,
                        "by_status": {
                            "collected": 50,
                            "processing": 75,
                            "archived": 25
                        },
                        "by_type": {
                            "blood": 80,
                            "saliva": 40,
                            "tissue": 30
                        },
                        "collection_date_range": {
                            "earliest": "2023-01-15",
                            "latest": "2023-12-01"
                        },
                        "unique_subjects": 45,
                        "storage_locations": {
                            "freezer_locations": 8,
                            "room_locations": 3
                        }
                    }
                }
            }
        },
        401: {
            "description": "Authentication required",
            "content": {
                "application/json": {
                    "example": {
                        "error": True,
                        "message": "Token has expired",
                        "error_code": "AUTHENTICATION_ERROR",
                        "details": {},
                        "timestamp": "2023-12-01T10:00:00Z"
                    }
                }
            }
        }
    }
)
async def get_sample_statistics(
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve comprehensive statistics and analytics for clinical samples.

    This endpoint provides statistical insights into the sample collection,
    processing status, and distribution across different categories.

    **Authentication Required:**
    - Must provide a valid Bearer token in the Authorization header
    - Statistics are calculated only for the authenticated user's samples

    **Data Isolation:**
    - Statistics reflect only the current user's samples
    - No cross-user data is included in calculations
    - Ensures privacy and data isolation

    **Statistics Included:**
    - **total_samples**: Total number of samples
    - **by_status**: Breakdown by processing status (collected, processing, archived)
    - **by_type**: Breakdown by sample type (blood, saliva, tissue)
    - **collection_date_range**: Earliest and latest collection dates
    - **unique_subjects**: Number of unique subjects/patients
    - **storage_locations**: Distribution across storage locations

    **Use Cases:**
    - **Dashboard Analytics**: Display key metrics on management dashboards
    - **Research Planning**: Understand sample distribution for study planning
    - **Quality Control**: Monitor collection and processing patterns
    - **Capacity Planning**: Assess storage utilization and requirements
    - **Audit Reports**: Generate summary reports for regulatory compliance

    **Example Usage:**
    ```
    GET /api/v1/samples/stats/overview
    ```

    **Response Format:**
    The response includes numerical counts and breakdowns that can be used
    for charts, graphs, and summary displays in client applications.

    **Performance Notes:**
    - Statistics are calculated in real-time
    - Response time depends on the number of samples
    - Consider caching for high-frequency access
    """
    sample_service = SampleService(db)
    return await sample_service.get_sample_statistics(current_user)
