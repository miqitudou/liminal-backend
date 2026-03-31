from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_admin
from app.core.exceptions import AppException
from app.core.id_utils import normalize_int_id
from app.db.session import get_db
from app.models import Category
from app.schemas.admin import CategoryItem, CategoryListData, CategoryPayload
from app.schemas.common import ApiResponse
from app.services.catalog_service import delete_category, list_categories, save_category


router = APIRouter(prefix="/admin/categories", tags=["admin-categories"])


def serialize_category(category: Category) -> CategoryItem:
    return CategoryItem(
        category_id=str(category.id),
        category_name=category.category_name,
        category_desc=category.category_desc,
        badge_text=category.badge_text,
        delivery_mode=category.delivery_mode,
        sort=category.sort,
        status=category.status,
        goods_count=len(category.goods),
        created_at=category.created_at,
        updated_at=category.updated_at,
    )


@router.get("", response_model=ApiResponse[CategoryListData])
def get_categories(
    keyword: str = "",
    status: str = "",
    delivery_mode: str = "",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> ApiResponse[dict]:
    items, pagination = list_categories(
        db,
        keyword=keyword,
        status=status,
        delivery_mode=delivery_mode,
        page=page,
        page_size=page_size,
    )
    return ApiResponse.success(
        data={"list": [serialize_category(item) for item in items], "pagination": pagination}
    )


@router.post("", response_model=ApiResponse[CategoryItem])
def create_category(
    payload: CategoryPayload,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> ApiResponse[CategoryItem]:
    category = save_category(db, payload)
    db.commit()
    db.refresh(category)
    return ApiResponse.success(data=serialize_category(category))


@router.put("/{category_id}", response_model=ApiResponse[CategoryItem])
def update_category(
    category_id: str,
    payload: CategoryPayload,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> ApiResponse[CategoryItem]:
    category = db.get(Category, normalize_int_id(category_id, "分类ID"))
    if not category:
        raise AppException(code=40402, message="分类不存在")
    category = save_category(db, payload, existing=category)
    db.commit()
    db.refresh(category)
    return ApiResponse.success(data=serialize_category(category))


@router.delete("/{category_id}", response_model=ApiResponse[dict])
def remove_category(
    category_id: str,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> ApiResponse[dict]:
    category = db.scalar(
        select(Category)
        .options(selectinload(Category.goods))
        .where(Category.id == normalize_int_id(category_id, "分类ID"))
    )
    if not category:
        raise AppException(code=40402, message="分类不存在")
    delete_category(db, category)
    db.commit()
    return ApiResponse.success(data={"deleted": True})
