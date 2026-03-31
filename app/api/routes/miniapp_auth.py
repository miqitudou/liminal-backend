from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.common import ApiResponse
from app.schemas.miniapp import MiniappLoginData, MiniappSimpleLoginRequest
from app.services.auth_service import simple_user_login


router = APIRouter(tags=["miniapp-auth"])


@router.post("/auth/wechat_phone_login", response_model=ApiResponse[MiniappLoginData])
def miniapp_login(
    payload: MiniappSimpleLoginRequest,
    db: Session = Depends(get_db),
) -> ApiResponse[dict]:
    return ApiResponse.success(
        data=simple_user_login(
            db,
            mobile=payload.mobile,
            nickname=payload.nickname,
            avatar_url=payload.avatar_url,
        )
    )
