import pytest
from pydantic import ValidationError

from app.schemas.auth import UserCreate


class TestAuthSchemas:
    def test_password_complexity(self):
        with pytest.raises(ValidationError):
            UserCreate(username="user1", email="user1@test.com", password="weak")
        with pytest.raises(ValidationError):
            UserCreate(
                username="user1", email="user1@test.com", password="alllowercase1!"
            )
        with pytest.raises(ValidationError):
            UserCreate(username="user1", email="user1@test.com", password="PASSWORD1!")
        with pytest.raises(ValidationError):
            UserCreate(username="user1", email="user1@test.com", password="Password1")

    def test_email_edge_cases(self):
        with pytest.raises(ValidationError):
            UserCreate(username="user1", email="bademail", password="Password1!")
        with pytest.raises(ValidationError):
            UserCreate(username="user1", email="user1@bad.com", password="Password1!")

    def test_username_edge_cases(self):
        with pytest.raises(ValidationError):
            UserCreate(
                username="1invalid", email="user1@test.com", password="Password1!"
            )
        with pytest.raises(ValidationError):
            UserCreate(username="admin", email="user1@test.com", password="Password1!")
