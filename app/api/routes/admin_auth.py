from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.admin import AdminLoginData, AdminLoginRequest
from app.schemas.common import ApiResponse
from app.services.auth_service import admin_login


router = APIRouter(prefix="/admin/auth", tags=["admin-auth"])


@router.post("/login", response_model=ApiResponse[AdminLoginData])
def login(payload: AdminLoginRequest, db: Session = Depends(get_db)) -> ApiResponse[dict]:
    return ApiResponse.success(data=admin_login(db, payload.username, payload.password))
