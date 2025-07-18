"""
Critical Data Isolation Tests for Clinical Sample Service.

These tests are CRITICAL for medical data protection - they ensure that users
can only access their own samples and never see or modify other users' data.
"""
# from uuid import uuid4  # Removed unused import

import pytest

from app.core.exceptions import AuthorizationError
from app.models.sample import Sample, SampleStatus, SampleType
from app.models.user import User
from app.schemas.sample import SampleFilter
from app.services.sample_service import SampleService


@pytest.mark.asyncio
@pytest.mark.auth
@pytest.mark.samples
class TestDataIsolation:
    """Critical data isolation tests for medical data protection."""

    async def test_user_can_only_see_own_samples(
        self,
        sample_service: SampleService,
        test_user1: User,
        test_user2: User,
        test_samples_user1: list[Sample],
        test_samples_user2: list[Sample],
    ):
        """
        CRITICAL: Test that users can only see their own samples.

        This test ensures fundamental data isolation - a core security requirement
        for medical data systems.
        """
        # User1 should see only their own samples (3 samples)
        user1_samples = await sample_service.get_samples(
            filters=SampleFilter(),
            skip=0,
            limit=100,
            current_user=test_user1,
        )

        # User2 should see only their own samples (3 samples)
        user2_samples = await sample_service.get_samples(
            filters=SampleFilter(),
            skip=0,
            limit=100,
            current_user=test_user2,
        )

        # Verify counts
        assert (
            user1_samples.total == 3
        ), f"User1 should see 3 samples, got {user1_samples.total}"
        assert (
            user2_samples.total == 3
        ), f"User2 should see 3 samples, got {user2_samples.total}"

        # Verify all returned samples belong to the correct user
        for sample_response in user1_samples.samples:
            # Find the actual sample from test data
            actual_sample = next(
                (s for s in test_samples_user1 if str(s.id) == str(sample_response.id)),
                None,
            )
            assert (
                actual_sample is not None
            ), f"Sample {sample_response.id} not found in user1 test data"
            assert str(actual_sample.user_id) == str(
                test_user1.id
            ), "Sample should belong to user1"

        for sample_response in user2_samples.samples:
            # Find the actual sample from test data
            actual_sample = next(
                (s for s in test_samples_user2 if str(s.id) == str(sample_response.id)),
                None,
            )
            assert (
                actual_sample is not None
            ), f"Sample {sample_response.id} not found in user2 test data"
            assert str(actual_sample.user_id) == str(
                test_user2.id
            ), "Sample should belong to user2"

        # Verify no overlap between user samples
        user1_sample_ids = {str(s.id) for s in user1_samples.samples}
        user2_sample_ids = {str(s.id) for s in user2_samples.samples}

        assert (
            len(user1_sample_ids.intersection(user2_sample_ids)) == 0
        ), "Users should not see each other's samples"

    async def test_user_cannot_access_other_user_samples(
        self,
        sample_service: SampleService,
        test_user1: User,
        test_user2: User,
        test_samples_user1: list[Sample],
        test_samples_user2: list[Sample],
    ):
        """
        CRITICAL: Test that users cannot access other users' samples by ID.

        This prevents unauthorized access to medical records via direct ID access.
        """
        # User2 tries to access User1's first sample
        user1_sample_id = test_samples_user1[0].id

        with pytest.raises(AuthorizationError) as exc_info:
            await sample_service.get_sample_by_id(user1_sample_id, test_user2)

        assert "Access denied to sample" in str(exc_info.value)
        assert str(user1_sample_id) in str(exc_info.value.details)

        # User1 tries to access User2's first sample
        user2_sample_id = test_samples_user2[0].id

        with pytest.raises(AuthorizationError) as exc_info:
            await sample_service.get_sample_by_id(user2_sample_id, test_user1)

        assert "Access denied to sample" in str(exc_info.value)
        assert str(user2_sample_id) in str(exc_info.value.details)

        # But users can access their own samples
        user1_own_sample = await sample_service.get_sample_by_id(
            user1_sample_id, test_user1
        )
        assert str(user1_own_sample.id) == str(user1_sample_id)

        user2_own_sample = await sample_service.get_sample_by_id(
            user2_sample_id, test_user2
        )
        assert str(user2_own_sample.id) == str(user2_sample_id)

    async def test_statistics_only_show_user_data(
        self,
        sample_service: SampleService,
        test_user1: User,
        test_user2: User,
        test_samples_user1: list[Sample],
        test_samples_user2: list[Sample],
    ):
        """
        CRITICAL: Test that statistics show only current user's data.

        This was a critical security bug found in the system - statistics
        were showing data from all users instead of being isolated.
        """
        # Get statistics for User1
        user1_stats = await sample_service.get_sample_statistics(test_user1)

        # Get statistics for User2
        user2_stats = await sample_service.get_sample_statistics(test_user2)

        # User1 should have: 2 blood, 1 tissue, 0 saliva
        # Status: 1 collected, 1 processing, 1 archived
        assert (
            user1_stats["total_samples"] == 3
        ), f"User1 total should be 3, got {user1_stats['total_samples']}"
        assert (
            user1_stats["by_type"]["blood"] == 2
        ), f"User1 blood should be 2, got {user1_stats['by_type']['blood']}"
        assert (
            user1_stats["by_type"]["tissue"] == 1
        ), f"User1 tissue should be 1, got {user1_stats['by_type']['tissue']}"
        assert (
            user1_stats["by_type"]["saliva"] == 0
        ), f"User1 saliva should be 0, got {user1_stats['by_type']['saliva']}"

        assert (
            user1_stats["by_status"]["collected"] == 1
        ), f"User1 collected should be 1, got {user1_stats['by_status']['collected']}"
        assert (
            user1_stats["by_status"]["processing"] == 1
        ), f"User1 processing should be 1, got {user1_stats['by_status']['processing']}"
        assert (
            user1_stats["by_status"]["archived"] == 1
        ), f"User1 archived should be 1, got {user1_stats['by_status']['archived']}"

        # User2 should have: 1 blood, 2 saliva, 0 tissue
        # Status: 2 collected, 1 processing, 0 archived
        assert (
            user2_stats["total_samples"] == 3
        ), f"User2 total should be 3, got {user2_stats['total_samples']}"
        assert (
            user2_stats["by_type"]["blood"] == 1
        ), f"User2 blood should be 1, got {user2_stats['by_type']['blood']}"
        assert (
            user2_stats["by_type"]["saliva"] == 2
        ), f"User2 saliva should be 2, got {user2_stats['by_type']['saliva']}"
        assert (
            user2_stats["by_type"]["tissue"] == 0
        ), f"User2 tissue should be 0, got {user2_stats['by_type']['tissue']}"

        assert (
            user2_stats["by_status"]["collected"] == 2
        ), f"User2 collected should be 2, got {user2_stats['by_status']['collected']}"
        assert (
            user2_stats["by_status"]["processing"] == 1
        ), f"User2 processing should be 1, got {user2_stats['by_status']['processing']}"
        assert (
            user2_stats["by_status"]["archived"] == 0
        ), f"User2 archived should be 0, got {user2_stats['by_status']['archived']}"

        # Verify totals consistency
        user1_type_total = sum(user1_stats["by_type"].values())
        user1_status_total = sum(user1_stats["by_status"].values())
        assert (
            user1_type_total == user1_stats["total_samples"]
        ), "User1 type totals should match total_samples"
        assert (
            user1_status_total == user1_stats["total_samples"]
        ), "User1 status totals should match total_samples"

        user2_type_total = sum(user2_stats["by_type"].values())
        user2_status_total = sum(user2_stats["by_status"].values())
        assert (
            user2_type_total == user2_stats["total_samples"]
        ), "User2 type totals should match total_samples"
        assert (
            user2_status_total == user2_stats["total_samples"]
        ), "User2 status totals should match total_samples"

    async def test_filtering_respects_user_boundaries(
        self,
        sample_service: SampleService,
        test_user1: User,
        test_user2: User,
        test_samples_user1: list[Sample],
        test_samples_user2: list[Sample],
    ):
        """
        CRITICAL: Test that filtering only returns current user's samples.

        Users should never see filtered results from other users' data.
        """
        # Filter by blood type for User1 (should get 2 samples)
        user1_blood_samples = await sample_service.get_samples(
            filters=SampleFilter(sample_type=SampleType.BLOOD),
            skip=0,
            limit=100,
            current_user=test_user1,
        )

        # Filter by blood type for User2 (should get 1 sample)
        user2_blood_samples = await sample_service.get_samples(
            filters=SampleFilter(sample_type=SampleType.BLOOD),
            skip=0,
            limit=100,
            current_user=test_user2,
        )

        assert (
            user1_blood_samples.total == 2
        ), f"User1 should have 2 blood samples, got {user1_blood_samples.total}"
        assert (
            user2_blood_samples.total == 1
        ), f"User2 should have 1 blood sample, got {user2_blood_samples.total}"

        # Verify all samples have correct type and belong to correct user
        for sample in user1_blood_samples.samples:
            assert (
                sample.sample_type == SampleType.BLOOD
            ), "Should only return blood samples"
            # Verify this sample belongs to user1
            actual_sample = next(
                (s for s in test_samples_user1 if str(s.id) == str(sample.id)), None
            )
            assert actual_sample is not None, "Sample should belong to user1"

        for sample in user2_blood_samples.samples:
            assert (
                sample.sample_type == SampleType.BLOOD
            ), "Should only return blood samples"
            # Verify this sample belongs to user2
            actual_sample = next(
                (s for s in test_samples_user2 if str(s.id) == str(sample.id)), None
            )
            assert actual_sample is not None, "Sample should belong to user2"

        # Filter by status for User1 (collected status - should get 1 sample)
        user1_collected_samples = await sample_service.get_samples(
            filters=SampleFilter(status=SampleStatus.COLLECTED),
            skip=0,
            limit=100,
            current_user=test_user1,
        )

        # Filter by status for User2 (collected status - should get 2 samples)
        user2_collected_samples = await sample_service.get_samples(
            filters=SampleFilter(status=SampleStatus.COLLECTED),
            skip=0,
            limit=100,
            current_user=test_user2,
        )

        assert (
            user1_collected_samples.total == 1
        ), f"User1 should have 1 collected sample, got {user1_collected_samples.total}"
        assert (
            user2_collected_samples.total == 2
        ), f"User2 should have 2 collected samples, got {user2_collected_samples.total}"

    async def test_subject_search_isolated_by_user(
        self,
        sample_service: SampleService,
        test_user1: User,
        test_user2: User,
        test_samples_user1: list[Sample],
        test_samples_user2: list[Sample],
    ):
        """
        CRITICAL: Test that subject search only returns current user's samples.

        Subject ID search must respect user boundaries to protect patient privacy.
        """
        # User1 searches for their subject "P001"
        user1_p001_samples = await sample_service.get_samples_by_subject_id(
            "P001", test_user1
        )
        assert (
            len(user1_p001_samples) == 1
        ), f"User1 should find 1 sample for P001, got {len(user1_p001_samples)}"
        assert user1_p001_samples[0].subject_id == "P001"

        # User2 searches for "P001" (which belongs to User1) - should find nothing
        user2_p001_samples = await sample_service.get_samples_by_subject_id(
            "P001", test_user2
        )
        assert (
            len(user2_p001_samples) == 0
        ), f"User2 should find 0 samples for P001, got {len(user2_p001_samples)}"

        # User2 searches for their own subject "S001"
        user2_s001_samples = await sample_service.get_samples_by_subject_id(
            "S001", test_user2
        )
        assert (
            len(user2_s001_samples) == 1
        ), f"User2 should find 1 sample for S001, got {len(user2_s001_samples)}"
        assert user2_s001_samples[0].subject_id == "S001"

        # User1 searches for "S001" (which belongs to User2) - should find nothing
        user1_s001_samples = await sample_service.get_samples_by_subject_id(
            "S001", test_user1
        )
        assert (
            len(user1_s001_samples) == 0
        ), f"User1 should find 0 samples for S001, got {len(user1_s001_samples)}"

        # Cross-user subject ID collision test - even if subject IDs were the same,
        # users should only see their own
        # This simulates a real-world scenario where different hospitals might use
        # the same patient numbering scheme
