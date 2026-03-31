from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.schemas.common import ApiResponse
from app.schemas.miniapp import (
    MiniappCreateOrderRequest,
    MiniappOrderActionResponse,
    MiniappOrderListData,
    MiniappOrdersCountResponse,
)
from app.services.mappers import serialize_order_for_miniapp
from app.services.order_service import (
    cancel_order,
    create_order_from_miniapp,
    get_order_or_404,
    get_user_order_counts,
    list_user_orders,
    mark_order_paid,
)


router = APIRouter(prefix="/orders", tags=["miniapp-orders"])


@router.post("", response_model=ApiResponse[dict])
def create_order(
    payload: MiniappCreateOrderRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> ApiResponse[dict]:
    order = create_order_from_miniapp(db, user=user, payload=payload)
    db.commit()
    return ApiResponse.success(data=serialize_order_for_miniapp(order))


@router.get("", response_model=ApiResponse[MiniappOrderListData])
def get_orders(
    status: str = Query(default="all"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> ApiResponse[dict]:
    orders = list_user_orders(db, user_id=user.id, status=status)
    return ApiResponse.success(
        data={"orders": [serialize_order_for_miniapp(item) for item in orders]}
    )


@router.get("/counts", response_model=ApiResponse[MiniappOrdersCountResponse])
def get_order_counts(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> ApiResponse[dict]:
    return ApiResponse.success(data=get_user_order_counts(db, user.id))


@router.get("/{order_no}", response_model=ApiResponse[dict])
def get_order_detail(
    order_no: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> ApiResponse[dict]:
    order = get_order_or_404(db, order_no)
    if order.user_id != user.id:
        return ApiResponse(code=40301, message="无权限查看该订单", data=None)
    return ApiResponse.success(data=serialize_order_for_miniapp(order))


@router.post("/{order_no}/pay", response_model=ApiResponse[MiniappOrderActionResponse])
def pay_order(
    order_no: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> ApiResponse[dict]:
    order = get_order_or_404(db, order_no)
    if order.user_id != user.id:
        return ApiResponse(code=40301, message="无权限操作该订单", data=None)
    order = mark_order_paid(db, order)
    db.commit()
    return ApiResponse.success(
        data={
            "orderNo": order.order_no,
            "status": order.status,
            "paymentStatus": order.payment_status,
        }
    )


@router.post("/{order_no}/cancel", response_model=ApiResponse[MiniappOrderActionResponse])
def cancel_user_order(
    order_no: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> ApiResponse[dict]:
    order = get_order_or_404(db, order_no)
    if order.user_id != user.id:
        return ApiResponse(code=40301, message="无权限操作该订单", data=None)
    order = cancel_order(db, order)
    db.commit()
    return ApiResponse.success(
        data={
            "orderNo": order.order_no,
            "status": order.status,
            "paymentStatus": order.payment_status,
        }
    )
