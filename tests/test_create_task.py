import pytest
from utils import StorageMock, minify
from entity.task import Task
from entity.session import UserSession
from unittest.mock import patch
from typing import Optional

from app import app

@pytest.fixture
def client():
    """A test client for the app."""
    with app.test_client() as client:
        yield client


def test_create_task_unauthorized(client):
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

    response = client.post("/tasks/create", data={
            "task_name": "Погулять в парке",
        })

    assert response.status_code == 401
    assert minify(response.get_data(as_text=True)) == minify(
        """
<!doctype html>
<html lang=en>
<title>401 Unauthorized</title>
<h1>Unauthorized</h1>
<p>The server could not verify that you are authorized to access the URL requested. You either supplied the wrong credentials (e.g. a bad password), or your browser doesn&#39;t understand how to supply the credentials required.</p>
        """
)


def test_create_task_authorized(client):
    test_csrf_token = "fixed_csrf_token_value"
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
    def create_mock(task: Task) -> int:
        assert task.name == "Пилатес"
        return 5

    app.config["task_storage"] = StorageMock({"create": create_mock})

    response = client.post(
        "/tasks/create",  # query of HTTP request
        data={
            "task_name": "Пилатес",
            "csrf_token": test_csrf_token,
        },  # data - body of http post-request
    )

    assert response.status_code == 302
    assert response.headers.get("Location") == "/tasks"  # header of HTTP post-response
