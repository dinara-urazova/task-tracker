import sys
import os
import re
import pytest
from entity.task import Task

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app


class TaskStorageMock:
    def __init__(self, dictionary: dict) -> None:
        for k, v in dictionary.items():
            setattr(self, k, v)


def minify(html: str) -> str:
    """
    Remove line breaks and spaces betweeen HTML tags
    TODO: fix test_minify_line_break and delete pytest.mark.skip
    Example: "<tag> </tag>   " -> "<tag></tag>"
    """
    return re.sub(r">\s+<", "><", html).strip()


def test_minify() -> None:
    html = """
    <h1>Hello world</h1>
    <p>Lorem ipsum</p>
"""
    assert minify(html) == "<h1>Hello world</h1><p>Lorem ipsum</p>"


@pytest.mark.skip(reason="need to implement a line break between tag attributes")
def test_minify_line_break() -> None:
    html = """
    <textarea id="task_description" name="task_description" rows="10" cols="30" required minlength="3"
        maxlength="2000"></textarea><br><br>
"""
    assert (
        minify(html)
        == '<textarea id="task_description" name="task_description" rows="10" cols="30" required minlength="3" maxlength="2000"></textarea><br><br>'
    )


def test_root():
    client = app.test_client()
    response = client.get("/")

    assert response.status_code == 302
    assert response.headers.get("Location") == "/tasks"  # header of HTTP response


def test_get_tasks_empty():
    app.config["task_storage"] = TaskStorageMock(
        {
            "read_all": lambda: [],  # autotests for this endpoint feature a use of lambda func instead of a regular func
        }
    )

    client = app.test_client()
    response = client.get("/tasks")

    assert response.status_code == 200
    assert (
        minify(response.get_data(as_text=True))
        == '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Task Tracker</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet"></head><body><div class="container mt-5"><h1 class="text-center mb-4">To Do List</h1><div class="row justify-content-center"><div class="col-md-8"><div class="card"><div class="card-body"><form id="todo-form" action="/tasks/create" method="post"><div class="input-group mb-3"><input type="text" class="form-control" id="todo-input" placeholder="Add new task" required name="task_name"><input type="hidden" name="task_description" value="undefined"><button class="btn btn-primary" type="submit">Add</button></div></form><ul class="list-group" id="todo-list"><p>Список пуст. Создайте свою первую задачу.</p></ul></div></div></div></div></div></body></html>'
    )


def test_get_tasks_not_empty():
    app.config["task_storage"] = TaskStorageMock(
        {
            "read_all": lambda: [
                {
                    "id": 1,
                    "name": "Отдохнуть",
                    "description": "Посмотреть фильм",
                },
                {
                    "id": 7,
                    "name": "Сходить в магазин",
                    "description": "Хлеб, молоко",
                },
            ]
        }
    )

    client = app.test_client()
    response = client.get("/tasks")

    assert response.status_code == 200
    assert (
        minify(response.get_data(as_text=True))
        == '<h1>Все задачи</h1><a href="/tasks/new">Создать новую</a><ol><li><a href="/tasks/1">Отдохнуть</a></li><li><a href="/tasks/7">Сходить в магазин</a></li></ol>'
    )


def test_get_task_not_found():
    def read_by_id_mock(id):
        assert id == "1"
        return None

    app.config["task_storage"] = TaskStorageMock({"read_by_id": read_by_id_mock})

    client = app.test_client()
    response = client.get("/tasks/1")

    assert response.status_code == 404
    assert (
        minify(response.get_data(as_text=True))
        == "<!doctype html><html lang=en><title>404 Not Found</title><h1>Not Found</h1><p>Task with id = 1 not found</p>"
    )


def test_get_task_found():
    def read_by_id_mock(id):
        assert id == "1"
        return {
            "id": 1,
            "name": "Продукты",
            "description": "Купить хлеб и молоко",
        }

    app.config["task_storage"] = TaskStorageMock({"read_by_id": read_by_id_mock})

    client = app.test_client()
    response = client.get("/tasks/1")  # query of HTTP request

    assert response.status_code == 200  # status code of HTTP response
    assert (
        minify(response.get_data(as_text=True))
        == '<a href="/tasks">Вернуться на главную</a><h1>Продукты</h1><h2>Описание</h2><p>Купить хлеб и молоко</p><p><em>Дата и время создания:</em></p><p><em>Дата и время последнего изменения:</em></p><a href="/tasks/1/edit">Редактировать</a>'
    )


def test_get_new_task_form():
    client = app.test_client()
    response = client.get("/tasks/new")  # query of HTTP request

    assert response.status_code == 200
    assert (
        minify(response.get_data(as_text=True))
        == '<a href="/tasks">Назад</a><br><br><form action="/tasks/create" method="post"><label for="task_name">Название:</label><input type="text" id="task_name" name="task_name" required minlength="3" maxlength="100"><br><br><label for="task_description">Описание:</label><textarea id="task_description" name="task_description" rows="10" cols="30" required minlength="3" maxlength="2000"></textarea><br><br><input type="submit" value="Сохранить"></form>'
    )


