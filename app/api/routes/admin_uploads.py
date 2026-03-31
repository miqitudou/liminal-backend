from fastapi import APIRouter, Depends, File, UploadFile

from app.api.deps import get_current_admin
from app.schemas.admin import UploadData
from app.schemas.common import ApiResponse
from app.services.upload_service import upload_image


router = APIRouter(prefix="/admin/uploads", tags=["admin-uploads"])


@router.post("/image", response_model=ApiResponse[UploadData])
def upload_image_file(
    file: UploadFile = File(...),
    _admin=Depends(get_current_admin),
) -> ApiResponse[dict]:
    return ApiResponse.success(data=upload_image(file))
