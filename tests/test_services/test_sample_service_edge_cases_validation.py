"""
Edge Cases and Validation Tests for Clinical Sample Service.

These tests focus on input validation, error handling, and edge cases
to ensure robust and secure operation under various conditions.
"""
from datetime import date, timedelta

# from typing import Any, Dict  # Removed unused import
from uuid import uuid4

import pytest
from pydantic import ValidationError as PydanticValidationError

from app.core.exceptions import NotFoundError
from app.models.sample import SampleStatus, SampleType
from app.models.user import User
from app.schemas.sample import (
    SampleCreate,
    SampleFilter,
    SampleListResponse,
    SampleUpdate,
)
from app.services.sample_service import SampleService


@pytest.mark.asyncio
@pytest.mark.validation
@pytest.mark.edge_cases
class TestPaginationValidation:
    """Test pagination parameter validation and edge cases."""

    async def test_pagination_parameters_handling(
        self,
        sample_service: SampleService,
        test_user1: User,
    ):
        """
        Test that service correctly handles pagination parameters.

        Note: Validation of skip/limit ranges is handled by FastAPI Query validators
        at the API layer. This test verifies the service processes valid parameters correctly.
        """
        # Test valid pagination parameters
        result = await sample_service.get_samples(
            filters=SampleFilter(),
            skip=0,
            limit=10,
            current_user=test_user1,
        )
        assert isinstance(
            result, SampleListResponse
        ), "Should return valid response for valid parameters"
        assert result.skip == 0, "Skip should be preserved"
        assert result.limit == 10, "Limit should be preserved"

        # Test edge case: maximum valid limit
        result = await sample_service.get_samples(
            filters=SampleFilter(),
            skip=0,
            limit=1000,  # Maximum allowed limit
            current_user=test_user1,
        )
        assert isinstance(result, SampleListResponse), "Should handle maximum limit"
        assert result.limit == 1000, "Maximum limit should be preserved"

        # Test large skip values (should work gracefully)
        result = await sample_service.get_samples(
            filters=SampleFilter(),
            skip=1000,
            limit=10,
            current_user=test_user1,
        )
        assert isinstance(result, SampleListResponse), "Should handle large skip values"
        assert result.skip == 1000, "Large skip should be preserved"
        assert (
            len(result.samples) == 0
        ), "Should return empty list when skip exceeds data"

    async def test_pagination_boundary_values(
        self,
        sample_service: SampleService,
        test_user1: User,
    ):
        """Test pagination boundary values work correctly."""
        # Test minimum valid values
        result = await sample_service.get_samples(
            filters=SampleFilter(),
            skip=0,
            limit=1,
            current_user=test_user1,
        )
        assert isinstance(
            result, SampleListResponse
        ), "Should return valid response for minimum values"
        assert result.skip == 0, "Skip should be preserved"
        assert result.limit == 1, "Limit should be preserved"

        # Test maximum valid limit
        result = await sample_service.get_samples(
            filters=SampleFilter(),
            skip=0,
            limit=1000,
            current_user=test_user1,
        )
        assert isinstance(
            result, SampleListResponse
        ), "Should return valid response for maximum limit"
        assert result.limit == 1000, "Maximum limit should be preserved"

        # Test large skip value (should not error)
        result = await sample_service.get_samples(
            filters=SampleFilter(),
            skip=1000000,  # Very large skip
            limit=10,
            current_user=test_user1,
        )
        assert isinstance(
            result, SampleListResponse
        ), "Should handle large skip values gracefully"
        assert result.skip == 1000000, "Large skip should be preserved"
        assert len(result.samples) == 0, "Should return empty list for skip beyond data"


