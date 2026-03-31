from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.schemas.common import ApiResponse
from app.schemas.miniapp import MiniappUserMeData
from app.services.mappers import serialize_user_for_miniapp


router = APIRouter(tags=["miniapp-users"])


@router.get("/users/me", response_model=ApiResponse[MiniappUserMeData])
def get_me(user=Depends(get_current_user)) -> ApiResponse[dict]:
    return ApiResponse.success(data={"userInfo": serialize_user_for_miniapp(user)})
