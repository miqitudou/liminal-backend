from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    nickname: Mapped[str] = mapped_column(String(64), nullable=False)
    avatar_url: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    mobile: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    member_since: Mapped[str] = mapped_column(String(32), nullable=False)
    level_text: Mapped[str] = mapped_column(String(64), default="烘焙常客", nullable=False)
    wechat_bound: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    phone_bound: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    profile_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="enabled", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    orders = relationship("Order", back_populates="user")
