"""Khách hàng: đối tác hoặc kênh trả tiền (bảng customer; TK mục 4)."""

from __future__ import annotations

from django.db import models
from django.db.models import Q

from catalog.models.common import ActiveStatus
from core.models import TimeStampedModel


class CustomerKind(models.TextChoices):
    EXPORTER = "EXPORTER", "DN xuất khẩu"
    AGENT = "AGENT", "Đại lý"
    CORPORATE = "CORPORATE", "Quà tặng DN"
    RETAIL = "RETAIL", "Khách lẻ"
    MARKETPLACE = "MARKETPLACE", "Sàn"


class Customer(TimeStampedModel):
    code = models.TextField(unique=True)  # KH-0007
    name = models.TextField()
    kind = models.TextField(choices=CustomerKind.choices)
    phone = models.TextField(null=True, blank=True)  # noqa: DJ001
    address = models.TextField(null=True, blank=True)  # noqa: DJ001
    status = models.TextField(choices=ActiveStatus.choices, default=ActiveStatus.ACTIVE)

    class Meta:
        db_table = "customer"
        constraints = [
            models.CheckConstraint(
                condition=Q(kind__in=CustomerKind.values), name="customer_kind_valid"
            ),
            models.CheckConstraint(
                condition=Q(status__in=ActiveStatus.values), name="customer_status_valid"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.code} {self.name}"
