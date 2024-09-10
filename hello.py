from flask import Flask, redirect, render_template, request

app = Flask(__name__)

chores = {
    2: {
        "name": "Съездить на дачу",
        "description": "Взять фонарь, купить корм кошкам, не забыть ноутбук",
    },
    3: {"name": "Постирать одежду", "description": "Не позднее пятницы 13-го"},
    100: {"name": "Сходить в магазин", "description": "Сходить в 'Байрам'"},
}


@app.route("/", methods=["GET"])
def root():
    return redirect("/tasks")


@app.route("/tasks", methods=["GET"])
def get_tasks():
    return render_template("tasks.html", tasks=chores)


@app.route("/tasks/<int:id>", methods=["GET"])
def show_task(id: int):
    return render_template("task.html", task=chores[id], task_id=id)


@app.route("/tasks/new", methods=["GET"])
def new_task_form():
    return render_template("new.html")


@app.route("/tasks/create", methods=["POST"])
def create_task():
    new_task_id = max(chores.keys()) + 1
    name = request.form["task_name"]
    description = request.form["task_description"]

    chores[new_task_id] = {
        "name": name,
        "description": description,
    }

    return redirect(f"/tasks/{new_task_id}")


@app.route("/tasks/<int:id>/edit", methods=["GET"])
def edit_task_form(id: int):
    return render_template("edit.html", task=chores[id], task_id=id)


@app.route("/tasks/<int:id>/update", methods=["POST"])
def update_task(id: int):
    new_name = request.form["task_name"]
    new_description = request.form["task_description"]

    chores[id] = {
        "name": new_name,
        "description": new_description,
    }

    return redirect(f"/tasks/{id}")


@app.route("/tasks/<int:id>/delete", methods=["GET"])
def delete_task(id: int):
    del chores[id]

    return redirect("/tasks")
