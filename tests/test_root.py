from app import app
import pytest
from entity.session import UserSession
from typing import Optional
from utils import StorageMock, minify


@pytest.fixture
def client():
    """A test client for the app."""
    with app.test_client() as client:
        yield client


def test_root_authorized(client):
    test_session_uuid = "e6bb1782-fbab-4c25-8bfd-92757bcdf1db"

    def find_session_mock(session_uuid: str) -> Optional[UserSession]:
        assert session_uuid == test_session_uuid
        return UserSession(id=1, session_uuid=test_session_uuid, user_id=1)

    app.config["session_storage"] = StorageMock({"find_session": find_session_mock})

    app.config["cookie_storage"] = StorageMock(
        {
            "get_cookie_value": lambda: test_session_uuid,
        }
    )

    response = client.get("/")

    assert response.status_code == 200
    assert minify(response.get_data(as_text=True)) == minify(
        """
<!DOCTYPE html><html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Task Tracker :: Home</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
</head>

<body>
    <div class="'container">
        <h1>Task Tracker</h1>
        <nav>
            <a href="/">Home</a>
            <a href="/tasks">Tasks</a>
            <a href="/logout">Logout</a>
        </nav>
        <hr>
    </div>
</body>
</html>
"""
    )


def test_root_unauthorized(client):
    test_session_uuid = "e6bb1782-fbab-4c25-8bfd-92757bcdf1db"

    def find_session_mock(session_uuid: str) -> Optional[UserSession]:
        assert session_uuid == test_session_uuid
        return None

    app.config["session_storage"] = StorageMock({"find_session": find_session_mock})

    app.config["cookie_storage"] = StorageMock(
        {
            "get_cookie_value": lambda: test_session_uuid,
        }
    )

    response = client.get("/")

    assert response.status_code == 200
    assert minify(response.get_data(as_text=True)) == minify(
        """
<!DOCTYPE html><html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Task Tracker :: Home</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
</head>

<body>
    <div class="'container">
        <h1>Task Tracker</h1>
        <nav>
            <a href="/">Home</a>
            <a href="/login">Login</a>
            <a href="/register">Register</a>
        </nav>
        <hr>
    </div>
</body>
</html>
"""
    )
