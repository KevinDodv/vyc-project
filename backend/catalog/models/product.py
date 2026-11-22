"""Sản phẩm thành phẩm và chuyển hướng slug cũ (bảng product, slug_redirect; TK mục 4)."""

from __future__ import annotations

from django.db import models
from django.db.models import Q

from catalog.models.goods import GoodsType
from core.models import TimeStampedModel


class ProductStatus(models.TextChoices):
    DRAFT = "DRAFT", "Nháp"
    PUBLISHED = "PUBLISHED", "Đã đăng"
    HIDDEN = "HIDDEN", "Ẩn"


class Product(TimeStampedModel):
    sku = models.TextField(unique=True)  # TD10
    name = models.TextField()
    slug = models.TextField(unique=True)
    goods_type = models.ForeignKey(GoodsType, on_delete=models.PROTECT, related_name="products")
    size_label = models.TextField()  # '10 ml', '50 g'
    unit = models.TextField()  # 'chai', 'túi', 'hộp'
    shelf_life_months = models.SmallIntegerField(null=True, blank=True)
    requires_retention_sample = models.BooleanField(default=False)
    recipe_code = models.TextField(null=True, blank=True)  # noqa: DJ001
    retail_price = models.BigIntegerField(null=True, blank=True)
    short_desc = models.TextField(null=True, blank=True)  # noqa: DJ001
    story_md = models.TextField(null=True, blank=True)  # noqa: DJ001
    usage_md = models.TextField(null=True, blank=True)  # noqa: DJ001
    seo_title = models.CharField(max_length=70, null=True, blank=True)  # noqa: DJ001
    seo_description = models.CharField(max_length=170, null=True, blank=True)  # noqa: DJ001
    # [{url, alt, key, w, h, widths}] (backend.md 6.5)
    images = models.JSONField(default=list)
    # [{channel, url}]
    buy_links = models.JSONField(default=list)
    serial_tracked = models.BooleanField(default=True)
    status = models.TextField(choices=ProductStatus.choices, default=ProductStatus.DRAFT)
    # null = không nổi bật; 1 đứng đầu. Không UNIQUE: trùng hạng thì sắp phụ theo updated_at.
    featured_rank = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        db_table = "product"
        constraints = [
            models.CheckConstraint(
                condition=Q(status__in=ProductStatus.values), name="product_status_valid"
            ),
            models.CheckConstraint(
                condition=Q(featured_rank__isnull=True) | Q(featured_rank__gt=0),
                name="product_featured_rank_gt_0",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.sku} {self.name}"


class SlugRedirect(models.Model):
    """301 khi đổi slug sản phẩm. Django không tự chuyển hướng; Astro so slug trong DTO."""

    old_slug = models.TextField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="slug_redirects")

    class Meta:
        db_table = "slug_redirect"

    def __str__(self) -> str:
        return f"{self.old_slug} -> {self.product_id}"
