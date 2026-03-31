from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import AppException
from app.models import Banner, Category, Goods, GoodsBookingRule, GoodsSpec
from app.schemas.admin import BannerPayload, CategoryPayload, GoodsPayload
from app.services.mappers import build_pagination
from app.services.seed import generate_id


def list_categories(
    db: Session,
    *,
    keyword: str = "",
    status: str = "",
    delivery_mode: str = "",
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Category], dict]:
    stmt = select(Category)

    if keyword:
        stmt = stmt.where(
            or_(
                Category.category_name.like(f"%{keyword}%"),
                Category.category_desc.like(f"%{keyword}%"),
            )
        )
    if status:
        stmt = stmt.where(Category.status == status)
    if delivery_mode:
        stmt = stmt.where(Category.delivery_mode == delivery_mode)

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    items = (
        db.scalars(
            stmt.order_by(Category.sort.asc(), Category.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        .unique()
        .all()
    )
    return items, build_pagination(page, page_size, total)


def save_category(
    db: Session,
    payload: CategoryPayload,
    *,
    existing: Category | None = None,
) -> Category:
    category = existing or Category(id=payload.category_id or generate_id("cat"))
    category.category_name = payload.category_name
    category.category_desc = payload.category_desc
    category.badge_text = payload.badge_text
    category.delivery_mode = payload.delivery_mode
    category.sort = payload.sort
    category.status = payload.status
    db.add(category)
    db.flush()
    return category


def delete_category(db: Session, category: Category) -> None:
    if category.goods:
        raise AppException(code=40901, message="该分类下仍有关联商品，不能删除")
    db.delete(category)


def list_goods(
    db: Session,
    *,
    keyword: str = "",
    category_id: str = "",
    status: str = "",
    is_recommend: bool | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Goods], dict]:
    stmt = select(Goods).options(joinedload(Goods.category), joinedload(Goods.specs))

    if keyword:
        stmt = stmt.where(
            or_(
                Goods.goods_name.like(f"%{keyword}%"),
                Goods.goods_desc.like(f"%{keyword}%"),
            )
        )
    if category_id:
        stmt = stmt.where(Goods.category_id == category_id)
    if status:
        stmt = stmt.where(Goods.status == status)
    if is_recommend is not None:
        stmt = stmt.where(Goods.is_recommend == is_recommend)

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    items = (
        db.scalars(
            stmt.order_by(Goods.sort.asc(), Goods.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        .unique()
        .all()
    )
    return items, build_pagination(page, page_size, total)


def get_goods_or_404(db: Session, goods_id: str) -> Goods:
    goods = db.scalar(
        select(Goods)
        .options(
            joinedload(Goods.category),
            joinedload(Goods.specs),
            joinedload(Goods.booking_rule),
        )
        .where(Goods.id == goods_id)
    )
    if not goods:
        raise AppException(code=40401, message="商品不存在")
    return goods


def save_goods(
    db: Session,
    payload: GoodsPayload,
    *,
    existing: Goods | None = None,
) -> Goods:
    category = db.get(Category, payload.category_id)
    if not category:
        raise AppException(code=40402, message="分类不存在")

    goods = existing or Goods(id=payload.goods_id or generate_id("goods"))
    goods.category_id = payload.category_id
    goods.goods_name = payload.goods_name
    goods.goods_desc = payload.goods_desc
    goods.cover_text = payload.cover_text
    goods.cover_color = payload.cover_color
    goods.cover_image = payload.cover_image
    goods.price_cents = payload.price_cents
    goods.sales_count = payload.sales_count
    goods.status = payload.status
    goods.is_recommend = payload.is_recommend
    goods.sort = payload.sort
    goods.tags = payload.tags
    goods.detail_tips = payload.detail_tips
    db.add(goods)
    db.flush()

    for spec in list(goods.specs):
        db.delete(spec)
    if goods.booking_rule:
        db.delete(goods.booking_rule)
    db.flush()

    for item in payload.specs:
        db.add(
            GoodsSpec(
                id=item.spec_id or generate_id("spec"),
                goods_id=goods.id,
                spec_name=item.spec_name,
                price_cents=item.price_cents,
                stock=item.stock,
                min_advance_hours=item.min_advance_hours,
                sort=item.sort,
                status=item.status,
            )
        )

    db.add(
        GoodsBookingRule(
            goods_id=goods.id,
            min_advance_hours=payload.booking_rule.min_advance_hours,
            pickup_slots=payload.booking_rule.pickup_slots,
        )
    )
    db.flush()
    return get_goods_or_404(db, goods.id)


def list_banners(
    db: Session,
    *,
    status: str = "",
    keyword: str = "",
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Banner], dict]:
    stmt = select(Banner)
    if status:
        stmt = stmt.where(Banner.status == status)
    if keyword:
        stmt = stmt.where(
            or_(
                Banner.title.like(f"%{keyword}%"),
                Banner.subtitle.like(f"%{keyword}%"),
            )
        )
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    items = db.scalars(
        stmt.order_by(Banner.sort.asc(), Banner.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return items, build_pagination(page, page_size, total)


def save_banner(
    db: Session,
    payload: BannerPayload,
    *,
    existing: Banner | None = None,
) -> Banner:
    banner = existing or Banner(id=payload.banner_id or generate_id("banner"))
    banner.title = payload.title
    banner.subtitle = payload.subtitle
    banner.image_url = payload.image_url
    banner.action_type = payload.action_type
    banner.action_value = payload.action_value
    banner.action_text = payload.action_text
    banner.sort = payload.sort
    banner.status = payload.status
    db.add(banner)
    db.flush()
    return banner
