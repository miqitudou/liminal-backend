from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.db.session import get_db
from app.schemas.admin import OrderData, OrderItemData, OrderListData, OrderListItem, OrderStatusUpdateRequest
from app.schemas.common import ApiResponse
from app.services.order_service import get_order_or_404, list_admin_orders, update_order_status


router = APIRouter(prefix="/admin/orders", tags=["admin-orders"])


def serialize_order_detail(order) -> OrderData:
    return OrderData(
        order_no=order.order_no,
        status=order.status,
        payment_status=order.payment_status,
        amount_cents=order.amount_cents,
        contact_name=order.contact_name,
        mobile=order.mobile,
        booking_date=order.booking_date,
        pickup_slot=order.pickup_slot,
        remark=order.remark,
        pickup_store_name=order.pickup_store_name,
        pickup_store_address=order.pickup_store_address,
        pickup_store_phone=order.pickup_store_phone,
        created_at=order.created_at,
        paid_at=order.paid_at,
        items=[
            OrderItemData(
                goods_id=item.goods_id,
                goods_name=item.goods_name,
                cover_text=item.cover_text,
                cover_color=item.cover_color,
                cover_image=item.cover_image,
                spec_id=item.spec_id,
                spec_name=item.spec_name,
                price_cents=item.price_cents,
                quantity=item.quantity,
                booking_date=item.booking_date,
                pickup_slot=item.pickup_slot,
            )
            for item in order.items
        ],
    )


@router.get("", response_model=ApiResponse[OrderListData])
def get_orders(
    order_no: str = "",
    status: str = "",
    mobile: str = "",
    booking_date: str = "",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> ApiResponse[dict]:
    items, pagination = list_admin_orders(
        db,
        order_no=order_no,
        status=status,
        mobile=mobile,
        booking_date=booking_date,
        page=page,
        page_size=page_size,
    )
    return ApiResponse.success(
        data={
            "list": [
                OrderListItem(
                    order_no=item.order_no,
                    status=item.status,
                    payment_status=item.payment_status,
                    amount_cents=item.amount_cents,
                    contact_name=item.contact_name,
                    mobile=item.mobile,
                    booking_date=item.booking_date,
                    pickup_slot=item.pickup_slot,
                    created_at=item.created_at,
                    goods_count=sum(order_item.quantity for order_item in item.items),
                )
                for item in items
            ],
            "pagination": pagination,
        }
    )


@router.get("/{order_no}", response_model=ApiResponse[OrderData])
def get_order_detail(
    order_no: str,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> ApiResponse[OrderData]:
    return ApiResponse.success(data=serialize_order_detail(get_order_or_404(db, order_no)))


@router.post("/{order_no}/status", response_model=ApiResponse[OrderData])
def change_order_status(
    order_no: str,
    payload: OrderStatusUpdateRequest,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> ApiResponse[OrderData]:
    order = update_order_status(db, get_order_or_404(db, order_no), payload.status)
    if payload.remark:
        order.remark = payload.remark
    db.commit()
    return ApiResponse.success(data=serialize_order_detail(get_order_or_404(db, order_no)))