@pytest.mark.asyncio
@pytest.mark.validation
@pytest.mark.edge_cases
class TestInvalidUUIDHandling:
    """Test handling of invalid UUIDs in various contexts."""

    async def test_invalid_uuid_handling(
        self,
        sample_service: SampleService,
        test_user1: User,
    ):
        """
        Test that invalid UUID in sample_id is handled gracefully.

        This ensures the system properly validates UUIDs and returns
        appropriate errors rather than crashing.
        """
        # Test completely invalid UUID string - this should be caught by FastAPI/Pydantic
        # before reaching the service layer, but we test service layer robustness

        # Generate a properly formatted but non-existent UUID
        non_existent_uuid = uuid4()

        # Should raise NotFoundError for non-existent sample
        with pytest.raises(NotFoundError) as exc_info:
            await sample_service.get_sample_by_id(non_existent_uuid, test_user1)

        assert "Sample" in str(exc_info.value), "Error should mention sample not found"
        assert str(non_existent_uuid) in str(
            exc_info.value
        ), "Error should include the UUID"

        # Test update with non-existent UUID
        with pytest.raises(NotFoundError) as exc_info:
            await sample_service.update_sample(
                non_existent_uuid,
                SampleUpdate(status=SampleStatus.PROCESSING),
                test_user1,
            )

        assert "Sample" in str(
            exc_info.value
        ), "Update should fail for non-existent sample"

        # Test delete with non-existent UUID
        with pytest.raises(NotFoundError) as exc_info:
            await sample_service.delete_sample(non_existent_uuid, test_user1)

        assert "Sample" in str(
            exc_info.value
        ), "Delete should fail for non-existent sample"

    async def test_malformed_uuid_strings(self):
        """Test that malformed UUID strings are rejected at the schema level."""
        # These should be caught by Pydantic validation before reaching service layer

        # Test invalid UUID format in response schema
        with pytest.raises(PydanticValidationError):
            # This simulates what happens when trying to create a response with invalid UUID
            from datetime import datetime

            from app.schemas.sample import SampleResponse

            # This should fail validation
            SampleResponse(
                id="not-a-uuid",  # Invalid UUID format
                sample_id="also-not-a-uuid",  # Invalid UUID format
                sample_type=SampleType.BLOOD,
                subject_id="P001",
                collection_date=date.today(),
                status=SampleStatus.COLLECTED,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )


@pytest.mark.asyncio
@pytest.mark.validation
@pytest.mark.edge_cases
class TestSampleValidationEdgeCases:
    """Test core business rule validation in sample data."""

    async def test_subject_id_business_validation(self):
        """Test core subject ID validation - business rule: letter + 3 digits."""

        # Test valid subject ID format
        valid_sample = SampleCreate(
            sample_type=SampleType.BLOOD,
            subject_id="P001",
            collection_date=date.today() - timedelta(days=1),
            storage_location="freezer-1-rowA",
        )
        assert valid_sample.subject_id == "P001", "Valid subject ID should be accepted"

        # Test case conversion (business rule)
        mixed_case_sample = SampleCreate(
            sample_type=SampleType.BLOOD,
            subject_id="p001",  # lowercase
            collection_date=date.today() - timedelta(days=1),
            storage_location="freezer-1-rowA",
        )
        assert (
            mixed_case_sample.subject_id == "P001"
        ), "Subject ID should be converted to uppercase"

        # Test key invalid patterns (business rule violations)
        with pytest.raises(PydanticValidationError):
            SampleCreate(
                sample_type=SampleType.BLOOD,
                subject_id="001",  # Missing letter prefix
                collection_date=date.today() - timedelta(days=1),
                storage_location="freezer-1-rowA",
            )

        with pytest.raises(PydanticValidationError):
            SampleCreate(
                sample_type=SampleType.BLOOD,
                subject_id="P1",  # Too few digits
                collection_date=date.today() - timedelta(days=1),
                storage_location="freezer-1-rowA",
            )

    async def test_collection_date_business_validation(self):
        """Test core collection date business rules - no future dates, max 10 years old."""

        # Test valid dates
        today_sample = SampleCreate(
            sample_type=SampleType.BLOOD,
            subject_id="P001",
            collection_date=date.today(),
            storage_location="freezer-1-rowA",
        )
        assert (
            today_sample.collection_date == date.today()
        ), "Today's date should be valid"

        # Test future date (business rule violation)
        with pytest.raises(PydanticValidationError):
            SampleCreate(
                sample_type=SampleType.BLOOD,
                subject_id="P001",
                collection_date=date.today() + timedelta(days=1),  # Tomorrow
                storage_location="freezer-1-rowA",
            )

        # Test very old date (business rule violation)
        very_old_date = date.today() - timedelta(days=365 * 11)  # 11 years ago
        with pytest.raises(PydanticValidationError):
            SampleCreate(
                sample_type=SampleType.BLOOD,
                subject_id="P001",
                collection_date=very_old_date,
                storage_location="freezer-1-rowA",
            )

    async def test_storage_location_format_validation(self):
        """Test storage location format business rule."""

        # Test valid format
        valid_sample = SampleCreate(
            sample_type=SampleType.BLOOD,
            subject_id="P001",
            collection_date=date.today() - timedelta(days=1),
            storage_location="freezer-1-rowA",
        )
        assert (
            valid_sample.storage_location == "freezer-1-rowA"
        ), "Valid location format should be accepted"

    async def test_tissue_sample_storage_business_rule(self):
        """Test critical business rule: tissue samples must be stored in freezer."""

        # Tissue sample with freezer storage (should be valid)
        valid_tissue = SampleCreate(
            sample_type=SampleType.TISSUE,
            subject_id="P001",
            collection_date=date.today() - timedelta(days=1),
            storage_location="freezer-1-rowA",
        )
        assert (
            valid_tissue.sample_type == SampleType.TISSUE
        ), "Valid tissue sample should be accepted"

        # Tissue sample with room storage (business rule violation)
        with pytest.raises(PydanticValidationError):
            SampleCreate(
                sample_type=SampleType.TISSUE,
                subject_id="P001",
                collection_date=date.today() - timedelta(days=1),
                storage_location="room-1-shelfA",  # Invalid for tissue
            )


