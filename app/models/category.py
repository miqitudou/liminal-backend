from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    category_name: Mapped[str] = mapped_column(String(64), nullable=False)
    category_desc: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    badge_text: Mapped[str] = mapped_column(String(64), default="", nullable=False)
    delivery_mode: Mapped[str] = mapped_column(String(32), nullable=False)
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

    goods = relationship("Goods", back_populates="category")
