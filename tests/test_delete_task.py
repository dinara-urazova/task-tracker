import pytest
from unittest.mock import patch
from utils import minify, StorageMock
from entity.session import UserSession
from entity.task import Task
from typing import Optional

from app import app


@pytest.fixture
def client():
    """A test client for the app."""
    with app.test_client() as client:
        yield client


def test_delete_task_unauthorized(client):

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

    response = client.get("/tasks/1/delete")

    assert response.status_code == 401
    assert (
        minify(response.get_data(as_text=True))
        == "<!doctype html><html lang=en><title>401 Unauthorized</title><h1>Unauthorized</h1><p>The server could not verify that you are authorized to access the URL requested. You either supplied the wrong credentials (e.g. a bad password), or your browser doesn&#39;t understand how to supply the credentials required.</p>"
    )


def test_delete_task_authorized(client):

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

    def read_by_id_mock(id, user_id):
        assert id == 1
        assert user_id == 1
        return Task(id=1, name="Отдохнуть", user_id=1)

    def delete_mock(task_to_delete: Task):
        assert task_to_delete.id == 1
        assert task_to_delete.user_id == 1

    app.config["task_storage"] = StorageMock(
        {
            "read_by_id": read_by_id_mock,
            "delete": delete_mock,
        }
    )

    response = client.get("/tasks/1/delete")  # query of HTTP request
    assert response.status_code == 302
    assert response.headers.get("Location") == "/tasks"