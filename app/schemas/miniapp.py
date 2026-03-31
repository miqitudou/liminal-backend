from datetime import datetime

from pydantic import BaseModel, Field


class MiniappSimpleLoginRequest(BaseModel):
    code: str | None = None
    mobile: str | None = None
    nickname: str | None = None
    avatar_url: str | None = None


class MiniappOrderItemInput(BaseModel):
    goodsId: str | int
    specId: str | int
    quantity: int
    bookingDate: str
    pickupSlot: str


class MiniappCreateOrderRequest(BaseModel):
    items: list[MiniappOrderItemInput] = Field(default_factory=list)
    status: str = "pending_payment"
    contactName: str
    mobile: str
    bookingDate: str
    pickupSlot: str
    remark: str = ""


class MiniappOrderActionResponse(BaseModel):
    orderNo: str
    status: str
    paymentStatus: str


class MiniappOrdersCountResponse(BaseModel):
    all: int
    pending_payment: int
    paid: int
    baking: int
    ready_pickup: int
    finished: int
    cancelled: int


class MiniappLoginData(BaseModel):
    accessToken: str
    expiresIn: int
    userInfo: dict
    isNewUser: bool


class MiniappHomeData(BaseModel):
    banners: list[dict]
    categories: list[dict]
    recommends: list[dict]
    goods: list[dict]
    storeInfo: dict


class MiniappOrderListData(BaseModel):
    orders: list[dict]


class MiniappUserMeData(BaseModel):
    userInfo: dict


class MiniappGoodsListData(BaseModel):
    list: list[dict]
