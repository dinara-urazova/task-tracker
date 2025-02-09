from sqlalchemy import func, String, Integer, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
import datetime

class Base(DeclarativeBase):
    pass

class Task(Base):
    __tablename__ = "tasks"  # название таблицы в БД (смотри через DBeaver)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str]
    created_at: Mapped[datetime.datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(
        default=func.now(),
        onupdate=func.now(),
    )

class User(Base):
    __tablename__ = "users"  # название таблицы в БД (смотри через DBeaver)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    login: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)

class UserSession(Base):
    __tablename__ = "sessions"  # название таблицы в БД (смотри через DBeaver)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_uuid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id")) 
  
