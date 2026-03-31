from fastapi import HTTPException, status


class AppException(HTTPException):
    def __init__(
        self,
        *,
        code: int,
        message: str,
        http_status: int = status.HTTP_400_BAD_REQUEST,
    ) -> None:
        super().__init__(
            status_code=http_status,
            detail={
                "code": code,
                "message": message,
            },
        )
