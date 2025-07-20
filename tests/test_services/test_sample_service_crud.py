"""
Basic Sample CRUD Tests for Clinical Sample Service.

These tests cover the fundamental CRUD operations for samples:
- Creating samples with valid data
- Updating samples while preserving data isolation
- Deleting samples and verifying removal
- Retrieving samples by ID
- Handling not found errors appropriately
"""

from datetime import date
from uuid import uuid4

import pytest

from app.core.exceptions import AuthorizationError, NotFoundError
from app.models.sample import SampleStatus, SampleType
from app.models.user import User
from app.schemas.sample import SampleCreate, SampleUpdate
from app.services.sample_service import SampleService


@pytest.mark.asyncio
@pytest.mark.samples
@pytest.mark.crud
class TestSampleCRUD:
    """Basic CRUD operation tests for Sample service."""

    async def test_create_sample_with_valid_data(
        self, sample_service: SampleService, test_user1: User
    ):
        """
        Test creating a sample with valid data.

        Verifies that all fields are saved correctly and user_id is properly assigned.
        """
        # Arrange
        sample_data = SampleCreate(
            sample_type=SampleType.BLOOD,
            subject_id="P999",
            collection_date=date(2024, 3, 15),
            status=SampleStatus.COLLECTED,
            storage_location="freezer-1-rowC",
        )

        # Act
        created_sample = await sample_service.create_sample(sample_data, test_user1)

        # Assert
        assert created_sample is not None, "Created sample should not be None"
        assert (
            created_sample.sample_type == SampleType.BLOOD
        ), "Sample type should match input"
        assert created_sample.subject_id == "P999", "Subject ID should match input"
        assert created_sample.collection_date == date(
            2024, 3, 15
        ), "Collection date should match input"
        assert (
            created_sample.status == SampleStatus.COLLECTED
        ), "Status should match input"
        assert (
            created_sample.storage_location == "freezer-1-rowC"
        ), "Storage location should match input"

        # Verify UUID fields are generated
        assert created_sample.id is not None, "Sample record ID should be generated"
        assert (
            created_sample.sample_id is not None
        ), "Sample tracking ID should be generated"

        # Verify timestamps are set
        assert created_sample.created_at is not None, "Created timestamp should be set"
        assert created_sample.updated_at is not None, "Updated timestamp should be set"

        # Verify we can retrieve the created sample by ID to confirm it's persisted
        retrieved_sample = await sample_service.get_sample_by_id(
            created_sample.id, test_user1
        )
        assert str(retrieved_sample.id) == str(
            created_sample.id
        ), "Retrieved sample should match created sample"

    async def test_update_sample_fields(
        self, sample_service: SampleService, test_user1: User
    ):
        """
        Test updating sample fields with valid data.

        Verifies that changes are applied correctly and immutable fields remain unchanged.
        """
        # Arrange - Create a sample first
        original_sample_data = SampleCreate(
            sample_type=SampleType.SALIVA,
            subject_id="P888",
            collection_date=date(2024, 2, 10),
            status=SampleStatus.COLLECTED,
            storage_location="room-1-shelfA",
        )
        created_sample = await sample_service.create_sample(
            original_sample_data, test_user1
        )
        original_created_at = created_sample.created_at
        original_updated_at = created_sample.updated_at

        # Act - Update the sample
        update_data = SampleUpdate(
            sample_type=SampleType.TISSUE,
            subject_id="P777",  # Valid subject ID format
            status=SampleStatus.PROCESSING,
            storage_location="freezer-2-rowA",
        )
        updated_sample = await sample_service.update_sample(
            created_sample.id, update_data, test_user1
        )

        # Assert - Verify changes were applied
        assert (
            updated_sample.sample_type == SampleType.TISSUE
        ), "Sample type should be updated"
        assert updated_sample.subject_id == "P777", "Subject ID should be updated"
        assert (
            updated_sample.status == SampleStatus.PROCESSING
        ), "Status should be updated"
        assert (
            updated_sample.storage_location == "freezer-2-rowA"
        ), "Storage location should be updated"

        # Verify immutable fields remain unchanged
        assert updated_sample.collection_date == date(
            2024, 2, 10
        ), "Collection date should remain unchanged"
        assert str(updated_sample.id) == str(
            created_sample.id
        ), "Record ID should remain unchanged"
        assert str(updated_sample.sample_id) == str(
            created_sample.sample_id
        ), "Sample tracking ID should remain unchanged"

        # Verify timestamps behavior
        assert updated_sample.created_at is not None, "Created timestamp should exist"
        assert updated_sample.updated_at is not None, "Updated timestamp should exist"
        assert (
            updated_sample.updated_at >= original_updated_at
        ), "Updated timestamp should be newer or equal"

    async def test_update_preserves_user_isolation(
        self, sample_service: SampleService, test_user1: User, test_user2: User
    ):
        """
        Test that updating a sample preserves user isolation.

        Verifies that after update, the original user still has access
        and other users still cannot access the sample.
        """
        # Arrange - Create a sample
        sample_data = SampleCreate(
            sample_type=SampleType.BLOOD,
            subject_id="P555",
            collection_date=date(2024, 3, 1),
            status=SampleStatus.COLLECTED,
            storage_location="freezer-1-rowB",
        )
        created_sample = await sample_service.create_sample(sample_data, test_user1)

        # Act - Update the sample
        update_data = SampleUpdate(status=SampleStatus.PROCESSING)
        updated_sample = await sample_service.update_sample(
            created_sample.id, update_data, test_user1
        )

        # Assert - Verify user1 still has access
        retrieved_sample = await sample_service.get_sample_by_id(
            updated_sample.id, test_user1
        )
        assert (
            retrieved_sample is not None
        ), "Original user should still have access after update"

        # Assert - Verify user2 still cannot access
        with pytest.raises(AuthorizationError):
            await sample_service.get_sample_by_id(updated_sample.id, test_user2)

    async def test_delete_existing_sample(
        self, sample_service: SampleService, test_user1: User
    ):
        """
        Test deleting an existing sample.

        Verifies that the sample is removed and no longer accessible.
        """
        # Arrange - Create a sample first
        sample_data = SampleCreate(
            sample_type=SampleType.BLOOD,
            subject_id="P777",
            collection_date=date(2024, 1, 20),
            status=SampleStatus.ARCHIVED,
            storage_location="freezer-3-rowB",
        )
        created_sample = await sample_service.create_sample(sample_data, test_user1)
        sample_id = created_sample.id

        # Verify sample exists before deletion
        sample_exists_before = await sample_service.get_sample_by_id(
            sample_id, test_user1
        )
        assert sample_exists_before is not None, "Sample should exist before deletion"

        # Act - Delete the sample
        delete_result = await sample_service.delete_sample(sample_id, test_user1)

        # Assert - Verify deletion response
        assert delete_result is not None, "Delete operation should return a result"
        assert "message" in delete_result, "Delete result should contain a message"
        assert (
            "success" in delete_result["message"].lower()
        ), "Delete message should indicate success"

        # Verify sample no longer exists
        with pytest.raises(NotFoundError) as exc_info:
            await sample_service.get_sample_by_id(sample_id, test_user1)

        assert "Sample" in str(exc_info.value), "Error should indicate Sample not found"
        assert str(sample_id) in str(
            exc_info.value
        ), "Error should include the sample ID"

    async def test_get_sample_by_id(
        self, sample_service: SampleService, test_user1: User
    ):
        """
        Test retrieving a sample by ID.

        Verifies that the correct sample is returned with all data intact.
        """
        # Arrange - Create a sample with specific data
        expected_data = SampleCreate(
            sample_type=SampleType.TISSUE,
            subject_id="P666",
            collection_date=date(2024, 4, 5),
            status=SampleStatus.PROCESSING,
            storage_location="freezer-1-rowD",
        )
        created_sample = await sample_service.create_sample(expected_data, test_user1)

        # Act - Retrieve the sample by ID
        retrieved_sample = await sample_service.get_sample_by_id(
            created_sample.id, test_user1
        )

        # Assert - Verify all data matches
        assert retrieved_sample is not None, "Retrieved sample should not be None"
        assert str(retrieved_sample.id) == str(created_sample.id), "IDs should match"
        assert str(retrieved_sample.sample_id) == str(
            created_sample.sample_id
        ), "Sample tracking IDs should match"

        # Verify all business data fields
        assert (
            retrieved_sample.sample_type == expected_data.sample_type
        ), "Sample type should match"
        assert (
            retrieved_sample.subject_id == expected_data.subject_id
        ), "Subject ID should match"
        assert (
            retrieved_sample.collection_date == expected_data.collection_date
        ), "Collection date should match"
        assert retrieved_sample.status == expected_data.status, "Status should match"
        assert (
            retrieved_sample.storage_location == expected_data.storage_location
        ), "Storage location should match"

        # Verify timestamps are properly set
        assert retrieved_sample.created_at is not None, "Created timestamp should exist"
        assert retrieved_sample.updated_at is not None, "Updated timestamp should exist"
        assert (
            retrieved_sample.updated_at >= retrieved_sample.created_at
        ), "Updated timestamp should be >= created timestamp"

        # Verify data types are correct
        assert isinstance(
            retrieved_sample.sample_type, SampleType
        ), "Sample type should be enum"
        assert isinstance(
            retrieved_sample.status, SampleStatus
        ), "Status should be enum"
        assert isinstance(
            retrieved_sample.collection_date, date
        ), "Collection date should be date object"

    async def test_sample_not_found_error(
        self, sample_service: SampleService, test_user1: User
    ):
        """
        Test that attempting to get a non-existent sample returns NotFoundError.

        Verifies proper error handling for invalid sample IDs.
        """
        # Arrange - Generate a random UUID that doesn't exist
        non_existent_id = uuid4()

        # Act & Assert - Attempt to retrieve non-existent sample
        with pytest.raises(NotFoundError) as exc_info:
            await sample_service.get_sample_by_id(non_existent_id, test_user1)

        # Verify error details
        error = exc_info.value
        assert "Sample" in str(error), "Error should indicate Sample resource"
        assert str(non_existent_id) in str(
            error
        ), "Error should include the requested ID"

        # Verify error message is informative
        # NotFoundError stores the resource and resource_id in constructor parameters
        # but they're not directly exposed as attributes - they're used to build the message

        # Test with update operation on non-existent sample
        update_data = SampleUpdate(status=SampleStatus.ARCHIVED)
        with pytest.raises(NotFoundError) as exc_info:
            await sample_service.update_sample(non_existent_id, update_data, test_user1)

        assert "Sample" in str(
            exc_info.value
        ), "Update error should indicate Sample not found"
        assert str(non_existent_id) in str(
            exc_info.value
        ), "Update error should include the sample ID"

        # Test with delete operation on non-existent sample
        with pytest.raises(NotFoundError) as exc_info:
            await sample_service.delete_sample(non_existent_id, test_user1)

        assert "Sample" in str(
            exc_info.value
        ), "Delete error should indicate Sample not found"
        assert str(non_existent_id) in str(
            exc_info.value
        ), "Delete error should include the sample ID"
