"""Công thức và thành phần (bảng recipe, recipe_item, TK mục 4).

Một dòng recipe là một phiên bản. Công thức lồng nhau đi qua ingredient: bán thành phẩm
là một ingredient, recipe.output_ingredient trỏ tới công thức làm ra nó.
"""

from __future__ import annotations

from django.db import models
from django.db.models import F, Q

from catalog.models.ingredient import Ingredient
from core.models import TimeStampedModel


class RecipeOutputKind(models.TextChoices):
    PRODUCT = "PRODUCT", "Thành phẩm"
    INTERMEDIATE = "INTERMEDIATE", "Bán thành phẩm"


class RecipeStatus(models.TextChoices):
    DRAFT = "DRAFT", "Nháp"
    ACTIVE = "ACTIVE", "Đang dùng"
    RETIRED = "RETIRED", "Đã thay thế"


class Recipe(TimeStampedModel):
    code = models.TextField()  # QC1, TT1, U-Q, SC-VQH...
    version = models.SmallIntegerField(default=1)
    name = models.TextField()
    output_kind = models.TextField(choices=RecipeOutputKind.choices)
    # Bắt buộc khi INTERMEDIATE (bán thành phẩm làm ra), cấm khi PRODUCT.
    output_ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="recipes",
    )
    base_batch_g = models.DecimalField(max_digits=10, decimal_places=2)  # Σ qty_g (1 dòng/nhóm)
    base_label = models.TextField(null=True, blank=True)  # noqa: DJ001  # 'mẻ 100 ml ≈ 89,72 g'
    cure_min_days = models.SmallIntegerField(default=0)  # 0 = không ủ
    cure_max_days = models.SmallIntegerField(null=True, blank=True)  # tham khảo, không chặn
    # NULL = dùng setting.retain_default_months. Có lưu mẫu hay không do product quyết định.
    retain_months = models.SmallIntegerField(null=True, blank=True)
    status = models.TextField(choices=RecipeStatus.choices, default=RecipeStatus.DRAFT)
    note = models.TextField(null=True, blank=True)  # noqa: DJ001  # các bước thủ công, lưu ý

    class Meta:
        db_table = "recipe"
        constraints = [
            models.UniqueConstraint(fields=["code", "version"], name="recipe_code_version_uniq"),
            # Mỗi code tối đa một phiên bản ACTIVE.
            models.UniqueConstraint(
                fields=["code"],
                condition=Q(status=RecipeStatus.ACTIVE),
                name="recipe_one_active_per_code",
            ),
            models.CheckConstraint(
                condition=Q(output_kind__in=RecipeOutputKind.values),
                name="recipe_output_kind_valid",
            ),
            models.CheckConstraint(
                condition=Q(status__in=RecipeStatus.values), name="recipe_status_valid"
            ),
            models.CheckConstraint(
                condition=(
                    Q(output_kind=RecipeOutputKind.INTERMEDIATE, output_ingredient__isnull=False)
                    | Q(output_kind=RecipeOutputKind.PRODUCT, output_ingredient__isnull=True)
                ),
                name="recipe_output_ingredient_matches_kind",
            ),
            models.CheckConstraint(condition=Q(base_batch_g__gt=0), name="recipe_base_batch_gt_0"),
            models.CheckConstraint(condition=Q(version__gte=1), name="recipe_version_gte_1"),
            models.CheckConstraint(condition=Q(cure_min_days__gte=0), name="recipe_cure_min_gte_0"),
            models.CheckConstraint(
                condition=Q(cure_max_days__isnull=True) | Q(cure_max_days__gte=F("cure_min_days")),
                name="recipe_cure_max_gte_min",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.code} v{self.version}"


class RecipeItem(TimeStampedModel):
    recipe = models.ForeignKey(Recipe, on_delete=models.PROTECT, related_name="items")
    line_no = models.SmallIntegerField()
    # Có thể là bán thành phẩm của công thức khác (lồng nhau).
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.PROTECT, related_name="recipe_items"
    )
    qty_g = models.DecimalField(max_digits=10, decimal_places=2)  # gram trên mẻ chuẩn
    # Các dòng cùng alt_group là phương án thay nhau (TT1 hoặc TT2); lệnh chọn đúng một.
    alt_group = models.SmallIntegerField(null=True, blank=True)
    is_optional = models.BooleanField(default=False)  # bột màu khoáng
    note = models.TextField(null=True, blank=True)  # noqa: DJ001

    class Meta:
        db_table = "recipe_item"
        constraints = [
            models.UniqueConstraint(fields=["recipe", "line_no"], name="recipe_item_line_uniq"),
            models.CheckConstraint(condition=Q(qty_g__gt=0), name="recipe_item_qty_gt_0"),
        ]

    def __str__(self) -> str:
        return f"{self.recipe_id}#{self.line_no}"
