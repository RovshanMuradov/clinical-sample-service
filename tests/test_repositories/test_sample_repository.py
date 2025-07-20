from datetime import date, timedelta
from uuid import uuid4

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.models.sample import SampleStatus, SampleType
from app.repositories.sample_repository import SampleRepository
from app.schemas.sample import SampleFilter


class TestSampleRepository:
    @pytest.mark.asyncio
    async def test_filter_combination(
        self, sample_repository: SampleRepository, test_samples_user1
    ):
        filt = SampleFilter(
            sample_type=SampleType.BLOOD,
            status=SampleStatus.COLLECTED,
            collection_date_from=date(2024, 1, 1),
            collection_date_to=date(2024, 12, 31),
        )
        results = await sample_repository.get_samples_with_filters(
            filt, user_id=test_samples_user1[0].user_id
        )
        assert len(results) == 1
        assert results[0].subject_id == "P001"

    @pytest.mark.asyncio
    async def test_count_no_results(
        self, sample_repository: SampleRepository, test_samples_user1
    ):
        filt = SampleFilter(subject_id="Z999")
        count = await sample_repository.count_samples_with_filters(
            filt, user_id=test_samples_user1[0].user_id
        )
        assert count == 0

    @pytest.mark.asyncio
    async def test_get_samples_by_subject_no_user(
        self, sample_repository: SampleRepository, test_samples_user1
    ):
        results = await sample_repository.get_samples_by_subject_id("P001")
        assert len(results) >= 1

    @pytest.mark.asyncio
    async def test_db_error_handled(
        self, sample_repository: SampleRepository, monkeypatch
    ):
        async def boom(*args, **kwargs):
            raise SQLAlchemyError("db fail")

        monkeypatch.setattr(sample_repository.db, "execute", boom)
        with pytest.raises(SQLAlchemyError):
            await sample_repository.get_sample_by_id(uuid4())
