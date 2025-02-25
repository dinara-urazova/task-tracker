import sys
import os
import pytest
from entity.task import Task
from config_reader import Settings
from utils import minify, StorageMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

env_config = Settings()


@pytest.fixture
def client():
    """A test client for the app."""
    with app.test_client() as client:
        yield client


def test_get_tasks_unauthorized(client):

    response = client.get("/tasks")

    assert response.status_code == 401
    assert (
        minify(response.get_data(as_text=True))
        == """<!doctype html><html lang=en><title>401 Unauthorized</title><h1>Unauthorized</h1><p>The server could not verify that you are authorized to access the URL requested. You either supplied the wrong credentials (e.g. a bad password), or your browser doesn&#39;t understand how to supply the credentials required.</p>"""
    )


def test_get_tasks_authorized(client):

    app.config["session_storage"] = StorageMock(
        {
            "find_session": lambda: {
                "id": 1,
                "session_uuid": "test_session_uuid",
                "user_id": 1,
            }
        }
    )

    app.config["task_storage"] = StorageMock(
        {
            "read_all": lambda user_id: [
                {"id": 1, "name": "Отдохнуть", user_id: 1},
                {
                    "id": 2,
                    "name": "Сходить в магазин",
                    user_id: 1,
                },
            ]
        }
    )

    response = client.get("/tasks")

    assert response.status_code == 200
    assert (
        minify(response.get_data(as_text=True))
        == """
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Task Tracker :: Tasks</title>
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
        

<div class="container mt-5">
    <h1 class="text-center mb-4">To Do List</h1>
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="card">
                <div class="card-body">
                    <form id="todo-form" action="/tasks/create" method="post">
                        <input id="csrf_token" name="csrf_token" type="hidden" value="IjhlY2JkOWQyNDYzOTY2ZTk3NjI2NDZmYTcxYWY3YmE4MmM4NTFjNDQi.Z72a3Q.ZYDXYZ9J4uAmgdZjF8KhtEcT_FA"> 
                        <div class="input-group mb-3">
                            <input class="form-control" id="task_name" maxlength="100" minlength="3" name="task_name" placeholder="Add new task" required type="text" value=""> 
                            <input class="btn btn-primary" id="submit" name="submit" type="submit" value="Add Task"> 
                        </div>
                    </form>
                    <ul class="list-group" id="todo-list">
                        
                        
                        <form action="/tasks/1/update" method="post">
                            <input id="csrf_token" name="csrf_token" type="hidden" value="IjhlY2JkOWQyNDYzOTY2ZTk3NjI2NDZmYTcxYWY3YmE4MmM4NTFjNDQi.Z72a3Q.ZYDXYZ9J4uAmgdZjF8KhtEcT_FA">
                            <li class="list-group-item d-flex justify-content-between align-items-center">                            
                                <span class="task-text">Отдохнуть</span>
                                <input type="text" name="task_name" class="form-control edit-input" style="display: none;" value="Отдохнуть">
                                <div class="btn-group">
                                    <a href="/tasks/1/delete" class="btn btn-danger btn-sm delete-btn">&#x2715;</a>
                                    <button type="button" class="btn btn-primary btn-sm edit-btn">&#9998;</button>
                                </div>
                            </li>
                        </form>
                        
                        <form action="/tasks/2/update" method="post">
                            <input id="csrf_token" name="csrf_token" type="hidden" value="IjhlY2JkOWQyNDYzOTY2ZTk3NjI2NDZmYTcxYWY3YmE4MmM4NTFjNDQi.Z72a3Q.ZYDXYZ9J4uAmgdZjF8KhtEcT_FA">
                            <li class="list-group-item d-flex justify-content-between align-items-center">                            
                                <span class="task-text">Сходить в магазин</span>
                                <input type="text" name="task_name" class="form-control edit-input" style="display: none;" value="Сходить в магазин">
                                <div class="btn-group">
                                    <a href="/tasks/2/delete" class="btn btn-danger btn-sm delete-btn">&#x2715;</a>
                                    <button type="button" class="btn btn-primary btn-sm edit-btn">&#9998;</button>
                                </div>
                            </li>
                        </form>
                        
                        
                    </ul>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
    document.getElementById("todo-list").addEventListener("click", function (event) {
        if (event.target.classList.contains("edit-btn")) {
            const taskText = event.target.parentElement
                .parentElement.querySelector(".task-text");
            const editInput = event.target.parentElement
                .parentElement.querySelector(".edit-input");
            const taskEditBlueButton = event.target.parentElement
                .parentElement.querySelector(".btn-group .edit-btn");

            const taskForm = event.target.parentElement.parentElement.parentElement;

            if (taskText.style.display !== "none") {
                event.preventDefault();
                // этот код переводит задачу в режим редактирования (синяя кнопка - галочка)
                taskText.style.display = "none";
                editInput.style.display = "block";
                editInput.focus();
                event.target.innerHTML = "&#10004;";
                taskEditBlueButton.type = "submit";
                // нужно у синей кнопки-галочки сделать type = submit при помощи JavaScript
            } else {
                // этот код переводит задачу в режим просмотра (синяя кнопка - карандаш)
                taskText.textContent = editInput.value;
                taskText.style.display = "inline";
                editInput.style.display = "none";
                event.target.innerHTML = "&#9998;";
                taskForm.submit();
            }
        }
    });
</script>


    </div>
</body>

</html>
"""
    )


