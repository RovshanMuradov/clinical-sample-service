import pytest
from httpx import AsyncClient
from fastapi import status
from uuid import uuid4

# Use the async_client fixture from conftest

@pytest.mark.asyncio
async def test_register_user_success(async_client: AsyncClient):
    payload = {
        "username": "user_api_1",
        "email": "user_api_1@example.com",
        "password": "Passw0rd!",
    }
    response = await async_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == payload["email"]


@pytest.mark.asyncio
async def test_register_duplicate_email_fails(async_client: AsyncClient):
    payload = {
        "username": "user_dup",
        "email": "dup@example.com",
        "password": "Passw0rd!",
    }
    await async_client.post("/api/v1/auth/register", json=payload)
    response = await async_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio
async def test_login_valid_credentials(async_client: AsyncClient):
    reg = {
        "username": "login_user",
        "email": "login_user@example.com",
        "password": "Passw0rd!",
    }
    await async_client.post("/api/v1/auth/register", json=reg)
    response = await async_client.post(
        "/api/v1/auth/login", json={"email": reg["email"], "password": reg["password"]}
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_login_invalid_credentials(async_client: AsyncClient):
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "nouser@example.com", "password": "wrong"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_refresh_token_valid(async_client: AsyncClient):
    reg = {
        "username": "refresh_user",
        "email": "refresh@example.com",
        "password": "Passw0rd!",
    }
    await async_client.post("/api/v1/auth/register", json=reg)
    login = await async_client.post(
        "/api/v1/auth/login", json={"email": reg["email"], "password": reg["password"]}
    )
    token = login.json()["access_token"]
    response = await async_client.post(
        "/api/v1/auth/refresh",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_refresh_token_expired(async_client: AsyncClient):
    response = await async_client.post(
        "/api/v1/auth/refresh",
        headers={"Authorization": "Bearer invalid"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def _auth_token(async_client: AsyncClient, suffix: str = "") -> str:
    reg = {
        "username": f"sample_user{suffix}",
        "email": f"sample{suffix}@example.com",
        "password": "Passw0rd!",
    }
    await async_client.post("/api/v1/auth/register", json=reg)
    login = await async_client.post(
        "/api/v1/auth/login", json={"email": reg["email"], "password": reg["password"]}
    )
    return login.json()["access_token"]


@pytest.mark.asyncio
async def test_create_sample_authenticated(async_client: AsyncClient):
    token = await _auth_token(async_client, "_create")
    payload = {
        "sample_type": "blood",
        "subject_id": "P100",
        "collection_date": "2024-01-01",
        "status": "collected",
        "storage_location": "freezer-1-rowA",
    }
    response = await async_client.post(
        "/api/v1/samples",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["subject_id"] == "P100"


@pytest.mark.asyncio
async def test_create_sample_unauthenticated_fails(async_client: AsyncClient):
    payload = {
        "sample_type": "blood",
        "subject_id": "P101",
        "collection_date": "2024-01-02",
        "status": "collected",
        "storage_location": "freezer-1-rowA",
    }
    response = await async_client.post("/api/v1/samples", json=payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_samples_list_authenticated(async_client: AsyncClient):
    token = await _auth_token(async_client, "_list")
    response = await async_client.get(
        "/api/v1/samples",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert "samples" in response.json()


@pytest.mark.asyncio
async def test_get_samples_with_filtering(async_client: AsyncClient):
    token = await _auth_token(async_client, "_filter")
    # create sample
    await async_client.post(
        "/api/v1/samples",
        json={
            "sample_type": "tissue",
            "subject_id": "PX01",
            "collection_date": "2024-01-03",
            "status": "collected",
            "storage_location": "freezer-1-rowB",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    response = await async_client.get(
        "/api/v1/samples?sample_type=tissue",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert all(s["sample_type"] == "tissue" for s in data["samples"])


@pytest.mark.asyncio
async def test_get_sample_by_id_success(async_client: AsyncClient):
    token = await _auth_token(async_client, "_get")
    sample = await async_client.post(
        "/api/v1/samples",
        json={
            "sample_type": "blood",
            "subject_id": "P200",
            "collection_date": "2024-01-04",
            "status": "collected",
            "storage_location": "freezer-1-rowC",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    sample_id = sample.json()["id"]
    response = await async_client.get(
        f"/api/v1/samples/{sample_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == sample_id


@pytest.mark.asyncio
async def test_get_sample_by_id_not_found(async_client: AsyncClient):
    token = await _auth_token(async_client, "_get_not_found")
    random_id = uuid4()
    response = await async_client.get(
        f"/api/v1/samples/{random_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_update_sample_authenticated(async_client: AsyncClient):
    token = await _auth_token(async_client, "_update")
    sample = await async_client.post(
        "/api/v1/samples",
        json={
            "sample_type": "blood",
            "subject_id": "P300",
            "collection_date": "2024-01-05",
            "status": "collected",
            "storage_location": "freezer-1-rowD",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    sample_id = sample.json()["id"]
    response = await async_client.put(
        f"/api/v1/samples/{sample_id}",
        json={"status": "processing"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "processing"


@pytest.mark.asyncio
async def test_update_sample_unauthorized_fails(async_client: AsyncClient):
    token1 = await _auth_token(async_client, "_own")
    sample = await async_client.post(
        "/api/v1/samples",
        json={
            "sample_type": "blood",
            "subject_id": "P301",
            "collection_date": "2024-01-05",
            "status": "collected",
            "storage_location": "freezer-1-rowD",
        },
        headers={"Authorization": f"Bearer {token1}"},
    )
    sample_id = sample.json()["id"]
    token2 = await _auth_token(async_client, "_other")
    response = await async_client.put(
        f"/api/v1/samples/{sample_id}",
        json={"status": "processing"},
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_delete_sample_authenticated(async_client: AsyncClient):
    token = await _auth_token(async_client, "_delete")
    sample = await async_client.post(
        "/api/v1/samples",
        json={
            "sample_type": "blood",
            "subject_id": "P400",
            "collection_date": "2024-01-06",
            "status": "collected",
            "storage_location": "freezer-2-rowA",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    sample_id = sample.json()["id"]
    response = await async_client.delete(
        f"/api/v1/samples/{sample_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_delete_sample_unauthorized_fails(async_client: AsyncClient):
    token1 = await _auth_token(async_client, "_del1")
    sample = await async_client.post(
        "/api/v1/samples",
        json={
            "sample_type": "blood",
            "subject_id": "P401",
            "collection_date": "2024-01-06",
            "status": "collected",
            "storage_location": "freezer-2-rowA",
        },
        headers={"Authorization": f"Bearer {token1}"},
    )
    sample_id = sample.json()["id"]
    token2 = await _auth_token(async_client, "_del2")
    response = await async_client.delete(
        f"/api/v1/samples/{sample_id}", headers={"Authorization": f"Bearer {token2}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_get_sample_statistics_authenticated(async_client: AsyncClient):
    token = await _auth_token(async_client, "_stats")
    response = await async_client.get(
        "/api/v1/samples/stats/overview",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert "by_status" in response.json()


@pytest.mark.asyncio
async def test_get_samples_by_subject_authenticated(async_client: AsyncClient):
    token = await _auth_token(async_client, "_subject")
    await async_client.post(
        "/api/v1/samples",
        json={
            "sample_type": "blood",
            "subject_id": "SUBJ1",
            "collection_date": "2024-01-07",
            "status": "collected",
            "storage_location": "freezer-2-rowB",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    response = await async_client.get(
        "/api/v1/samples/subject/SUBJ1",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_health_check_endpoint(async_client: AsyncClient):
    response = await async_client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "healthy"
