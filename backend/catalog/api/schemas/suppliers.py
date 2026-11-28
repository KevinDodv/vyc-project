"""Schema vào/ra của `/api/v1/suppliers` và `/suppliers/{id}/plots` (TK mục 5, 9).

Toạ độ đồi nhận hai cách: `lat` + `lng` (số), hoặc `coordinates` là chuỗi dán từ Google Maps
(`21.0285791, 105.8541934`); chuỗi được tách thành `lat`, `lng` ngay ở schema.
"""

from __future__ import annotations

import re
from datetime import datetime
from decimal import Decimal
from typing import Annotated, Any, ClassVar, Literal

from ninja import Schema
from pydantic import AfterValidator, Field, StringConstraints, model_validator

from catalog.services.suppliers import MAX_PHOTOS, require_photo_url

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
Phone = Annotated[str, StringConstraints(strip_whitespace=True, max_length=30)]
PhotoUrl = Annotated[str, AfterValidator(require_photo_url)]
SupplierKindLiteral = Literal["FAMILY", "FARMER", "TRADER"]
SupplierStreamLiteral = Literal["CONTROLLED", "GENERAL"]
ActiveStatusLiteral = Literal["ACTIVE", "INACTIVE"]

_COORDINATES = re.compile(r"^\s*(-?\d{1,3}(?:\.\d+)?)\s*[,;\s]\s*(-?\d{1,3}(?:\.\d+)?)\s*$")
_SIX_PLACES = Decimal("0.000001")


def _quantize(value: Decimal | None) -> Decimal | None:
    return None if value is None else value.quantize(_SIX_PLACES)


def parse_coordinates(text: str) -> tuple[Decimal, Decimal]:
    """«21.0285791, 105.8541934» (dán từ Google Maps) thành (lat, lng), làm tròn 6 chữ số."""
    match = _COORDINATES.match(text)
    if match is None:
        raise ValueError("Toạ độ phải có dạng «vĩ độ, kinh độ», ví dụ 21.028579, 105.854193")
    return Decimal(match.group(1)).quantize(_SIX_PLACES), Decimal(match.group(2)).quantize(
        _SIX_PLACES
    )


def _check_ranges(lat: Decimal | None, lng: Decimal | None) -> None:
    if lat is not None and not -90 <= lat <= 90:
        raise ValueError("Vĩ độ phải từ -90 đến 90")
    if lng is not None and not -180 <= lng <= 180:
        raise ValueError("Kinh độ phải từ -180 đến 180")


# ----------------------------------------------------------------------------- người bán


class SupplierIn(Schema):
    """WORKSHOP cũng gọi được (thêm nhanh): khi đó `stream`, `public_consent` bị bỏ qua
    (luôn GENERAL và false) và người bán nằm ở trạng thái chờ duyệt."""

    name: Name
    kind: SupplierKindLiteral
    area_id: int
    phone: Phone | None = None
    stream: SupplierStreamLiteral = "GENERAL"
    public_consent: bool = False


class SupplierPatch(Schema):
    name: Name | None = None
    kind: SupplierKindLiteral | None = None
    phone: Phone | None = None
    area_id: int | None = None
    stream: SupplierStreamLiteral | None = None
    public_consent: bool | None = None
    status: ActiveStatusLiteral | None = None
    # Cột NOT NULL: gửi `null` là sai (khác phone, nơi null có nghĩa «xoá số»).
    _NOT_NULL: ClassVar[frozenset[str]] = frozenset(
        {"name", "kind", "area_id", "stream", "public_consent", "status"}
    )

    @model_validator(mode="after")
    def _reject_null_for_required(self) -> SupplierPatch:
        for name in self._NOT_NULL & self.model_fields_set:
            if getattr(self, name) is None:
                raise ValueError(f"{name} không được để trống")
        return self

    def patch_fields(self) -> dict[str, Any]:
        return self.model_dump(exclude_unset=True)


