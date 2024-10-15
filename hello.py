from flask import Flask, redirect, render_template, request
from task_storage import TaskStorage, Task
from datetime import datetime, timezone


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
    created_at = updated_at = datetime.now(timezone.utc).isoformat
    new_task = Task(
        request.form["task_name"],
        request.form["task_description"],
        created_at,
        updated_at,
    )
    new_task_id = task_storage.create(new_task)
    return redirect(f"/tasks/{new_task_id}")


@app.route("/tasks/<string:id>/edit", methods=["GET"])
def show_edit_task_form(id: str):
    chores = task_storage.read_json()
    return render_template("edit.html", task=chores[id], task_id=id)


@app.route("/tasks/<string:id>/update", methods=["POST"])
def update_task(id: str):
    """
    Пользователь открыл в браузере существующую задачу, отредактировал её и нажал
    кнопку "Сохранить" на форме.

    В результате браузер отправил на сервер HTTP POST-запрос с данными, которые
    ввел пользователь.
    Какие данные придут в этом запросе? (чтобы это понять см. файл edit.html)

    ```
    POST /tasks/<task_id>/update

    task_name=...
    task_description=...
    ```
    """
    updated_at = datetime.now(timezone.utc).isoformat
    updated_task = Task(
        request.form["task_name"],
        request.form["task_description"],
        None,
        updated_at,
    )
    task_storage.update(id, updated_task)
    return redirect(f"/tasks/{id}")


@app.route("/tasks/<string:id>/delete", methods=["GET"])
def delete_task(id: str):
    task_storage.delete(id)
    return redirect("/tasks")
