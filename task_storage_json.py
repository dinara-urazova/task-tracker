import json
from task import Task


class TaskStorageJson:
    def _read_json(self) -> dict:
        try:
            f = open("tasks.json", "r", encoding="utf-8")
            tasks = json.load(f)
            f.close()
        except FileNotFoundError:
            print("[INFO] tasks file not found, creating a new one")
            tasks = {}
            self._write_json(tasks)
        except json.JSONDecodeError:
            print(
                "[WARNING] tasks file contains invalid JSON content, creating a new one"
            )
            tasks = {}
            self._write_json(tasks)
        return tasks

    def _write_json(self, tasks: dict) -> None:
        with open("tasks.json", "w", encoding="utf-8") as f:
            json.dump(tasks, f, sort_keys=True, indent=2, ensure_ascii=False)

    def read_all(self) -> dict:
        return self._read_json()

    def read_by_id(self, id: int) -> Task:
        tasks = self._read_json()
        if id not in tasks:
            return None
        return Task(
            tasks[id]["name"],
            tasks[id]["description"],
            tasks[id]["created_at"],
            tasks[id]["updated_at"],
        )

    def create(self, task: Task) -> int:
        tasks = self._read_json()
        if len(tasks.keys()) == 0:
            new_task_id = 1
        else:
            task_ids = map(lambda x: int(x), tasks.keys())
            new_task_id = max(task_ids) + 1
        tasks[str(new_task_id)] = {
            "name": task.name,
            "description": task.description,
            "created_at": task.created_at,
            "updated_at": task.created_at,
        }
        self._write_json(tasks)

        return new_task_id

    def update(self, task_key: str, updated_task: Task) -> None:
        tasks = self._read_json()
        tasks[task_key] = {
            "name": updated_task.name,
            "description": updated_task.description,
            "created_at": tasks[task_key]["created_at"],
            "updated_at": updated_task.updated_at,
        }
        self._write_json(tasks)

    def delete(self, task_key: str) -> None:
        tasks = self._read_json()
        del tasks[task_key]
        self._write_json(tasks)
