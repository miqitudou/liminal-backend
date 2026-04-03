from __future__ import annotations

from math import ceil

from app.core.constants import ORDER_STATUS_PENDING_PAYMENT, ORDER_STATUS_TEXT_MAP
from app.models import (
    Banner,
    Category,
    Goods,
    Order,
    PointsProduct,
    PointsRedemption,
    PointsTransaction,
    StoreConfig,
    User,
)


def cents_to_yuan(cents: int) -> int | float:
    if cents % 100 == 0:
        return cents // 100
    return round(cents / 100, 2)


def build_pagination(page: int, page_size: int, total: int) -> dict:
    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": ceil(total / page_size) if page_size else 1,
    }


def serialize_store_for_miniapp(store: StoreConfig) -> dict:
    return {
        "name": store.store_name,
        "shortName": store.short_name,
        "phone": store.phone,
        "businessHours": store.business_hours,
        "address": store.address,
        "pickupNotice": store.pickup_notice,
        "socialQrs": [
            {
                "title": "小红书",
                "note": "看上新与日常",
                "imageUrl": store.xiaohongshu_qr_url,
            },
            {
                "title": "微信号",
                "note": "加好友咨询下单",
                "imageUrl": store.wechat_qr_url,
            },
            {
                "title": "抖音",
                "note": "看制作与开箱",
                "imageUrl": store.douyin_qr_url,
            },
        ],
    }


def serialize_category_for_miniapp(category: Category) -> dict:
    return {
        "id": str(category.id),
        "name": category.category_name,
        "desc": category.category_desc,
        "badge": category.badge_text,
    }


def serialize_banner_for_miniapp(banner: Banner) -> dict:
    return {
        "id": str(banner.id),
        "title": banner.title,
        "subtitle": banner.subtitle,
        "actionText": banner.action_text,
        "categoryId": banner.action_value if banner.action_type == "category" else "",
        "imageUrl": banner.image_url,
    }


def get_enabled_goods_specs(goods: Goods) -> list:
    return [spec for spec in goods.specs if spec.status == "enabled"] if goods.specs else []


def get_goods_price_range_cents(goods: Goods) -> tuple[int, int]:
    enabled_specs = get_enabled_goods_specs(goods)

    if enabled_specs:
        prices = [spec.price_cents for spec in enabled_specs]
        return min(prices), max(prices)

    return goods.price_cents, goods.price_cents


def serialize_goods_for_miniapp(goods: Goods, detail: bool = False) -> dict:
    enabled_specs = get_enabled_goods_specs(goods)
    price_min_cents, price_max_cents = get_goods_price_range_cents(goods)

    payload = {
        "id": str(goods.id),
        "name": goods.goods_name,
        "featureText": goods.feature_text,
        "categoryId": str(goods.category_id),
        "coverText": goods.cover_text,
        "coverColor": goods.cover_color,
        "coverImage": goods.cover_image,
        "price": cents_to_yuan(price_min_cents),
        "priceMin": cents_to_yuan(price_min_cents),
        "priceMax": cents_to_yuan(price_max_cents),
        "desc": goods.goods_desc,
        "sales": goods.sales_count,
        "status": goods.status,
        "isRecommend": goods.is_recommend,
        "tags": goods.tags or [],
        "specCount": len(enabled_specs),
    }
    if detail:
        payload["specs"] = [
            {
                "specId": str(spec.id),
                "specName": spec.spec_name,
                "price": cents_to_yuan(spec.price_cents),
                "stock": spec.stock,
                "minAdvanceHours": spec.min_advance_hours,
            }
            for spec in enabled_specs
        ]
        payload["bookingRules"] = {
            "minAdvanceHours": goods.booking_rule.min_advance_hours
            if goods.booking_rule
            else 0,
            "pickupSlots": goods.booking_rule.pickup_slots if goods.booking_rule else [],
        }
        payload["detailTips"] = goods.detail_tips or []
    return payload


def serialize_user_for_miniapp(user: User) -> dict:
    nickname = user.nickname or "微信用户"
    return {
        "nickname": nickname,
        "avatarText": nickname[:1],
        "avatarUrl": user.avatar_url,
        "mobile": user.mobile,
        "memberSince": user.member_since,
        "levelText": user.level_text,
        "pointsBalance": user.points_balance,
        "wechatBound": user.wechat_bound,
        "phoneBound": user.phone_bound,
        "profileCompleted": user.profile_completed,
    }


def serialize_order_for_miniapp(order: Order) -> dict:
    return {
        "orderNo": order.order_no,
        "items": [
            {
                "goodsId": str(item.goods_id),
                "goodsName": item.goods_name,
                "coverText": item.cover_text,
                "coverColor": item.cover_color,
                "coverImage": item.cover_image,
                "specId": str(item.spec_id),
                "specName": item.spec_name,
                "price": cents_to_yuan(item.price_cents),
                "quantity": item.quantity,
                "bookingDate": item.booking_date,
                "pickupSlot": item.pickup_slot,
            }
            for item in order.items
        ],
        "amount": cents_to_yuan(order.amount_cents),
        "status": order.status,
        "statusText": ORDER_STATUS_TEXT_MAP.get(order.status, "待处理"),
        "contactName": order.contact_name,
        "mobile": order.mobile,
        "bookingDate": order.booking_date,
        "pickupSlot": order.pickup_slot,
        "remark": order.remark,
        "createdAt": order.created_at.strftime("%Y-%m-%d %H:%M") if order.created_at else "",
        "pickupStoreName": order.pickup_store_name,
        "pickupStoreAddress": order.pickup_store_address,
        "pickupStorePhone": order.pickup_store_phone,
        "canPay": order.status == ORDER_STATUS_PENDING_PAYMENT,
        "canCancel": order.status == ORDER_STATUS_PENDING_PAYMENT,
    }


def serialize_points_product_for_miniapp(product: PointsProduct) -> dict:
    return {
        "id": str(product.id),
        "title": product.title,
        "subtitle": product.subtitle,
        "desc": product.description,
        "imageUrl": product.image_url,
        "points": product.points_cost,
        "stock": product.stock,
        "tag": product.subtitle or "积分兑换",
        "status": product.status,
    }


def serialize_points_redemption_for_miniapp(redemption: PointsRedemption) -> dict:
    return {
        "id": str(redemption.id),
        "productId": str(redemption.product_id),
        "title": redemption.product_snapshot_title,
        "imageUrl": redemption.product_snapshot_image,
        "points": redemption.points_cost,
        "status": redemption.status,
        "createdAt": redemption.created_at.strftime("%Y-%m-%d %H:%M")
        if redemption.created_at
        else "",
    }


def serialize_points_transaction_for_miniapp(transaction: PointsTransaction) -> dict:
    return {
        "id": str(transaction.id),
        "changePoints": transaction.change_points,
        "balanceAfter": transaction.balance_after,
        "transactionType": transaction.transaction_type,
        "remark": transaction.remark,
        "createdAt": transaction.created_at.strftime("%Y-%m-%d %H:%M")
        if transaction.created_at
        else "",
    }
