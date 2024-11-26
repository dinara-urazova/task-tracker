import sys
import os
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app


class TaskStorageMock:
    def __init__(self, dictionary: dict) -> None:
        for k, v in dictionary.items():
            setattr(self, k, v)


def minify(html: str) -> str:
    """
    Remove line breaks and spaces betweeen HTML tags

    Example: "<tag> </tag>   " -> "<tag></tag>"
    """
    return re.sub(r">\s+<", "><", html).strip()


def test_minify() -> None:
    html = """
    <h1>Hello world</h1>
    <p>Lorem ipsum</p>
"""
    assert minify(html) == "<h1>Hello world</h1><p>Lorem ipsum</p>"


def test_root():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 302
    assert response.headers.get("Location") == "/tasks"


def test_get_tasks_empty():
    app.config["task_storage"] = TaskStorageMock(
        {
            "read_all": lambda: {},
        }
    )
    client = app.test_client()
    response = client.get("/tasks")
    assert response.status_code == 200
    assert (
        minify(response.get_data(as_text=True))
        == '<h1>Все задачи</h1><a href="/tasks/new">Создать новую</a><p>Список пуст. Создайте свою первую задачу.</p>'
    )


def test_get_tasks_not_empty():
    app.config["task_storage"] = TaskStorageMock(
        {
            "read_all": lambda: {
                1: {
                    "name": "Отдохнуть",
                    "description": "Посмотреть фильм",
                },
                7: {
                    "name": "Сходить в магазин",
                    "description": "Хлеб, молоко",
                },
            }
        }
    )
    client = app.test_client()
    response = client.get("/tasks")
    assert response.status_code == 200
    assert (
        minify(response.get_data(as_text=True))
        == '<h1>Все задачи</h1><a href="/tasks/new">Создать новую</a><ol><li><a href="/tasks/1">Отдохнуть</a></li><li><a href="/tasks/7">Сходить в магазин</a></li></ol>'
    )


def test_show_task_not_found():
    app.config["task_storage"] = TaskStorageMock({"read_by_id": lambda id: None})
    client = app.test_client()
    response = client.get("/tasks/1")
    assert response.status_code == 404
    assert (
        minify(response.get_data(as_text=True))
        == "<!doctype html><html lang=en><title>404 Not Found</title><h1>Not Found</h1><p>Task with id = 1 not found</p>"
    )


def test_show_task_found():
    app.config["task_storage"] = TaskStorageMock(
        {
            "read_by_id": lambda id: {
                "name": "Продукты",
                "description": "Купить хлеб и молоко",
            },
        }
    )
    client = app.test_client()
    response = client.get("/tasks/1")
    assert response.status_code == 200
    assert (
        minify(response.get_data(as_text=True))
        == '<a href="/tasks">Вернуться на главную</a><h1>Продукты</h1><h2>Описание</h2><p>Купить хлеб и молоко</p><p><em>Дата и время создания:</em></p><p><em>Дата и время последнего изменения:</em></p><a href="/tasks/1/edit">Редактировать</a>'
    )


def test_show_new_task_form():
    client = app.test_client()
    response = client.get("/tasks/new")
    assert response.status_code == 200
    assert (
        (response.get_data(as_text=True))
        == '<a href="/tasks">Назад</a><br><br><form action="/tasks/create" method="post"><label for="task_name">Название:</label><input type="text" id="task_name" name="task_name" required minlength="3" maxlength="100"><br><br><label for="task_description">Описание:</label><textarea id="task_description" name="task_description" rows="10" cols="30" required minlength="3"maxlength="2000"></textarea><br><br><input type="submit" value="Сохранить"></form>'
    )


def test_update_task_not_found():
    app.config["task_storage"] = TaskStorageMock({"read_by_id": lambda id: None})
    client = app.test_client()
    response = client.post("/tasks/1/update")
    assert response.status_code == 404
    assert (
        minify(response.get_data(as_text=True))
        == "<!doctype html><html lang=en><title>404 Not Found</title><h1>Not Found</h1><p>Task with id = 1 not found</p>"
    )


def test_update_task_found():
    app.config["task_storage"] = TaskStorageMock(
        {
            "read_by_id": lambda id: {
                "name": "Продукты",
                "description": "Купить хлеб и молоко",
            },
        }
    )
    client = app.test_client()
    response = client.get("/tasks/1/update")
    assert response.status_code == 200 # всего 2 запроса 302 + 200  
    assert response.headers.post("Location") == "/tasks/1"
    # дб какое-то изменение 

def test_delete_task_not_found():
    app.config["task_storage"] = TaskStorageMock(
        {
            "read_by_id": lambda id: None
        }
    )
    client = app.test_client()
    response = client.get("/tasks/1/delete")
    assert response.status_code == 404
    assert (
        minify(response.get_data(as_text=True))
        == "<!doctype html><html lang=en><title>404 Not Found</title><h1>Not Found</h1><p>Task with id = 1 not found</p>"
    )
    
    
    
    def test_delete_task_found():
        app.config["task_storage"] = TaskStorageMock(
        {
            "read_all": lambda: {
                1: {
                    "name": "Отдохнуть",
                    "description": "Посмотреть фильм",
                },
            }
        }
    )
    client = app.test_client()
    response = client.get("/tasks/1/delete")
    assert response.status_code == 200 # всего 2 запроса 302 + 200  
    assert response.headers.post("Location") == "/tasks"
    # дб какое-то изменение 

 