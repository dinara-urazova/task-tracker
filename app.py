from flask import abort, Flask, redirect, render_template, request
from task import Task
from task_storage_sqlite import TaskStorageSQLite
from task_storage_json import TaskStorageJson
from task_storage_postgresql import TaskStoragePostgreSQL
from datetime import datetime, timezone


app = Flask(__name__)
task_storage = TaskStoragePostgreSQL()
# task_storage = TaskStorageSQLite()
# task_storage = TaskStorageJson()


@app.route("/", methods=["GET"])
def root():
    return redirect("/tasks")


@app.route("/tasks", methods=["GET"])
def get_tasks():
    chores = task_storage.read_all()
    return render_template("tasks.html", tasks=chores)


@app.route("/tasks/<string:id>", methods=["GET"])
def show_task(id: str):
    task_to_show = task_storage.read_by_id(id)
    if task_to_show == None:
        return abort(404, f"Task with id = {id} not found")
    return render_template("task.html", task=task_to_show, task_id=id)


@app.route("/tasks/new", methods=["GET"])
def show_new_task_form():
    return render_template("new.html")


@app.route("/tasks/create", methods=["POST"])
def create_task():
    created_at = updated_at = datetime.now(timezone.utc).isoformat()
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
    task_to_edit = task_storage.read_by_id(id)
    if task_to_edit == None:
        return abort(404, f"Task with id = {id} not found")
    return render_template("edit.html", task=task_to_edit, task_id=id)


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
    # здесь id проверять не нужно, так как 56-57 строки не передают invalid id ни в шаблон edit.html, ни далее в эту функцию-обработчик update_task (указана в form action)
    updated_at = datetime.now(timezone.utc).isoformat()
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
    task_to_delete = task_storage.read_by_id(id)
    if task_to_delete == None:
        return abort(404, f"Task with id = {id} not found")
    task_storage.delete(id)
    return redirect("/tasks")
