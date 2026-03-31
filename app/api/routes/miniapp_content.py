from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.id_utils import normalize_int_id
from app.db.session import get_db
from app.models import Banner, Category, Goods, StoreConfig
from app.schemas.common import ApiResponse
from app.schemas.miniapp import MiniappGoodsListData, MiniappHomeData
from app.services.mappers import (
    serialize_banner_for_miniapp,
    serialize_category_for_miniapp,
    serialize_goods_for_miniapp,
    serialize_store_for_miniapp,
)


router = APIRouter(tags=["miniapp-content"])


@router.get("/home/index", response_model=ApiResponse[MiniappHomeData])
def get_home_index(
    delivery_mode: str = Query(default="local"),
    db: Session = Depends(get_db),
) -> ApiResponse[dict]:
    categories = db.scalars(
        select(Category)
        .where(Category.status == "enabled", Category.delivery_mode == delivery_mode)
        .order_by(Category.sort.asc())
    ).all()
    goods = db.scalars(
        select(Goods)
        .options(joinedload(Goods.specs), joinedload(Goods.booking_rule))
        .join(Category, Category.id == Goods.category_id)
        .where(Category.delivery_mode == delivery_mode, Goods.status == "on")
        .order_by(Goods.sort.asc())
    ).unique().all()
    banners = db.scalars(
        select(Banner).where(Banner.status == "enabled").order_by(Banner.sort.asc())
    ).all()
    store = db.scalar(select(StoreConfig).order_by(StoreConfig.id.asc()).limit(1))

    return ApiResponse.success(
        data={
            "banners": [serialize_banner_for_miniapp(item) for item in banners],
            "categories": [serialize_category_for_miniapp(item) for item in categories],
            "recommends": [
                serialize_goods_for_miniapp(item) for item in goods if item.is_recommend
            ][:4],
            "goods": [serialize_goods_for_miniapp(item) for item in goods][:6],
            "storeInfo": serialize_store_for_miniapp(store) if store else {},
        }
    )


@router.get("/categories", response_model=ApiResponse[list[dict]])
def get_categories(
    delivery_mode: str = "",
    db: Session = Depends(get_db),
) -> ApiResponse[list[dict]]:
    stmt = select(Category).where(Category.status == "enabled").order_by(Category.sort.asc())
    if delivery_mode:
        stmt = stmt.where(Category.delivery_mode == delivery_mode)
    categories = db.scalars(stmt).all()
    return ApiResponse.success(
        data=[serialize_category_for_miniapp(item) for item in categories]
    )


@router.get("/goods", response_model=ApiResponse[MiniappGoodsListData])
def get_goods_list(
    categoryId: str = "",
    keyword: str = "",
    db: Session = Depends(get_db),
) -> ApiResponse[dict]:
    stmt = (
        select(Goods)
        .options(joinedload(Goods.specs), joinedload(Goods.booking_rule))
        .where(Goods.status == "on")
        .order_by(Goods.sort.asc())
    )
    if categoryId:
        stmt = stmt.where(Goods.category_id == normalize_int_id(categoryId, "分类ID"))
    if keyword:
        stmt = stmt.where(Goods.goods_name.like(f"%{keyword}%"))
    goods = db.scalars(stmt).unique().all()
    return ApiResponse.success(
        data={"list": [serialize_goods_for_miniapp(item) for item in goods]}
    )


@router.get("/goods/{goods_id}", response_model=ApiResponse[dict])
def get_goods_detail(goods_id: str, db: Session = Depends(get_db)) -> ApiResponse[dict]:
    goods = db.scalar(
        select(Goods)
        .options(joinedload(Goods.specs), joinedload(Goods.booking_rule))
        .where(Goods.id == normalize_int_id(goods_id, "商品ID"), Goods.status == "on")
    )
    if not goods:
        return ApiResponse(code=40401, message="商品不存在", data=None)
    return ApiResponse.success(data=serialize_goods_for_miniapp(goods, detail=True))
