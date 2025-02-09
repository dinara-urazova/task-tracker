from sqlalchemy import create_engine, select, delete
from sqlalchemy.orm import Session
from config_reader import env_config
from entity.table_models import Task, User, UserSession
from werkzeug.security import check_password_hash
from typing import List, Optional
from sqlalchemy.exc import NoResultFound


class TaskStorageSqlAlchemy:
    def __init__(self):
        connection_str = f"postgresql+pg8000://{env_config.postgresql_username}:{env_config.postgresql_password}@{env_config.postgresql_hostname}:{env_config.postgresql_port}/{env_config.postgresql_database}"
        self.engine = create_engine(connection_str, echo=True)

    def read_all(self) -> List[Task]:
        with Session(self.engine) as session:
            stmt = select(Task).order_by(Task.id)
            return session.scalars(stmt).all()

    def read_by_id(self, id: int) -> Optional[Task]:
        with Session(self.engine) as session:
            return session.get(Task, id)

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


class UserStorageSqlAlchemy:
    def __init__(self):
        connection_str = f"postgresql+pg8000://{env_config.postgresql_username}:{env_config.postgresql_password}@{env_config.postgresql_hostname}:{env_config.postgresql_port}/{env_config.postgresql_database}"
        self.engine = create_engine(connection_str, echo=True)


    def create_user(self, login: str, hashed_password: str) -> None:
        with Session(self.engine) as session:
            new_user = User(login=login, password=hashed_password)
            session.add(new_user)
            session.commit()


    def find_or_verify_user(self, username: str, password: Optional[str]) -> Optional[User]:
            with Session(self.engine) as session:
                stmt = select(User).where(User.login == username)
                try:
                    user = session.execute(stmt).scalar_one()
                except NoResultFound:
                    return None # пользователь не найден в БД
                if password is None:
                    return user # возвр польз-ля (без проверки пароля)
                if check_password_hash(user.password, password):
                        return user # пароль совпадает
                return None # пароль не совпадает


class SessionStorageSqlAlchemy:
    def __init__(self):
        connection_str = f"postgresql+pg8000://{env_config.postgresql_username}:{env_config.postgresql_password}@{env_config.postgresql_hostname}:{env_config.postgresql_port}/{env_config.postgresql_database}"
        self.engine = create_engine(connection_str, echo=True)

    def create_session(self, session_uuid: str, user_id: int) -> None:  # when logging in
        with Session(self.engine) as session:
            user_session = UserSession(session_uuid=session_uuid, user_id=user_id)
            session.add(user_session)
            session.commit()
     
    def find_session(self, session_uuid: str) -> Optional[UserSession]:
        with Session(self.engine) as session:
            stmt = select(UserSession).where(UserSession.session_uuid == session_uuid)
            result = session.execute(stmt).scalar_one_or_none()
            return result

    def delete_session(self, session_uuid: str) -> None:
        with Session(self.engine) as session:
            stmt = select(UserSession).where(UserSession.session_uuid == session_uuid)
            session_to_delete = session.execute(stmt).scalar_one_or_none()
            if session_to_delete:
                session.delete(session_to_delete)
                session.commit()
