from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_no: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    store_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("store_configs.id"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    payment_status: Mapped[str] = mapped_column(
        String(32),
        default="pending",
        nullable=False,
    )
    amount_cents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    contact_name: Mapped[str] = mapped_column(String(64), nullable=False)
    mobile: Mapped[str] = mapped_column(String(32), nullable=False)
    booking_date: Mapped[str] = mapped_column(String(32), nullable=False)
    pickup_slot: Mapped[str] = mapped_column(String(64), nullable=False)
    remark: Mapped[str] = mapped_column(Text, default="", nullable=False)
    pickup_store_name: Mapped[str] = mapped_column(String(128), nullable=False)
    pickup_store_address: Mapped[str] = mapped_column(String(255), nullable=False)
    pickup_store_phone: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )
    paid_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user = relationship("User", back_populates="orders")
    store = relationship("StoreConfig", back_populates="orders")
    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("orders.id"),
        nullable=False,
        index=True,
    )
    goods_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("goods.id"),
        nullable=False,
        index=True,
    )
    goods_name: Mapped[str] = mapped_column(String(128), nullable=False)
    cover_text: Mapped[str] = mapped_column(String(128), default="", nullable=False)
    cover_color: Mapped[str] = mapped_column(String(32), default="#f3e1cf", nullable=False)
    cover_image: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    spec_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("goods_specs.id"),
        nullable=False,
        index=True,
    )
    spec_name: Mapped[str] = mapped_column(String(128), nullable=False)
    price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    booking_date: Mapped[str] = mapped_column(String(32), nullable=False)
    pickup_slot: Mapped[str] = mapped_column(String(64), nullable=False)

    order = relationship("Order", back_populates="items")
    goods = relationship("Goods")
    spec = relationship("GoodsSpec")
