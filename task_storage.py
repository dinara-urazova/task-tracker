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
