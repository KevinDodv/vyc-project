"""Địa bàn hành chính: Tỉnh > Xã > Thôn (bảng area, TK mục 4)."""

from __future__ import annotations

import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q

from catalog.models.common import ActiveStatus
from core.models import TimeStampedModel


class AreaLevel(models.TextChoices):
    PROVINCE = "PROVINCE", "Tỉnh"
    COMMUNE = "COMMUNE", "Xã"
    VILLAGE = "VILLAGE", "Thôn"


# Cấp của cha đúng với từng cấp (TK mục 5: Xã → Tỉnh, Thôn → Xã).
PARENT_LEVEL = {
    AreaLevel.COMMUNE: AreaLevel.PROVINCE,
    AreaLevel.VILLAGE: AreaLevel.COMMUNE,
}


class Area(TimeStampedModel):
    code = models.TextField(unique=True)
    level = models.TextField(choices=AreaLevel.choices)
    name = models.TextField()  # 'Lào Cai', 'Châu Quế', 'Thôn 3'
    # NULL chỉ với PROVINCE. PROTECT: không xoá cha khi còn con.
    parent = models.ForeignKey(
        "self", on_delete=models.PROTECT, null=True, blank=True, related_name="children"
    )
    former_name = models.TextField(null=True, blank=True)  # noqa: DJ001  # 'huyện Văn Yên, tỉnh Yên Bái'
    valid_from = models.DateField(default=datetime.date(2025, 7, 1))
    valid_to = models.DateField(null=True, blank=True)
    status = models.TextField(choices=ActiveStatus.choices, default=ActiveStatus.ACTIVE)

    class Meta:
        db_table = "area"
        constraints = [
            models.CheckConstraint(
                condition=Q(level__in=AreaLevel.values), name="area_level_valid"
            ),
            models.CheckConstraint(
                condition=Q(status__in=ActiveStatus.values), name="area_status_valid"
            ),
            # Tỉnh không có cha; xã, thôn bắt buộc có cha. Cấp của cha: xem clean().
            models.CheckConstraint(
                condition=(Q(level=AreaLevel.PROVINCE, parent__isnull=True))
                | (~Q(level=AreaLevel.PROVINCE) & Q(parent__isnull=False)),
                name="area_parent_matches_level",
            ),
            models.CheckConstraint(
                condition=Q(valid_to__isnull=True) | Q(valid_to__gte=F("valid_from")),
                name="area_valid_range",
            ),
            # Không trùng tên trong cùng cha (TK mục 5); tỉnh (không cha) không trùng tên nhau.
            models.UniqueConstraint(
                fields=["parent", "name"],
                condition=Q(parent__isnull=False),
                name="area_parent_name_uniq",
            ),
            models.UniqueConstraint(
                fields=["name"],
                condition=Q(parent__isnull=True),
                name="area_province_name_uniq",
            ),
        ]

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        """Cha đúng cấp. CHECK ở DB chỉ bắt được 'có/không có cha', không so được cấp của cha."""
        super().clean()
        if self.level == AreaLevel.PROVINCE:
            if self.parent_id is not None:
                raise ValidationError({"parent": "Tỉnh không có cấp trên"})
            return
        expected = PARENT_LEVEL.get(AreaLevel(self.level)) if self.level in AreaLevel else None
        if expected is None:
            return
        if self.parent_id is None:
            raise ValidationError({"parent": "Phải chọn cấp trên"})
        if self.parent is not None and self.parent.level != expected:
            raise ValidationError(
                {"parent": f"Cấp trên của {AreaLevel(self.level).label} phải là {expected.label}"}
            )
