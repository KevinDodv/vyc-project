"""Ngày giờ theo giờ Việt Nam. Mọi so sánh "hôm nay" đi qua đây (backend.md 6.1)."""

from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

from django.utils import timezone

VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")


def now_vn() -> datetime:
    return timezone.now().astimezone(VN_TZ)


def today_vn() -> date:
    return now_vn().date()


def to_vn_date(value: datetime) -> date:
    """Ngày giờ VN của một thời điểm có múi giờ."""
    return value.astimezone(VN_TZ).date()


def period_yymmdd(d: date) -> str:
    """`261120` cho 20/11/2026."""
    return d.strftime("%y%m%d")


def period_yymm(d: date) -> str:
    """`2611` cho tháng 11/2026."""
    return d.strftime("%y%m")
