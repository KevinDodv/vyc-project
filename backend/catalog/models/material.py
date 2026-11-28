"""Nguyên vật liệu và hạng (bảng material, grade; TK mục 4)."""

from __future__ import annotations

from django.db import models
from django.db.models import Q

from catalog.models.common import ActiveStatus
from catalog.models.goods import GoodsType
from core.models import TimeStampedModel


class Material(TimeStampedModel):
    """Chỉ 2 bản ghi: VQ Vỏ quế, QV Quế vụn."""

    code = models.TextField(unique=True)
    name = models.TextField()
    goods_type = models.ForeignKey(GoodsType, on_delete=models.PROTECT, related_name="materials")
    image_url = models.TextField(null=True, blank=True)  # noqa: DJ001  # ảnh trên nút bấm
    sort_order = models.IntegerField(default=0)
    status = models.TextField(choices=ActiveStatus.choices, default=ActiveStatus.ACTIVE)

    class Meta:
        db_table = "material"
        constraints = [
            models.CheckConstraint(
                condition=Q(status__in=ActiveStatus.values), name="material_status_valid"
            ),
        ]

    def __str__(self) -> str:
        return self.name


class Grade(TimeStampedModel):
    """Loại 1/2/3 cho mỗi nguyên liệu."""

    material = models.ForeignKey(Material, on_delete=models.PROTECT, related_name="grades")
    rank = models.SmallIntegerField()
    name = models.TextField()  # 'Loại 1'
    status = models.TextField(choices=ActiveStatus.choices, default=ActiveStatus.ACTIVE)

    class Meta:
        db_table = "grade"
        constraints = [
            models.CheckConstraint(condition=Q(rank__gte=1, rank__lte=9), name="grade_rank_1_9"),
            models.CheckConstraint(
                condition=Q(status__in=ActiveStatus.values), name="grade_status_valid"
            ),
            models.UniqueConstraint(fields=["material", "rank"], name="grade_material_rank_uniq"),
        ]

    def __str__(self) -> str:
        return f"{self.material_id}/{self.name}"
