"""Phụ liệu và bán thành phẩm, tính theo gram (bảng ingredient, TK mục 4)."""

from __future__ import annotations

from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q
from django.db.models.functions import Length, Upper
from django.db.models.lookups import GreaterThanOrEqual, LessThanOrEqual

from catalog.models.common import ActiveStatus
from core.models import TimeStampedModel


class IngredientKind(models.TextChoices):
    ESSENTIAL_OIL = "ESSENTIAL_OIL", "Tinh dầu"
    SOLVENT = "SOLVENT", "Dung môi"
    WAX = "WAX", "Sáp"
    MINERAL = "MINERAL", "Khoáng"
    BOTANICAL = "BOTANICAL", "Thực vật"
    BLEND = "BLEND", "Hương nền, dung dịch tẩm"
    OTHER = "OTHER", "Khác"


# Mã phụ liệu dùng làm đầu mã lô (BR-20): chữ hoa, số, 1-6 ký tự (TT1, DDT, NUOC).
INGREDIENT_CODE_RE = r"^[A-Z0-9]{1,6}$"


class Ingredient(TimeStampedModel):
    code = models.TextField(  # Q, QM, CAM, TTV, HH, HOI, DPG, SD, SO, TC, TT1, DDT...
        unique=True,
        validators=[
            RegexValidator(INGREDIENT_CODE_RE, "Mã gồm chữ hoa hoặc số, dài 1-6 ký tự"),
        ],
    )
    name = models.TextField()
    kind = models.TextField(choices=IngredientKind.choices)
    # g/ml, chỉ để quy đổi tham khảo; công thức tính theo gram.
    density_g_ml = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    track_stock = models.BooleanField(default=True)  # false: nước sạch, không quản lý lô và tồn
    requires_coa = models.BooleanField(default=False)  # tinh dầu mua ngoài cần phiếu kiểm nghiệm
    # Hạn dùng mặc định của lô tự làm (Q: 24 tháng); lô mua ngoài lấy hạn trên nhãn.
    shelf_life_months = models.SmallIntegerField(null=True, blank=True)
    status = models.TextField(choices=ActiveStatus.choices, default=ActiveStatus.ACTIVE)

    class Meta:
        db_table = "ingredient"
        constraints = [
            models.CheckConstraint(
                condition=Q(kind__in=IngredientKind.values), name="ingredient_kind_valid"
            ),
            models.CheckConstraint(
                condition=Q(status__in=ActiveStatus.values), name="ingredient_status_valid"
            ),
            # Chữ hoa 1-6 ký tự. Tập ký tự cho phép (A-Z, 0-9) do validator ở full_clean kiểm.
            models.CheckConstraint(
                condition=Q(code=Upper("code"))
                & GreaterThanOrEqual(Length("code"), 1)
                & LessThanOrEqual(Length("code"), 6),
                name="ingredient_code_upper_1_6",
            ),
            models.CheckConstraint(
                condition=Q(density_g_ml__isnull=True) | Q(density_g_ml__gt=0),
                name="ingredient_density_gt_0",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.code} {self.name}"