@pytest.mark.asyncio
@pytest.mark.validation
@pytest.mark.edge_cases
class TestFilterValidationEdgeCases:
    """Test critical filter validation business rules."""

    async def test_date_range_filter_business_rules(self):
        """Test critical date range filter business rules."""
        from app.schemas.sample import SampleFilter

        # Valid date range
        valid_filter = SampleFilter(
            collection_date_from=date.today() - timedelta(days=30),
            collection_date_to=date.today() - timedelta(days=1),
        )
        assert (
            valid_filter.collection_date_from is not None
        ), "Valid date range should be accepted"

        # Invalid: from date after to date (critical business rule)
        with pytest.raises(PydanticValidationError):
            SampleFilter(
                collection_date_from=date.today() - timedelta(days=1),
                collection_date_to=date.today()
                - timedelta(days=30),  # Earlier than from date
            )


@pytest.mark.asyncio
@pytest.mark.validation
@pytest.mark.edge_cases
class TestSampleUpdateValidation:
    """Test validation in sample update scenarios."""

    async def test_sample_update_business_rules(self):
        """Test sample update follows same business rules as creation."""
        from app.schemas.sample import SampleUpdate

        # Test empty update (should be valid)
        empty_update = SampleUpdate()
        assert empty_update.sample_type is None, "Empty update should be valid"

        # Test invalid future date (business rule violation)
        with pytest.raises(PydanticValidationError):
            SampleUpdate(
                collection_date=date.today() + timedelta(days=1),  # Future date
            )


@pytest.mark.asyncio
@pytest.mark.validation
@pytest.mark.edge_cases
class TestSystemRobustness:
    """Test system robustness for edge cases."""

    async def test_multiple_sequential_calls_consistency(
        self,
        sample_service: SampleService,
        test_user1: User,
    ):
        """Test that multiple sequential operations return consistent results."""
        # Multiple get_samples calls should all work independently
        filter_obj = SampleFilter()

        # Sequential requests should return consistent results
        result1 = await sample_service.get_samples(filter_obj, 0, 10, test_user1)
        result2 = await sample_service.get_samples(filter_obj, 0, 10, test_user1)

        # Results should be identical and valid
        assert (
            result1.total == result2.total
        ), "Sequential calls should return consistent results"
        assert len(result1.samples) == len(
            result2.samples
        ), "Sample counts should be consistent"

    async def test_large_skip_values_handling(
        self,
        sample_service: SampleService,
        test_user1: User,
    ):
        """Test system gracefully handles large skip values."""
        result = await sample_service.get_samples(
            SampleFilter(),
            skip=999999,  # Very large skip
            limit=1,
            current_user=test_user1,
        )
        assert isinstance(
            result, SampleListResponse
        ), "Should handle large skip values gracefully"
        assert result.skip == 999999, "Skip value should be preserved"
        assert (
            len(result.samples) == 0
        ), "Should return empty list when skip exceeds data"
