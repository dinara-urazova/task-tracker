from sqlalchemy import String, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from entity.base import Base


class User(Base):
    __tablename__ = "users"  # название таблицы в БД (смотри через DBeaver)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    login: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)
    db_hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
