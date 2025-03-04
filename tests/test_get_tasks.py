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


def test_get_tasks_unauthorized(client):
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

    response = client.get("/tasks")

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


def test_get_tasks_authorized(client):
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

    def read_all_mock(user_id):
        assert user_id == 1
        return [
            Task(id=1, name="Отдохнуть", user_id=1),
            Task(id=2, name="Сходить в магазин", user_id=1),
        ]

    app.config["task_storage"] = StorageMock({"read_all": read_all_mock})

    response = client.get("/tasks")

    assert response.status_code == 200
    assert minify(response.get_data(as_text=True)) == minify(
        """
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
                        <div class="input-group mb-3">
                            <input class="form-control" id="task_name" maxlength="100" minlength="3" name="task_name" placeholder="Add new task" required type="text" value=""> 
                            <input class="btn btn-primary" id="submit" name="submit" type="submit" value="Add Task"> 
                        </div>
                    </form>
                    <ul class="list-group" id="todo-list">                        
                        <form action="/tasks/1/update" method="post">
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
