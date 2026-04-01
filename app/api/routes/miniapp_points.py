from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_optional_user
from app.db.session import get_db
from app.schemas.common import ApiResponse
from app.schemas.miniapp import (
    MiniappPointsMallData,
    MiniappPointsRedeemRequest,
    MiniappPointsRedeemResponse,
)
from app.services.mappers import (
    serialize_points_product_for_miniapp,
    serialize_points_redemption_for_miniapp,
)
from app.services.points_service import get_points_mall_data, redeem_points_product


router = APIRouter(prefix="/points", tags=["miniapp-points"])


@router.get("/mall", response_model=ApiResponse[MiniappPointsMallData])
def get_points_mall(
    db: Session = Depends(get_db),
    user=Depends(get_optional_user),
) -> ApiResponse[dict]:
    payload = get_points_mall_data(db, user)
    return ApiResponse.success(
        data={
            "pointsBalance": payload["pointsBalance"],
            "tips": payload["tips"],
            "goods": [
                serialize_points_product_for_miniapp(item)
                for item in payload["goods"]
            ],
            "records": [
                serialize_points_redemption_for_miniapp(item)
                for item in payload["records"]
            ],
        }
    )


@router.post("/redeem", response_model=ApiResponse[MiniappPointsRedeemResponse])
def redeem_points(
    payload: MiniappPointsRedeemRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> ApiResponse[dict]:
    redemption = redeem_points_product(db, user=user, product_id=payload.productId)
    db.commit()
    return ApiResponse.success(
        data={
            "redemptionId": str(redemption.id),
            "pointsBalance": user.points_balance,
        },
        message="兑换成功",
    )
