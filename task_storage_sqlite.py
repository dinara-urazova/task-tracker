from task import Task
from datetime import datetime, timezone
from sqlite_singleton import SQLiteSingleton


class TaskStorageSQLite:

    def read_all(self) -> dict:
        cursor = SQLiteSingleton.getConnection().cursor()
        result = cursor.execute("SELECT * FROM tasks")

        tasks = {}
        for row in result:
            tasks[row[0]] = {
                "name": row[1],
                "description": row[2],
                "created_at": row[3],
                "updated_at": row[4],
            }

        return tasks

    def read_by_id(self, id: int) -> Task:
        cursor = SQLiteSingleton.getConnection().cursor()
        result = cursor.execute(f"SELECT * FROM tasks WHERE id = {id}")
        row = result.fetchone()
        if row == None:
            return None
        return Task(row[1], row[2], row[3], row[4])

    def create(self, task: Task) -> int:
        cursor = SQLiteSingleton.getConnection().cursor()
        created_at = updated_at = datetime.now(timezone.utc).isoformat()
        cursor.execute(
            f"""
            INSERT INTO tasks (name, description, created_at, updated_at) VALUES
                ('{task.name}', 
                '{task.description}', 
                '{created_at}', 
                '{updated_at}')
        """
        )
        SQLiteSingleton.getConnection().commit()
        return cursor.lastrowid

    def update(self, task_key: str, updated_task: Task) -> None:
        cursor = SQLiteSingleton.getConnection().cursor()
        updated_at = datetime.now(timezone.utc).isoformat()

        cursor.execute(
            f"""
            UPDATE tasks SET 
                name = '{updated_task.name}',
                description = '{updated_task.description}',
                updated_at = '{updated_at}'
            WHERE id = {task_key}
        """
        )
        SQLiteSingleton.getConnection().commit()

    def delete(self, task_key: str) -> None:
        cursor = SQLiteSingleton.getConnection().cursor()
        cursor.execute(f"DELETE FROM tasks WHERE id = {task_key}")
        SQLiteSingleton.getConnection().commit()
