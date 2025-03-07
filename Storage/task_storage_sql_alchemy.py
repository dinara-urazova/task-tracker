from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from config_reader import env_config
from entity.task import Task
from typing import List, Optional


class TaskStorageSqlAlchemy:
    def __init__(self):
        connection_str = f"postgresql+pg8000://{env_config.postgresql_username}:{env_config.postgresql_password}@{env_config.postgresql_hostname}:{env_config.postgresql_port}/{env_config.postgresql_database}"
        self.engine = create_engine(connection_str, echo=True)

    def read_all(self, user_id: int) -> List[Task]:
        with Session(self.engine) as session:
            stmt = select(Task).where(Task.user_id == user_id).order_by(Task.id)
            return session.scalars(stmt).all()

    def read_by_id(self, task_id: int, user_id: int) -> Optional[Task]:
        with Session(self.engine) as session:
            stmt = (
                select(Task)
                .where(Task.user_id == user_id)
                .where(Task.id == task_id)
            )
            return session.execute(stmt).scalar_one_or_none()

    def create(self, task: Task) -> int:
        with Session(self.engine) as session:
            session.add(task)
            session.commit()
            return task.id

    def update(self, task: Task) -> None:
        with Session(self.engine) as session:
            session.add(task)
            session.commit()

    def delete(self, task: Task) -> None:
        with Session(self.engine) as session:
            session.delete(task)
            session.commit()
