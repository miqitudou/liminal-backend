from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.core.constants import (
    ORDER_STATUS_CANCELLED,
    ORDER_STATUS_PAID,
    ORDER_STATUS_PENDING_PAYMENT,
)
from app.core.exceptions import AppException
from app.core.id_utils import normalize_int_id
from app.models import Goods, Order, OrderItem, StoreConfig, User
from app.schemas.miniapp import MiniappCreateOrderRequest
from app.services.mappers import build_pagination
from app.services.points_service import award_order_points


def build_order_no() -> str:
    now = datetime.now()
    return f"{now.strftime('%Y%m%d%H%M%S')}{str(now.microsecond)[:4]}"


def get_order_or_404(db: Session, order_no: str) -> Order:
    order = db.scalar(
        select(Order)
        .options(joinedload(Order.items), joinedload(Order.user))
        .where(Order.order_no == order_no)
    )
    if not order:
        raise AppException(code=40404, message="订单不存在")
    return order


def list_admin_orders(
    db: Session,
    *,
    order_no: str = "",
    status: str = "",
    mobile: str = "",
    booking_date: str = "",
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Order], dict]:
    stmt = select(Order).options(joinedload(Order.items), joinedload(Order.user))
    if order_no:
        stmt = stmt.where(Order.order_no.like(f"%{order_no}%"))
    if status:
        stmt = stmt.where(Order.status == status)
    if mobile:
        stmt = stmt.where(Order.mobile.like(f"%{mobile}%"))
    if booking_date:
        stmt = stmt.where(Order.booking_date == booking_date)
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    items = (
        db.scalars(
            stmt.order_by(Order.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        .unique()
        .all()
    )
    return items, build_pagination(page, page_size, total)


def update_order_status(db: Session, order: Order, status: str) -> Order:
    previous_status = order.status
    order.status = status
    if status == ORDER_STATUS_PAID:
        order.payment_status = "paid"
        if not order.paid_at:
            order.paid_at = datetime.now()
        if previous_status != ORDER_STATUS_PAID:
            award_order_points(db, order)
    db.add(order)
    db.flush()
    return get_order_or_404(db, order.order_no)


def create_order_from_miniapp(
    db: Session,
    *,
    user: User,
    payload: MiniappCreateOrderRequest,
) -> Order:
    if not payload.items:
        raise AppException(code=40001, message="订单商品不能为空")

    store = db.scalar(select(StoreConfig).order_by(StoreConfig.id.asc()).limit(1))
    if not store:
        raise AppException(code=50001, message="门店配置不存在")

    order = Order(
        order_no=build_order_no(),
        user_id=user.id,
        store_id=store.id,
        status=payload.status or ORDER_STATUS_PENDING_PAYMENT,
        payment_status="pending",
        amount_cents=0,
        contact_name=payload.contactName,
        mobile=payload.mobile,
        booking_date=payload.bookingDate,
        pickup_slot=payload.pickupSlot,
        remark=payload.remark,
        pickup_store_name=store.store_name,
        pickup_store_address=store.address,
        pickup_store_phone=store.phone,
    )
    db.add(order)
    db.flush()

    total_cents = 0
    for item in payload.items:
        goods_id = normalize_int_id(item.goodsId, "商品ID")
        spec_id = normalize_int_id(item.specId, "规格ID")
        goods = db.scalar(
            select(Goods)
            .options(joinedload(Goods.specs))
            .where(Goods.id == goods_id)
        )
        if not goods:
            raise AppException(code=40401, message="商品不存在")

        spec = next((spec for spec in goods.specs if spec.id == spec_id), None)
        if not spec:
            raise AppException(code=40403, message="商品规格不存在")

        line_amount = spec.price_cents * item.quantity
        total_cents += line_amount
        db.add(
            OrderItem(
                order_id=order.id,
                goods_id=goods.id,
                goods_name=goods.goods_name,
                cover_text=goods.cover_text,
                cover_color=goods.cover_color,
                cover_image=goods.cover_image,
                spec_id=spec.id,
                spec_name=spec.spec_name,
                price_cents=spec.price_cents,
                quantity=item.quantity,
                booking_date=item.bookingDate,
                pickup_slot=item.pickupSlot,
            )
        )

    order.amount_cents = total_cents
    db.add(order)
    db.flush()
    return get_order_or_404(db, order.order_no)


def list_user_orders(
    db: Session,
    *,
    user_id: str | int,
    status: str = "",
) -> list[Order]:
    normalized_user_id = normalize_int_id(user_id, "用户ID")
    stmt = (
        select(Order)
        .options(joinedload(Order.items))
        .where(Order.user_id == normalized_user_id)
        .order_by(Order.created_at.desc())
    )
    if status and status != "all":
        stmt = stmt.where(Order.status == status)
    return db.scalars(stmt).unique().all()


def get_user_order_counts(db: Session, user_id: str | int) -> dict:
    orders = list_user_orders(db, user_id=user_id)
    result = {
        "all": len(orders),
        "pending_payment": 0,
        "paid": 0,
        "baking": 0,
        "ready_pickup": 0,
        "finished": 0,
        "cancelled": 0,
    }
    for order in orders:
        if order.status in result:
            result[order.status] += 1
    return result


def mark_order_paid(db: Session, order: Order) -> Order:
    if order.status == ORDER_STATUS_CANCELLED:
        raise AppException(code=40905, message="已取消订单不能支付")
    return update_order_status(db, order, ORDER_STATUS_PAID)


def cancel_order(db: Session, order: Order) -> Order:
    if order.status != ORDER_STATUS_PENDING_PAYMENT:
        raise AppException(code=40905, message="当前订单状态不允许取消")
    return update_order_status(db, order, ORDER_STATUS_CANCELLED)
