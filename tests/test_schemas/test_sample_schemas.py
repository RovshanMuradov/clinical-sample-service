from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from app.models.sample import SampleStatus, SampleType
from app.schemas.sample import SampleCreate, SampleUpdate


class TestSampleSchemas:
    def test_subject_id_variations(self):
        with pytest.raises(ValidationError):
            SampleCreate(
                sample_type=SampleType.BLOOD,
                subject_id="123",
                collection_date=date.today(),
                storage_location="freezer-1-rowA",
            )

    def test_date_boundaries(self):
        future = date.today() + timedelta(days=1)
        with pytest.raises(ValidationError):
            SampleCreate(
                sample_type=SampleType.BLOOD,
                subject_id="P123",
                collection_date=future,
                storage_location="freezer-1-rowA",
            )

    def test_storage_location_validation(self):
        with pytest.raises(ValidationError):
            SampleCreate(
                sample_type=SampleType.BLOOD,
                subject_id="P123",
                collection_date=date.today(),
                storage_location="bad-location",
            )

    def test_cross_field_validation(self):
        with pytest.raises(ValidationError):
            SampleCreate(
                sample_type=SampleType.TISSUE,
                subject_id="P123",
                collection_date=date.today(),
                storage_location="room-1-shelfA",
            )

    def test_update_optional_validations(self):
        update = SampleUpdate(subject_id="S001", collection_date=date.today())
        assert update.subject_id == "S001"
