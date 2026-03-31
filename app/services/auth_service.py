from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.constants import TOKEN_TYPE_ADMIN, TOKEN_TYPE_USER
from app.core.exceptions import AppException
from app.core.security import create_access_token, verify_password
from app.models import AdminUser, User
from app.services.mappers import serialize_user_for_miniapp
from app.services.seed import generate_id, generate_member_since


def admin_login(db: Session, username: str, password: str) -> dict:
    admin = db.scalar(select(AdminUser).where(AdminUser.username == username))
    if not admin or not verify_password(password, admin.password_hash):
        raise AppException(code=40001, message="账号或密码错误")

    token = create_access_token(subject=admin.id, token_type=TOKEN_TYPE_ADMIN)
    return {
        "access_token": token,
        "token_type": "bearer",
        "admin_info": {
            "id": admin.id,
            "username": admin.username,
            "display_name": admin.display_name,
        },
    }


def simple_user_login(
    db: Session,
    *,
    mobile: str | None,
    nickname: str | None,
    avatar_url: str | None,
) -> dict:
    resolved_mobile = mobile or "13800000000"
    user = db.scalar(select(User).where(User.mobile == resolved_mobile))
    is_new_user = False

    if not user:
        is_new_user = True
        user = User(
            id=generate_id("user"),
            nickname=nickname or f"微信用户{resolved_mobile[-4:]}",
            avatar_url=avatar_url or "",
            mobile=resolved_mobile,
            member_since=generate_member_since(),
            level_text="烘焙常客",
            wechat_bound=True,
            phone_bound=True,
            profile_completed=bool(nickname or avatar_url),
            status="enabled",
        )
        db.add(user)
        db.flush()
    else:
        if nickname:
            user.nickname = nickname
        if avatar_url:
            user.avatar_url = avatar_url
        user.wechat_bound = True
        user.phone_bound = True
        db.flush()

    token = create_access_token(subject=user.id, token_type=TOKEN_TYPE_USER)
    return {
        "accessToken": token,
        "expiresIn": 86400,
        "userInfo": serialize_user_for_miniapp(user),
        "isNewUser": is_new_user,
    }
