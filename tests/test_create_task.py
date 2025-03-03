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
    test_csrf_token = "fixed_csrf_token_value"
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

    with patch("flask_wtf.csrf.generate_csrf", return_value=test_csrf_token):
        response = client.post("/tasks/create", data={
            "csrf_token": test_csrf_token, "task_name": "12",
        })

    assert response.status_code == 401
    assert minify(response.get_data(as_text=True)) == minify(
        """
<!doctype html>
<html lang=en>
<title>400 Bad Request</title>
<h1>Unauthorized</h1>
<p>The server could not verify that you are authorized to access the URL requested. You either supplied the wrong credentials (e.g. a bad password), or your browser doesn&#39;t understand how to supply the credentials required.</p>
        """
    )


def test_create_task_authorized():
    def create_mock(task: Task) -> int:
        assert task.name == "Пилатес"
        return 506

    app.config["task_storage"] = StorageMock({"create": create_mock})

    client = app.test_client()
    response = client.post(
        "/tasks/create",  # query of HTTP request
        data={
            "task_name": "Пилатес",
        },  # data - body of http post-request
    )

    assert response.status_code == 302
    assert response.headers.get("Location") == "/tasks"  # header of HTTP post-response


# def test_create_task_name_too_small():
#     def create_mock(task: Task) -> int:
#         assert False

#     app.config["task_storage"] = StorageMock({"create": create_mock})

#     client = app.test_client()
#     response = client.post(
#         "/tasks/create",  # query of HTTP request
#         data={
#             "task_name": "12",
#         },  # data - body of http post-request
#     )

#     assert response.status_code == 400
#     assert (
#         minify(response.get_data(as_text=True))
#         == "<!doctype html><html lang=en><title>400 Bad Request</title><h1>Bad Request</h1><p>Task name should contain at least 3 characters</p>"
#     )

