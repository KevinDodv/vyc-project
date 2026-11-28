"""Service chứng nhận (OCOP, hữu cơ, ATTP, công bố; TK mục 5).

Mỗi chứng nhận áp dụng cho **đúng một** sản phẩm hoặc đồi (DB chỉ bắt buộc có ít nhất một).
`active_public_for_product()` là cửa cho website: chỉ chứng nhận công khai và còn hiệu lực.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from typing import Any

from django.db import transaction
from django.db.models import Q, QuerySet

from accounts.models import User
from catalog.models import Certificate, CertificateKind, Plot, Product
from core import audit
from core.errors import ApiError
from core.timeutil import today_vn

UPDATABLE_FIELDS = frozenset(
    {
        "kind",
        "number",
        "issuer",
        "issued_on",
        "expires_on",
        "stars",
        "file_url",
        "product_id",
        "plot_id",
        "is_public",
    }
)


@dataclass(frozen=True)
class CertificateCreate:
    kind: str
    number: str
    issuer: str | None = None
    issued_on: date | None = None
    expires_on: date | None = None
    stars: int | None = None
    file_url: str | None = None
    product_id: int | None = None
    plot_id: int | None = None
    is_public: bool = True


def valid_on(on: date | None = None) -> Q:
    """Điều kiện «chưa quá hạn» tại ngày `on` (mặc định hôm nay theo giờ VN)."""
    return Q(expires_on__isnull=True) | Q(expires_on__gte=on or today_vn())


def active_public_for_product(product_id: int, *, on: date | None = None) -> QuerySet[Certificate]:
    """Chứng nhận công khai, còn hiệu lực, gắn trực tiếp với sản phẩm: dùng cho trang web.

    Sắp theo loại rồi số để thứ tự ổn định. Chứng nhận của đồi không nằm trong kết quả này.
    """
    return Certificate.objects.filter(valid_on(on), product_id=product_id, is_public=True).order_by(
        "kind", "number", "id"
    )


def _validate(values: dict[str, Any]) -> None:
    """Kiểm trạng thái đầy đủ của một chứng nhận (đã gộp PATCH)."""
    if (values["product_id"] is None) == (values["plot_id"] is None):
        raise ApiError(
            "CERTIFICATE_TARGET_INVALID",
            "Chọn đúng một nơi áp dụng: sản phẩm hoặc đồi",
            field="product_id",
        )
    issued, expires = values["issued_on"], values["expires_on"]
    if issued is not None and expires is not None and expires < issued:
        raise ApiError(
            "CERTIFICATE_DATES_INVALID",
            "Ngày hết hạn không được trước ngày cấp",
            field="expires_on",
        )
    if values["stars"] is not None and values["kind"] != CertificateKind.OCOP:
        raise ApiError(
            "CERTIFICATE_STARS_INVALID", "Chỉ chứng nhận OCOP mới có số sao", field="stars"
        )
    if (
        values["product_id"] is not None
        and not Product.objects.filter(pk=values["product_id"]).exists()
    ):
        raise ApiError("PRODUCT_INVALID", "Sản phẩm không có", field="product_id")
    if values["plot_id"] is not None and not Plot.objects.filter(pk=values["plot_id"]).exists():
        raise ApiError("PLOT_INVALID", "Đồi quế không có", field="plot_id")


@transaction.atomic
def create_certificate(*, data: CertificateCreate, actor: User) -> Certificate:
    values = asdict(data)
    _validate(values)
    certificate = Certificate.objects.create(**values)
    audit.record(actor, certificate, "CREATE")
    return certificate


@transaction.atomic
def update_certificate(*, certificate_id: int, changes: dict[str, Any], actor: User) -> Certificate:
    """Sửa một phần: chỉ khoá trong `changes`. Không đổi gì thì không ghi audit_log."""
    unknown = set(changes) - UPDATABLE_FIELDS
    if unknown:
        raise ValueError(f"trường không sửa được: {sorted(unknown)}")
    certificate = Certificate.objects.select_for_update().get(pk=certificate_id)
    changes = {k: v for k, v in changes.items() if getattr(certificate, k) != v}
    if not changes:
        return certificate

    before = audit.snapshot(certificate)
    merged = {name: getattr(certificate, name) for name in UPDATABLE_FIELDS} | changes
    _validate(merged)
    for name, value in changes.items():
        setattr(certificate, name, value)
    certificate.save()
    audit.record(actor, certificate, "UPDATE", before=before)
    return certificate
