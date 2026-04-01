from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.db.session import get_db
from app.schemas.admin import (
    PointsProductItem,
    PointsProductListData,
    PointsProductPayload,
    PointsRedemptionItem,
    PointsRedemptionListData,
    PointsRedemptionStatusUpdateRequest,
)
from app.schemas.common import ApiResponse
from app.services.points_service import (
    get_points_product_or_404,
    get_points_redemption_or_404,
    list_points_products,
    list_points_redemptions,
    save_points_product,
    update_redemption_status,
)


router = APIRouter(prefix="/admin/points", tags=["admin-points"])


def serialize_points_product(item) -> PointsProductItem:
    return PointsProductItem(
        id=str(item.id),
        title=item.title,
        subtitle=item.subtitle,
        description=item.description,
        image_url=item.image_url,
        points_cost=item.points_cost,
        stock=item.stock,
        sort=item.sort,
        status=item.status,
        redemption_count=len(item.redemptions),
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def serialize_points_redemption(item) -> PointsRedemptionItem:
    return PointsRedemptionItem(
        id=str(item.id),
        user_id=str(item.user_id),
        nickname=item.user.nickname if item.user else "",
        mobile=item.user.mobile if item.user else "",
        product_id=str(item.product_id),
        product_title=item.product_snapshot_title,
        points_cost=item.points_cost,
        status=item.status,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.get("/products", response_model=ApiResponse[PointsProductListData])
def get_points_products(
    keyword: str = "",
    status: str = "",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> ApiResponse[dict]:
    items, pagination = list_points_products(
        db,
        keyword=keyword,
        status=status,
        page=page,
        page_size=page_size,
    )
    return ApiResponse.success(
        data={
            "list": [serialize_points_product(item) for item in items],
            "pagination": pagination,
        }
    )


@router.get("/products/{product_id}", response_model=ApiResponse[PointsProductItem])
def get_points_product_detail(
    product_id: str,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> ApiResponse[PointsProductItem]:
    return ApiResponse.success(
        data=serialize_points_product(get_points_product_or_404(db, product_id))
    )


@router.post("/products", response_model=ApiResponse[PointsProductItem])
def create_points_product(
    payload: PointsProductPayload,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> ApiResponse[PointsProductItem]:
    item = save_points_product(db, payload)
    db.commit()
    return ApiResponse.success(
        data=serialize_points_product(get_points_product_or_404(db, item.id))
    )


@router.put("/products/{product_id}", response_model=ApiResponse[PointsProductItem])
def update_points_product(
    product_id: str,
    payload: PointsProductPayload,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> ApiResponse[PointsProductItem]:
    item = save_points_product(
        db,
        payload,
        existing=get_points_product_or_404(db, product_id),
    )
    db.commit()
    return ApiResponse.success(
        data=serialize_points_product(get_points_product_or_404(db, item.id))
    )


@router.get("/redemptions", response_model=ApiResponse[PointsRedemptionListData])
def get_points_redemptions(
    keyword: str = "",
    status: str = "",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> ApiResponse[dict]:
    items, pagination = list_points_redemptions(
        db,
        keyword=keyword,
        status=status,
        page=page,
        page_size=page_size,
    )
    return ApiResponse.success(
        data={
            "list": [serialize_points_redemption(item) for item in items],
            "pagination": pagination,
        }
    )


@router.post(
    "/redemptions/{redemption_id}/status",
    response_model=ApiResponse[PointsRedemptionItem],
)
def change_points_redemption_status(
    redemption_id: str,
    payload: PointsRedemptionStatusUpdateRequest,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> ApiResponse[PointsRedemptionItem]:
    item = update_redemption_status(
        db,
        redemption=get_points_redemption_or_404(db, redemption_id),
        status=payload.status,
    )
    db.commit()
    return ApiResponse.success(
        data=serialize_points_redemption(get_points_redemption_or_404(db, item.id))
    )
