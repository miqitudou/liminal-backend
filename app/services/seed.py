from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.models import (
    AdminUser,
    Banner,
    Category,
    Goods,
    GoodsBookingRule,
    GoodsSpec,
    PointsProduct,
    StoreConfig,
)


def seed_admin_user(db: Session) -> None:
    existing = db.scalar(
        select(AdminUser).where(AdminUser.username == settings.default_admin_username)
    )
    if existing:
        return

    db.add(
        AdminUser(
            username=settings.default_admin_username,
            password_hash=hash_password(settings.default_admin_password),
            display_name=settings.default_admin_display_name,
            status="enabled",
        )
    )


def seed_store_config(db: Session) -> StoreConfig:
    store = db.scalar(select(StoreConfig).limit(1))
    if store:
        return store

    store = StoreConfig(
        store_name="Liminal",
        short_name="里米",
        phone="400-820-1314",
        business_hours="09:00-20:00",
        address="四川天府新区",
        pickup_notice="蛋糕类建议至少提前 4 小时预约，节日款请尽量提前 1 天预定。",
    )
    db.add(store)
    db.flush()
    return store


def seed_catalog_content(db: Session) -> None:
    if db.scalar(select(Category.id).limit(1)):
        return

    category_seed = [
        {
            "key": "cake",
            "category_name": "奶油蛋糕",
            "category_desc": "适合生日庆祝与朋友聚会",
            "badge_text": "人气",
            "delivery_mode": "local",
            "sort": 1,
        },
        {
            "key": "bread",
            "category_name": "欧包吐司",
            "category_desc": "适合早餐与常温快递",
            "badge_text": "新鲜",
            "delivery_mode": "express",
            "sort": 2,
        },
        {
            "key": "dessert",
            "category_name": "甜点下午茶",
            "category_desc": "适合门店自提和下午茶分享",
            "badge_text": "推荐",
            "delivery_mode": "local",
            "sort": 3,
        },
        {
            "key": "gift",
            "category_name": "分享礼盒",
            "category_desc": "适合送礼与办公室分享",
            "badge_text": "限定",
            "delivery_mode": "express",
            "sort": 4,
        },
    ]

    categories_by_key: dict[str, Category] = {}
    for item in category_seed:
        category = Category(
            category_name=item["category_name"],
            category_desc=item["category_desc"],
            badge_text=item["badge_text"],
            delivery_mode=item["delivery_mode"],
            sort=item["sort"],
            status="enabled",
        )
        db.add(category)
        db.flush()
        categories_by_key[item["key"]] = category

    banner_seed = [
        {
            "title": "春日草莓蛋糕",
            "subtitle": "轻奶油搭配鲜果夹层，适合同城预约配送",
            "image_url": "https://images.pexels.com/photos/30177790/pexels-photo-30177790.jpeg?auto=compress&cs=tinysrgb&w=1400",
            "action_type": "category",
            "action_value": str(categories_by_key["cake"].id),
            "action_text": "查看蛋糕",
            "sort": 1,
        },
        {
            "title": "晨光现烤面包",
            "subtitle": "吐司与餐包陆续出炉，适合早餐囤货",
            "image_url": "https://images.pexels.com/photos/8508106/pexels-photo-8508106.jpeg?auto=compress&cs=tinysrgb&w=1400",
            "action_type": "category",
            "action_value": str(categories_by_key["bread"].id),
            "action_text": "进入面包区",
            "sort": 2,
        },
        {
            "title": "下午茶分享礼盒",
            "subtitle": "曲奇与常温烘焙组合，适合快递分享",
            "image_url": "https://images.pexels.com/photos/32414204/pexels-photo-32414204.jpeg?auto=compress&cs=tinysrgb&w=1400",
            "action_type": "category",
            "action_value": str(categories_by_key["gift"].id),
            "action_text": "查看礼盒",
            "sort": 3,
        },
    ]

    for item in banner_seed:
        db.add(
            Banner(
                title=item["title"],
                subtitle=item["subtitle"],
                image_url=item["image_url"],
                action_type=item["action_type"],
                action_value=item["action_value"],
                action_text=item["action_text"],
                sort=item["sort"],
                status="enabled",
            )
        )

    goods_seed = [
        {
            "category_key": "cake",
            "goods_name": "云朵草莓盒子",
            "goods_desc": "新鲜草莓搭配轻奶油和松软蛋糕胚，适合当天分享。",
            "cover_text": "草莓盒子",
            "cover_color": "#f7d8d9",
            "cover_image": "https://images.pexels.com/photos/20849554/pexels-photo-20849554.jpeg?auto=compress&cs=tinysrgb&w=1200",
            "price_cents": 5800,
            "sales_count": 286,
            "is_recommend": True,
            "tags": ["招牌", "草莓季"],
            "detail_tips": ["建议冷藏保存口感更好", "请在当天食用", "支持附赠祝福卡"],
            "specs": [
                ("单人分享装", 5800, 30, 4, 1),
                ("双人分享装", 8800, 18, 4, 2),
            ],
            "pickup_slots": ["10:00-12:00", "13:00-15:00", "16:00-18:00"],
            "min_advance_hours": 4,
        },
        {
            "category_key": "bread",
            "goods_name": "海盐奶香卷",
            "goods_desc": "奶香柔和，带一点海盐回甘，适合早餐和下午茶。",
            "cover_text": "奶香卷",
            "cover_color": "#f1dfc8",
            "cover_image": "https://images.pexels.com/photos/8508106/pexels-photo-8508106.jpeg?auto=compress&cs=tinysrgb&w=1200",
            "price_cents": 2200,
            "sales_count": 412,
            "is_recommend": True,
            "tags": ["热销", "早餐"],
            "detail_tips": ["常温保存 1 天", "复烤后更香", "适合搭配咖啡"],
            "specs": [
                ("2 只装", 2200, 50, 2, 1),
                ("4 只装", 3900, 30, 2, 2),
            ],
            "pickup_slots": ["09:00-11:00", "11:00-13:00", "15:00-17:00"],
            "min_advance_hours": 2,
        },
        {
            "category_key": "dessert",
            "goods_name": "伯爵红茶司康",
            "goods_desc": "茶香细腻，外酥内软，适合搭配果酱和奶油。",
            "cover_text": "红茶司康",
            "cover_color": "#e8dccd",
            "cover_image": "https://images.pexels.com/photos/30359470/pexels-photo-30359470.jpeg?auto=compress&cs=tinysrgb&w=1200",
            "price_cents": 1800,
            "sales_count": 198,
            "is_recommend": False,
            "tags": ["下午茶"],
            "detail_tips": ["建议搭配红茶", "现烤出炉更香", "适合朋友分享"],
            "specs": [
                ("2 枚装", 1800, 40, 2, 1),
                ("6 枚装", 4900, 16, 4, 2),
            ],
            "pickup_slots": ["10:00-12:00", "13:00-15:00", "17:00-19:00"],
            "min_advance_hours": 2,
        },
        {
            "category_key": "dessert",
            "goods_name": "焦糖坚果挞",
            "goods_desc": "焦糖香气浓郁，层次丰富，香甜但不腻口。",
            "cover_text": "坚果挞",
            "cover_color": "#edd6b8",
            "cover_image": "https://images.pexels.com/photos/7451861/pexels-photo-7451861.jpeg?auto=compress&cs=tinysrgb&w=1200",
            "price_cents": 3600,
            "sales_count": 165,
            "is_recommend": True,
            "tags": ["招牌"],
            "detail_tips": ["坚果过敏人群慎选", "常温保存 2 天", "适合搭配美式咖啡"],
            "specs": [
                ("单枚", 3600, 25, 4, 1),
                ("双枚礼盒", 6800, 12, 6, 2),
            ],
            "pickup_slots": ["11:00-13:00", "14:00-16:00", "17:00-19:00"],
            "min_advance_hours": 4,
        },
        {
            "category_key": "bread",
            "goods_name": "原味手撕吐司",
            "goods_desc": "低糖松软，奶香自然，适合家庭早餐分享。",
            "cover_text": "手撕吐司",
            "cover_color": "#f0e2cf",
            "cover_image": "https://images.pexels.com/photos/7884507/pexels-photo-7884507.jpeg?auto=compress&cs=tinysrgb&w=1200",
            "price_cents": 2400,
            "sales_count": 365,
            "is_recommend": False,
            "tags": ["早餐", "回购高"],
            "detail_tips": ["可切片", "适合复烤", "建议 2 天内食用"],
            "specs": [
                ("标准条装", 2400, 36, 2, 1),
                ("双条分享装", 4600, 20, 4, 2),
            ],
            "pickup_slots": ["09:00-11:00", "12:00-14:00", "16:00-18:00"],
            "min_advance_hours": 2,
        },
        {
            "category_key": "cake",
            "goods_name": "香草缎带蛋糕",
            "goods_desc": "奶油纹理细腻，适合生日、纪念日和小型聚会。",
            "cover_text": "缎带蛋糕",
            "cover_color": "#f6e7db",
            "cover_image": "https://images.pexels.com/photos/30177790/pexels-photo-30177790.jpeg?auto=compress&cs=tinysrgb&w=1200",
            "price_cents": 16800,
            "sales_count": 108,
            "is_recommend": True,
            "tags": ["庆生", "可写字"],
            "detail_tips": ["支持写字留言", "建议冷藏保存", "请提前预约"],
            "specs": [
                ("4 寸", 16800, 12, 6, 1),
                ("6 寸", 23800, 8, 6, 2),
            ],
            "pickup_slots": ["10:00-12:00", "14:00-16:00", "18:00-20:00"],
            "min_advance_hours": 6,
        },
        {
            "category_key": "gift",
            "goods_name": "手作曲奇礼盒",
            "goods_desc": "黄油香气浓郁，多口味组合，适合送礼和多人分享。",
            "cover_text": "曲奇礼盒",
            "cover_color": "#ead3c4",
            "cover_image": "https://images.pexels.com/photos/32414204/pexels-photo-32414204.jpeg?auto=compress&cs=tinysrgb&w=1200",
            "price_cents": 9600,
            "sales_count": 134,
            "is_recommend": True,
            "tags": ["礼盒", "送礼"],
            "detail_tips": ["含原味与可可口味", "礼盒附赠手提袋", "常温保存 3 天"],
            "specs": [
                ("12 枚礼盒", 9600, 15, 6, 1),
                ("24 枚礼盒", 16800, 10, 12, 2),
            ],
            "pickup_slots": ["10:00-12:00", "13:00-15:00", "16:00-18:00"],
            "min_advance_hours": 6,
        },
        {
            "category_key": "dessert",
            "goods_name": "柠檬磅蛋糕",
            "goods_desc": "酸甜清新，组织紧实，适合春夏下午茶。",
            "cover_text": "磅蛋糕",
            "cover_color": "#f3e3b5",
            "cover_image": "https://images.pexels.com/photos/30700685/pexels-photo-30700685.jpeg?auto=compress&cs=tinysrgb&w=1200",
            "price_cents": 4200,
            "sales_count": 97,
            "is_recommend": False,
            "tags": ["清新"],
            "detail_tips": ["冷藏口感更扎实", "适合下午茶", "礼盒装适合分享"],
            "specs": [
                ("单条装", 4200, 22, 4, 1),
                ("双条礼盒", 7800, 10, 6, 2),
            ],
            "pickup_slots": ["10:00-12:00", "14:00-16:00", "17:00-19:00"],
            "min_advance_hours": 4,
        },
    ]

    for index, item in enumerate(goods_seed, start=1):
        goods = Goods(
            category_id=categories_by_key[item["category_key"]].id,
            goods_name=item["goods_name"],
            goods_desc=item["goods_desc"],
            cover_text=item["cover_text"],
            cover_color=item["cover_color"],
            cover_image=item["cover_image"],
            price_cents=item["price_cents"],
            sales_count=item["sales_count"],
            status="on",
            is_recommend=item["is_recommend"],
            sort=index,
            tags=item["tags"],
            detail_tips=item["detail_tips"],
        )
        db.add(goods)
        db.flush()

        db.add(
            GoodsBookingRule(
                goods_id=goods.id,
                min_advance_hours=item["min_advance_hours"],
                pickup_slots=item["pickup_slots"],
            )
        )

        for spec_name, price_cents, stock, min_hours, spec_sort in item["specs"]:
            db.add(
                GoodsSpec(
                    goods_id=goods.id,
                    spec_name=spec_name,
                    price_cents=price_cents,
                    stock=stock,
                    min_advance_hours=min_hours,
                    sort=spec_sort,
                    status="enabled",
                )
            )


