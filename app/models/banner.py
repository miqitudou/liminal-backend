from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Banner(Base):
    __tablename__ = "banners"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    subtitle: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    image_url: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    action_type: Mapped[str] = mapped_column(String(32), default="none", nullable=False)
    action_value: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    action_text: Mapped[str] = mapped_column(String(64), default="", nullable=False)
    sort: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
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
