from flask import (
    abort,
    Flask,
    redirect,
    render_template,
    current_app,
    make_response,
    flash,
    g,
)
from entity.task import Task
import uuid
from http import HTTPStatus
from forms import LoginForm, RegisterForm, TaskForm
from werkzeug.security import generate_password_hash
from typing import cast

from Storage.task_storage_sql_alchemy import TaskStorageSqlAlchemy
from Storage.user_storage_sql_alchemy import UserStorageSqlAlchemy
from Storage.session_storage_sql_alchemy import SessionStorageSqlAlchemy
from Storage.cookie_storage import CookieStorage

from flask_wtf.csrf import CSRFProtect
from config_reader import Settings
from entity.session import UserSession

env_config = Settings()
secret_key = env_config.secret_key

app = Flask(__name__)

app.config["SECRET_KEY"] = secret_key  # Set the secret key
app.config["task_storage"] = TaskStorageSqlAlchemy()
app.config["user_storage"] = UserStorageSqlAlchemy()
app.config["session_storage"] = SessionStorageSqlAlchemy()
app.config["cookie_storage"] = CookieStorage()

# Initialize CSRF protection
csrf = CSRFProtect(app)

COOKIE_NAME = "task_tracker_session"


def find_session() -> UserSession | None:
    session_storage = cast(
        SessionStorageSqlAlchemy, current_app.config["session_storage"]
    )
    cookie_storage = cast(CookieStorage, current_app.config["cookie_storage"])

    session_uuid = cookie_storage.get_cookie_value()
    user_session = session_storage.find_session(session_uuid)
    if user_session:
        g.logged_in = True
        return user_session

    return None


@app.route("/", methods=["GET"])
def root():
    find_session()
    return render_template("index.html")


@app.route("/register", methods=["GET"])
def register_get():
    if find_session():
        return redirect("/")

    return render_template(
        "register.html",
        form=RegisterForm(),
    )


@app.route("/register", methods=["POST"])
def register_post():
    if find_session():
        return redirect("/")

    form = RegisterForm()
    if not form.validate_on_submit():
        return render_template(
            "register.html",
            form=form,
        )

    username = form.username.data
    password = form.password.data

    user_storage = cast(UserStorageSqlAlchemy, current_app.config["user_storage"])

    is_user_already_exists = user_storage.find_or_verify_user(username, password=None)

    if is_user_already_exists:
        flash("You are already registered, try to log in")
        return render_template(
            "register.html",
            form=form,
        )

    hashed_password = generate_password_hash(password)
    user_storage.create_user(username, hashed_password)
    flash("You have successfully registered")
    return redirect("/login")


@app.route("/login", methods=["GET"])
def login_get():
    if find_session():
        return redirect("/")

    return render_template(
        "login.html",
        form=LoginForm(),
    )


@app.route("/login", methods=["POST"])
def login_post():
    if find_session():
        return redirect("/")

    form = LoginForm()

    if not form.validate_on_submit():
        return abort(HTTPStatus.BAD_REQUEST.value)

    if form.csrf_token.errors:
        return abort(HTTPStatus.FORBIDDEN.value)

    username = form.username.data
    password = form.password.data

    user_storage = cast(UserStorageSqlAlchemy, current_app.config["user_storage"])

    user = user_storage.find_or_verify_user(
        username, password
    )  # поиск и проверка пользователя

    if not user:
        flash("Invalid username or password")
        return redirect("/login")

    session_uuid = str(uuid.uuid4())
    session_storage = cast(
        SessionStorageSqlAlchemy, current_app.config["session_storage"]
    )
    session_storage.create_session(session_uuid, user.id)
    r = make_response(redirect("/tasks"))
    r.set_cookie(COOKIE_NAME, session_uuid, path="/", max_age=60 * 60)
    return r


