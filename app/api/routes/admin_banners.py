from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.core.exceptions import AppException
from app.core.id_utils import normalize_int_id
from app.db.session import get_db
from app.models import Banner
from app.schemas.admin import BannerItem, BannerListData, BannerPayload
from app.schemas.common import ApiResponse
from app.services.catalog_service import list_banners, save_banner


router = APIRouter(prefix="/admin/banners", tags=["admin-banners"])


def serialize_banner(banner: Banner) -> BannerItem:
    return BannerItem(
        banner_id=str(banner.id),
        title=banner.title,
        subtitle=banner.subtitle,
        image_url=banner.image_url,
        action_type=banner.action_type,
        action_value=banner.action_value,
        action_text=banner.action_text,
        sort=banner.sort,
        status=banner.status,
        created_at=banner.created_at,
        updated_at=banner.updated_at,
    )


@router.get("", response_model=ApiResponse[BannerListData])
def get_banner_list(
    keyword: str = "",
    status: str = "",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> ApiResponse[dict]:
    items, pagination = list_banners(
        db,
        keyword=keyword,
        status=status,
        page=page,
        page_size=page_size,
    )
    return ApiResponse.success(
        data={
            "list": [serialize_banner(item) for item in items],
            "pagination": pagination,
        }
    )


@router.get("/{banner_id}", response_model=ApiResponse[BannerItem])
def get_banner_detail(
    banner_id: str,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> ApiResponse[BannerItem]:
    banner = db.get(Banner, normalize_int_id(banner_id, "Banner ID"))
    if not banner:
        raise AppException(code=40405, message="轮播图不存在")
    return ApiResponse.success(data=serialize_banner(banner))


@router.post("", response_model=ApiResponse[BannerItem])
def create_banner(
    payload: BannerPayload,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> ApiResponse[BannerItem]:
    banner = save_banner(db, payload)
    db.commit()
    return ApiResponse.success(data=serialize_banner(banner))


@router.put("/{banner_id}", response_model=ApiResponse[BannerItem])
def update_banner(
    banner_id: str,
    payload: BannerPayload,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> ApiResponse[BannerItem]:
    banner = db.get(Banner, normalize_int_id(banner_id, "Banner ID"))
    if not banner:
        raise AppException(code=40405, message="轮播图不存在")
    banner = save_banner(db, payload, existing=banner)
    db.commit()
    return ApiResponse.success(data=serialize_banner(banner))


@router.delete("/{banner_id}", response_model=ApiResponse[dict])
def delete_banner(
    banner_id: str,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> ApiResponse[dict]:
    banner = db.get(Banner, normalize_int_id(banner_id, "Banner ID"))
    if not banner:
        raise AppException(code=40405, message="轮播图不存在")
    db.delete(banner)
    db.commit()
    return ApiResponse.success(data={"deleted": True})
