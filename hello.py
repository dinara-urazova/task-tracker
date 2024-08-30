from flask import Flask, redirect, render_template

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


@app.route("/")
def root():
    return redirect("/tasks")


@app.route("/tasks")
def get_tasks():
    return render_template("tasks.html", tasks=chores)


@app.route("/tasks/<int:id>")
def show_task(id: int):
    return render_template("task.html", task=chores[id - 1])


@app.route("/tasks/<int:id>/edit")
def edit_task_form(id: int):
    return render_template("edit.html", task=chores[id - 1])
