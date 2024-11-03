from task import Task
from datetime import datetime, timezone
from postgresql_singleton import PostgreSQLSingleton


class TaskStoragePostgreSQL:

    def read_all(self) -> dict:
        result = PostgreSQLSingleton.getConnection().run("SELECT * FROM tasks")

        tasks = {}
        for row in result:
            tasks[row[0]] = {
                "name": row[1],
                "description": row[2],
                "created_at": row[3],
                "updated_at": row[4],
            }

        return tasks

    def read_by_id(self, id: int) -> Task | None:
        results = PostgreSQLSingleton.getConnection().run(
            f"SELECT * FROM tasks WHERE id = {id}"
        )
        if len(results) == 0:
            return None
        row = results[0]
        return Task(row[1], row[2], row[3], row[4])

    def create(self, task: Task) -> int:
        results = PostgreSQLSingleton.getConnection().run(
            f"""
            INSERT INTO tasks (name, description, created_at, updated_at) VALUES
                ('{task.name}', 
                '{task.description}', 
                '{task.created_at}', 
                '{task.updated_at}') RETURNING id
        """
        )
        row = results[0]
        return row[0]

    def update(self, task_key: str, updated_task: Task) -> None:
        updated_at = datetime.now(timezone.utc).isoformat()
        PostgreSQLSingleton.getConnection().run(
            f"""
            UPDATE tasks SET 
                name = '{updated_task.name}',
                description = '{updated_task.description}',
                updated_at = '{updated_at}'
            WHERE id = {task_key}
        """
        )

    def delete(self, task_key: str) -> None:
        PostgreSQLSingleton.getConnection().run(
            f"DELETE FROM tasks WHERE id = {task_key}"
        )
