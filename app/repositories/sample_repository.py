from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.sample import Sample, SampleStatus, SampleType
from ..schemas.sample import SampleFilter


class SampleRepository:
    """Repository for sample-related database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_sample(self, sample_data: dict) -> Sample:
        """
        Create a new sample.

        Args:
            sample_data: Dictionary containing sample data

        Returns:
            Sample: Created sample
        """
        sample = Sample(**sample_data)
        self.db.add(sample)
        await self.db.commit()
        await self.db.refresh(sample)
        return sample

    async def get_sample_by_id(self, sample_id: UUID) -> Optional[Sample]:
        """
        Get sample by ID.

        Args:
            sample_id: Sample ID to search for

        Returns:
            Optional[Sample]: Sample if found, None otherwise
        """
        query = select(Sample).where(Sample.id == sample_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_sample_by_sample_id(self, sample_id: UUID) -> Optional[Sample]:
        """
        Get sample by sample_id field.

        Args:
            sample_id: Sample ID to search for

        Returns:
            Optional[Sample]: Sample if found, None otherwise
        """
        query = select(Sample).where(Sample.sample_id == sample_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_samples_with_filters(
        self,
        filters: SampleFilter,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[UUID] = None,
    ) -> List[Sample]:
        """
        Get samples with filtering and pagination.

        Args:
            filters: SampleFilter containing filter criteria
            skip: Number of records to skip
            limit: Maximum number of records to return
            user_id: Optional user ID to filter by (for data isolation)

        Returns:
            List[Sample]: List of samples matching criteria
        """
        query = select(Sample)
        
        # Apply filters
        conditions = []
        
        # Always filter by user_id if provided (for data isolation)
        if user_id is not None:
            conditions.append(Sample.user_id == user_id)
        
        if filters.sample_type is not None:
            conditions.append(Sample.sample_type == filters.sample_type)
        
        if filters.subject_id is not None:
            conditions.append(Sample.subject_id == filters.subject_id)
        
        if filters.status is not None:
            conditions.append(Sample.status == filters.status)
        
        if filters.collection_date_from is not None:
            conditions.append(Sample.collection_date >= filters.collection_date_from)
        
        if filters.collection_date_to is not None:
            conditions.append(Sample.collection_date <= filters.collection_date_to)
        
        if filters.storage_location is not None:
            conditions.append(Sample.storage_location.ilike(f"%{filters.storage_location}%"))
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Apply pagination and ordering
        query = query.order_by(Sample.created_at.desc()).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_samples_with_filters(self, filters: SampleFilter, user_id: Optional[UUID] = None) -> int:
        """
        Count samples matching filter criteria.

        Args:
            filters: SampleFilter containing filter criteria
            user_id: Optional user ID to filter by (for data isolation)

        Returns:
            int: Number of samples matching criteria
        """
        query = select(func.count(Sample.id))
        
        # Apply same filters as in get_samples_with_filters
        conditions = []
        
        # Always filter by user_id if provided (for data isolation)
        if user_id is not None:
            conditions.append(Sample.user_id == user_id)
        
        if filters.sample_type is not None:
            conditions.append(Sample.sample_type == filters.sample_type)
        
        if filters.subject_id is not None:
            conditions.append(Sample.subject_id == filters.subject_id)
        
        if filters.status is not None:
            conditions.append(Sample.status == filters.status)
        
        if filters.collection_date_from is not None:
            conditions.append(Sample.collection_date >= filters.collection_date_from)
        
        if filters.collection_date_to is not None:
            conditions.append(Sample.collection_date <= filters.collection_date_to)
        
        if filters.storage_location is not None:
            conditions.append(Sample.storage_location.ilike(f"%{filters.storage_location}%"))
        
        if conditions:
            query = query.where(and_(*conditions))
        
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def update_sample(self, sample_id: UUID, sample_data: dict) -> Optional[Sample]:
        """
        Update sample information.

        Args:
            sample_id: Sample ID to update
            sample_data: Dictionary containing updated sample data

        Returns:
            Optional[Sample]: Updated sample if found, None otherwise
        """
        sample = await self.get_sample_by_id(sample_id)
        if not sample:
            return None

        for key, value in sample_data.items():
            if hasattr(sample, key) and value is not None:
                setattr(sample, key, value)

        await self.db.commit()
        await self.db.refresh(sample)
        return sample

    async def delete_sample(self, sample_id: UUID) -> bool:
        """
        Delete a sample.

        Args:
            sample_id: Sample ID to delete

        Returns:
            bool: True if sample was deleted, False if not found
        """
        sample = await self.get_sample_by_id(sample_id)
        if not sample:
            return False

        await self.db.delete(sample)
        await self.db.commit()
        return True

    async def sample_id_exists(self, sample_id: UUID) -> bool:
        """
        Check if sample_id already exists in database.

        Args:
            sample_id: Sample ID to check

        Returns:
            bool: True if sample_id exists, False otherwise
        """
        sample = await self.get_sample_by_sample_id(sample_id)
        return sample is not None

    async def get_samples_by_subject_id(self, subject_id: str, user_id: Optional[UUID] = None) -> List[Sample]:
        """
        Get all samples for a specific subject.

        Args:
            subject_id: Subject ID to search for
            user_id: Optional user ID to filter by (for data isolation)

        Returns:
            List[Sample]: List of samples for the subject
        """
        query = select(Sample).where(Sample.subject_id == subject_id)
        
        # Filter by user_id if provided
        if user_id is not None:
            query = query.where(Sample.user_id == user_id)
            
        query = query.order_by(Sample.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_samples_by_status(self, status: SampleStatus, user_id: Optional[UUID] = None) -> List[Sample]:
        """
        Get all samples with a specific status.

        Args:
            status: Status to filter by
            user_id: Optional user ID to filter by (for data isolation)

        Returns:
            List[Sample]: List of samples with the status
        """
        query = select(Sample).where(Sample.status == status)
        
        # Filter by user_id if provided (for data isolation)
        if user_id is not None:
            query = query.where(Sample.user_id == user_id)
            
        query = query.order_by(Sample.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_samples_by_type(self, sample_type: SampleType, user_id: Optional[UUID] = None) -> List[Sample]:
        """
        Get all samples with a specific type.

        Args:
            sample_type: Sample type to filter by
            user_id: Optional user ID to filter by (for data isolation)

        Returns:
            List[Sample]: List of samples with the type
        """
        query = select(Sample).where(Sample.sample_type == sample_type)
        
        # Filter by user_id if provided (for data isolation)
        if user_id is not None:
            query = query.where(Sample.user_id == user_id)
            
        query = query.order_by(Sample.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())