from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from config_reader import env_config
from entity.user import User
from werkzeug.security import check_password_hash
from typing import Optional
from sqlalchemy.exc import NoResultFound


class UserStorageSqlAlchemy:
    def __init__(self):
        connection_str = f"postgresql+pg8000://{env_config.postgresql_username}:{env_config.postgresql_password}@{env_config.postgresql_hostname}:{env_config.postgresql_port}/{env_config.postgresql_database}"
        self.engine = create_engine(connection_str, echo=True)

    def create_user(self, login: str, hashed_password: str) -> None:
        with Session(self.engine) as session:
            new_user = User(login=login, db_hashed_password=hashed_password)
            session.add(new_user)
            session.commit()

    def find_or_verify_user(
        self, username: str, password: Optional[str]
    ) -> Optional[User]:
        with Session(self.engine) as session:
            stmt = select(User).where(User.login == username)
            try:
                user = session.execute(stmt).scalar_one()
            except NoResultFound:
                return None  # пользователь не найден в БД
            if password is None:
                return user  # возвр-т польз-ля (без проверки пароля)
            elif check_password_hash(user.db_hashed_password, password):
                return user  # пароль совпадает
            return None  # пароль не совпадает
