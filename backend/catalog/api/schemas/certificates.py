"""Schema `/api/v1/certificates` (TK mục 5, 9).

`file_url` có thể ra trang truy xuất công khai nên chỉ nhận `/media/...` hoặc `https://...`
(chặn `javascript:`, `data:`, `http:`). Quan hệ ngày và «đúng một đích» kiểm ở service, vì PATCH
phải xét trạng thái sau khi gộp với dòng đang có.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Annotated, Any, ClassVar, Literal

from ninja import Schema
from pydantic import AfterValidator, Field, StringConstraints, model_validator

from core.schemas import require_http_url, require_media_path
from core.timeutil import today_vn

KindLiteral = Literal["OCOP", "ORGANIC", "FOOD_SAFETY", "DECLARATION"]
Number = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
Issuer = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]


def _media_or_https(value: str) -> str:
    if value.startswith("/"):
        return require_media_path(value)
    if not value.startswith("https://"):
        raise ValueError("Đường dẫn file phải bắt đầu bằng /media/ hoặc https://")
    return require_http_url(value)


FileUrl = Annotated[str, Field(max_length=500), AfterValidator(_media_or_https)]


class CertificateIn(Schema):
    kind: KindLiteral
    number: Number
    issuer: Issuer | None = None
    issued_on: date | None = None
    expires_on: date | None = None
    stars: int | None = Field(None, ge=3, le=5)  # OCOP 3-5 sao
    file_url: FileUrl | None = None
    product_id: int | None = None
    plot_id: int | None = None
    is_public: bool = True


class CertificatePatch(Schema):
    """Chỉ đổi trường có trong body. Cột NOT NULL (`_NOT_NULL`) mà gửi `null` thì 400."""

    kind: KindLiteral | None = None
    number: Number | None = None
    issuer: Issuer | None = None
    issued_on: date | None = None
    expires_on: date | None = None
    stars: int | None = Field(None, ge=3, le=5)
    file_url: FileUrl | None = None
    product_id: int | None = None
    plot_id: int | None = None
    is_public: bool | None = None
    _NOT_NULL: ClassVar[frozenset[str]] = frozenset({"kind", "number", "is_public"})

    @model_validator(mode="after")
    def _reject_null_for_required(self) -> CertificatePatch:
        for name in self._NOT_NULL & self.model_fields_set:
            if getattr(self, name) is None:
                raise ValueError(f"{name} không được để trống")
        return self

    def patch_fields(self) -> dict[str, Any]:
        return self.model_dump(exclude_unset=True)


class CertificateOut(Schema):
    id: int
    kind: str
    number: str
    issuer: str | None
    issued_on: date | None
    expires_on: date | None
    stars: int | None
    file_url: str | None
    product_id: int | None
    plot_id: int | None
    is_public: bool
    is_expired: bool  # đã quá ngày hết hạn (theo ngày VN); không có ngày hết hạn thì chưa hết
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def resolve_is_expired(obj: Any) -> bool:
        return obj.expires_on is not None and obj.expires_on < today_vn()
