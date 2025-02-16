from sqlalchemy import func, String, Integer, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import datetime
from entity.base import Base


class UserSession(Base):
    __tablename__ = "sessions"  # название таблицы в БД (смотри через DBeaver)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_uuid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
