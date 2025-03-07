import pytest
from utils import minify, StorageMock
from entity.session import UserSession
from entity.task import Task
from typing import Optional

from app import app


@pytest.fixture
def client():
    """A test client for the app."""

    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as client:
        yield client


def test_update_unauthorized(client):
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

    response = client.post("/tasks/1/update", data={"task_name": "Пойти в кино"})

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


def test_update_task_authorized(client):
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

    def read_by_id_mock(task_id: int, user_id: int) -> Task:
        assert task_id == 1
        assert user_id == 1
        return Task(id=1, name="Отдохнуть", user_id=1)

    def update_mock(task: Task):
        assert task.id == 1
        assert task.name == "Пилатес"
        assert task.user_id == 1

    app.config["task_storage"] = StorageMock(
        {
            "read_by_id": read_by_id_mock,
            "update": update_mock,
        }
    )

    response = client.post(
        "/tasks/1/update",  # query of HTTP request
        data={
            "task_name": "Пилатес",
        },  # data - body of http post-request
    )

    assert response.status_code == 302
    assert response.headers.get("Location") == "/tasks"
