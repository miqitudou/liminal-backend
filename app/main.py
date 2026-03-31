from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import AppException
from app.db.init_db import init_db
from app.schemas.common import ApiResponse


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.exception_handler(AppException)
async def handle_app_exception(_: Request, exc: AppException) -> JSONResponse:
    detail = exc.detail if isinstance(exc.detail, dict) else {}
    return JSONResponse(
        status_code=exc.status_code,
        content=ApiResponse(
            code=detail.get("code", exc.status_code),
            message=detail.get("message", "请求失败"),
            data=None,
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def handle_generic_exception(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content=ApiResponse(
            code=50001,
            message=str(exc) if settings.debug else "服务器内部错误",
            data=None,
        ).model_dump(),
    )


@app.get("/", response_model=ApiResponse[dict])
async def root() -> ApiResponse[dict]:
    return ApiResponse.success(
        data={
            "app_name": settings.app_name,
            "app_version": settings.app_version,
            "docs_url": "/docs",
        }
    )
