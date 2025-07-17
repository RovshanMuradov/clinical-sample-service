"""Tests for SampleService."""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4, UUID
from datetime import date, datetime

from app.services.sample_service import SampleService
from app.models.user import User
from app.models.sample import Sample, SampleStatus, SampleType
from app.schemas.sample import SampleCreate, SampleUpdate, SampleFilter, SampleResponse
from app.core.exceptions import AuthorizationError, NotFoundError, ValidationError


class TestSampleService:
    """Test SampleService functionality."""

    @pytest.fixture
    def mock_db_session(self):
        """Create mock database session."""
        return Mock()

    @pytest.fixture
    def mock_sample_repository(self):
        """Create mock sample repository."""
        return Mock()

    @pytest.fixture
    def sample_service(self, mock_db_session, mock_sample_repository):
        """Create SampleService instance with mocked dependencies."""
        service = SampleService(mock_db_session)
        service.sample_repository = mock_sample_repository
        return service

    @pytest.fixture
    def test_user(self):
        """Create test user."""
        return User(
            id=uuid4(),
            username="testuser",
            email="test@example.com",
            hashed_password="$2b$12$test_hash",
            is_active=True
        )

    @pytest.fixture
    def test_sample(self, test_user):
        """Create test sample."""
        now = datetime.now()
        return Sample(
            id=uuid4(),
            sample_id=uuid4(),
            sample_type=SampleType.BLOOD,
            subject_id="P001",
            collection_date=date(2023, 12, 1),
            status=SampleStatus.COLLECTED,
            storage_location="freezer-1-rowA",
            user_id=test_user.id,
            created_at=now,
            updated_at=now
        )

    @pytest.fixture
    def sample_create_data(self):
        """Create SampleCreate data."""
        return SampleCreate(
            sample_type=SampleType.BLOOD,
            subject_id="P001",
            collection_date=date(2023, 12, 1),
            status=SampleStatus.COLLECTED,
            storage_location="freezer-1-rowA"
        )

    @pytest.fixture
    def sample_update_data(self):
        """Create SampleUpdate data."""
        return SampleUpdate(
            status=SampleStatus.PROCESSING,
            storage_location="freezer-2-rowB"
        )

    @pytest.fixture
    def sample_filter(self):
        """Create SampleFilter data."""
        return SampleFilter(
            sample_type=SampleType.BLOOD,
            subject_id="P001"
        )

    @pytest.mark.asyncio
    async def test_create_sample_success(
        self, sample_service, sample_create_data, test_user, test_sample, mock_sample_repository
    ):
        """Test successful sample creation."""
        mock_sample_repository.create_sample = AsyncMock(return_value=test_sample)
        
        result = await sample_service.create_sample(sample_create_data, test_user)
        
        assert isinstance(result, SampleResponse)
        assert result.sample_type == sample_create_data.sample_type
        assert result.subject_id == sample_create_data.subject_id
        
        # Check that user_id was added to the sample data
        mock_sample_repository.create_sample.assert_called_once()
        call_args = mock_sample_repository.create_sample.call_args[0][0]
        assert call_args["user_id"] == test_user.id

    @pytest.mark.asyncio
    async def test_get_sample_by_id_success(
        self, sample_service, test_sample, test_user, mock_sample_repository
    ):
        """Test successful sample retrieval by ID."""
        mock_sample_repository.get_sample_by_id = AsyncMock(return_value=test_sample)
        
        result = await sample_service.get_sample_by_id(test_sample.id, test_user)
        
        assert isinstance(result, SampleResponse)
        assert result.id == test_sample.id
        mock_sample_repository.get_sample_by_id.assert_called_once_with(test_sample.id)

    @pytest.mark.asyncio
    async def test_get_sample_by_id_not_found(
        self, sample_service, test_user, mock_sample_repository
    ):
        """Test sample retrieval when sample not found."""
        sample_id = uuid4()
        mock_sample_repository.get_sample_by_id = AsyncMock(return_value=None)
        
        with pytest.raises(NotFoundError) as exc_info:
            await sample_service.get_sample_by_id(sample_id, test_user)
        
        assert "Sample" in str(exc_info.value)
        mock_sample_repository.get_sample_by_id.assert_called_once_with(sample_id)

    @pytest.mark.asyncio
    async def test_get_sample_by_id_unauthorized(
        self, sample_service, test_sample, mock_sample_repository
    ):
        """Test sample retrieval when user doesn't own the sample."""
        other_user = User(
            id=uuid4(),
            username="otheruser",
            email="other@example.com",
            hashed_password="$2b$12$test_hash",
            is_active=True
        )
        mock_sample_repository.get_sample_by_id = AsyncMock(return_value=test_sample)
        
        with pytest.raises(AuthorizationError) as exc_info:
            await sample_service.get_sample_by_id(test_sample.id, other_user)
        
        assert "Access denied" in str(exc_info.value)
        mock_sample_repository.get_sample_by_id.assert_called_once_with(test_sample.id)

    @pytest.mark.asyncio
    async def test_get_samples_success(
        self, sample_service, sample_filter, test_user, mock_sample_repository
    ):
        """Test successful samples retrieval with filtering."""
        now = datetime.now()
        test_samples = [
            Sample(
                id=uuid4(),
                sample_id=uuid4(),
                sample_type=SampleType.BLOOD,
                subject_id="P001",
                collection_date=date(2023, 12, 1),
                status=SampleStatus.COLLECTED,
                storage_location="freezer-1-rowA",
                user_id=test_user.id,
                created_at=now,
                updated_at=now
            ),
            Sample(
                id=uuid4(),
                sample_id=uuid4(),
                sample_type=SampleType.BLOOD,
                subject_id="P001",
                collection_date=date(2023, 12, 2),
                status=SampleStatus.PROCESSING,
                storage_location="freezer-1-rowB",
                user_id=test_user.id,
                created_at=now,
                updated_at=now
            )
        ]
        
        mock_sample_repository.get_samples_with_filters = AsyncMock(return_value=test_samples)
        mock_sample_repository.count_samples_with_filters = AsyncMock(return_value=2)
        
        result = await sample_service.get_samples(sample_filter, 0, 10, test_user)
        
        assert len(result.samples) == 2
        assert result.total == 2
        assert result.skip == 0
        assert result.limit == 10
        
        mock_sample_repository.get_samples_with_filters.assert_called_once_with(
            sample_filter, 0, 10, test_user.id
        )
        mock_sample_repository.count_samples_with_filters.assert_called_once_with(
            sample_filter, test_user.id
        )

    @pytest.mark.asyncio
    async def test_get_samples_invalid_skip(
        self, sample_service, sample_filter, test_user
    ):
        """Test samples retrieval with invalid skip parameter."""
        with pytest.raises(ValidationError) as exc_info:
            await sample_service.get_samples(sample_filter, -1, 10, test_user)
        
        assert "Skip parameter must be non-negative" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_samples_invalid_limit(
        self, sample_service, sample_filter, test_user
    ):
        """Test samples retrieval with invalid limit parameter."""
        with pytest.raises(ValidationError) as exc_info:
            await sample_service.get_samples(sample_filter, 0, 0, test_user)
        
        assert "Limit parameter must be between 1 and 1000" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_samples_limit_too_high(
        self, sample_service, sample_filter, test_user
    ):
        """Test samples retrieval with limit too high."""
        with pytest.raises(ValidationError) as exc_info:
            await sample_service.get_samples(sample_filter, 0, 1001, test_user)
        
        assert "Limit parameter must be between 1 and 1000" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_sample_success(
        self, sample_service, test_sample, sample_update_data, test_user, mock_sample_repository
    ):
        """Test successful sample update."""
        updated_sample = Sample(
            id=test_sample.id,
            sample_id=test_sample.sample_id,
            sample_type=test_sample.sample_type,
            subject_id=test_sample.subject_id,
            collection_date=test_sample.collection_date,
            status=SampleStatus.PROCESSING,
            storage_location="freezer-2-rowB",
            user_id=test_sample.user_id,
            created_at=test_sample.created_at,
            updated_at=datetime.now()
        )
        
        mock_sample_repository.get_sample_by_id = AsyncMock(return_value=test_sample)
        mock_sample_repository.update_sample = AsyncMock(return_value=updated_sample)
        
        result = await sample_service.update_sample(test_sample.id, sample_update_data, test_user)
        
        assert isinstance(result, SampleResponse)
        assert result.status == SampleStatus.PROCESSING
        assert result.storage_location == "freezer-2-rowB"
        
        mock_sample_repository.get_sample_by_id.assert_called_once_with(test_sample.id)
        mock_sample_repository.update_sample.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_sample_not_found(
        self, sample_service, sample_update_data, test_user, mock_sample_repository
    ):
        """Test sample update when sample not found."""
        sample_id = uuid4()
        mock_sample_repository.get_sample_by_id = AsyncMock(return_value=None)
        
        with pytest.raises(NotFoundError) as exc_info:
            await sample_service.update_sample(sample_id, sample_update_data, test_user)
        
        assert "Sample" in str(exc_info.value)
        mock_sample_repository.get_sample_by_id.assert_called_once_with(sample_id)

    @pytest.mark.asyncio
    async def test_update_sample_unauthorized(
        self, sample_service, test_sample, sample_update_data, mock_sample_repository
    ):
        """Test sample update when user doesn't own the sample."""
        other_user = User(
            id=uuid4(),
            username="otheruser",
            email="other@example.com",
            hashed_password="$2b$12$test_hash",
            is_active=True
        )
        mock_sample_repository.get_sample_by_id = AsyncMock(return_value=test_sample)
        
        with pytest.raises(AuthorizationError) as exc_info:
            await sample_service.update_sample(test_sample.id, sample_update_data, other_user)
        
        assert "Access denied" in str(exc_info.value)
        mock_sample_repository.get_sample_by_id.assert_called_once_with(test_sample.id)

    @pytest.mark.asyncio
    async def test_update_sample_repository_returns_none(
        self, sample_service, test_sample, sample_update_data, test_user, mock_sample_repository
    ):
        """Test sample update when repository returns None."""
        mock_sample_repository.get_sample_by_id = AsyncMock(return_value=test_sample)
        mock_sample_repository.update_sample = AsyncMock(return_value=None)
        
        with pytest.raises(NotFoundError) as exc_info:
            await sample_service.update_sample(test_sample.id, sample_update_data, test_user)
        
        assert "Sample" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_delete_sample_success(
        self, sample_service, test_sample, test_user, mock_sample_repository
    ):
        """Test successful sample deletion."""
        mock_sample_repository.get_sample_by_id = AsyncMock(return_value=test_sample)
        mock_sample_repository.delete_sample = AsyncMock(return_value=True)
        
        result = await sample_service.delete_sample(test_sample.id, test_user)
        
        assert result["message"] == "Sample deleted successfully"
        mock_sample_repository.get_sample_by_id.assert_called_once_with(test_sample.id)
        mock_sample_repository.delete_sample.assert_called_once_with(test_sample.id)

    @pytest.mark.asyncio
    async def test_delete_sample_not_found(
        self, sample_service, test_user, mock_sample_repository
    ):
        """Test sample deletion when sample not found."""
        sample_id = uuid4()
        mock_sample_repository.get_sample_by_id = AsyncMock(return_value=None)
        
        with pytest.raises(NotFoundError) as exc_info:
            await sample_service.delete_sample(sample_id, test_user)
        
        assert "Sample" in str(exc_info.value)
        mock_sample_repository.get_sample_by_id.assert_called_once_with(sample_id)

    @pytest.mark.asyncio
    async def test_delete_sample_unauthorized(
        self, sample_service, test_sample, mock_sample_repository
    ):
        """Test sample deletion when user doesn't own the sample."""
        other_user = User(
            id=uuid4(),
            username="otheruser",
            email="other@example.com",
            hashed_password="$2b$12$test_hash",
            is_active=True
        )
        mock_sample_repository.get_sample_by_id = AsyncMock(return_value=test_sample)
        
        with pytest.raises(AuthorizationError) as exc_info:
            await sample_service.delete_sample(test_sample.id, other_user)
        
        assert "Access denied" in str(exc_info.value)
        mock_sample_repository.get_sample_by_id.assert_called_once_with(test_sample.id)

    @pytest.mark.asyncio
    async def test_delete_sample_repository_returns_false(
        self, sample_service, test_sample, test_user, mock_sample_repository
    ):
        """Test sample deletion when repository returns False."""
        mock_sample_repository.get_sample_by_id = AsyncMock(return_value=test_sample)
        mock_sample_repository.delete_sample = AsyncMock(return_value=False)
        
        with pytest.raises(NotFoundError) as exc_info:
            await sample_service.delete_sample(test_sample.id, test_user)
        
        assert "Sample" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_samples_by_subject_id_success(
        self, sample_service, test_user, mock_sample_repository
    ):
        """Test successful samples retrieval by subject ID."""
        subject_id = "P001"
        now = datetime.now()
        test_samples = [
            Sample(
                id=uuid4(),
                sample_id=uuid4(),
                sample_type=SampleType.BLOOD,
                subject_id=subject_id,
                collection_date=date(2023, 12, 1),
                status=SampleStatus.COLLECTED,
                storage_location="freezer-1-rowA",
                user_id=test_user.id,
                created_at=now,
                updated_at=now
            ),
            Sample(
                id=uuid4(),
                sample_id=uuid4(),
                sample_type=SampleType.SALIVA,
                subject_id=subject_id,
                collection_date=date(2023, 12, 2),
                status=SampleStatus.PROCESSING,
                storage_location="freezer-1-rowB",
                user_id=test_user.id,
                created_at=now,
                updated_at=now
            )
        ]
        
        mock_sample_repository.get_samples_by_subject_id = AsyncMock(return_value=test_samples)
        
        result = await sample_service.get_samples_by_subject_id(subject_id, test_user)
        
        assert len(result) == 2
        assert all(isinstance(sample, SampleResponse) for sample in result)
        assert all(sample.subject_id == subject_id for sample in result)
        
        mock_sample_repository.get_samples_by_subject_id.assert_called_once_with(
            subject_id, test_user.id
        )

    @pytest.mark.asyncio
    async def test_get_sample_statistics_success(
        self, sample_service, test_user, mock_sample_repository
    ):
        """Test successful sample statistics retrieval."""
        # Mock repository responses for different status and type queries
        collected_samples = [Mock(), Mock()]  # 2 collected samples
        processing_samples = [Mock()]  # 1 processing sample
        archived_samples = []  # 0 archived samples
        
        blood_samples = [Mock(), Mock()]  # 2 blood samples
        saliva_samples = [Mock()]  # 1 saliva sample
        tissue_samples = []  # 0 tissue samples
        
        mock_sample_repository.get_samples_by_status = AsyncMock(side_effect=[
            collected_samples,
            processing_samples,
            archived_samples
        ])
        
        mock_sample_repository.get_samples_by_type = AsyncMock(side_effect=[
            blood_samples,
            saliva_samples,
            tissue_samples
        ])
        
        result = await sample_service.get_sample_statistics(test_user)
        
        assert result["total_samples"] == 3  # 2 + 1 + 0
        assert result["by_status"]["collected"] == 2
        assert result["by_status"]["processing"] == 1
        assert result["by_status"]["archived"] == 0
        assert result["by_type"]["blood"] == 2
        assert result["by_type"]["saliva"] == 1
        assert result["by_type"]["tissue"] == 0
        
        # Check that all status queries were made with user_id
        status_calls = mock_sample_repository.get_samples_by_status.call_args_list
        assert len(status_calls) == 3
        for call in status_calls:
            assert call[0][1] == test_user.id  # user_id parameter
        
        # Check that all type queries were made with user_id
        type_calls = mock_sample_repository.get_samples_by_type.call_args_list
        assert len(type_calls) == 3
        for call in type_calls:
            assert call[0][1] == test_user.id  # user_id parameter

    @pytest.mark.asyncio
    async def test_get_samples_without_user(
        self, sample_service, sample_filter, mock_sample_repository
    ):
        """Test samples retrieval without user (should still work for system queries)."""
        test_samples = []
        mock_sample_repository.get_samples_with_filters = AsyncMock(return_value=test_samples)
        mock_sample_repository.count_samples_with_filters = AsyncMock(return_value=0)
        
        result = await sample_service.get_samples(sample_filter, 0, 10, None)
        
        assert len(result.samples) == 0
        assert result.total == 0
        
        mock_sample_repository.get_samples_with_filters.assert_called_once_with(
            sample_filter, 0, 10, None
        )
        mock_sample_repository.count_samples_with_filters.assert_called_once_with(
            sample_filter, None
        )