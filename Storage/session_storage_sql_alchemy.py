from sqlalchemy import create_engine, select, delete
from sqlalchemy.orm import Session
from config_reader import env_config
from entity.session import UserSession
from typing import Optional

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
