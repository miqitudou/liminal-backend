from fastapi import Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.constants import TOKEN_TYPE_ADMIN, TOKEN_TYPE_USER
from app.core.exceptions import AppException
from app.core.security import decode_token
from app.db.session import get_db
from app.models import AdminUser, User


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> AdminUser:
    if not credentials:
        raise AppException(
            code=40101,
            message="未登录",
            http_status=status.HTTP_401_UNAUTHORIZED,
        )

    try:
        payload = decode_token(credentials.credentials)
    except ValueError:
        raise AppException(
            code=40102,
            message="登录已过期",
            http_status=status.HTTP_401_UNAUTHORIZED,
        )
    if payload.get("token_type") != TOKEN_TYPE_ADMIN:
        raise AppException(
            code=40102,
            message="登录已过期",
            http_status=status.HTTP_401_UNAUTHORIZED,
        )

    admin = db.get(AdminUser, payload.get("sub"))
    if not admin:
        raise AppException(
            code=40102,
            message="登录已过期",
            http_status=status.HTTP_401_UNAUTHORIZED,
        )
    return admin


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if not credentials:
        raise AppException(
            code=40101,
            message="未登录",
            http_status=status.HTTP_401_UNAUTHORIZED,
        )

    try:
        payload = decode_token(credentials.credentials)
    except ValueError:
        raise AppException(
            code=40102,
            message="登录已过期",
            http_status=status.HTTP_401_UNAUTHORIZED,
        )
    if payload.get("token_type") != TOKEN_TYPE_USER:
        raise AppException(
            code=40102,
            message="登录已过期",
            http_status=status.HTTP_401_UNAUTHORIZED,
        )

    user = db.get(User, payload.get("sub"))
    if not user:
        raise AppException(
            code=40102,
            message="登录已过期",
            http_status=status.HTTP_401_UNAUTHORIZED,
        )
    return user
