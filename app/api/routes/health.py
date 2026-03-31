from fastapi import APIRouter

from app.core.config import settings
from app.schemas.common import ApiResponse


router = APIRouter()


@router.get("/health", response_model=ApiResponse[dict])
async def health_check() -> ApiResponse[dict]:
    return ApiResponse.success(
        data={
            "status": "ok",
            "app_name": settings.app_name,
            "app_version": settings.app_version,
        }
    )
