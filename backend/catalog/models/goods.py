"""Loại hàng hóa (bảng goods_type, TK mục 4)."""

from __future__ import annotations

from django.db import models
from django.db.models import Q


class GoodsGroup(models.TextChoices):
    MATERIAL = "MATERIAL", "Nguyên liệu"
    PRODUCT = "PRODUCT", "Thành phẩm"


class GoodsTypeStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Đang dùng"
    INACTIVE = "INACTIVE", "Ngừng dùng"


class GoodsType(models.Model):
    code = models.TextField(unique=True)
    name = models.TextField()
    grp = models.TextField(choices=GoodsGroup.choices)
    # true: chặn đăng bán khi chưa có giấy tờ ATTP (BR-14, làm ở GĐ3).
    is_food = models.BooleanField(default=False)
    status = models.TextField(choices=GoodsTypeStatus.choices, default=GoodsTypeStatus.ACTIVE)

    class Meta:
        db_table = "goods_type"
        constraints = [
            models.CheckConstraint(
                condition=Q(grp__in=GoodsGroup.values), name="goods_type_grp_valid"
            ),
            models.CheckConstraint(
                condition=Q(status__in=GoodsTypeStatus.values), name="goods_type_status_valid"
            ),
        ]

    def __str__(self) -> str:
        return self.name
