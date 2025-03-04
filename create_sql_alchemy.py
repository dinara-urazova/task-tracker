from sqlalchemy import create_engine

from config_reader import env_config
from entity.base import Base

from entity.task import Task # noqa: F401
from entity.user import User # noqa: F401
from entity.session import UserSession # noqa: F401

connection_str = f"postgresql+pg8000://{env_config.postgresql_username}:{env_config.postgresql_password}@{env_config.postgresql_hostname}:{env_config.postgresql_port}/{env_config.postgresql_database}"
engine = create_engine(connection_str, echo=True)
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
