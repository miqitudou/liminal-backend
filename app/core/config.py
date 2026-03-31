from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Liminal Backend"
    app_version: str = "0.1.0"
    debug: bool = True
    api_prefix: str = "/api"
    database_url: str = (
        "mysql+pymysql://user_liminal:gaoyuan_1997@139.155.146.73:3306/db_liminal?charset=utf8mb4"
    )
    cors_allow_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]
    )
    jwt_secret_key: str = "liminal-dev-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expires_minutes: int = 60 * 24
    default_admin_username: str = "admin"
    default_admin_password: str = "admin123"
    default_admin_display_name: str = "系统管理员"
    cos_secret_id: str = ""
    cos_secret_key: str = ""
    cos_region: str = ""
    cos_bucket: str = ""
    cos_domain: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
