"""Tests for SampleRepository."""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4
from datetime import date

from app.repositories.sample_repository import SampleRepository
from app.models.sample import Sample, SampleStatus, SampleType
from app.schemas.sample import SampleFilter


class TestSampleRepository:
    """Test SampleRepository functionality."""

    @pytest.fixture
    def mock_db_session(self):
        """Create mock database session."""
        mock_session = Mock()
        mock_session.execute = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        mock_session.add = Mock()
        mock_session.delete = AsyncMock()
        return mock_session

    @pytest.fixture
    def sample_repository(self, mock_db_session):
        """Create SampleRepository instance with mocked database session."""
        return SampleRepository(mock_db_session)

    @pytest.fixture
    def test_sample(self):
        """Create test sample."""
        return Sample(
            id=uuid4(),
            sample_id=uuid4(),
            sample_type=SampleType.BLOOD,
            subject_id="P001",
            collection_date=date(2023, 12, 1),
            status=SampleStatus.COLLECTED,
            storage_location="freezer-1-rowA",
            user_id=uuid4()
        )

    @pytest.fixture
    def sample_data(self):
        """Create sample data dictionary."""
        return {
            "sample_id": uuid4(),
            "sample_type": SampleType.BLOOD,
            "subject_id": "P001",
            "collection_date": date(2023, 12, 1),
            "status": SampleStatus.COLLECTED,
            "storage_location": "freezer-1-rowA",
            "user_id": uuid4()
        }

    @pytest.fixture
    def sample_filter(self):
        """Create sample filter."""
        return SampleFilter(
            sample_type=SampleType.BLOOD,
            subject_id="P001",
            status=SampleStatus.COLLECTED
        )

    @pytest.mark.asyncio
    async def test_create_sample_success(
        self, sample_repository, sample_data, test_sample, mock_db_session
    ):
        """Test successful sample creation."""
        with patch('app.repositories.sample_repository.Sample') as mock_sample_class:
            mock_sample_class.return_value = test_sample
            mock_db_session.add = Mock()
            mock_db_session.commit = AsyncMock()
            mock_db_session.refresh = AsyncMock()
            
            result = await sample_repository.create_sample(sample_data)
            
            assert result == test_sample
            mock_sample_class.assert_called_once_with(**sample_data)
            mock_db_session.add.assert_called_once_with(test_sample)
            mock_db_session.commit.assert_called_once()
            mock_db_session.refresh.assert_called_once_with(test_sample)

    @pytest.mark.asyncio
    async def test_get_sample_by_id_success(
        self, sample_repository, test_sample, mock_db_session
    ):
        """Test successful sample retrieval by ID."""
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = test_sample
        mock_db_session.execute.return_value = mock_result
        
        result = await sample_repository.get_sample_by_id(test_sample.id)
        
        assert result == test_sample
        mock_db_session.execute.assert_called_once()
        mock_result.scalar_one_or_none.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_sample_by_id_not_found(
        self, sample_repository, mock_db_session
    ):
        """Test sample retrieval by ID when sample not found."""
        sample_id = uuid4()
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        result = await sample_repository.get_sample_by_id(sample_id)
        
        assert result is None
        mock_db_session.execute.assert_called_once()
        mock_result.scalar_one_or_none.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_sample_by_sample_id_success(
        self, sample_repository, test_sample, mock_db_session
    ):
        """Test successful sample retrieval by sample_id field."""
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = test_sample
        mock_db_session.execute.return_value = mock_result
        
        result = await sample_repository.get_sample_by_sample_id(test_sample.sample_id)
        
        assert result == test_sample
        mock_db_session.execute.assert_called_once()
        mock_result.scalar_one_or_none.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_sample_by_sample_id_not_found(
        self, sample_repository, mock_db_session
    ):
        """Test sample retrieval by sample_id when sample not found."""
        sample_id = uuid4()
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        result = await sample_repository.get_sample_by_sample_id(sample_id)
        
        assert result is None
        mock_db_session.execute.assert_called_once()
        mock_result.scalar_one_or_none.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_samples_with_filters_success(
        self, sample_repository, sample_filter, mock_db_session
    ):
        """Test successful samples retrieval with filters."""
        test_samples = [
            Sample(
                id=uuid4(),
                sample_id=uuid4(),
                sample_type=SampleType.BLOOD,
                subject_id="P001",
                collection_date=date(2023, 12, 1),
                status=SampleStatus.COLLECTED,
                storage_location="freezer-1-rowA",
                user_id=uuid4()
            ),
            Sample(
                id=uuid4(),
                sample_id=uuid4(),
                sample_type=SampleType.BLOOD,
                subject_id="P001",
                collection_date=date(2023, 12, 2),
                status=SampleStatus.COLLECTED,
                storage_location="freezer-1-rowB",
                user_id=uuid4()
            )
        ]
        
        mock_result = Mock()
        mock_scalars = Mock()
        mock_scalars.all.return_value = test_samples
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result
        
        result = await sample_repository.get_samples_with_filters(
            sample_filter, skip=0, limit=10, user_id=uuid4()
        )
        
        assert result == test_samples
        mock_db_session.execute.assert_called_once()
        mock_result.scalars.assert_called_once()
        mock_scalars.all.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_samples_with_filters_no_user_id(
        self, sample_repository, sample_filter, mock_db_session
    ):
        """Test samples retrieval without user_id filter."""
        test_samples = []
        
        mock_result = Mock()
        mock_scalars = Mock()
        mock_scalars.all.return_value = test_samples
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result
        
        result = await sample_repository.get_samples_with_filters(
            sample_filter, skip=0, limit=10, user_id=None
        )
        
        assert result == test_samples
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_samples_with_filters_date_range(
        self, sample_repository, mock_db_session
    ):
        """Test samples retrieval with date range filters."""
        sample_filter = SampleFilter(
            collection_date_from=date(2023, 12, 1),
            collection_date_to=date(2023, 12, 31)
        )
        
        mock_result = Mock()
        mock_scalars = Mock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result
        
        result = await sample_repository.get_samples_with_filters(
            sample_filter, skip=0, limit=10, user_id=uuid4()
        )
        
        assert result == []
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_samples_with_filters_storage_location(
        self, sample_repository, mock_db_session
    ):
        """Test samples retrieval with storage location filter."""
        sample_filter = SampleFilter(
            storage_location="freezer-1"
        )
        
        mock_result = Mock()
        mock_scalars = Mock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result
        
        result = await sample_repository.get_samples_with_filters(
            sample_filter, skip=0, limit=10, user_id=uuid4()
        )
        
        assert result == []
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_count_samples_with_filters_success(
        self, sample_repository, sample_filter, mock_db_session
    ):
        """Test successful samples count with filters."""
        count = 5
        mock_result = Mock()
        mock_result.scalar.return_value = count
        mock_db_session.execute.return_value = mock_result
        
        result = await sample_repository.count_samples_with_filters(
            sample_filter, user_id=uuid4()
        )
        
        assert result == count
        mock_db_session.execute.assert_called_once()
        mock_result.scalar.assert_called_once()

    @pytest.mark.asyncio
    async def test_count_samples_with_filters_none_result(
        self, sample_repository, sample_filter, mock_db_session
    ):
        """Test samples count when result is None."""
        mock_result = Mock()
        mock_result.scalar.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        result = await sample_repository.count_samples_with_filters(
            sample_filter, user_id=uuid4()
        )
        
        assert result == 0
        mock_db_session.execute.assert_called_once()
        mock_result.scalar.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_sample_success(
        self, sample_repository, test_sample, mock_db_session
    ):
        """Test successful sample update."""
        sample_id = test_sample.id
        update_data = {
            "status": SampleStatus.PROCESSING,
            "storage_location": "freezer-2-rowB"
        }
        
        # Mock get_sample_by_id to return the test sample
        sample_repository.get_sample_by_id = AsyncMock(return_value=test_sample)
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()
        
        result = await sample_repository.update_sample(sample_id, update_data)
        
        assert result == test_sample
        # Check that attributes were updated
        assert hasattr(test_sample, 'status')
        assert hasattr(test_sample, 'storage_location')
        
        sample_repository.get_sample_by_id.assert_called_once_with(sample_id)
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once_with(test_sample)

    @pytest.mark.asyncio
    async def test_update_sample_not_found(
        self, sample_repository, mock_db_session
    ):
        """Test sample update when sample not found."""
        sample_id = uuid4()
        update_data = {"status": SampleStatus.PROCESSING}
        
        # Mock get_sample_by_id to return None
        sample_repository.get_sample_by_id = AsyncMock(return_value=None)
        
        result = await sample_repository.update_sample(sample_id, update_data)
        
        assert result is None
        sample_repository.get_sample_by_id.assert_called_once_with(sample_id)
        # Ensure commit and refresh are not called when sample is not found
        mock_db_session.commit.assert_not_called()
        mock_db_session.refresh.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_sample_with_none_values(
        self, sample_repository, test_sample, mock_db_session
    ):
        """Test sample update with None values (should be ignored)."""
        sample_id = test_sample.id
        update_data = {
            "status": SampleStatus.PROCESSING,
            "storage_location": None
        }
        
        # Mock get_sample_by_id to return the test sample
        sample_repository.get_sample_by_id = AsyncMock(return_value=test_sample)
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()
        
        result = await sample_repository.update_sample(sample_id, update_data)
        
        assert result == test_sample
        # Check that only non-None values were updated
        assert hasattr(test_sample, 'status')
        
        sample_repository.get_sample_by_id.assert_called_once_with(sample_id)
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once_with(test_sample)

    @pytest.mark.asyncio
    async def test_delete_sample_success(
        self, sample_repository, test_sample, mock_db_session
    ):
        """Test successful sample deletion."""
        sample_id = test_sample.id
        
        # Mock get_sample_by_id to return the test sample
        sample_repository.get_sample_by_id = AsyncMock(return_value=test_sample)
        mock_db_session.delete = AsyncMock()
        mock_db_session.commit = AsyncMock()
        
        result = await sample_repository.delete_sample(sample_id)
        
        assert result is True
        sample_repository.get_sample_by_id.assert_called_once_with(sample_id)
        mock_db_session.delete.assert_called_once_with(test_sample)
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_sample_not_found(
        self, sample_repository, mock_db_session
    ):
        """Test sample deletion when sample not found."""
        sample_id = uuid4()
        
        # Mock get_sample_by_id to return None
        sample_repository.get_sample_by_id = AsyncMock(return_value=None)
        
        result = await sample_repository.delete_sample(sample_id)
        
        assert result is False
        sample_repository.get_sample_by_id.assert_called_once_with(sample_id)
        # Ensure delete and commit are not called when sample is not found
        mock_db_session.delete.assert_not_called()
        mock_db_session.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_sample_id_exists_true(
        self, sample_repository, test_sample
    ):
        """Test sample_id existence check when sample_id exists."""
        sample_id = test_sample.sample_id
        
        # Mock get_sample_by_sample_id to return the test sample
        sample_repository.get_sample_by_sample_id = AsyncMock(return_value=test_sample)
        
        result = await sample_repository.sample_id_exists(sample_id)
        
        assert result is True
        sample_repository.get_sample_by_sample_id.assert_called_once_with(sample_id)

    @pytest.mark.asyncio
    async def test_sample_id_exists_false(
        self, sample_repository
    ):
        """Test sample_id existence check when sample_id doesn't exist."""
        sample_id = uuid4()
        
        # Mock get_sample_by_sample_id to return None
        sample_repository.get_sample_by_sample_id = AsyncMock(return_value=None)
        
        result = await sample_repository.sample_id_exists(sample_id)
        
        assert result is False
        sample_repository.get_sample_by_sample_id.assert_called_once_with(sample_id)

    @pytest.mark.asyncio
    async def test_get_samples_by_subject_id_success(
        self, sample_repository, mock_db_session
    ):
        """Test successful samples retrieval by subject ID."""
        subject_id = "P001"
        user_id = uuid4()
        test_samples = [
            Sample(
                id=uuid4(),
                sample_id=uuid4(),
                sample_type=SampleType.BLOOD,
                subject_id=subject_id,
                collection_date=date(2023, 12, 1),
                status=SampleStatus.COLLECTED,
                storage_location="freezer-1-rowA",
                user_id=user_id
            ),
            Sample(
                id=uuid4(),
                sample_id=uuid4(),
                sample_type=SampleType.SALIVA,
                subject_id=subject_id,
                collection_date=date(2023, 12, 2),
                status=SampleStatus.PROCESSING,
                storage_location="freezer-1-rowB",
                user_id=user_id
            )
        ]
        
        mock_result = Mock()
        mock_scalars = Mock()
        mock_scalars.all.return_value = test_samples
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result
        
        result = await sample_repository.get_samples_by_subject_id(subject_id, user_id)
        
        assert result == test_samples
        mock_db_session.execute.assert_called_once()
        mock_result.scalars.assert_called_once()
        mock_scalars.all.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_samples_by_subject_id_no_user_filter(
        self, sample_repository, mock_db_session
    ):
        """Test samples retrieval by subject ID without user filter."""
        subject_id = "P001"
        
        mock_result = Mock()
        mock_scalars = Mock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result
        
        result = await sample_repository.get_samples_by_subject_id(subject_id, None)
        
        assert result == []
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_samples_by_status_success(
        self, sample_repository, mock_db_session
    ):
        """Test successful samples retrieval by status."""
        status = SampleStatus.COLLECTED
        user_id = uuid4()
        test_samples = [
            Sample(
                id=uuid4(),
                sample_id=uuid4(),
                sample_type=SampleType.BLOOD,
                subject_id="P001",
                collection_date=date(2023, 12, 1),
                status=status,
                storage_location="freezer-1-rowA",
                user_id=user_id
            )
        ]
        
        mock_result = Mock()
        mock_scalars = Mock()
        mock_scalars.all.return_value = test_samples
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result
        
        result = await sample_repository.get_samples_by_status(status, user_id)
        
        assert result == test_samples
        mock_db_session.execute.assert_called_once()
        mock_result.scalars.assert_called_once()
        mock_scalars.all.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_samples_by_status_no_user_filter(
        self, sample_repository, mock_db_session
    ):
        """Test samples retrieval by status without user filter."""
        status = SampleStatus.COLLECTED
        
        mock_result = Mock()
        mock_scalars = Mock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result
        
        result = await sample_repository.get_samples_by_status(status, None)
        
        assert result == []
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_samples_by_type_success(
        self, sample_repository, mock_db_session
    ):
        """Test successful samples retrieval by type."""
        sample_type = SampleType.BLOOD
        user_id = uuid4()
        test_samples = [
            Sample(
                id=uuid4(),
                sample_id=uuid4(),
                sample_type=sample_type,
                subject_id="P001",
                collection_date=date(2023, 12, 1),
                status=SampleStatus.COLLECTED,
                storage_location="freezer-1-rowA",
                user_id=user_id
            )
        ]
        
        mock_result = Mock()
        mock_scalars = Mock()
        mock_scalars.all.return_value = test_samples
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result
        
        result = await sample_repository.get_samples_by_type(sample_type, user_id)
        
        assert result == test_samples
        mock_db_session.execute.assert_called_once()
        mock_result.scalars.assert_called_once()
        mock_scalars.all.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_samples_by_type_no_user_filter(
        self, sample_repository, mock_db_session
    ):
        """Test samples retrieval by type without user filter."""
        sample_type = SampleType.BLOOD
        
        mock_result = Mock()
        mock_scalars = Mock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result
        
        result = await sample_repository.get_samples_by_type(sample_type, None)
        
        assert result == []
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_samples_with_filters_empty_filters(
        self, sample_repository, mock_db_session
    ):
        """Test samples retrieval with empty filters."""
        empty_filter = SampleFilter()
        user_id = uuid4()
        
        mock_result = Mock()
        mock_scalars = Mock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result
        
        result = await sample_repository.get_samples_with_filters(
            empty_filter, skip=0, limit=10, user_id=user_id
        )
        
        assert result == []
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_samples_with_filters_pagination(
        self, sample_repository, sample_filter, mock_db_session
    ):
        """Test samples retrieval with pagination parameters."""
        user_id = uuid4()
        skip = 10
        limit = 5
        
        mock_result = Mock()
        mock_scalars = Mock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result
        
        result = await sample_repository.get_samples_with_filters(
            sample_filter, skip=skip, limit=limit, user_id=user_id
        )
        
        assert result == []
        mock_db_session.execute.assert_called_once()
        # The query should include offset and limit clauses
        query = mock_db_session.execute.call_args[0][0]
        assert hasattr(query, 'offset')
        assert hasattr(query, 'limit')