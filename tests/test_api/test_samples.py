import pytest
from datetime import date, timedelta


class TestSampleCreation:
    """Tests for POST /samples endpoint."""

    @pytest.mark.asyncio
    async def test_create_sample_success(self, authenticated_client, test_data_builder):
        payload = test_data_builder()
        resp = await authenticated_client.post("/api/v1/samples/", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["sample_type"] == payload["sample_type"]
        assert data["subject_id"] == payload["subject_id"]
        assert "id" in data and "sample_id" in data

    @pytest.mark.asyncio
    async def test_create_sample_subject_validation(self, authenticated_client, test_data_builder):
        payload = test_data_builder(subject_id="1234")
        resp = await authenticated_client.post("/api/v1/samples/", json=payload)
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_create_sample_collection_date_future(self, authenticated_client, test_data_builder):
        future_date = date.today() + timedelta(days=1)
        payload = test_data_builder(collection_date=str(future_date))
        resp = await authenticated_client.post("/api/v1/samples/", json=payload)
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_create_sample_tissue_storage_rule(self, authenticated_client, test_data_builder):
        payload = test_data_builder(sample_type="tissue", storage_location="room-1-shelfA")
        resp = await authenticated_client.post("/api/v1/samples/", json=payload)
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_create_sample_unauthenticated(self, client, test_data_builder):
        payload = test_data_builder()
        resp = await client.post("/api/v1/samples/", json=payload)
        assert resp.status_code == 403


class TestSampleListing:
    """Tests for GET /samples endpoint."""

    @pytest.mark.asyncio
    async def test_list_samples(self, authenticated_client, test_samples_user1):
        resp = await authenticated_client.get("/api/v1/samples/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == len(test_samples_user1)
        assert len(data["samples"]) == len(test_samples_user1)

    @pytest.mark.asyncio
    async def test_list_samples_pagination(self, authenticated_client, test_samples_user1):
        resp = await authenticated_client.get("/api/v1/samples/?skip=1&limit=1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["skip"] == 1
        assert data["limit"] == 1
        assert len(data["samples"]) == 1
        assert data["total"] == len(test_samples_user1)

    @pytest.mark.asyncio
    async def test_list_samples_filter_type(self, authenticated_client, test_samples_user1):
        resp = await authenticated_client.get("/api/v1/samples/?sample_type=blood")
        assert resp.status_code == 200
        data = resp.json()
        assert all(s["sample_type"] == "blood" for s in data["samples"])

    @pytest.mark.asyncio
    async def test_list_samples_filter_status(self, authenticated_client, test_samples_user1):
        resp = await authenticated_client.get("/api/v1/samples/?sample_status=processing")
        assert resp.status_code == 200
        data = resp.json()
        assert all(s["status"] == "processing" for s in data["samples"])

    @pytest.mark.asyncio
    async def test_list_samples_date_range(self, authenticated_client, test_samples_user1):
        resp = await authenticated_client.get(
            "/api/v1/samples/?collection_date_from=2024-01-16&collection_date_to=2024-01-17"
        )
        assert resp.status_code == 200
        data = resp.json()
        assert all("2024-01-16" <= s["collection_date"] <= "2024-01-17" for s in data["samples"])

    @pytest.mark.asyncio
    async def test_list_samples_empty_results(self, authenticated_client, test_samples_user1):
        resp = await authenticated_client.get("/api/v1/samples/?sample_type=saliva")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["samples"] == []

    @pytest.mark.asyncio
    async def test_list_samples_invalid_pagination(self, authenticated_client):
        resp = await authenticated_client.get("/api/v1/samples/?skip=-1")
        assert resp.status_code == 422


class TestSampleDetail:
    """Tests for GET /samples/{id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_sample_own(self, authenticated_client, test_samples_user1):
        sample = test_samples_user1[0]
        resp = await authenticated_client.get(f"/api/v1/samples/{sample.id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == str(sample.id)

    @pytest.mark.asyncio
    async def test_get_sample_other_user(self, authenticated_client, test_samples_user2):
        sample = test_samples_user2[0]
        resp = await authenticated_client.get(f"/api/v1/samples/{sample.id}")
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_get_sample_not_found(self, authenticated_client):
        from uuid import uuid4

        resp = await authenticated_client.get(f"/api/v1/samples/{uuid4()}")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_get_sample_invalid_uuid(self, authenticated_client):
        resp = await authenticated_client.get("/api/v1/samples/not-a-uuid")
        assert resp.status_code == 422


class TestSampleUpdate:
    """Tests for PUT /samples/{id} endpoint."""

    @pytest.mark.asyncio
    async def test_update_sample(self, authenticated_client, test_samples_user1):
        sample = test_samples_user1[0]
        payload = {"status": "processing"}
        resp = await authenticated_client.put(f"/api/v1/samples/{sample.id}", json=payload)
        assert resp.status_code == 200
        assert resp.json()["status"] == "processing"

    @pytest.mark.asyncio
    async def test_update_sample_partial(self, authenticated_client, test_samples_user1):
        sample = test_samples_user1[1]
        payload = {"storage_location": "freezer-9-rowZ"}
        resp = await authenticated_client.put(f"/api/v1/samples/{sample.id}", json=payload)
        assert resp.status_code == 200
        assert resp.json()["storage_location"] == "freezer-9-rowZ"

    @pytest.mark.asyncio
    async def test_update_sample_other_user(self, authenticated_client, test_samples_user2):
        sample = test_samples_user2[0]
        resp = await authenticated_client.put(f"/api/v1/samples/{sample.id}", json={"status": "archived"})
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_update_sample_validation_error(self, authenticated_client, test_samples_user1):
        sample = test_samples_user1[0]
        resp = await authenticated_client.put(f"/api/v1/samples/{sample.id}", json={"subject_id": "1234"})
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_update_sample_not_found(self, authenticated_client):
        from uuid import uuid4

        resp = await authenticated_client.put(f"/api/v1/samples/{uuid4()}", json={"status": "processing"})
        assert resp.status_code == 404


class TestSampleDeletion:
    """Tests for DELETE /samples/{id} endpoint."""

    @pytest.mark.asyncio
    async def test_delete_sample(self, authenticated_client, test_samples_user1):
        sample = test_samples_user1[0]
        resp = await authenticated_client.delete(f"/api/v1/samples/{sample.id}")
        assert resp.status_code == 200
        # verify gone
        resp2 = await authenticated_client.get(f"/api/v1/samples/{sample.id}")
        assert resp2.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_sample_other_user(self, authenticated_client, test_samples_user2):
        sample = test_samples_user2[0]
        resp = await authenticated_client.delete(f"/api/v1/samples/{sample.id}")
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_sample_not_found(self, authenticated_client):
        from uuid import uuid4

        resp = await authenticated_client.delete(f"/api/v1/samples/{uuid4()}")
        assert resp.status_code == 404


class TestSampleStatistics:
    """Tests for GET /samples/statistics endpoint."""

    @pytest.mark.asyncio
    async def test_get_statistics(self, authenticated_client, test_samples_user1, test_samples_user2):
        resp = await authenticated_client.get("/api/v1/samples/stats/overview")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_samples"] == len(test_samples_user1)
        assert data["by_type"]["blood"] == 2
        assert data["by_type"].get("saliva", 0) == 0
        assert data["by_type"]["tissue"] == 1

    @pytest.mark.asyncio
    async def test_get_statistics_unauthenticated(self, client):
        resp = await client.get("/api/v1/samples/stats/overview")
        assert resp.status_code == 403


class TestSamplesBySubject:
    """Tests for GET /samples/subject/{subject_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_samples_by_subject(self, authenticated_client, test_samples_user1):
        sample = test_samples_user1[0]
        resp = await authenticated_client.get(f"/api/v1/samples/subject/{sample.subject_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert all(s["subject_id"] == sample.subject_id for s in data)

    @pytest.mark.asyncio
    async def test_get_samples_by_subject_no_results(self, authenticated_client):
        resp = await authenticated_client.get("/api/v1/samples/subject/P999")
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_get_samples_by_subject_invalid(self, authenticated_client):
        resp = await authenticated_client.get("/api/v1/samples/subject/1234")
        assert resp.status_code == 422