@app.route("/logout", methods=["GET"])
def logout():
    user_session = find_session()
    if not user_session:
        return redirect("/")

    session_storage = cast(
        SessionStorageSqlAlchemy, current_app.config["session_storage"]
    )
    session_storage.delete_session(user_session.session_uuid)  # delete on server

    r = make_response(redirect("/"))
    r.set_cookie(
        COOKIE_NAME, user_session.session_uuid, path="/", max_age=0
    )  # delete in browser
    return r


@app.route("/tasks", methods=["GET"])
def get_tasks():
    user_session = find_session()
    if not user_session:
        return abort(HTTPStatus.UNAUTHORIZED.value)

    task_storage = cast(TaskStorageSqlAlchemy, current_app.config["task_storage"])
    chores = task_storage.read_all(user_session.user_id)
    r = make_response(render_template("tasks.html", tasks=chores, form=TaskForm()))
    r.set_cookie(COOKIE_NAME, user_session.session_uuid, path="/", max_age=60 * 60)
    return r


@app.route("/tasks/create", methods=["POST"])
def create_task():
    user_session = find_session()
    if not user_session:
        return abort(HTTPStatus.UNAUTHORIZED.value)
    form = TaskForm()

    if not form.validate_on_submit():
        return abort(HTTPStatus.BAD_REQUEST.value)

    task_name = form.task_name.data
    task_storage = cast(TaskStorageSqlAlchemy, current_app.config["task_storage"])
    new_task = Task(name=task_name, user_id=user_session.user_id)
    task_storage.create(new_task)
    return redirect("/tasks")


@app.route("/tasks/<int:id>/update", methods=["POST"])
def update_task(id: int):
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
    user_session = find_session()
    if not user_session:
        return abort(HTTPStatus.UNAUTHORIZED.value)

    task_storage = cast(TaskStorageSqlAlchemy, current_app.config["task_storage"])
    task_to_update = task_storage.read_by_id(id, user_session.user_id)
    if task_to_update is None:
        return abort(404, f"Task with id = {id} not found")

    form = TaskForm()
    if not form.validate_on_submit():
        return abort(HTTPStatus.BAD_REQUEST.value)

    task_to_update.name = form.task_name.data

    task_storage.update(task_to_update)
    return redirect("/tasks")


# @app.route("/tasks/<int:id>/update", methods=["GET", "POST"])

# def update_task(id: int):
#     if request.method == "POST":
#         return update_task_post(id)
#     return update_task_get(id)

# def update_task_get(id: int):
#     user_session = find_session()
#     if not user_session:
#         return abort(HTTPStatus.UNAUTHORIZED.value)

#     task_storage = cast(TaskStorageSqlAlchemy, current_app.config["task_storage"])
#     task_to_update = task_storage.read_by_id(id, user_session.user_id)
#     if task_to_update is None:
#         return abort(404, f"Task with id = {id} not found")
#     return redirect("/")


# def update_task_post(id: int):
#     user_session = find_session()
#     if not user_session:
#         return abort(HTTPStatus.UNAUTHORIZED.value)

#     task_storage = cast(TaskStorageSqlAlchemy, current_app.config["task_storage"])
#     task_to_update = task_storage.read_by_id(id, user_session.user_id)
#     if task_to_update is None:
#         return abort(404, f"Task with id = {id} not found")

#     form = TaskForm()
#     if not form.validate_on_submit():
#         return abort(HTTPStatus.BAD_REQUEST.value)

#     task_to_update.name = form.task_name.data
#     task_storage.update(task_to_update)
#     return redirect("/tasks")


@app.route("/tasks/<int:id>/delete", methods=["GET"])
def delete_task(id: int):
    user_session = find_session()
    if not user_session:
        return abort(HTTPStatus.UNAUTHORIZED.value)

    task_storage = cast(TaskStorageSqlAlchemy, current_app.config["task_storage"])
    task_to_delete = task_storage.read_by_id(id, user_session.user_id)
    if task_to_delete is None:
        return abort(404, f"Task with id = {id} not found")
    task_storage.delete(task_to_delete)
    return redirect("/tasks")
