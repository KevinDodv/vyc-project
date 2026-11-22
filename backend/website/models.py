"""Model của PH3: trang tĩnh (bảng site_page, TK mục 4)."""

from __future__ import annotations

from django.db import models
from django.db.models import Q

from core.models import TimeStampedModel


class PageStatus(models.TextChoices):
    DRAFT = "DRAFT", "Nháp"
    PUBLISHED = "PUBLISHED", "Đã đăng"


class SitePage(TimeStampedModel):
    slug = models.TextField(unique=True)
    title = models.TextField()
    body_md = models.TextField()
    seo_title = models.CharField(max_length=70, null=True, blank=True)  # noqa: DJ001
    seo_description = models.CharField(max_length=170, null=True, blank=True)  # noqa: DJ001
    og_image_url = models.TextField(null=True, blank=True)  # noqa: DJ001
    status = models.TextField(choices=PageStatus.choices, default=PageStatus.DRAFT)

    class Meta:
        db_table = "site_page"
        constraints = [
            models.CheckConstraint(
                condition=Q(status__in=PageStatus.values), name="site_page_status_valid"
            ),
        ]

    def __str__(self) -> str:
        return self.slug
