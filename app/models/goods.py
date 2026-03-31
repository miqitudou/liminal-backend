from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Goods(Base):
    __tablename__ = "goods"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    category_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("categories.id"),
        nullable=False,
    )
    goods_name: Mapped[str] = mapped_column(String(128), nullable=False)
    goods_desc: Mapped[str] = mapped_column(Text, default="", nullable=False)
    cover_text: Mapped[str] = mapped_column(String(128), default="", nullable=False)
    cover_color: Mapped[str] = mapped_column(String(32), default="#f3e1cf", nullable=False)
    cover_image: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    price_cents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sales_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="on", nullable=False)
    is_recommend: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sort: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    detail_tips: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
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

    category = relationship("Category", back_populates="goods")
    specs = relationship(
        "GoodsSpec",
        back_populates="goods",
        cascade="all, delete-orphan",
        order_by="GoodsSpec.sort",
    )
    booking_rule = relationship(
        "GoodsBookingRule",
        back_populates="goods",
        uselist=False,
        cascade="all, delete-orphan",
    )


class GoodsSpec(Base):
    __tablename__ = "goods_specs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    goods_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("goods.id"),
        nullable=False,
    )
    spec_name: Mapped[str] = mapped_column(String(128), nullable=False)
    price_cents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    min_advance_hours: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sort: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="enabled", nullable=False)

    goods = relationship("Goods", back_populates="specs")


class GoodsBookingRule(Base):
    __tablename__ = "goods_booking_rules"

    goods_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("goods.id"),
        primary_key=True,
    )
    min_advance_hours: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    pickup_slots: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

    goods = relationship("Goods", back_populates="booking_rule")
