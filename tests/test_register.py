import pytest
from utils import StorageMock
from entity.session import UserSession
from typing import Optional
from werkzeug.security import check_password_hash

from app import app


@pytest.fixture
def client():
    """A test client for the app."""

    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as client:
        yield client


def test_register_success(client):
    def find_session_mock(session_uuid: str) -> Optional[UserSession]:
        assert session_uuid is None
        return None

    app.config["session_storage"] = StorageMock({"find_session": find_session_mock})
    app.config["cookie_storage"] = StorageMock({"get_cookie_value": lambda: None})

    def find_or_verify_user_mock(username: str, password: Optional[str]) -> None:
        assert username == "John"
        assert password is None
        return None

    def create_user_mock(login: str, hashed_password: str) -> None:
        assert login == "John"
        assert check_password_hash(hashed_password, "12345678")
        return None

    app.config["user_storage"] = StorageMock(
        {
            "find_or_verify_user": find_or_verify_user_mock,
            "create_user": create_user_mock,
        }
    )

    response = client.post(
        "/register",
        data={
            "username": "John",
            "password": "12345678",
            "confirm": "12345678",
        },
    )

    assert response.status_code == 302
    assert response.headers.get("Location") == "/login"


def test_register_invalid_confirm(client):
    def find_session_mock(session_uuid: str) -> Optional[UserSession]:
        assert session_uuid is None
        return None

    app.config["session_storage"] = StorageMock({"find_session": find_session_mock})
    app.config["cookie_storage"] = StorageMock({"get_cookie_value": lambda: None})

    def find_or_verify_user_mock(username: str, password: Optional[str]) -> None:
        assert username == "John"
        assert password is None
        return None

    app.config["user_storage"] = StorageMock(
        {
            "find_or_verify_user": find_or_verify_user_mock,
        }
    )

    response = client.post(
        "/register",
        data={
            "username": "John",
            "password": "12345678",
            "confirm": "87654321",
        },
    )

    assert response.status_code == 200
    assert "Passwords must match" in response.get_data(as_text=True)


def test_register_too_short_password(client):
    def find_session_mock(session_uuid: str) -> Optional[UserSession]:
        assert session_uuid is None
        return None

    app.config["session_storage"] = StorageMock({"find_session": find_session_mock})
    app.config["cookie_storage"] = StorageMock({"get_cookie_value": lambda: None})

    def find_or_verify_user_mock(username: str, password: Optional[str]) -> None:
        assert username == "John"
        assert password is None
        return None

    app.config["user_storage"] = StorageMock(
        {
            "find_or_verify_user": find_or_verify_user_mock,
        }
    )

    response = client.post(
        "/register",
        data={
            "username": "John",
            "password": "123",
            "confirm": "123",
        },
    )

    assert response.status_code == 200
    assert "Password should be at least 8 characters" in response.get_data(as_text=True)
