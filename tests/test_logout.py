import pytest
from utils import StorageMock
from entity.session import UserSession
from typing import Optional


from app import app


@pytest.fixture
def client():
    """A test client for the app."""
    with app.test_client() as client:
        yield client


def test_logout_unauthorized(client):
    def find_session_mock(session_uuid: str) -> Optional[UserSession]:
        assert session_uuid is None
        return None

    app.config["session_storage"] = StorageMock({"find_session": find_session_mock})

    app.config["cookie_storage"] = StorageMock(
        {
            "get_cookie_value": lambda: None,
        }
    )
    
    response = client.get("/logout")

    assert response.status_code == 302
    assert response.headers.get("Location") == "/"


def test_logout_authorized(client):
    test_session_uuid = "e6bb1782-fbab-4c25-8bfd-92757bcdf1db"

    def find_session_mock(session_uuid: str) -> Optional[UserSession]:
        assert session_uuid == test_session_uuid
        return UserSession(id=1, session_uuid=test_session_uuid, user_id=1)

    def delete_session_mock(session_uuid: str) -> None:
        assert test_session_uuid == session_uuid
        return None

    app.config["session_storage"] = StorageMock(
        {
            "find_session": find_session_mock,
            "delete_session": delete_session_mock,
        }
    )

    app.config["cookie_storage"] = StorageMock(
        {
            "get_cookie_value": lambda: test_session_uuid,
        }
    )

    response = client.get("/logout")

    assert response.status_code == 302
    assert response.headers.get("Location") == "/"
