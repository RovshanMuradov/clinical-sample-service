from datetime import timedelta

from app.core.security import create_access_token


def token_headers_for_user(user):
    """Return authorization headers for a given user."""
    token = create_access_token({"sub": str(user.id)})
    return {"Authorization": f"Bearer {token}"}


def expired_token_headers_for_user(user):
    """Return headers with an already-expired token."""
    token = create_access_token(
        {"sub": str(user.id)}, expires_delta=timedelta(minutes=-1)
    )
    return {"Authorization": f"Bearer {token}"}


def invalid_token_headers():
    """Return headers with an invalid token string."""
    return {"Authorization": "Bearer invalid.token.here"}


def build_user_data(**overrides):
    """Return valid user creation data with optional overrides."""
    data = {
        "username": "user" + overrides.get("username_suffix", "1"),
        "email": f"user{overrides.get('email_suffix', '1')}@test.com",
        "password": "StrongPass1$",
    }
    data.update(
        {
            k: v
            for k, v in overrides.items()
            if k not in {"username_suffix", "email_suffix"}
        }
    )
    return data


def build_sample_data(**overrides):
    """Return valid sample creation data with optional overrides."""
    from datetime import date

    data = {
        "sample_type": "blood",
        "subject_id": "P001",
        "collection_date": str(date.today()),
        "status": "collected",
        "storage_location": "freezer-1-rowA",
    }
    data.update(overrides)
    return data


def assert_error_response(resp, status_code: int):
    """Assert standard error response."""
    assert resp.status_code == status_code
    body = resp.json()
    assert "detail" in body


async def count_users(session):
    """Return number of users in the database."""
    from sqlalchemy import func, select

    from app.models.user import User

    result = await session.execute(select(func.count(User.id)))
    return result.scalar() or 0
