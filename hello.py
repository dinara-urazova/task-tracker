from flask import Flask, redirect, render_template

app = Flask(__name__, template_folder='templates')

tasks = [
    {
        "name": "Сходить в магазин"
    }
]

@app.route("/")
def root():
    return redirect("/tasks")

@app.route('/tasks')
def get_tasks():
    return render_template('tasks.html', tasks=tasks)
    
