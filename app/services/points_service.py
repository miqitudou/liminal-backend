from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.core.constants import (
    POINTS_PRODUCT_STATUS_ENABLED,
    POINTS_REDEMPTION_STATUS_CANCELLED,
    POINTS_REDEMPTION_STATUS_FULFILLED,
    POINTS_REDEMPTION_STATUS_PENDING,
    POINTS_TRANSACTION_TYPE_ORDER_REWARD,
    POINTS_TRANSACTION_TYPE_REDEEM_REFUND,
    POINTS_TRANSACTION_TYPE_REDEEM_SPEND,
    POINTS_TRANSACTION_TYPE_WELCOME_BONUS,
)
from app.core.exceptions import AppException
from app.core.id_utils import normalize_int_id
from app.models import Order, PointsProduct, PointsRedemption, PointsTransaction, User
from app.schemas.admin import PointsProductPayload
from app.services.mappers import build_pagination


DEFAULT_POINTS_TIPS = [
    "每消费 1 元可获得 1 积分",
    "新会员首次登录可领取 1280 积分欢迎礼",
    "积分商品兑换后支持到店自提",
]

WELCOME_BONUS_POINTS = 1280


def create_points_transaction(
    db: Session,
    *,
    user: User,
    change_points: int,
    transaction_type: str,
    remark: str,
    order: Order | None = None,
    redemption: PointsRedemption | None = None,
) -> PointsTransaction:
    user.points_balance += change_points
    if user.points_balance < 0:
        raise AppException(code=40911, message="积分余额不足")

    transaction = PointsTransaction(
        user_id=user.id,
        change_points=change_points,
        balance_after=user.points_balance,
        transaction_type=transaction_type,
        remark=remark,
        order_id=order.id if order else None,
        redemption_id=redemption.id if redemption else None,
    )
    db.add(user)
    db.add(transaction)
    db.flush()
    return transaction


def grant_welcome_bonus(db: Session, user: User) -> None:
    create_points_transaction(
        db,
        user=user,
        change_points=WELCOME_BONUS_POINTS,
        transaction_type=POINTS_TRANSACTION_TYPE_WELCOME_BONUS,
        remark="新会员欢迎积分",
    )


