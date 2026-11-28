"""Router `/api/v1/prices` (TK mục 9: GET cả hai vai, PUT chỉ OWNER).

`GET /prices?date=` trả lưới giá hiệu lực tại ngày đó (mặc định hôm nay, giờ VN): mỗi hạng đang dùng
một ô, kèm `effective_date`. `GET /prices/history` trả lịch sử 30 ngày. `PUT /prices/{date}` ghi giá
các ô được gửi.
"""

from __future__ import annotations

import datetime
from typing import cast

from django.http import HttpRequest
from ninja import Router

from accounts.models import User
from catalog.api.schemas.prices import (
    PriceHistoryDayOut,
    PriceHistoryItemOut,
    PriceSheetIn,
    PriceSheetOut,
)
from catalog.services import prices as service
from core.permissions import ANY_STAFF
from core.timeutil import today_vn

router = Router(tags=["Bảng giá"])


def _actor(request: HttpRequest) -> User:
    return cast(User, request.user)  # RoleAuth đã chắc chắn là người dùng đăng nhập


@router.get("", auth=ANY_STAFF, response=PriceSheetOut, summary="Lưới giá tại một ngày")
def get_prices(request: HttpRequest, date: datetime.date | None = None) -> service.PriceSheet:
    return service.get_sheet(date or today_vn())


@router.get(
    "/history",
    auth=ANY_STAFF,
    response=list[PriceHistoryDayOut],
    summary="Lịch sử giá 30 ngày tính đến ngày chọn",
)
def get_price_history(
    request: HttpRequest, to: datetime.date | None = None
) -> list[PriceHistoryDayOut]:
    days = service.get_history(to=to or today_vn())
    return [
        PriceHistoryDayOut(
            price_date=day.price_date,
            items=[
                PriceHistoryItemOut(
                    grade_id=p.grade_id,
                    buy_price=p.buy_price,
                    sell_price=p.sell_price,
                    updated_by_id=p.updated_by_id,
                )
                for p in day.items
            ],
        )
        for day in days
    ]


@router.put("/{price_date}", response=PriceSheetOut, summary="Lưu giá một ngày")
def put_prices(
    request: HttpRequest, price_date: datetime.date, payload: PriceSheetIn
) -> service.PriceSheet:
    items = [service.PriceInput(**i.model_dump()) for i in payload.items]
    return service.save_sheet(date=price_date, items=items, actor=_actor(request))
