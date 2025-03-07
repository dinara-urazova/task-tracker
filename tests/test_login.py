import pytest
from utils import StorageMock, minify
from entity.session import UserSession
from entity.user import User
from typing import Optional
from werkzeug.security import check_password_hash, generate_password_hash

from app import app


@pytest.fixture
def client():
    """A test client for the app."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as client:
        yield client


def test_login_unauthorized(client):  # GET request - no session

    def find_session_mock(session_uuid: str) -> Optional[UserSession]:
        assert session_uuid is None
        return None

    app.config["session_storage"] = StorageMock(
        {
            "find_session": find_session_mock,
        }
    )

    app.config["cookie_storage"] = StorageMock(
        {
            "get_cookie_value": lambda: None,
        }
    )
    response = client.get("/login")

    assert response.status_code == 200
    assert minify(response.get_data(as_text=True)) == minify(
        """
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Task Tracker :: Login</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
</head>

<body>
    <div class="container">
        <h1>Task Tracker</h1>
        <nav>
            <a href="/">Home</a>
            <a href="/login">Login</a>
            <a href="/register">Register</a>    
        </nav>
        <hr>
        <h1>Login</h1>

<form action="" method="post" novalidate>
  <p>
    <label for="username">Username</label><br>
    <input id="username" name="username" required size="32" type="text" value="">
  </p>
  <p>
    <label for="password">Password</label><br>
    <input id="password" name="password" required size="32" type="password" value="">
  </p>
  <p><input id="submit" name="submit" type="submit" value="Sign In"></p>
</form>

    </div>
</body>

</html>
        """
    )


def test_login_authorized(client):  # a user has already logged in
    test_session_uuid = "e6bb1782-fbab-4c25-8bfd-92757bcdf1db"

    def find_session_mock(session_uuid: str) -> Optional[UserSession]:
        assert session_uuid == test_session_uuid
        return UserSession(id=1, session_uuid=test_session_uuid, user_id=1)

    app.config["session_storage"] = StorageMock(
        {
            "find_session": find_session_mock,
        }
    )

    app.config["cookie_storage"] = StorageMock(
        {
            "get_cookie_value": lambda: test_session_uuid,
        }
    )
    response = client.post(
        "/login",
        data={
            "username": "Dina",
            "password": "55555555",
        },
    )

    assert response.status_code == 302
    assert response.headers.get("Location") == "/"


def test_login_invalid_password(client):
    hashed_password = generate_password_hash("8754321") # правильный пароль

    def find_session_mock(session_uuid: str) -> Optional[UserSession]:
        assert session_uuid is None
        return None

    app.config["session_storage"] = StorageMock({"find_session": find_session_mock})

    app.config["cookie_storage"] = StorageMock({"get_cookie_value": lambda: None})

    def find_or_verify_user_mock(username: str, password: Optional[str]) -> None:
        assert username == "Dina"
        assert not check_password_hash(hashed_password, password) # проверяем, что пароль неправильный
        return None

    app.config["user_storage"] = StorageMock(
        {
            "find_or_verify_user": find_or_verify_user_mock,
        }
    )

    response = client.post(
        "/login",
        data={
            "username": "Dina",
            "password": "12345678", # передаем неправильный пароль
        },
    )

    assert response.status_code == 302
    assert response.headers.get("Location") == "/login"

def test_login_success(client):
    hashed_password = generate_password_hash("12345678")

    def find_session_mock(session_uuid: str) -> None:
        assert session_uuid is None
        return None

    def create_session_mock(session_uuid, id) -> None:
        assert id == 1
        return None

    app.config["session_storage"] = StorageMock(
        {
            "find_session": find_session_mock,
            "create_session": create_session_mock,
        }
    )

    app.config["cookie_storage"] = StorageMock(
        {
            "get_cookie_value": lambda: None,
        }
    )

    def find_or_verify_user_mock(username: str, password: str) -> User:
        assert username == "Dina"
        assert check_password_hash(hashed_password, password)
        return User(id=1, login="Dina", db_hashed_password=hashed_password)

    app.config["user_storage"] = StorageMock(
        {
            "find_or_verify_user": find_or_verify_user_mock,
        }
    )

    response = client.post(
        "/login",
        data={
            "username": "Dina",
            "password": "12345678",
        },
    )

    assert response.status_code == 302
    assert response.headers.get("Location") == "/tasks"