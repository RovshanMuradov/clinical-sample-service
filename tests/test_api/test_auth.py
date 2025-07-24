import pytest


class TestAuthEndpoints:
    """Authentication API endpoint tests."""

    @pytest.mark.asyncio
    async def test_register_and_login(self, client):
        user_data = {
            "username": "apiuser",
            "email": "apiuser@test.com",
            "password": "ComplexPass1$",
        }
        resp = await client.post("/api/v1/auth/register", json=user_data)
        assert resp.status_code == 200

        login_data = {"email": user_data["email"], "password": user_data["password"]}
        login_resp = await client.post("/api/v1/auth/login", json=login_data)
        assert login_resp.status_code == 200
        token = login_resp.json().get("access_token")
        assert token

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client):
        payload1 = {
            "username": "first",
            "email": "dup@test.com",
            "password": "ComplexPass1$",
        }
        payload2 = {
            "username": "second",
            "email": "dup@test.com",
            "password": "AnotherPass2$",
        }
        await client.post("/api/v1/auth/register", json=payload1)
        resp = await client.post("/api/v1/auth/register", json=payload2)
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_register_duplicate_username(self, client):
        first = {
            "username": "duper",
            "email": "duper1@test.com",
            "password": "ComplexPass1$",
        }
        second = {
            "username": "duper",
            "email": "duper2@test.com",
            "password": "AnotherPass2$",
        }
        await client.post("/api/v1/auth/register", json=first)
        resp = await client.post("/api/v1/auth/register", json=second)
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_register_invalid_password(self, client):
        bad_data = {
            "username": "badpass",
            "email": "badpass@test.com",
            "password": "short",
        }
        resp = await client.post("/api/v1/auth/register", json=bad_data)
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client):
        bad_data = {
            "username": "bademail",
            "email": "user@unauthorized.com",
            "password": "ComplexPass1$",
        }
        resp = await client.post("/api/v1/auth/register", json=bad_data)
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_register_missing_fields(self, client):
        resp = await client.post("/api/v1/auth/register", json={"username": "u"})
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, client, test_user1):
        login_data = {
            "email": test_user1.email,
            "password": "wrongpass1$",
        }
        resp = await client.post("/api/v1/auth/login", json=login_data)
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_login_inactive_user(self, client, inactive_user):
        login_data = {
            "email": inactive_user.email,
            "password": "inactivePass1$",
        }
        resp = await client.post("/api/v1/auth/login", json=login_data)
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_login_missing_fields(self, client):
        resp = await client.post("/api/v1/auth/login", json={"email": "user@test.com"})
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_refresh_token(self, authenticated_client):
        refresh_resp = await authenticated_client.post("/api/v1/auth/refresh")
        assert refresh_resp.status_code == 200
        assert refresh_resp.json()["access_token"]

    @pytest.mark.asyncio
    async def test_refresh_token_expired(self, client, test_user1):
        from tests.helpers import expired_token_headers_for_user

        resp = await client.post(
            "/api/v1/auth/refresh",
            headers=expired_token_headers_for_user(test_user1),
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self, client):
        from tests.helpers import invalid_token_headers

        resp = await client.post(
            "/api/v1/auth/refresh", headers=invalid_token_headers()
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_token_missing(self, client):
        resp = await client.post("/api/v1/auth/refresh")
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_get_me(self, client, test_user1):
        from tests.helpers import token_headers_for_user

        resp = await client.get(
            "/api/v1/auth/me", headers=token_headers_for_user(test_user1)
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == test_user1.email

    @pytest.mark.asyncio
    async def test_get_me_invalid_token(self, client):
        from tests.helpers import invalid_token_headers

        resp = await client.get("/api/v1/auth/me", headers=invalid_token_headers())
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_get_me_no_token(self, client):
        resp = await client.get("/api/v1/auth/me")
        assert resp.status_code == 403
