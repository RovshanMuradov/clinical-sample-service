"""
Critical Authorization Tests for Clinical Sample Service.

These tests are CRITICAL for medical data protection - they ensure that users
can only modify, delete, and access their own samples and never perform
unauthorized operations on other users' data.

Tests verify:
1. Users cannot update samples belonging to other users
2. Users cannot delete samples belonging to other users
3. Users cannot view samples belonging to other users by ID
4. Sample creation correctly assigns the authenticated user
"""
from datetime import date

import pytest

from app.core.exceptions import AuthorizationError
from app.models.sample import Sample, SampleStatus, SampleType
from app.models.user import User
from app.schemas.sample import SampleCreate, SampleUpdate
from app.services.sample_service import SampleService

# from uuid import uuid4  # Removed unused import




@pytest.mark.asyncio
@pytest.mark.auth
@pytest.mark.samples
class TestSampleServiceAuthorization:
    """Critical authorization tests for sample operations."""

    async def test_cannot_update_other_user_sample(
        self,
        sample_service: SampleService,
        test_user1: User,
        test_user2: User,
        test_samples_user1: list[Sample],
    ):
        """
        CRITICAL: Test that User2 cannot update User1's sample.

        This ensures users cannot modify medical data belonging to other users.
        """
        # Get User1's first sample
        user1_sample = test_samples_user1[0]

        # User2 tries to update User1's sample - should raise AuthorizationError
        update_data = SampleUpdate(
            status=SampleStatus.PROCESSING, storage_location="freezer-2-rowC"
        )

        with pytest.raises(AuthorizationError) as exc_info:
            await sample_service.update_sample(
                sample_id=user1_sample.id,
                sample_data=update_data,
                current_user=test_user2,
            )

        # Verify the error details
        assert "Access denied to sample" in str(exc_info.value)
        assert str(user1_sample.id) in str(exc_info.value.details)

        # Verify User1 can still update their own sample
        updated_sample = await sample_service.update_sample(
            sample_id=user1_sample.id, sample_data=update_data, current_user=test_user1
        )
        assert updated_sample.status == SampleStatus.PROCESSING
        assert updated_sample.storage_location == "freezer-2-rowC"

    async def test_cannot_delete_other_user_sample(
        self,
        sample_service: SampleService,
        test_user1: User,
        test_user2: User,
        test_samples_user1: list[Sample],
    ):
        """
        CRITICAL: Test that User2 cannot delete User1's sample.

        This prevents unauthorized deletion of medical data.
        """
        # Get User1's first sample
        user1_sample = test_samples_user1[0]

        # User2 tries to delete User1's sample - should raise AuthorizationError
        with pytest.raises(AuthorizationError) as exc_info:
            await sample_service.delete_sample(
                sample_id=user1_sample.id, current_user=test_user2
            )

        # Verify the error details
        assert "Access denied to sample" in str(exc_info.value)
        assert str(user1_sample.id) in str(exc_info.value.details)

        # Verify the sample still exists and User1 can access it
        sample_still_exists = await sample_service.get_sample_by_id(
            sample_id=user1_sample.id, current_user=test_user1
        )
        assert str(sample_still_exists.id) == str(user1_sample.id)

        # Verify User1 can delete their own sample
        delete_result = await sample_service.delete_sample(
            sample_id=user1_sample.id, current_user=test_user1
        )
        assert delete_result["message"] == "Sample deleted successfully"

    async def test_cannot_view_other_user_sample(
        self,
        sample_service: SampleService,
        test_user1: User,
        test_user2: User,
        test_samples_user1: list[Sample],
        test_samples_user2: list[Sample],
    ):
        """
        CRITICAL: Test that User2 cannot view User1's sample by ID.

        This prevents unauthorized access to medical records via direct ID access.
        """
        # User2 tries to view User1's first sample
        user1_sample_id = test_samples_user1[0].id

        with pytest.raises(AuthorizationError) as exc_info:
            await sample_service.get_sample_by_id(user1_sample_id, test_user2)

        # Verify the error details
        assert "Access denied to sample" in str(exc_info.value)
        assert str(user1_sample_id) in str(exc_info.value.details)

        # User1 tries to view User2's first sample
        user2_sample_id = test_samples_user2[0].id

        with pytest.raises(AuthorizationError) as exc_info:
            await sample_service.get_sample_by_id(user2_sample_id, test_user1)

        # Verify the error details
        assert "Access denied to sample" in str(exc_info.value)
        assert str(user2_sample_id) in str(exc_info.value.details)

        # But users can view their own samples
        user1_own_sample = await sample_service.get_sample_by_id(
            user1_sample_id, test_user1
        )
        assert str(user1_own_sample.id) == str(user1_sample_id)

        user2_own_sample = await sample_service.get_sample_by_id(
            user2_sample_id, test_user2
        )
        assert str(user2_own_sample.id) == str(user2_sample_id)

    async def test_sample_creation_assigns_correct_user(
        self,
        sample_service: SampleService,
        test_user1: User,
        test_user2: User,
    ):
        """
        CRITICAL: Test that sample creation correctly assigns the authenticated user.

        This ensures users cannot create samples attributed to other users.
        """
        # Create sample data
        sample_data = SampleCreate(
            sample_type=SampleType.BLOOD,
            subject_id="P999",
            collection_date=date(2024, 3, 15),
            status=SampleStatus.COLLECTED,
            storage_location="freezer-1-rowZ",
        )

        # User1 creates a sample
        user1_sample = await sample_service.create_sample(sample_data, test_user1)

        # Verify the sample was created and assigned to User1
        assert user1_sample.subject_id == "P999"
        assert user1_sample.sample_type == SampleType.BLOOD

        # Retrieve the sample to verify user assignment
        retrieved_sample = await sample_service.get_sample_by_id(
            user1_sample.id, test_user1
        )
        assert str(retrieved_sample.id) == str(user1_sample.id)

        # User2 should NOT be able to access User1's sample
        with pytest.raises(AuthorizationError) as exc_info:
            await sample_service.get_sample_by_id(user1_sample.id, test_user2)

        assert "Access denied to sample" in str(exc_info.value)
        assert str(user1_sample.id) in str(exc_info.value.details)

        # User2 creates their own sample with the same data
        user2_sample = await sample_service.create_sample(sample_data, test_user2)

        # Verify User2's sample is separate and different from User1's
        assert str(user2_sample.id) != str(user1_sample.id)
        assert user2_sample.subject_id == "P999"  # Same subject ID but different user

        # User2 can access their own sample
        user2_retrieved = await sample_service.get_sample_by_id(
            user2_sample.id, test_user2
        )
        assert str(user2_retrieved.id) == str(user2_sample.id)

        # User1 cannot access User2's sample
        with pytest.raises(AuthorizationError) as exc_info:
            await sample_service.get_sample_by_id(user2_sample.id, test_user1)

        assert "Access denied to sample" in str(exc_info.value)
        assert str(user2_sample.id) in str(exc_info.value.details)

        # Verify data isolation: each user sees only their own sample
        from app.schemas.sample import SampleFilter

        user1_samples = await sample_service.get_samples(
            filters=SampleFilter(subject_id="P999"),
            skip=0,
            limit=100,
            current_user=test_user1,
        )
        user2_samples = await sample_service.get_samples(
            filters=SampleFilter(subject_id="P999"),
            skip=0,
            limit=100,
            current_user=test_user2,
        )

        # Each user should see only 1 sample (their own)
        assert user1_samples.total == 1
        assert user2_samples.total == 1
        assert str(user1_samples.samples[0].id) == str(user1_sample.id)
        assert str(user2_samples.samples[0].id) == str(user2_sample.id)