def test_create_task():
    def create_mock(task: Task) -> int:
        assert task.name == "Пилатес"
        assert task.description == "Заниматься 30 мин"
        return 506

    app.config["task_storage"] = TaskStorageMock({"create": create_mock})

    client = app.test_client()
    response = client.post(
        "/tasks/create",  # query of HTTP request
        data={
            "task_name": "Пилатес",
            "task_description": "Заниматься 30 мин",
        },  # data - body of http post-request
    )

    assert response.status_code == 302
    assert (
        response.headers.get("Location") == "/tasks/506"
    )  # header of HTTP post-response


def test_create_task_name_too_small():
    def create_mock(task: Task) -> int:
        assert False

    app.config["task_storage"] = TaskStorageMock({"create": create_mock})

    client = app.test_client()
    response = client.post(
        "/tasks/create",  # query of HTTP request
        data={
            "task_name": "12",
            "task_description": "Сходить в магазин",
        },  # data - body of http post-request
    )

    assert response.status_code == 400
    assert (
        minify(response.get_data(as_text=True))
        == "<!doctype html><html lang=en><title>400 Bad Request</title><h1>Bad Request</h1><p>Task name and task description should both contain at least 3 characters</p>"
    )


def test_create_task_description_too_small():
    def create_mock(task: Task) -> int:
        assert False

    app.config["task_storage"] = TaskStorageMock({"create": create_mock})

    client = app.test_client()
    response = client.post(
        "/tasks/create",  # query of HTTP request
        data={
            "task_name": "Купить продукты",
            "task_description": "Сх",
        },  # data - body of http post-request
    )

    assert response.status_code == 400
    assert (
        minify(response.get_data(as_text=True))
        == "<!doctype html><html lang=en><title>400 Bad Request</title><h1>Bad Request</h1><p>Task name and task description should both contain at least 3 characters</p>"
    )


def test_create_task_name_too_big():
    def create_mock(task: Task) -> int:
        assert False

    app.config["task_storage"] = TaskStorageMock({"create": create_mock})

    client = app.test_client()
    task_name = "a" * 101
    response = client.post(
        "/tasks/create",  # query of HTTP request
        data={
            "task_name": task_name,
            "task_description": "Сходить в магазин",
        },  # data - body of http post-request
    )

    assert response.status_code == 400
    assert (
        minify(response.get_data(as_text=True))
        == "<!doctype html><html lang=en><title>400 Bad Request</title><h1>Bad Request</h1><p>Task name should contain no more than 100 characters</p>"
    )


def test_create_task_description_too_big():
    def create_mock(task: Task) -> int:
        assert False

    app.config["task_storage"] = TaskStorageMock({"create": create_mock})

    client = app.test_client()
    task_description = "a" * 2001
    response = client.post(
        "/tasks/create",  # query of HTTP request
        data={
            "task_name": "Сделать домашнее",
            "task_description": task_description,
        },  # data - body of http post-request
    )

    assert response.status_code == 400
    assert (
        minify(response.get_data(as_text=True))
        == "<!doctype html><html lang=en><title>400 Bad Request</title><h1>Bad Request</h1><p>Task description should contain no more than 2000 characters</p>"
    )


def test_edit_task_not_found_form():
    def read_by_id_mock(id):
        assert id == "1"
        return None

    app.config["task_storage"] = TaskStorageMock({"read_by_id": read_by_id_mock})

    client = app.test_client()
    response = client.get("/tasks/1/edit")  # query of HTTP request

    assert response.status_code == 404
    assert (
        minify(response.get_data(as_text=True))
        == "<!doctype html><html lang=en><title>404 Not Found</title><h1>Not Found</h1><p>Task with id = 1 not found</p>"
    )


def test_edit_task_found_form():
    def read_by_id_mock(id):
        assert id == "1"
        return {
            "id": 1,
            "name": "Отдохнуть",
            "description": "Посмотреть фильм",
        }

    app.config["task_storage"] = TaskStorageMock({"read_by_id": read_by_id_mock})

    client = app.test_client()
    response = client.get("/tasks/1/edit")  # query of HTTP request

    assert response.status_code == 200
    assert (
        minify(response.get_data(as_text=True))
        == '<a href="/tasks/1">Назад</a><br><br><a href="/tasks/1/delete">Удалить</a><br><br><form action="/tasks/1/update" method="post"><label for="task_name">Название:</label><input type="text" id="task_name" name="task_name" value="Отдохнуть" required minlength="3" maxlength="100"><br><br><label for="task_description">Описание:</label><textarea id="task_description" name="task_description" rows="10" cols="30" required minlength="3" maxlength="2000">Посмотреть фильм</textarea><br><br><input type="submit" value="Сохранить"></form>'
    )


