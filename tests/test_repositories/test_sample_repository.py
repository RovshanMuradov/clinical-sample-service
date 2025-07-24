import asyncio
from datetime import date, timedelta
from uuid import uuid4

import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

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

    @pytest.mark.asyncio
    async def test_concurrent_creations(self, async_engine, test_user1):
        """Repository handles concurrent inserts using separate sessions."""
        session_maker = async_sessionmaker(
            bind=async_engine, class_=AsyncSession, expire_on_commit=False
        )

        async with session_maker() as s1, session_maker() as s2:
            repo1 = SampleRepository(s1)
            repo2 = SampleRepository(s2)
            data1 = {
                "sample_type": SampleType.BLOOD,
                "subject_id": "PX1",
                "collection_date": date.today(),
                "status": SampleStatus.COLLECTED,
                "storage_location": "freezer-1-rowA",
                "user_id": test_user1.id,
            }
            data2 = {
                "sample_type": SampleType.BLOOD,
                "subject_id": "PX2",
                "collection_date": date.today(),
                "status": SampleStatus.COLLECTED,
                "storage_location": "freezer-1-rowB",
                "user_id": test_user1.id,
            }

            await asyncio.gather(
                repo1.create_sample(data1),
                repo2.create_sample(data2),
            )

        async with session_maker() as check:
            repo = SampleRepository(check)
            count = await repo.count_samples_with_filters(
                SampleFilter(), user_id=test_user1.id
            )
            assert count >= 2
