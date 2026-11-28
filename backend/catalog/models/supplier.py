"""Người bán, đồi quế, nhật ký canh tác (bảng supplier, plot, farm_log; TK mục 4)."""

from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from catalog.models.area import Area, AreaLevel
from catalog.models.common import ActiveStatus
from core.models import TimeStampedModel
from core.timeutil import today_vn

PLANTED_YEAR_MIN = 1950


class SupplierKind(models.TextChoices):
    FAMILY = "FAMILY", "Gia đình"
    FARMER = "FARMER", "Hộ dân"
    TRADER = "TRADER", "Thương lái"


class SupplierStream(models.TextChoices):
    CONTROLLED = "CONTROLLED", "Luồng kiểm soát"
    GENERAL = "GENERAL", "Luồng thường"


class Supplier(TimeStampedModel):
    code = models.TextField(unique=True)  # NCC-CQ-012
    name = models.TextField()
    kind = models.TextField(choices=SupplierKind.choices)
    phone = models.TextField(null=True, blank=True)  # noqa: DJ001
    # FAMILY/FARMER: cấp VILLAGE; TRADER: tối thiểu COMMUNE (xem clean()).
    area = models.ForeignKey(Area, on_delete=models.PROTECT, related_name="suppliers")
    stream = models.TextField(choices=SupplierStream.choices)
    public_consent = models.BooleanField(default=False)  # đồng ý hiện tên trên trang truy xuất
    approved = models.BooleanField(default=True)  # false khi xưởng thêm nhanh (BR-03)
    status = models.TextField(choices=ActiveStatus.choices, default=ActiveStatus.ACTIVE)

    class Meta:
        db_table = "supplier"
        constraints = [
            models.CheckConstraint(
                condition=Q(kind__in=SupplierKind.values), name="supplier_kind_valid"
            ),
            models.CheckConstraint(
                condition=Q(stream__in=SupplierStream.values), name="supplier_stream_valid"
            ),
            models.CheckConstraint(
                condition=Q(status__in=ActiveStatus.values), name="supplier_status_valid"
            ),
            models.CheckConstraint(
                condition=~Q(kind=SupplierKind.TRADER) | Q(stream=SupplierStream.GENERAL),
                name="supplier_trader_general_stream",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.code} {self.name}"

    def clean(self) -> None:
        super().clean()
        if self.area_id is None:
            return
        level = self.area.level
        if self.kind in (SupplierKind.FAMILY, SupplierKind.FARMER):
            if level != AreaLevel.VILLAGE:
                raise ValidationError({"area": "Hộ dân, gia đình phải chọn địa bàn cấp thôn"})
        elif self.kind == SupplierKind.TRADER and level == AreaLevel.PROVINCE:
            raise ValidationError({"area": "Thương lái phải chọn địa bàn từ cấp xã trở xuống"})


class Plot(TimeStampedModel):
    """Đồi quế của một người bán."""

    code = models.TextField(unique=True)  # D-CQ-012-02
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name="plots")
    area = models.ForeignKey(Area, on_delete=models.PROTECT, related_name="plots")  # cấp VILLAGE
    area_ha = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    planted_year = models.SmallIntegerField(null=True, blank=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    photo_urls = models.JSONField(default=list, blank=True)
    is_default = models.BooleanField(default=False)
    status = models.TextField(choices=ActiveStatus.choices, default=ActiveStatus.ACTIVE)

    class Meta:
        db_table = "plot"
        constraints = [
            models.CheckConstraint(
                condition=Q(status__in=ActiveStatus.values), name="plot_status_valid"
            ),
            # Cận trên (năm nay) đổi theo thời gian nên không đặt được trong CHECK: xem clean().
            models.CheckConstraint(
                condition=Q(planted_year__isnull=True)
                | Q(planted_year__gte=PLANTED_YEAR_MIN, planted_year__lte=2100),
                name="plot_planted_year_range",
            ),
            models.CheckConstraint(
                condition=Q(area_ha__isnull=True) | Q(area_ha__gte=0), name="plot_area_ha_gte_0"
            ),
            models.CheckConstraint(
                condition=Q(lat__isnull=True) | Q(lat__gte=-90, lat__lte=90),
                name="plot_lat_range",
            ),
            models.CheckConstraint(
                condition=Q(lng__isnull=True) | Q(lng__gte=-180, lng__lte=180),
                name="plot_lng_range",
            ),
            # Tối đa 1 đồi mặc định mỗi người bán; "đúng 1 khi có ≥ 1 đồi" do service giữ.
            models.UniqueConstraint(
                fields=["supplier"],
                condition=Q(is_default=True),
                name="plot_one_default_per_supplier",
            ),
        ]

    def __str__(self) -> str:
        return self.code

    def clean(self) -> None:
        super().clean()
        if self.area_id is not None and self.area.level != AreaLevel.VILLAGE:
            raise ValidationError({"area": "Đồi quế phải thuộc một thôn"})
        if self.planted_year is not None and not (
            PLANTED_YEAR_MIN <= self.planted_year <= today_vn().year
        ):
            raise ValidationError(
                {"planted_year": f"Năm trồng phải từ {PLANTED_YEAR_MIN} đến năm nay"}
            )


class FarmLog(TimeStampedModel):
    """Nhật ký canh tác (GĐ4; bảng đã có sẵn)."""

    plot = models.ForeignKey(Plot, on_delete=models.PROTECT, related_name="farm_logs")
    log_date = models.DateField()
    activity = models.TextField()
    note = models.TextField(null=True, blank=True)  # noqa: DJ001
    photo_urls = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = "farm_log"
        indexes = [models.Index(fields=["plot", "log_date"], name="farm_log_plot_date_idx")]

    def __str__(self) -> str:
        return f"{self.plot_id} {self.log_date}"