def test_update_task_not_found():
    def read_by_id_mock(id):
        assert id == "1"
        return None

    app.config["task_storage"] = TaskStorageMock({"read_by_id": read_by_id_mock})

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
        return Task(id=1, name="Отдохнуть", description="Посмотреть фильм")

    def update_task_mock(task: Task):
        assert task.id == 1
        assert task.name == "Пилатес"
        assert task.description == "Заниматься 30 мин"

    app.config["task_storage"] = TaskStorageMock(
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
            "task_description": "Заниматься 30 мин",
        },  # data - body of http post-request
    )
    assert response.status_code == 302
    assert response.headers.get("Location") == "/tasks/1"


def test_update_task_name_too_small():
    def read_by_id_mock(id):
        assert id == "1"
        return Task(id=1, name="Купить продукты", description="Купить молоко и хлеб")

    def update_task_mock(task_key: str, updated_task: Task):
        assert False

    app.config["task_storage"] = TaskStorageMock(
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
            "task_description": "Заниматься 30 мин",
        },  # data - body of http post-request
    )

    assert response.status_code == 400
    assert (
        minify(response.get_data(as_text=True))
        == "<!doctype html><html lang=en><title>400 Bad Request</title><h1>Bad Request</h1><p>Task name and task description should both contain at least 3 characters</p>"
    )


def test_update_task_description_too_small():
    def read_by_id_mock(id):
        assert id == "1"
        return Task(id=1, name="Купить продукты", description="Купить молоко и хлеб")

    def update_task_mock(task_key: str, updated_task: Task):
        assert False

    app.config["task_storage"] = TaskStorageMock(
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
            "task_description": "За",
        },  # data - body of http post-request
    )

    assert response.status_code == 400
    assert (
        minify(response.get_data(as_text=True))
        == "<!doctype html><html lang=en><title>400 Bad Request</title><h1>Bad Request</h1><p>Task name and task description should both contain at least 3 characters</p>"
    )


def test_update_task_name_too_big():
    def read_by_id_mock(id):
        assert id == "1"
        return Task(id=1, name="Купить продукты", description="Купить молоко и хлеб")

    def update_task_mock(task_key: str, updated_task: Task):
        assert False

    app.config["task_storage"] = TaskStorageMock(
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
            "task_description": "Заниматься 30 мин",
        },  # data - body of http post-request
    )

    assert response.status_code == 400
    assert (
        minify(response.get_data(as_text=True))
        == "<!doctype html><html lang=en><title>400 Bad Request</title><h1>Bad Request</h1><p>Task name should contain no more than 100 characters</p>"
    )


def test_update_task_description_too_big():
    def read_by_id_mock(id):
        assert id == "1"
        return Task(id=1, name="Купить продукты", description="Купить молоко и хлеб")

    def update_task_mock(task_key: str, updated_task: Task):
        assert False

    app.config["task_storage"] = TaskStorageMock(
        {
            "read_by_id": read_by_id_mock,
            "update": update_task_mock,
        }
    )

    client = app.test_client()
    task_description = "a" * 2001
    response = client.post(
        "/tasks/1/update",  # query of HTTP request
        data={
            "task_name": "Пилатес",
            "task_description": task_description,
        },  # data - body of http post-request
    )

    assert response.status_code == 400
    assert (
        minify(response.get_data(as_text=True))
        == "<!doctype html><html lang=en><title>400 Bad Request</title><h1>Bad Request</h1><p>Task description should contain no more than 2000 characters</p>"
    )


def test_delete_task_not_found():
    def read_by_id_mock(id):
        assert id == "1"
        return None

    app.config["task_storage"] = TaskStorageMock({"read_by_id": read_by_id_mock})

    client = app.test_client()
    response = client.get("/tasks/1/delete")

    assert response.status_code == 404
    assert (
        minify(response.get_data(as_text=True))
        == "<!doctype html><html lang=en><title>404 Not Found</title><h1>Not Found</h1><p>Task with id = 1 not found</p>"
    )


def test_delete_task_found():
    def read_by_id_mock(id):
        assert id == "1"
        return {
            "id": 1,
            "name": "Отдохнуть",
            "description": "Посмотреть фильм",
        }

    def delete_mock(id):
        assert id == "1"

    app.config["task_storage"] = TaskStorageMock(
        {
            "read_by_id": read_by_id_mock,
            "delete": delete_mock,
        }
    )
    client = app.test_client()
    response = client.get("/tasks/1/delete")  # query of HTTP request
    assert response.status_code == 302
    assert response.headers.get("Location") == "/tasks"
