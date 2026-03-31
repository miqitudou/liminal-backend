from fastapi import APIRouter

from app.api.routes import (
    admin_auth,
    admin_banners,
    admin_categories,
    admin_goods,
    admin_orders,
    admin_uploads,
    health,
    miniapp_auth,
    miniapp_content,
    miniapp_orders,
    miniapp_users,
)


api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(admin_auth.router)
api_router.include_router(admin_categories.router)
api_router.include_router(admin_goods.router)
api_router.include_router(admin_banners.router)
api_router.include_router(admin_orders.router)
api_router.include_router(admin_uploads.router)
api_router.include_router(miniapp_auth.router)
api_router.include_router(miniapp_content.router)
api_router.include_router(miniapp_orders.router)
api_router.include_router(miniapp_users.router)
