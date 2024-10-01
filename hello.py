from flask import Flask, redirect, render_template, request
import json
from typing import NamedTuple


class Task(NamedTuple):
    name: str
    description: str


class TaskStorage:
    def read_json(self) -> dict:
        try:
            f = open("tasks.json", "r", encoding="utf-8")
            tasks = json.load(f)
            f.close()
        except FileNotFoundError:
            print("[INFO] tasks file not found, creating a new one")
            tasks = {}
            self.write_json(tasks)
        return tasks

    def write_json(self, tasks: dict) -> None:
        with open("tasks.json", "w", encoding="utf-8") as f:
            json.dump(tasks, f, sort_keys=True, indent=2, ensure_ascii=False)

    def add(self, task: Task) -> int:
        tasks = self.read_json()
        if len(tasks.keys()) == 0:
            new_task_id = 1
        else:
            task_ids = map(lambda x: int(x), tasks.keys())
            new_task_id = max(task_ids) + 1
        tasks[str(new_task_id)] = {
            "name": task.name,
            "description": task.description,
        }
        self.write_json(tasks)

        return new_task_id

    def update(self, task_key: str, updated_task: Task) -> None:
        tasks = self.read_json()
        tasks[task_key] = {
            "name": updated_task.name,
            "description": updated_task.description,
        }
        self.write_json(tasks)

    def delete(self, task_key: str) -> None:
        tasks = self.read_json()
        del tasks[task_key]
        self.write_json(tasks)


app = Flask(__name__)
task_storage = TaskStorage()


@app.route("/", methods=["GET"])
def root():
    return redirect("/tasks")


@app.route("/tasks", methods=["GET"])
def get_tasks():
    chores = task_storage.read_json()
    return render_template("tasks.html", tasks=chores)


@app.route("/tasks/<string:id>", methods=["GET"])
def show_task(id: str):
    chores = task_storage.read_json()
    return render_template("task.html", task=chores[id], task_id=id)


@app.route("/tasks/new", methods=["GET"])
def show_new_task_form():
    return render_template("new.html")


@app.route("/tasks/create", methods=["POST"])
def create_task():
    new_task = Task(
        request.form["task_name"],
        request.form["task_description"],
    )
    new_task_id = task_storage.add(new_task)
    return redirect(f"/tasks/{new_task_id}")


@app.route("/tasks/<string:id>/edit", methods=["GET"])
def show_edit_task_form(id: str):
    chores = task_storage.read_json()
    return render_template("edit.html", task=chores[id], task_id=id)


"""
Пользователь открыл в браузере существующую задачу, отредакровал её и нажал
кнопку Submit на форме.

В результате браузер отправил на сервер HTTP запрос:

```
POST /tasks/<task_id>/update

task_name=...
task_description=...
```

(чтобы это понять см. файл edit.html)
"""


@app.route("/tasks/<string:id>/update", methods=["POST"])
def update_task(id: str):
    updated_task = Task(request.form["task_name"], request.form["task_description"])
    task_storage.update(id, updated_task)
    return redirect(f"/tasks/{id}")


@app.route("/tasks/<string:id>/delete", methods=["GET"])
def delete_task(id: str):
    task_storage.delete(id)
    return redirect("/tasks")
