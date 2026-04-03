from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import AppException
from app.core.id_utils import normalize_int_id
from app.models import Banner, Category, Goods, GoodsBookingRule, GoodsSpec
from app.schemas.admin import BannerPayload, CategoryPayload, GoodsPayload
from app.services.mappers import build_pagination


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
    category = existing or Category()
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
        stmt = stmt.where(Goods.category_id == normalize_int_id(category_id, "分类ID"))
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


def get_goods_or_404(db: Session, goods_id: str | int) -> Goods:
    normalized_goods_id = normalize_int_id(goods_id, "商品ID")
    goods = db.scalar(
        select(Goods)
        .options(
            joinedload(Goods.category),
            joinedload(Goods.specs),
            joinedload(Goods.booking_rule),
        )
        .where(Goods.id == normalized_goods_id)
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
    category_id = normalize_int_id(payload.category_id, "分类ID")
    category = db.get(Category, category_id)
    if not category:
        raise AppException(code=40402, message="分类不存在")

    goods = existing or Goods()
    goods.category_id = category_id
    goods.goods_name = payload.goods_name
    goods.goods_desc = payload.goods_desc
    goods.feature_text = payload.feature_text
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

    existing_specs = {str(spec.id): spec for spec in goods.specs}
    retained_spec_ids: set[int] = set()

    for item in payload.specs:
        spec: GoodsSpec | None = None
        if item.spec_id:
            spec = existing_specs.get(str(item.spec_id))
        if not spec:
            spec = GoodsSpec(goods_id=goods.id)

        spec.goods_id = goods.id
        spec.spec_name = item.spec_name
        spec.price_cents = item.price_cents
        spec.stock = item.stock
        spec.min_advance_hours = item.min_advance_hours
        spec.sort = item.sort
        spec.status = item.status
        db.add(spec)
        db.flush()
        retained_spec_ids.add(spec.id)

    for spec in goods.specs:
        if spec.id not in retained_spec_ids:
            spec.status = "disabled"
            db.add(spec)

    booking_rule = goods.booking_rule or GoodsBookingRule(goods_id=goods.id)
    booking_rule.goods_id = goods.id
    booking_rule.min_advance_hours = payload.booking_rule.min_advance_hours
    booking_rule.pickup_slots = payload.booking_rule.pickup_slots
    db.add(booking_rule)
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
    banner = existing or Banner()
    banner.title = payload.title
    banner.subtitle = payload.subtitle
    banner.image_url = payload.image_url
    banner.action_type = payload.action_type
    banner.action_value = str(payload.action_value or "")
    banner.action_text = payload.action_text
    banner.sort = payload.sort
    banner.status = payload.status
    db.add(banner)
    db.flush()
    return banner