def award_order_points(db: Session, order: Order) -> int:
    if order.points_rewarded > 0:
        return order.points_rewarded

    reward_points = max(order.amount_cents // 100, 0)
    if reward_points <= 0:
        return 0

    create_points_transaction(
        db,
        user=order.user,
        change_points=reward_points,
        transaction_type=POINTS_TRANSACTION_TYPE_ORDER_REWARD,
        remark=f"订单 {order.order_no} 支付赠送积分",
        order=order,
    )
    order.points_rewarded = reward_points
    db.add(order)
    db.flush()
    return reward_points


def list_points_products(
    db: Session,
    *,
    keyword: str = "",
    status: str = "",
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[PointsProduct], dict]:
    stmt = select(PointsProduct).options(joinedload(PointsProduct.redemptions))

    if keyword:
        stmt = stmt.where(
            or_(
                PointsProduct.title.like(f"%{keyword}%"),
                PointsProduct.subtitle.like(f"%{keyword}%"),
                PointsProduct.description.like(f"%{keyword}%"),
            )
        )
    if status:
        stmt = stmt.where(PointsProduct.status == status)

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    items = (
        db.scalars(
            stmt.order_by(PointsProduct.sort.asc(), PointsProduct.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        .unique()
        .all()
    )
    return items, build_pagination(page, page_size, total)


def get_points_product_or_404(db: Session, product_id: str | int) -> PointsProduct:
    product = db.scalar(
        select(PointsProduct)
        .options(joinedload(PointsProduct.redemptions))
        .where(PointsProduct.id == normalize_int_id(product_id, "积分商品ID"))
    )
    if not product:
        raise AppException(code=40421, message="积分商品不存在")
    return product


def save_points_product(
    db: Session,
    payload: PointsProductPayload,
    *,
    existing: PointsProduct | None = None,
) -> PointsProduct:
    product = existing or PointsProduct()
    product.title = payload.title
    product.subtitle = payload.subtitle
    product.description = payload.description
    product.image_url = payload.image_url
    product.points_cost = payload.points_cost
    product.stock = payload.stock
    product.sort = payload.sort
    product.status = payload.status
    db.add(product)
    db.flush()
    return product


def list_points_redemptions(
    db: Session,
    *,
    keyword: str = "",
    status: str = "",
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[PointsRedemption], dict]:
    stmt = (
        select(PointsRedemption)
        .options(
            joinedload(PointsRedemption.user),
            joinedload(PointsRedemption.product),
        )
    )

    if keyword:
        stmt = stmt.join(User, User.id == PointsRedemption.user_id).where(
            or_(
                PointsRedemption.product_snapshot_title.like(f"%{keyword}%"),
                User.mobile.like(f"%{keyword}%"),
                User.nickname.like(f"%{keyword}%"),
            )
        )
    if status:
        stmt = stmt.where(PointsRedemption.status == status)

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    items = (
        db.scalars(
            stmt.order_by(PointsRedemption.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        .unique()
        .all()
    )
    return items, build_pagination(page, page_size, total)


def get_points_redemption_or_404(
    db: Session, redemption_id: str | int
) -> PointsRedemption:
    redemption = db.scalar(
        select(PointsRedemption)
        .options(
            joinedload(PointsRedemption.user),
            joinedload(PointsRedemption.product),
            joinedload(PointsRedemption.transactions),
        )
        .where(PointsRedemption.id == normalize_int_id(redemption_id, "兑换记录ID"))
    )
    if not redemption:
        raise AppException(code=40422, message="兑换记录不存在")
    return redemption


def update_redemption_status(
    db: Session,
    *,
    redemption: PointsRedemption,
    status: str,
) -> PointsRedemption:
    if redemption.status == status:
        return redemption

    if status == POINTS_REDEMPTION_STATUS_FULFILLED:
        redemption.status = status
    elif status == POINTS_REDEMPTION_STATUS_CANCELLED:
        if redemption.status == POINTS_REDEMPTION_STATUS_CANCELLED:
            return redemption

        redemption.status = status
        redemption.product.stock += 1
        db.add(redemption.product)
        create_points_transaction(
            db,
            user=redemption.user,
            change_points=redemption.points_cost,
            transaction_type=POINTS_TRANSACTION_TYPE_REDEEM_REFUND,
            remark=f"兑换 {redemption.product_snapshot_title} 已取消，积分已退回",
            redemption=redemption,
        )
    else:
        raise AppException(code=40021, message="不支持的兑换状态")

    db.add(redemption)
    db.flush()
    return redemption


def get_points_mall_data(db: Session, user: User | None) -> dict:
    products = db.scalars(
        select(PointsProduct)
        .where(PointsProduct.status == POINTS_PRODUCT_STATUS_ENABLED)
        .order_by(PointsProduct.sort.asc(), PointsProduct.created_at.desc())
    ).all()

    records: list[PointsRedemption] = []
    points_balance = 0
    if user:
        points_balance = user.points_balance
        records = db.scalars(
            select(PointsRedemption)
            .where(PointsRedemption.user_id == user.id)
            .order_by(PointsRedemption.created_at.desc())
            .limit(10)
        ).all()

    return {
        "pointsBalance": points_balance,
        "tips": DEFAULT_POINTS_TIPS,
        "goods": products,
        "records": records,
    }


def redeem_points_product(
    db: Session,
    *,
    user: User,
    product_id: str | int,
) -> PointsRedemption:
    product = get_points_product_or_404(db, product_id)
    if product.status != POINTS_PRODUCT_STATUS_ENABLED:
        raise AppException(code=40912, message="该积分商品暂不可兑换")
    if product.stock <= 0:
        raise AppException(code=40913, message="该积分商品已兑完")
    if user.points_balance < product.points_cost:
        raise AppException(code=40911, message="积分余额不足")

    product.stock -= 1
    redemption = PointsRedemption(
        user_id=user.id,
        product_id=product.id,
        points_cost=product.points_cost,
        status=POINTS_REDEMPTION_STATUS_PENDING,
        product_snapshot_title=product.title,
        product_snapshot_image=product.image_url,
    )
    db.add(product)
    db.add(redemption)
    db.flush()

    create_points_transaction(
        db,
        user=user,
        change_points=-product.points_cost,
        transaction_type=POINTS_TRANSACTION_TYPE_REDEEM_SPEND,
        remark=f"兑换 {product.title}",
        redemption=redemption,
    )
    return redemption
