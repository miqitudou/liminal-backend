from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.db.session import get_db
from app.models import StoreConfig
from app.schemas.admin import StoreConfigItem, StoreConfigPayload
from app.schemas.common import ApiResponse


router = APIRouter(prefix="/admin/store", tags=["admin-store"])


def get_or_create_store_config(db: Session) -> StoreConfig:
    store = db.scalar(select(StoreConfig).order_by(StoreConfig.id.asc()).limit(1))
    if store:
        return store

    store = StoreConfig(
        store_name="Liminal",
        short_name="里米",
        phone="400-820-1314",
        business_hours="09:00-20:00",
        address="四川天府新区",
        pickup_notice="蛋糕类建议至少提前 4 小时预约，节日款请尽量提前 1 天预定。",
    )
    db.add(store)
    db.flush()
    return store


def serialize_store(store: StoreConfig) -> StoreConfigItem:
    return StoreConfigItem(
        id=str(store.id),
        store_name=store.store_name,
        short_name=store.short_name,
        phone=store.phone,
        business_hours=store.business_hours,
        address=store.address,
        pickup_notice=store.pickup_notice,
        xiaohongshu_qr_url=store.xiaohongshu_qr_url,
        wechat_qr_url=store.wechat_qr_url,
        douyin_qr_url=store.douyin_qr_url,
        created_at=store.created_at,
        updated_at=store.updated_at,
    )


@router.get("", response_model=ApiResponse[StoreConfigItem])
def get_store_config(
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> ApiResponse[StoreConfigItem]:
    return ApiResponse.success(data=serialize_store(get_or_create_store_config(db)))


@router.put("", response_model=ApiResponse[StoreConfigItem])
def update_store_config(
    payload: StoreConfigPayload,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> ApiResponse[StoreConfigItem]:
    store = get_or_create_store_config(db)
    store.store_name = payload.store_name
    store.short_name = payload.short_name
    store.phone = payload.phone
    store.business_hours = payload.business_hours
    store.address = payload.address
    store.pickup_notice = payload.pickup_notice
    store.xiaohongshu_qr_url = payload.xiaohongshu_qr_url
    store.wechat_qr_url = payload.wechat_qr_url
    store.douyin_qr_url = payload.douyin_qr_url
    db.add(store)
    db.commit()
    db.refresh(store)
    return ApiResponse.success(data=serialize_store(store), message="门店配置已更新")
