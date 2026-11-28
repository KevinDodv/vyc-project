"""Service bảng giá theo hạng, theo ngày (TK mục 5 «Bảng giá», mục 9, BR-04).

`get_sheet(date)` trả mỗi hạng đang dùng một ô: giá của đúng ngày đó, hoặc của ngày gần nhất trước
đó (kèm `effective_date`); chưa từng có giá thì các trường giá là None. `save_sheet` chỉ ghi các ô
được gửi (lưới mở sẵn giá cũ, người dùng chỉ sửa ô đổi), mỗi ô một dòng audit_log.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass

from django.db import IntegrityError, transaction

from accounts.models import User
from catalog.models import ActiveStatus, Grade, Price
from core import audit
from core.errors import ApiError

HISTORY_DAYS = 30
# Giá VND/kg: chặn số vô lý, và nằm gọn trong bigint.
MAX_PRICE = 1_000_000_000


@dataclass(frozen=True)
class PriceInput:
    grade_id: int
    buy_price: int
    sell_price: int


@dataclass(frozen=True)
class PriceCell:
    """Một ô của lưới giá: hạng + giá hiệu lực tại ngày hỏi."""

    grade_id: int
    grade_rank: int
    grade_name: str
    material_id: int
    material_code: str
    material_name: str
    buy_price: int | None
    sell_price: int | None
    effective_date: datetime.date | None


@dataclass(frozen=True)
class PriceSheet:
    date: datetime.date
    items: list[PriceCell]


@dataclass(frozen=True)
class PriceHistoryDay:
    price_date: datetime.date
    items: list[Price]


def _active_grades() -> list[Grade]:
    return list(
        Grade.objects.select_related("material")
        .filter(status=ActiveStatus.ACTIVE, material__status=ActiveStatus.ACTIVE)
        .order_by("material__sort_order", "material_id", "rank")
    )


def get_sheet(date: datetime.date) -> PriceSheet:
    """Giá hiệu lực tại `date` cho mọi hạng đang dùng."""
    grades = _active_grades()
    wanted = {g.pk for g in grades}
    latest: dict[int, Price] = {}
    # Mới nhất trước: dòng đầu tiên gặp của mỗi hạng là giá hiệu lực. Dừng khi đủ mọi hạng.
    prices = Price.objects.filter(grade_id__in=wanted, price_date__lte=date)
    for row in prices.order_by("-price_date").iterator():
        latest.setdefault(row.grade_id, row)
        if len(latest) == len(wanted):
            break
    cells = []
    for grade in grades:
        price = latest.get(grade.pk)
        cells.append(
            PriceCell(
                grade_id=grade.pk,
                grade_rank=grade.rank,
                grade_name=grade.name,
                material_id=grade.material_id,
                material_code=grade.material.code,
                material_name=grade.material.name,
                buy_price=price.buy_price if price else None,
                sell_price=price.sell_price if price else None,
                effective_date=price.price_date if price else None,
            )
        )
    return PriceSheet(date=date, items=cells)


def get_history(*, to: datetime.date, days: int = HISTORY_DAYS) -> list[PriceHistoryDay]:
    """Các ngày có nhập giá trong `days` ngày tính đến `to` (gồm cả `to`), ngày mới nhất trước."""
    start = to - datetime.timedelta(days=days - 1)
    rows = (
        Price.objects.filter(price_date__gte=start, price_date__lte=to)
        .select_related("grade", "grade__material")
        .order_by("-price_date", "grade__material__sort_order", "grade__material_id", "grade__rank")
    )
    out: list[PriceHistoryDay] = []
    for row in rows:
        if not out or out[-1].price_date != row.price_date:
            out.append(PriceHistoryDay(price_date=row.price_date, items=[]))
        out[-1].items.append(row)
    return out


def _check_inputs(items: list[PriceInput]) -> None:
    if not items:
        raise ApiError("PRICE_EMPTY", "Chưa có giá nào để lưu", status=400, field="items")
    ids = [item.grade_id for item in items]
    if len(set(ids)) != len(ids):
        raise ApiError("PRICE_GRADE_DUPLICATE", "Một hạng xuất hiện hai lần", field="items")
    for item in items:
        for label, value in (("mua", item.buy_price), ("bán", item.sell_price)):
            if value < 0:
                raise ApiError(
                    "PRICE_NEGATIVE", f"Giá {label} không được âm", status=400, field="items"
                )
            if value > MAX_PRICE:
                raise ApiError(
                    "PRICE_TOO_LARGE",
                    f"Giá {label} quá lớn (tối đa {MAX_PRICE:,} đ/kg)".replace(",", "."),
                    status=400,
                    field="items",
                )
    grades = {g.pk: g for g in Grade.objects.select_related("material").filter(pk__in=ids)}
    for grade_id in ids:
        grade = grades.get(grade_id)
        if (
            grade is None
            or grade.status != ActiveStatus.ACTIVE
            or grade.material.status != ActiveStatus.ACTIVE
        ):
            raise ApiError(
                "PRICE_GRADE_INVALID",
                "Hạng không có hoặc đã ngừng dùng",
                status=400,
                field="items",
                grade_id=grade_id,
            )


def _save_cell(item: PriceInput, date: datetime.date, actor: User) -> None:
    price = (
        Price.objects.select_for_update().filter(grade_id=item.grade_id, price_date=date).first()
    )
    if price is None:
        price = Price(
            grade_id=item.grade_id,
            price_date=date,
            buy_price=item.buy_price,
            sell_price=item.sell_price,
            updated_by=actor,
        )
        try:
            with transaction.atomic():  # savepoint: hai request lưu cùng ô cùng lúc
                price.save()
        except IntegrityError:
            price = Price.objects.select_for_update().get(grade_id=item.grade_id, price_date=date)
        else:
            audit.record(actor, price, "CREATE")
            return
    if (price.buy_price, price.sell_price) == (item.buy_price, item.sell_price):
        return  # không đổi: không ghi audit_log
    before = audit.snapshot(price)
    price.buy_price = item.buy_price
    price.sell_price = item.sell_price
    price.updated_by = actor
    price.save()
    audit.record(actor, price, "UPDATE", before=before)


@transaction.atomic
def save_sheet(*, date: datetime.date, items: list[PriceInput], actor: User) -> PriceSheet:
    """Ghi (thêm hoặc sửa) giá của `date` cho các hạng được gửi, rồi trả lưới giá ngày đó."""
    _check_inputs(items)
    for item in items:
        _save_cell(item, date, actor)
    return get_sheet(date)
