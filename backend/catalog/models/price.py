"""Bảng giá theo hạng, theo ngày (bảng price; TK mục 4)."""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.db.models import Q

from catalog.models.material import Grade
from core.models import TimeStampedModel


class Price(TimeStampedModel):
    grade = models.ForeignKey(Grade, on_delete=models.PROTECT, related_name="prices")
    price_date = models.DateField()
    buy_price = models.BigIntegerField()  # VND/kg
    sell_price = models.BigIntegerField()  # VND/kg
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+"
    )

    class Meta:
        db_table = "price"
        constraints = [
            models.CheckConstraint(condition=Q(buy_price__gte=0), name="price_buy_price_gte_0"),
            models.CheckConstraint(condition=Q(sell_price__gte=0), name="price_sell_price_gte_0"),
            models.UniqueConstraint(fields=["grade", "price_date"], name="price_grade_date_uniq"),
        ]
        indexes = [models.Index(fields=["price_date"], name="price_price_date_idx")]

    def __str__(self) -> str:
        return f"{self.grade_id} {self.price_date}"
