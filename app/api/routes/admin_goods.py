from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.db.session import get_db
from app.models import Goods
from app.schemas.admin import (
    GoodsBookingRuleItem,
    GoodsItem,
    GoodsListData,
    GoodsListItem,
    GoodsPayload,
    GoodsSpecItem,
)
from app.schemas.common import ApiResponse
from app.services.catalog_service import get_goods_or_404, list_goods, save_goods


router = APIRouter(prefix="/admin/goods", tags=["admin-goods"])


def serialize_goods_detail(goods: Goods) -> GoodsItem:
    return GoodsItem(
        goods_id=str(goods.id),
        category_id=str(goods.category_id),
        category_name=goods.category.category_name,
        goods_name=goods.goods_name,
        goods_desc=goods.goods_desc,
        cover_text=goods.cover_text,
        cover_color=goods.cover_color,
        cover_image=goods.cover_image,
        price_cents=goods.price_cents,
        sales_count=goods.sales_count,
        status=goods.status,
        is_recommend=goods.is_recommend,
        sort=goods.sort,
        tags=goods.tags or [],
        detail_tips=goods.detail_tips or [],
        specs=[
            GoodsSpecItem(
                spec_id=str(spec.id),
                spec_name=spec.spec_name,
                price_cents=spec.price_cents,
                stock=spec.stock,
                min_advance_hours=spec.min_advance_hours,
                sort=spec.sort,
                status=spec.status,
            )
            for spec in goods.specs
            if spec.status == "enabled"
        ],
        booking_rule=GoodsBookingRuleItem(
            min_advance_hours=goods.booking_rule.min_advance_hours
            if goods.booking_rule
            else 0,
            pickup_slots=goods.booking_rule.pickup_slots if goods.booking_rule else [],
        ),
        created_at=goods.created_at,
        updated_at=goods.updated_at,
    )


@router.get("", response_model=ApiResponse[GoodsListData])
def get_goods_list(
    keyword: str = "",
    category_id: str = "",
    status: str = "",
    is_recommend: bool | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> ApiResponse[dict]:
    items, pagination = list_goods(
        db,
        keyword=keyword,
        category_id=category_id,
        status=status,
        is_recommend=is_recommend,
        page=page,
        page_size=page_size,
    )

    result = [
        GoodsListItem(
            goods_id=str(item.id),
            category_id=str(item.category_id),
            category_name=item.category.category_name,
            goods_name=item.goods_name,
            cover_image=item.cover_image,
            price_cents=item.price_cents,
            sales_count=item.sales_count,
            status=item.status,
            is_recommend=item.is_recommend,
            spec_count=len([spec for spec in item.specs if spec.status == "enabled"]),
            updated_at=item.updated_at,
        )
        for item in items
    ]
    return ApiResponse.success(data={"list": result, "pagination": pagination})


@router.get("/{goods_id}", response_model=ApiResponse[GoodsItem])
def get_goods_detail(
    goods_id: str,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> ApiResponse[GoodsItem]:
    return ApiResponse.success(data=serialize_goods_detail(get_goods_or_404(db, goods_id)))


@router.post("", response_model=ApiResponse[GoodsItem])
def create_goods(
    payload: GoodsPayload,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> ApiResponse[GoodsItem]:
    goods = save_goods(db, payload)
    db.commit()
    return ApiResponse.success(data=serialize_goods_detail(get_goods_or_404(db, goods.id)))


@router.put("/{goods_id}", response_model=ApiResponse[GoodsItem])
def update_goods(
    goods_id: str,
    payload: GoodsPayload,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> ApiResponse[GoodsItem]:
    goods = get_goods_or_404(db, goods_id)
    goods = save_goods(db, payload, existing=goods)
    db.commit()
    return ApiResponse.success(data=serialize_goods_detail(get_goods_or_404(db, goods.id)))
