from app.core.exceptions import AppException


def normalize_int_id(value: str | int, field_name: str = "ID") -> int:
    try:
        normalized = int(value)
    except (TypeError, ValueError):
        raise AppException(code=40001, message=f"{field_name}格式不正确")

    if normalized <= 0:
        raise AppException(code=40001, message=f"{field_name}格式不正确")

    return normalized
