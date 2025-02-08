from flask import (
    abort,
    Flask,
    redirect,
    render_template,
    request,
    current_app,
    make_response,
    flash,
)
from entity.table_models import Task, User, UserSession
import uuid
from http import HTTPStatus
from forms import LoginForm, RegisterForm
from werkzeug.security import generate_password_hash
from storage_sql_alchemy import (
    TaskStorageSqlAlchemy,
    UserStorageSqlAlchemy,
    SessionStorageSqlAlchemy,
)


app = Flask(__name__)
app.config["task_storage"] = TaskStorageSqlAlchemy()
app.config["user_storage"] = UserStorageSqlAlchemy()
app.config["session_storage"] = SessionStorageSqlAlchemy()

COOKIE_NAME = "session"


@app.route("/", methods=["GET"])
def root():
    session_storage = current_app.config["session_storage"]
    session_uuid = request.cookies.get(COOKIE_NAME)
    if session_storage.find_session(session_uuid):
        return redirect("/tasks")
    return render_template("base.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    session_storage = current_app.config["session_storage"]
    session_uuid = request.cookies.get(COOKIE_NAME)
    if session_storage.find_session(session_uuid):
        return redirect("/tasks")

    form = RegisterForm()
    user_storage = current_app.config["user_storage"]

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        if user_storage.find_or_verify_user(username, password=None):  # проверить, существует ли пользователь (без проверки пароля)
            flash("You are already registered, try to log in")

        else:  # пользователь не найден, нужно создать нового
            hashed_password = generate_password_hash(password)
            user_storage.create_user(username, hashed_password)
            flash("You have successfully registered")
            return redirect("/login")

    return render_template("register.html", title="Register", form=form)  # GET запрос

@app.route("/login", methods=["POST", "GET"])
def login():
    session_storage = current_app.config["session_storage"]
    user_storage = current_app.config["user_storage"]

    session_uuid = request.cookies.get(COOKIE_NAME)
    if session_storage.find_session(session_uuid):
        return redirect("/tasks")

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user_data = user_storage.find_or_verify_user(
            username, password
        )  # поиск и проверка пользователя
        if user_data:
            session_uuid = str(uuid.uuid4())
            session_storage.create_session(session_uuid, user_data.id)
            r = make_response(redirect("/tasks"))
            r.set_cookie(COOKIE_NAME, session_uuid, path="/", max_age=60 * 60)
            return r

        flash("Invalid username or password")

    elif form.csrf_token.errors:
        abort(HTTPStatus.FORBIDDEN.value)

    return render_template("login.html", title="Sign In", form=form)


@app.route("/logout", methods=["GET"])
def logout():
    session_storage = current_app.config["session_storage"]
    session_uuid = request.cookies.get(COOKIE_NAME)
    if session_storage.find_session(session_uuid):
        session_storage.delete_session(session_uuid)  # delete on server

        r = make_response(redirect("/"))
        r.set_cookie(COOKIE_NAME, session_uuid, path="/", max_age=0)  # delete in browser
        return r
    return redirect("/")

@app.route("/tasks", methods=["GET"])
def get_tasks():
    session_storage = current_app.config["session_storage"]
    session_uuid = request.cookies.get(COOKIE_NAME)
    task_storage = current_app.config["task_storage"]
    if session_storage.find_session(session_uuid):
        chores = task_storage.read_all()
        r = make_response(render_template("tasks.html", tasks=chores))
        r.set_cookie(COOKIE_NAME, session_uuid, path="/", max_age=60 * 60)
        return r
    return abort(HTTPStatus.UNAUTHORIZED.value)


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
    return redirect("/tasks")


@app.route("/tasks/<string:id>/delete", methods=["GET"])
def delete_task(id: str):
    task_storage = current_app.config["task_storage"]
    task_to_delete = task_storage.read_by_id(id)
    if task_to_delete is None:
        return abort(404, f"Task with id = {id} not found")
    task_storage.delete(task_to_delete)
    return redirect("/tasks")
