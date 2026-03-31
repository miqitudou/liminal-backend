from datetime import datetime, timezone
from typing import Generic, TypeVar
from uuid import uuid4

from pydantic import BaseModel, Field


T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    code: int = 200
    message: str = "success"
    data: T | None = None
    request_id: str = Field(default_factory=lambda: uuid4().hex)
    timestamp: int = Field(
        default_factory=lambda: int(datetime.now(timezone.utc).timestamp() * 1000)
    )

    @classmethod
    def success(
        cls,
        *,
        data: T | None = None,
        message: str = "success",
    ) -> "ApiResponse[T]":
        return cls(code=200, message=message, data=data)
