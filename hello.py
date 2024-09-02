from flask import Flask, redirect, render_template, request

app = Flask(__name__)

chores = [
    {"id": 1, "name": "Сходить в магазин", "description": "Сходить в 'Байрам'"},
    {
        "id": 2,
        "name": "Съездить на дачу",
        "description": "Взять фонарь, купить корм кошкам, не забыть ноутбук",
    },
    {"id": 3, "name": "Постирать одежду", "description": "Не позднее пятницы 13-го"},
]


@app.route("/", methods=["GET"])
def root():
    return redirect("/tasks")


@app.route("/tasks", methods=["GET"])
def get_tasks():
    return render_template("tasks.html", tasks=chores)


@app.route("/tasks/<int:id>", methods=["GET"])
def show_task(id: int):
    return render_template("task.html", task=chores[id - 1])


@app.route("/tasks/<int:id>/edit", methods=["GET"])
def edit_task_form(id: int):
    return render_template("edit.html", task=chores[id - 1])


@app.route("/tasks/<int:id>/update", methods=["POST"])
def update_task(id: int):
    print(f"id = {id}")

    new_name = request.form["task_name"]
    new_desription = request.form["task_description"]

    chores[id - 1] = {
        "id": id,
        "name": new_name,
        "description": new_desription,
    }

    return redirect(f"/tasks/{id}")
