"""Schema vào/ra của `/api/v1/prices` (backend.md 8, TK mục 5 «Bảng giá», mục 9).

Giá là số nguyên VND/kg. Khoảng giá hợp lệ kiểm ở service để báo lỗi tiếng Việt (`PRICE_NEGATIVE`).
"""

from __future__ import annotations

import datetime

from ninja import Schema


class PriceItemIn(Schema):
    grade_id: int
    buy_price: int
    sell_price: int


class PriceSheetIn(Schema):
    items: list[PriceItemIn]


class PriceCellOut(Schema):
    """Một ô lưới giá. Giá None: hạng chưa từng có giá tới ngày hỏi."""

    grade_id: int
    grade_rank: int
    grade_name: str
    material_id: int
    material_code: str
    material_name: str
    buy_price: int | None
    sell_price: int | None
    effective_date: datetime.date | None  # ngày của dòng giá đang áp dụng (≤ ngày hỏi)


class PriceSheetOut(Schema):
    date: datetime.date
    items: list[PriceCellOut]


class PriceHistoryItemOut(Schema):
    grade_id: int
    buy_price: int
    sell_price: int
    updated_by_id: int


class PriceHistoryDayOut(Schema):
    price_date: datetime.date
    items: list[PriceHistoryItemOut]
