import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app


class TaskStorageMock:
    def __init__(self, dictionary: dict) -> None:
        for k, v in dictionary.items():
            setattr(self, k, v)


def test_root():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 302
    assert response.headers.get("Location") == "/tasks"


def test_get_tasks_empty():
    app.config["task_storage"] = TaskStorageMock(
        {
            "read_all": lambda: [],
        }
    )
    client = app.test_client()
    response = client.get("/tasks")
    assert response.status_code == 200
    assert (
        response.get_data(as_text=True)
        == """<h1>Все задачи</h1>

<a href="/tasks/new">Создать новую</a>


<p>Список пуст. Создайте свою первую задачу.</p>
"""
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
        response.get_data(as_text=True)
        == """<h1>Все задачи</h1>\n
<a href="/tasks/new">Создать новую</a>\n\n
<ol>
    
    <li><a href="/tasks/1">Отдохнуть</a></li>
    
    <li><a href="/tasks/7">Сходить в магазин</a></li>
    
</ol>
"""
    )