def test_create_task():
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


def test_create_task_name_too_small():
    def create_mock(task: Task) -> int:
        assert False

    app.config["task_storage"] = StorageMock({"create": create_mock})

    client = app.test_client()
    response = client.post(
        "/tasks/create",  # query of HTTP request
        data={
            "task_name": "12",
        },  # data - body of http post-request
    )

    assert response.status_code == 400
    assert (
        minify(response.get_data(as_text=True))
        == "<!doctype html><html lang=en><title>400 Bad Request</title><h1>Bad Request</h1><p>Task name should contain at least 3 characters</p>"
    )


def test_create_task_name_too_big():
    def create_mock(task: Task) -> int:
        assert False

    app.config["task_storage"] = StorageMock({"create": create_mock})

    client = app.test_client()
    task_name = "a" * 101
    response = client.post(
        "/tasks/create",  # query of HTTP request
        data={
            "task_name": task_name,
        },  # data - body of http post-request
    )

    assert response.status_code == 400
    assert (
        minify(response.get_data(as_text=True))
        == "<!doctype html><html lang=en><title>400 Bad Request</title><h1>Bad Request</h1><p>Task name should contain no more than 100 characters</p>"
    )


def test_update_task_not_found():
    def read_by_id_mock(id):
        assert id == "1"
        return None

    app.config["task_storage"] = StorageMock({"read_by_id": read_by_id_mock})

    client = app.test_client()
    response = client.post("/tasks/1/update")

    assert response.status_code == 404
    assert (
        minify(response.get_data(as_text=True))
        == "<!doctype html><html lang=en><title>404 Not Found</title><h1>Not Found</h1><p>Task with id = 1 not found</p>"
    )


def test_update_task_found():
    def read_by_id_mock(id):
        assert id == "1"
        return Task(id=1, name="Отдохнуть", user_id=1)

    def update_task_mock(task: Task):
        assert task.id == 1
        assert task.name == "Пилатес"

    app.config["task_storage"] = StorageMock(
        {
            "read_by_id": read_by_id_mock,
            "update": update_task_mock,
        }
    )

    client = app.test_client()
    response = client.post(
        "/tasks/1/update",  # query of HTTP request
        data={
            "task_name": "Пилатес",
        },  # data - body of http post-request
    )
    assert response.status_code == 302
    assert response.headers.get("Location") == "/tasks"


def test_update_task_name_too_small():
    def read_by_id_mock(id):
        assert id == "1"
        return Task(id=1, name="Купить продукты")

    def update_task_mock(task_key: str, updated_task: Task):
        assert False

    app.config["task_storage"] = StorageMock(
        {
            "read_by_id": read_by_id_mock,
            "update": update_task_mock,
        }
    )

    client = app.test_client()
    response = client.post(
        "/tasks/1/update",  # query of HTTP request
        data={
            "task_name": "Пи",
        },  # data - body of http post-request
    )

    assert response.status_code == 400
    assert (
        minify(response.get_data(as_text=True))
        == "<!doctype html><html lang=en><title>400 Bad Request</title><h1>Bad Request</h1><p>Task name should contain at least 3 characters</p>"
    )


def test_update_task_name_too_big():
    def read_by_id_mock(id):
        assert id == "1"
        return Task(id=1, name="Купить продукты")

    def update_task_mock(task_key: str, updated_task: Task):
        assert False

    app.config["task_storage"] = StorageMock(
        {
            "read_by_id": read_by_id_mock,
            "update": update_task_mock,
        }
    )

    client = app.test_client()
    task_name = "a" * 101
    response = client.post(
        "/tasks/1/update",  # query of HTTP request
        data={
            "task_name": task_name,
        },  # data - body of http post-request
    )

    assert response.status_code == 400
    assert (
        minify(response.get_data(as_text=True))
        == "<!doctype html><html lang=en><title>400 Bad Request</title><h1>Bad Request</h1><p>Task name should contain no more than 100 characters</p>"
    )


def test_delete_task_unauthorized(client):

    response = client.get("/tasks/1/delete")

    assert response.status_code == 404
    assert (
        minify(response.get_data(as_text=True))
        == "<!doctype html><html lang=en><title>404 Not Found</title><h1>Not Found</h1><p>Task with id = 1 not found</p>"
    )


def test_delete_task_not_found(client):
    def read_by_id_mock(id):
        assert id == "1"
        return None

    app.config["task_storage"] = StorageMock({"read_by_id": read_by_id_mock})

    response = client.get("/tasks/1/delete")

    assert response.status_code == 404
    assert (
        minify(response.get_data(as_text=True))
        == "<!doctype html><html lang=en><title>404 Not Found</title><h1>Not Found</h1><p>Task with id = 1 not found</p>"
    )


def test_delete_task_found():
    def read_by_id_mock(id):
        assert id == "1"
        return Task(id=1, name="Отдохнуть")

    def delete_mock(task_to_delete: Task):
        assert task_to_delete.id == 1

    app.config["task_storage"] = StorageMock(
        {
            "read_by_id": read_by_id_mock,
            "delete": delete_mock,
        }
    )
    client = app.test_client()
    response = client.get("/tasks/1/delete")  # query of HTTP request
    assert response.status_code == 302
    assert response.headers.get("Location") == "/tasks"