def seed_points_products(db: Session) -> None:
    if db.scalar(select(PointsProduct.id).limit(1)):
        return

    points_products = [
        {
            "title": "曲奇礼盒兑换券",
            "subtitle": "热门兑换",
            "description": "兑换后可到店领取 1 份限定手作曲奇礼盒，适合送礼或办公室分享。",
            "image_url": "https://images.pexels.com/photos/32414204/pexels-photo-32414204.jpeg?auto=compress&cs=tinysrgb&w=1200",
            "points_cost": 980,
            "stock": 32,
            "sort": 1,
        },
        {
            "title": "饮品双杯券",
            "subtitle": "下午茶",
            "description": "可兑换本周限定饮品 2 杯，适合和朋友一起到店小坐。",
            "image_url": "https://images.pexels.com/photos/302903/pexels-photo-302903.jpeg?auto=compress&cs=tinysrgb&w=1200",
            "points_cost": 520,
            "stock": 48,
            "sort": 2,
        },
        {
            "title": "节日贺卡套组",
            "subtitle": "限定周边",
            "description": "包含 3 款烘焙主题贺卡，适合搭配蛋糕或礼盒一起送出。",
            "image_url": "https://images.pexels.com/photos/6270/morning-breakfast-croissant-lamp.jpg?auto=compress&cs=tinysrgb&w=1200",
            "points_cost": 360,
            "stock": 80,
            "sort": 3,
        },
    ]

    for item in points_products:
        db.add(
            PointsProduct(
                title=item["title"],
                subtitle=item["subtitle"],
                description=item["description"],
                image_url=item["image_url"],
                points_cost=item["points_cost"],
                stock=item["stock"],
                sort=item["sort"],
                status="enabled",
            )
        )


def seed_demo_content(db: Session) -> None:
    seed_catalog_content(db)
    seed_store_config(db)
    seed_points_products(db)


def generate_member_since() -> str:
    now = datetime.now()
    return f"{now.year}-{now.month:02d}"
