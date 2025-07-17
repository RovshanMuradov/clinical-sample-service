from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ..core.exceptions import AuthorizationError, NotFoundError, ValidationError
from ..models.user import User
from ..repositories.sample_repository import SampleRepository
from ..schemas.sample import (
    SampleCreate,
    SampleFilter,
    SampleListResponse,
    SampleResponse,
    SampleUpdate,
)


class SampleService:
    """Service for sample-related operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.sample_repository = SampleRepository(db)

    async def create_sample(
        self, sample_data: SampleCreate, current_user: User
    ) -> SampleResponse:
        """
        Create a new sample.

        Args:
            sample_data: Sample creation data
            current_user: Current authenticated user

        Returns:
            SampleResponse: Created sample

        Raises:
            HTTPException: If validation fails
        """
        # Convert Pydantic model to dict
        sample_dict = sample_data.model_dump()

        # Add user_id to track who created the sample
        sample_dict["user_id"] = current_user.id

        # Create sample
        sample = await self.sample_repository.create_sample(sample_dict)

        return SampleResponse.model_validate(sample)

    async def get_sample_by_id(
        self, sample_id: UUID, current_user: User
    ) -> SampleResponse:
        """
        Get sample by ID.

        Args:
            sample_id: Sample ID to retrieve
            current_user: Current authenticated user

        Returns:
            SampleResponse: Sample details

        Raises:
            HTTPException: If sample not found
        """
        sample = await self.sample_repository.get_sample_by_id(sample_id)

        if not sample:
            raise NotFoundError(resource="Sample", resource_id=str(sample_id))

        # Check if sample belongs to current user
        if sample.user_id != current_user.id:
            raise AuthorizationError(
                message="Access denied to this sample",
                resource="sample",
                details={"sample_id": str(sample_id)}
            )

        return SampleResponse.model_validate(sample)

    async def get_samples(
        self,
        filters: SampleFilter,
        skip: int = 0,
        limit: int = 100,
        current_user: Optional[User] = None,
    ) -> SampleListResponse:
        """
        Get samples with filtering and pagination.

        Args:
            filters: Filter criteria
            skip: Number of records to skip
            limit: Maximum number of records to return
            current_user: Current authenticated user

        Returns:
            SampleListResponse: List of samples with pagination info
        """
        # Validate pagination parameters
        if skip < 0:
            raise ValidationError(
                message="Skip parameter must be non-negative",
                field="skip"
            )

        if limit <= 0 or limit > 1000:
            raise ValidationError(
                message="Limit parameter must be between 1 and 1000",
                field="limit"
            )

        # Filter samples by current user to ensure data isolation
        if current_user:
            # We'll add user_id filtering in the repository method
            pass

        # Get samples and count (filtered by current user)
        samples = await self.sample_repository.get_samples_with_filters(
            filters, skip, limit, current_user.id if current_user else None
        )
        total = await self.sample_repository.count_samples_with_filters(
            filters, current_user.id if current_user else None
        )

        # Convert to response models
        sample_responses = [SampleResponse.model_validate(sample) for sample in samples]

        return SampleListResponse(
            samples=sample_responses, total=total, skip=skip, limit=limit
        )

    async def update_sample(
        self,
        sample_id: UUID,
        sample_data: SampleUpdate,
        current_user: User,
    ) -> SampleResponse:
        """
        Update sample.

        Args:
            sample_id: Sample ID to update
            sample_data: Updated sample data
            current_user: Current authenticated user

        Returns:
            SampleResponse: Updated sample

        Raises:
            HTTPException: If sample not found or access denied
        """
        # Check if sample exists
        existing_sample = await self.sample_repository.get_sample_by_id(sample_id)
        if not existing_sample:
            raise NotFoundError(resource="Sample", resource_id=str(sample_id))

        # Check if sample belongs to current user
        if existing_sample.user_id != current_user.id:
            raise AuthorizationError(
                message="Access denied to this sample",
                resource="sample",
                details={"sample_id": str(sample_id)}
            )

        # Convert Pydantic model to dict, excluding None values
        sample_dict = sample_data.model_dump(exclude_none=True)

        # Update sample
        updated_sample = await self.sample_repository.update_sample(
            sample_id, sample_dict
        )

        if not updated_sample:
            raise NotFoundError(resource="Sample", resource_id=str(sample_id))

        return SampleResponse.model_validate(updated_sample)

    async def delete_sample(self, sample_id: UUID, current_user: User) -> dict:
        """
        Delete sample.

        Args:
            sample_id: Sample ID to delete
            current_user: Current authenticated user

        Returns:
            dict: Success message

        Raises:
            HTTPException: If sample not found or access denied
        """
        # Check if sample exists
        existing_sample = await self.sample_repository.get_sample_by_id(sample_id)
        if not existing_sample:
            raise NotFoundError(resource="Sample", resource_id=str(sample_id))

        # Check if sample belongs to current user
        if existing_sample.user_id != current_user.id:
            raise AuthorizationError(
                message="Access denied to this sample",
                resource="sample",
                details={"sample_id": str(sample_id)}
            )

        # Delete sample
        deleted = await self.sample_repository.delete_sample(sample_id)

        if not deleted:
            raise NotFoundError(resource="Sample", resource_id=str(sample_id))

        return {"message": "Sample deleted successfully"}

    async def get_samples_by_subject_id(
        self,
        subject_id: str,
        current_user: User,
    ) -> List[SampleResponse]:
        """
        Get all samples for a specific subject.

        Args:
            subject_id: Subject ID to search for
            current_user: Current authenticated user

        Returns:
            List[SampleResponse]: List of samples for the subject
        """
        # Get samples for subject, filtered by current user
        samples = await self.sample_repository.get_samples_by_subject_id(
            subject_id, current_user.id
        )

        return [SampleResponse.model_validate(sample) for sample in samples]

    async def get_sample_statistics(self, current_user: User) -> Dict[str, Any]:
        """
        Get sample statistics for current user only (data isolation).

        Args:
            current_user: Current authenticated user

        Returns:
            dict: Sample statistics for the current user
        """
        # Get counts by status (with proper data isolation)
        from ..models.sample import SampleStatus, SampleType

        stats: Dict[str, Any] = {
            "total_samples": 0,
            "by_status": {},
            "by_type": {},
        }

        # Get statistics by status with user_id filtering for data isolation
        for sample_status in SampleStatus:
            samples = await self.sample_repository.get_samples_by_status(
                sample_status, current_user.id
            )
            count = len(samples)
            stats["by_status"][sample_status.value] = count
            stats["total_samples"] += count

        # Get statistics by type with user_id filtering for data isolation
        for sample_type in SampleType:
            samples = await self.sample_repository.get_samples_by_type(
                sample_type, current_user.id
            )
            count = len(samples)
            stats["by_type"][sample_type.value] = count

        return stats
