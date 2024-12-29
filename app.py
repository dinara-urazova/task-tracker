from flask import abort, Flask, redirect, render_template, request, current_app
from entity.task import Task

from task_storage_sql_alchemy import TaskStorageSqlAlchemy


app = Flask(__name__)
app.config["task_storage"] = TaskStorageSqlAlchemy()


@app.route("/", methods=["GET"])
def root():
    """
    Что должен проверить автотест?
    1. Делает HTTP-запрос GET /
    2. Проверяет, что ответил сервер
    2.1 status = 302 (Redirect)
    2.2 Response Header "Location" = "/tasks"
    """
    return redirect("/tasks")


@app.route("/tasks", methods=["GET"])
def get_tasks():
    task_storage = current_app.config["task_storage"]
    chores = task_storage.read_all()
    return render_template("tasks.html", tasks=chores)


@app.route("/tasks/<string:id>", methods=["GET"])
def get_task(id: str):
    task_storage = current_app.config["task_storage"]
    task_to_show = task_storage.read_by_id(id)
    if task_to_show is None:
        return abort(404, f"Task with id = {id} not found")
    return render_template("task.html", task=task_to_show, task_id=id)


@app.route("/tasks/create", methods=["POST"])
def create_task():
    new_task = Task(
        name=request.form["task_name"],
    )
    if len(new_task.name) < 3:
        return abort(
            400,
            "Task name should contain at least 3 characters",
        )
    if len(new_task.name) > 100:
        return abort(400, "Task name should contain no more than 100 characters")
    task_storage = current_app.config["task_storage"]
    task_storage.create(new_task)
    return redirect("/tasks")


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
    ```
    """
    task_storage = current_app.config["task_storage"]
    task_to_update = task_storage.read_by_id(id)
    if task_to_update is None:
        return abort(404, f"Task with id = {id} not found")
    task_to_update.name = request.form["task_name"]
    if len(task_to_update.name) < 3:
        return abort(
            400,
            "Task name should contain at least 3 characters",
        )
    if len(task_to_update.name) > 100:
        return abort(400, "Task name should contain no more than 100 characters")

    task_storage.update(task_to_update)
    return redirect(f"/tasks")


@app.route("/tasks/<string:id>/delete", methods=["GET"])
def delete_task(id: str):
    task_storage = current_app.config["task_storage"]
    task_to_delete = task_storage.read_by_id(id)
    if task_to_delete is None:
        return abort(404, f"Task with id = {id} not found")
    task_storage.delete(task_to_delete)
    return redirect("/tasks")
