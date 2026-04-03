from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AdminLoginRequest(BaseModel):
    username: str
    password: str


class AdminInfo(BaseModel):
    id: str
    username: str
    display_name: str

    model_config = ConfigDict(from_attributes=True)


class AdminLoginData(BaseModel):
    access_token: str
    token_type: str = "bearer"
    admin_info: AdminInfo


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int


class CategoryPayload(BaseModel):
    category_id: str | int | None = None
    category_name: str
    category_desc: str = ""
    badge_text: str = ""
    delivery_mode: str
    sort: int = 0
    status: str = "enabled"


class CategoryItem(BaseModel):
    category_id: str
    category_name: str
    category_desc: str
    badge_text: str
    delivery_mode: str
    sort: int
    status: str
    goods_count: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None


class CategoryListData(BaseModel):
    list: list[CategoryItem]
    pagination: PaginationMeta


class GoodsSpecPayload(BaseModel):
    spec_id: str | int | None = None
    spec_name: str
    price_cents: int
    stock: int
    min_advance_hours: int = 0
    sort: int = 0
    status: str = "enabled"


class GoodsBookingRulePayload(BaseModel):
    min_advance_hours: int = 0
    pickup_slots: list[str] = Field(default_factory=list)


class GoodsPayload(BaseModel):
    goods_id: str | int | None = None
    category_id: str | int
    goods_name: str
    goods_desc: str = ""
    feature_text: str = ""
    cover_text: str = ""
    cover_color: str = "#f3e1cf"
    cover_image: str = ""
    price_cents: int = 0
    sales_count: int = 0
    status: str = "on"
    is_recommend: bool = False
    sort: int = 0
    tags: list[str] = Field(default_factory=list)
    detail_tips: list[str] = Field(default_factory=list)
    specs: list[GoodsSpecPayload] = Field(default_factory=list)
    booking_rule: GoodsBookingRulePayload = Field(
        default_factory=GoodsBookingRulePayload
    )


class GoodsSpecItem(BaseModel):
    spec_id: str
    spec_name: str
    price_cents: int
    stock: int
    min_advance_hours: int
    sort: int
    status: str


class GoodsBookingRuleItem(BaseModel):
    min_advance_hours: int
    pickup_slots: list[str]


class GoodsItem(BaseModel):
    goods_id: str
    category_id: str
    category_name: str
    goods_name: str
    goods_desc: str
    feature_text: str = ""
    cover_text: str
    cover_color: str
    cover_image: str
    price_cents: int
    price_min_cents: int = 0
    price_max_cents: int = 0
    sales_count: int
    status: str
    is_recommend: bool
    sort: int
    tags: list[str]
    detail_tips: list[str]
    specs: list[GoodsSpecItem] = Field(default_factory=list)
    booking_rule: GoodsBookingRuleItem
    created_at: datetime | None = None
    updated_at: datetime | None = None


class GoodsListItem(BaseModel):
    goods_id: str
    category_id: str
    category_name: str
    goods_name: str
    feature_text: str = ""
    cover_image: str
    price_cents: int
    price_min_cents: int = 0
    price_max_cents: int = 0
    sales_count: int
    status: str
    is_recommend: bool
    spec_count: int
    updated_at: datetime | None = None


class GoodsListData(BaseModel):
    list: list[GoodsListItem]
    pagination: PaginationMeta


class BannerPayload(BaseModel):
    banner_id: str | int | None = None
    title: str
    subtitle: str = ""
    image_url: str = ""
    action_type: str = "none"
    action_value: str | int = ""
    action_text: str = ""
    sort: int = 0
    status: str = "enabled"


class BannerItem(BaseModel):
    banner_id: str
    title: str
    subtitle: str
    image_url: str
    action_type: str
    action_value: str
    action_text: str
    sort: int
    status: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


class BannerListData(BaseModel):
    list: list[BannerItem]
    pagination: PaginationMeta


class OrderItemData(BaseModel):
    goods_id: str
    goods_name: str
    cover_text: str
    cover_color: str
    cover_image: str
    spec_id: str
    spec_name: str
    price_cents: int
    quantity: int
    booking_date: str
    pickup_slot: str


class OrderData(BaseModel):
    order_no: str
    status: str
    payment_status: str
    amount_cents: int
    contact_name: str
    mobile: str
    booking_date: str
    pickup_slot: str
    remark: str
    pickup_store_name: str
    pickup_store_address: str
    pickup_store_phone: str
    created_at: datetime | None = None
    paid_at: datetime | None = None
    items: list[OrderItemData]


class OrderListItem(BaseModel):
    order_no: str
    status: str
    payment_status: str
    amount_cents: int
    contact_name: str
    mobile: str
    booking_date: str
    pickup_slot: str
    created_at: datetime | None = None
    goods_count: int


class OrderListData(BaseModel):
    list: list[OrderListItem]
    pagination: PaginationMeta


class OrderStatusUpdateRequest(BaseModel):
    status: str
    remark: str | None = None


class UploadData(BaseModel):
    file_name: str
    file_url: str
    file_key: str


class StoreConfigPayload(BaseModel):
    store_name: str
    short_name: str
    phone: str
    business_hours: str
    address: str
    pickup_notice: str = ""
    xiaohongshu_qr_url: str = ""
    wechat_qr_url: str = ""
    douyin_qr_url: str = ""


class StoreConfigItem(BaseModel):
    id: str
    store_name: str
    short_name: str
    phone: str
    business_hours: str
    address: str
    pickup_notice: str
    xiaohongshu_qr_url: str
    wechat_qr_url: str
    douyin_qr_url: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


class PointsProductPayload(BaseModel):
    title: str
    subtitle: str = ""
    description: str = ""
    image_url: str = ""
    points_cost: int
    stock: int = 0
    sort: int = 0
    status: str = "enabled"


class PointsProductItem(BaseModel):
    id: str
    title: str
    subtitle: str
    description: str
    image_url: str
    points_cost: int
    stock: int
    sort: int
    status: str
    redemption_count: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None


class PointsProductListData(BaseModel):
    list: list[PointsProductItem]
    pagination: PaginationMeta


class PointsRedemptionItem(BaseModel):
    id: str
    user_id: str
    nickname: str
    mobile: str
    product_id: str
    product_title: str
    points_cost: int
    status: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


class PointsRedemptionListData(BaseModel):
    list: list[PointsRedemptionItem]
    pagination: PaginationMeta


class PointsRedemptionStatusUpdateRequest(BaseModel):
    status: str
