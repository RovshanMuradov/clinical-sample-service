import pytest
from tests.helpers import build_sample_data, token_headers_for_user


@pytest.mark.asyncio
async def test_end_to_end_flow(client, test_user2):
    # register new user and login
    reg_data = {
        "username": "journey",
        "email": "journey@test.com",
        "password": "StrongPass1$",
    }
    resp = await client.post("/api/v1/auth/register", json=reg_data)
    assert resp.status_code == 200
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": reg_data["email"], "password": reg_data["password"]},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # create sample
    payload = build_sample_data()
    resp = await client.post("/api/v1/samples/", json=payload, headers=headers)
    assert resp.status_code == 200
    sample_id = resp.json()["id"]

    # query with filters
    list_resp = await client.get(
        "/api/v1/samples/", headers=headers, params={"sample_type": "blood"}
    )
    assert list_resp.status_code == 200
    assert list_resp.json()["total"] >= 1

    # update
    upd_resp = await client.put(
        f"/api/v1/samples/{sample_id}", json={"status": "processing"}, headers=headers
    )
    assert upd_resp.status_code == 200

    # other user cannot delete
    resp = await client.delete(
        f"/api/v1/samples/{sample_id}", headers=token_headers_for_user(test_user2)
    )
    assert resp.status_code == 403

    # delete sample
    del_resp = await client.delete(f"/api/v1/samples/{sample_id}", headers=headers)
    assert del_resp.status_code == 200

    # logout (simulate token expiry)
    logout_resp = await client.post("/api/v1/auth/refresh", headers=headers)
    assert logout_resp.status_code == 200
