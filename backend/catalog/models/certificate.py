"""Chứng nhận OCOP, hữu cơ, ATTP, công bố sản phẩm (bảng certificate; TK mục 4)."""

from __future__ import annotations

from django.db import models
from django.db.models import F, Q

from catalog.models.product import Product
from catalog.models.supplier import Plot
from core.models import TimeStampedModel


class CertificateKind(models.TextChoices):
    OCOP = "OCOP", "OCOP"
    ORGANIC = "ORGANIC", "Hữu cơ"
    FOOD_SAFETY = "FOOD_SAFETY", "ATTP"
    DECLARATION = "DECLARATION", "Công bố sản phẩm"


class Certificate(TimeStampedModel):
    kind = models.TextField(choices=CertificateKind.choices)
    number = models.TextField()
    issuer = models.TextField(null=True, blank=True)  # noqa: DJ001
    issued_on = models.DateField(null=True, blank=True)
    expires_on = models.DateField(null=True, blank=True)
    stars = models.SmallIntegerField(null=True, blank=True)  # OCOP 3-5 sao
    file_url = models.TextField(null=True, blank=True)  # noqa: DJ001
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, null=True, blank=True, related_name="certificates"
    )
    plot = models.ForeignKey(
        Plot, on_delete=models.PROTECT, null=True, blank=True, related_name="certificates"
    )
    is_public = models.BooleanField(default=True)

    class Meta:
        db_table = "certificate"
        constraints = [
            models.CheckConstraint(
                condition=Q(kind__in=CertificateKind.values), name="certificate_kind_valid"
            ),
            models.CheckConstraint(
                condition=Q(product__isnull=False) | Q(plot__isnull=False),
                name="certificate_has_target",
            ),
            # TK mục 5: hết hạn ≥ ngày cấp.
            models.CheckConstraint(
                condition=Q(issued_on__isnull=True)
                | Q(expires_on__isnull=True)
                | Q(expires_on__gte=F("issued_on")),
                name="certificate_expires_after_issued",
            ),
            models.CheckConstraint(
                condition=Q(stars__isnull=True) | Q(stars__gte=3, stars__lte=5),
                name="certificate_stars_3_5",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.kind} {self.number}"