class SupplierOut(Schema):
    id: int
    code: str
    name: str
    kind: str
    phone: str | None
    area_id: int
    area_name: str  # «Thôn 3, Châu Quế»: chữ trên nút của lưới người bán
    stream: str
    public_consent: bool
    approved: bool
    status: str
    plots_count: int  # đồi đang dùng
    created_at: datetime
    updated_at: datetime


class NoticeOut(Schema):
    """Cảnh báo không chặn, ví dụ `SUPPLIER_DUPLICATE` khi trùng tên + địa bàn."""

    code: str
    message: str
    supplier_ids: list[int]


class SupplierSavedOut(SupplierOut):
    notices: list[NoticeOut] = Field(default_factory=list)


# ----------------------------------------------------------------------------- đồi quế


class PlotIn(Schema):
    area_id: int  # cấp thôn
    area_ha: Decimal | None = Field(None, ge=0, max_digits=6, decimal_places=2)
    planted_year: int | None = Field(None, ge=1950, le=2100)  # cận trên «năm nay» kiểm ở service
    lat: Decimal | None = None
    lng: Decimal | None = None
    coordinates: str | None = Field(None, max_length=60)
    photo_urls: list[PhotoUrl] = Field(default_factory=list, max_length=MAX_PHOTOS)
    is_default: bool = False

    @model_validator(mode="after")
    def _resolve_coordinates(self) -> PlotIn:
        if self.coordinates is not None:
            if self.lat is not None or self.lng is not None:
                raise ValueError("Chỉ gửi coordinates hoặc lat + lng, không gửi cả hai")
            self.lat, self.lng = parse_coordinates(self.coordinates)
            self.coordinates = None
        self.lat, self.lng = _quantize(self.lat), _quantize(self.lng)
        _check_ranges(self.lat, self.lng)
        return self


class PlotPatch(Schema):
    """Chỉ đổi trường có trong body. `lat` + `lng` (hoặc `coordinates`) gửi `null` là xoá toạ độ."""

    area_id: int | None = None
    area_ha: Decimal | None = Field(None, ge=0, max_digits=6, decimal_places=2)
    planted_year: int | None = Field(None, ge=1950, le=2100)
    lat: Decimal | None = None
    lng: Decimal | None = None
    coordinates: str | None = Field(None, max_length=60)
    photo_urls: list[PhotoUrl] | None = Field(None, max_length=MAX_PHOTOS)
    is_default: bool | None = None
    status: ActiveStatusLiteral | None = None
    _NOT_NULL: ClassVar[frozenset[str]] = frozenset(
        {"area_id", "photo_urls", "is_default", "status"}
    )

    @model_validator(mode="after")
    def _validate(self) -> PlotPatch:
        for name in self._NOT_NULL & self.model_fields_set:
            if getattr(self, name) is None:
                raise ValueError(f"{name} không được để trống")
        if "coordinates" in self.model_fields_set:
            if (
                self.lat is not None
                or self.lng is not None
                or {"lat", "lng"} & self.model_fields_set
            ):
                raise ValueError("Chỉ gửi coordinates hoặc lat + lng, không gửi cả hai")
            if self.coordinates is None:
                self.lat = self.lng = None
            else:
                self.lat, self.lng = parse_coordinates(self.coordinates)
            self.model_fields_set.update({"lat", "lng"})
        self.lat, self.lng = _quantize(self.lat), _quantize(self.lng)
        _check_ranges(self.lat, self.lng)
        return self

    def patch_fields(self) -> dict[str, Any]:
        fields = self.model_dump(exclude_unset=True)
        fields.pop("coordinates", None)
        return fields


class PlotOut(Schema):
    id: int
    code: str
    supplier_id: int
    area_id: int
    area_name: str
    area_ha: float | None
    planted_year: int | None
    lat: float | None
    lng: float | None
    photo_urls: list[str]
    is_default: bool
    status: str
    created_at: datetime
    updated_at: datetime
