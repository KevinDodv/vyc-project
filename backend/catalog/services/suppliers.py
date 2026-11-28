"""Service người bán và đồi quế (TK mục 5: dòng Nhà cung cấp, Đồi quế, «Duyệt người bán mới»).

Quy tắc giữ ở đây (API chỉ chuyển schema sang dataclass):
- Thương lái: luồng khoá GENERAL. Hộ dân, gia đình: địa bàn cấp thôn (model `clean()`).
  Luồng CONTROLLED chỉ khi có ít nhất 1 đồi đang dùng, nên người bán mới luôn tạo ở GENERAL.
- WORKSHOP thêm nhanh: approved = false, luồng GENERAL, không đồng ý công khai tên (BR-03).
- Trùng tên + địa bàn chỉ cảnh báo (`notices`), không chặn.
- Đồi: mã D-<xã>-<số NCC>-<stt>; khi có ≥ 1 đồi đang dùng thì đúng 1 đồi mặc định.
- Cha đúng cấp và cấp của area nằm ở `clean()` của model nên mọi lần lưu gọi `full_clean()`.
- URL ảnh chỉ nhận `/media/...` hoặc `https://` (chặn `javascript:`, `data:`).
"""

from __future__ import annotations

import dataclasses
import unicodedata
from collections.abc import Callable
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, NoReturn

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Count, Q, QuerySet

from catalog.models import (
    ActiveStatus,
    Area,
    AreaLevel,
    Plot,
    Supplier,
    SupplierKind,
    SupplierStream,
)
from catalog.services.products import UNSET, _Unset
from core import audit, codes
from core.errors import ApiError, BusinessError
from core.roles import Actor, Role
from core.schemas import require_media_path

DUPLICATE_NOTICE = "SUPPLIER_DUPLICATE"
MAX_PHOTOS = 10

SupplierInUseCheck = Callable[[int], bool]
_supplier_in_use_checks: list[SupplierInUseCheck] = []


def register_supplier_in_use_check(check: SupplierInUseCheck) -> None:
    """Đợt 2 nối vào: `check(supplier_id)` True khi người bán còn lô IN_STOCK/RESERVED (BR-21)."""
    if check not in _supplier_in_use_checks:
        _supplier_in_use_checks.append(check)


def supplier_has_stock(supplier_id: int) -> bool:
    return any(check(supplier_id) for check in _supplier_in_use_checks)


@dataclass(frozen=True)
class SupplierCreate:
    name: str
    kind: str
    area_id: int
    phone: str | None = None
    stream: str = SupplierStream.GENERAL
    public_consent: bool = False


@dataclass(frozen=True)
class SupplierUpdate:
    """Mỗi trường mặc định UNSET: chỉ trường được gửi mới đổi. `phone: None` là xoá số."""

    name: str | _Unset = UNSET
    kind: str | _Unset = UNSET
    phone: str | _Unset | None = UNSET
    area_id: int | _Unset = UNSET
    stream: str | _Unset = UNSET
    public_consent: bool | _Unset = UNSET
    status: str | _Unset = UNSET


@dataclass(frozen=True)
class PlotCreate:
    area_id: int
    area_ha: Decimal | None = None
    planted_year: int | None = None
    lat: Decimal | None = None
    lng: Decimal | None = None
    photo_urls: list[str] = field(default_factory=list)
    is_default: bool = False


@dataclass(frozen=True)
class PlotUpdate:
    area_id: int | _Unset = UNSET
    area_ha: Decimal | _Unset | None = UNSET
    planted_year: int | _Unset | None = UNSET
    lat: Decimal | _Unset | None = UNSET
    lng: Decimal | _Unset | None = UNSET
    photo_urls: list[str] | _Unset = UNSET
    is_default: bool | _Unset = UNSET
    status: str | _Unset = UNSET


@dataclass(frozen=True)
class Notice:
    """Cảnh báo không chặn (đi kèm response của POST/PATCH)."""

    code: str
    message: str
    supplier_ids: list[int]


@dataclass(frozen=True)
class SupplierSaved:
    supplier: Supplier
    notices: list[Notice]


# ----------------------------------------------------------------------------- tiện ích


def fold(text: str) -> str:
    """Bỏ dấu, hạ chữ, gộp khoảng trắng: «Hùng» và «hung» như nhau (tìm không phân biệt dấu)."""
    text = text.replace("đ", "d").replace("Đ", "D")
    decomposed = unicodedata.normalize("NFD", text)
    stripped = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
    return " ".join(stripped.casefold().split())


def require_photo_url(value: str) -> str:
    """Ảnh đồi: `/media/...` hoặc `https://...`. `javascript:`, `data:`, `http:` đều sai."""
    if value.startswith("/"):
        return require_media_path(value)
    if not value.startswith("https://"):
        raise ValueError("Ảnh phải là đường dẫn /media/... hoặc địa chỉ https://")
    if len(value) > 500 or any(ord(ch) < 33 or ord(ch) == 127 for ch in value):
        raise ValueError("Địa chỉ ảnh không hợp lệ")
    if not value.removeprefix("https://").split("/", 1)[0]:
        raise ValueError("Địa chỉ ảnh thiếu tên miền")
    return value


def _raise_validation(exc: ValidationError) -> NoReturn:
    errors = [
        {"field": name, "message": message}
        for name, messages in exc.message_dict.items()
        for message in messages
    ]
    first = errors[0]
    raise ApiError(
        "VALIDATION_ERROR", first["message"], status=400, field=first["field"], errors=errors
    ) from exc


def _full_clean(obj: Supplier | Plot) -> None:
    """`full_clean()` của model (cấp địa bàn, năm trồng); lỗi thành 400 theo trường."""
    try:
        obj.full_clean(validate_unique=False, validate_constraints=False)
    except ValidationError as exc:
        _raise_validation(exc)


def _load_area(area_id: int) -> Area:
    area = Area.objects.select_related("parent").filter(pk=area_id).first()
    if area is None or area.status != ActiveStatus.ACTIVE:
        raise ApiError(
            "AREA_INVALID", "Địa bàn không có hoặc đã ngừng dùng", status=400, field="area_id"
        )
    return area


def _commune_code(area: Area) -> str:
    """Mã xã của địa bàn (thôn thì lấy xã cha) để sinh mã NCC."""
    commune = area.parent if area.level == AreaLevel.VILLAGE and area.parent else area
    return commune.code


def _split_supplier_code(code: str) -> tuple[str, str]:
    """`NCC-CQ-012` thành (`CQ`, `012`): mã đồi bám theo mã người bán, không theo địa bàn."""
    area_code, _, number = code.removeprefix("NCC-").rpartition("-")
    return area_code, number


def area_label(area: Area) -> str:
    """«Thôn 3, Châu Quế»: tên + xã, dùng cho lưới nút và danh sách."""
    return f"{area.name}, {area.parent.name}" if area.parent else area.name


# ----------------------------------------------------------------------------- người bán


def supplier_queryset() -> QuerySet[Supplier]:
    return Supplier.objects.select_related("area__parent").annotate(
        plots_count=Count("plots", filter=Q(plots__status=ActiveStatus.ACTIVE))
    )


def get_supplier(supplier_id: int) -> Supplier:
    return supplier_queryset().get(pk=supplier_id)


def list_suppliers(
    *,
    q: str | None = None,
    recent: int | None = None,
    status: str | None = None,
    approved: bool | None = None,
    kind: str | None = None,
    stream: str | None = None,
    area_id: int | None = None,
) -> QuerySet[Supplier]:
    """`recent=N`: N người bán đang dùng được cập nhật gần nhất (lưới nút trên phiếu nhập)."""
    qs = supplier_queryset()
    if status:
        qs = qs.filter(status=status)
    if approved is not None:
        qs = qs.filter(approved=approved)
    if kind:
        qs = qs.filter(kind=kind)
    if stream:
        qs = qs.filter(stream=stream)
    if area_id is not None:
        qs = qs.filter(area_id=area_id)
    if q and (needle := fold(q)):
        rows = qs.values_list("pk", "name", "code", "phone", "area__name")
        ids = [
            pk
            for pk, name, code, phone, area_name in rows
            if any(needle in fold(value or "") for value in (name, code, phone, area_name))
        ]
        qs = qs.filter(pk__in=ids)
    if recent is not None:
        recent_ids = list(
            qs.filter(status=ActiveStatus.ACTIVE)
            .order_by("-updated_at", "-pk")
            .values_list("pk", flat=True)[:recent]
        )
        return qs.filter(pk__in=recent_ids).order_by("-updated_at", "-pk")
    return qs.order_by("name", "pk")


def _duplicate_notices(supplier: Supplier) -> list[Notice]:
    same_place = Supplier.objects.filter(area_id=supplier.area_id).exclude(pk=supplier.pk)
    needle = fold(supplier.name)
    twins = [s for s in same_place if fold(s.name) == needle]
    if not twins:
        return []
    listing = ", ".join(f"{s.code} {s.name}" for s in twins)
    return [
        Notice(
            DUPLICATE_NOTICE,
            f"Đã có người bán trùng tên ở {area_label(supplier.area)}: {listing}",
            [s.pk for s in twins],
        )
    ]


def _check_stream(supplier: Supplier, *, active_plots: int) -> None:
    if supplier.kind == SupplierKind.TRADER and supplier.stream != SupplierStream.GENERAL:
        raise ApiError(
            "STREAM_LOCKED",
            "Thương lái chỉ có luồng thường (GENERAL)",
            status=400,
            field="stream",
        )
    if supplier.stream == SupplierStream.CONTROLLED and active_plots == 0:
        raise ApiError(
            "STREAM_NEEDS_PLOT",
            "Luồng kiểm soát chỉ chọn được khi người bán có ít nhất 1 đồi quế",
            status=409,
            field="stream",
        )


@transaction.atomic
def create_supplier(*, data: SupplierCreate, actor: Actor) -> SupplierSaved:
    """OWNER: duyệt sẵn. WORKSHOP (thêm nhanh): chờ duyệt, luồng GENERAL, không công khai tên."""
    is_owner = actor.role == Role.OWNER
    area = _load_area(data.area_id)
    supplier = Supplier(
        code="NCC-TMP",  # mã thật cấp sau khi dữ liệu hợp lệ, để lỗi nhập liệu không đốt số
        name=data.name,
        kind=data.kind,
        phone=data.phone,
        area=area,
        stream=data.stream if is_owner else SupplierStream.GENERAL,
        public_consent=data.public_consent if is_owner else False,
        approved=is_owner,
        status=ActiveStatus.ACTIVE,
    )
    _full_clean(supplier)
    _check_stream(supplier, active_plots=0)
    supplier.code = codes.supplier_code(_commune_code(area))
    supplier.save()
    audit.record(actor, supplier, "CREATE")
    return SupplierSaved(get_supplier(supplier.pk), _duplicate_notices(supplier))


@transaction.atomic
def update_supplier(*, supplier_id: int, data: SupplierUpdate, actor: Actor) -> SupplierSaved:
    supplier = Supplier.objects.select_for_update().get(pk=supplier_id)
    changes: dict[str, Any] = {
        f.name: getattr(data, f.name)
        for f in dataclasses.fields(data)
        if getattr(data, f.name) is not UNSET
    }
    # Chỉ giữ trường thật sự khác giá trị hiện tại: không đổi gì thì không ghi audit_log.
    changes = {k: v for k, v in changes.items() if getattr(supplier, k) != v}
    if not changes:
        return SupplierSaved(get_supplier(supplier_id), [])

    before = audit.snapshot(supplier)
    if "area_id" in changes:
        supplier.area = _load_area(changes.pop("area_id"))
    for name, value in changes.items():
        setattr(supplier, name, value)
    _full_clean(supplier)
    if "kind" in changes or "stream" in changes:
        active_plots = supplier.plots.filter(status=ActiveStatus.ACTIVE).count()
        _check_stream(supplier, active_plots=active_plots)
    if changes.get("status") == ActiveStatus.INACTIVE and supplier_has_stock(supplier.pk):
        raise BusinessError(
            "SUPPLIER_IN_USE",
            "Người bán còn lô trong kho, chưa ngừng dùng được",
            rule="BR-21",
            field="status",
        )
    supplier.save()
    audit.record(actor, supplier, "UPDATE", before=before)
    notices = (
        _duplicate_notices(supplier) if {"name", "area_id", "kind"} & set(data_keys(data)) else []
    )
    return SupplierSaved(get_supplier(supplier_id), notices)


def data_keys(data: SupplierUpdate) -> list[str]:
    return [f.name for f in dataclasses.fields(data) if getattr(data, f.name) is not UNSET]


@transaction.atomic
def approve_supplier(*, supplier_id: int, actor: Actor) -> Supplier:
    """Duyệt người bán thêm nhanh. Đã duyệt rồi thì giữ nguyên, không ghi audit_log."""
    supplier = Supplier.objects.select_for_update().get(pk=supplier_id)
    if not supplier.approved:
        before = audit.snapshot(supplier)
        supplier.approved = True
        supplier.save(update_fields=["approved", "updated_at"])
        audit.record(actor, supplier, "UPDATE", before=before, reason="Duyệt người bán")
    return get_supplier(supplier_id)


# ----------------------------------------------------------------------------- đồi quế


def list_plots(supplier_id: int, *, status: str | None = None) -> QuerySet[Plot]:
    Supplier.objects.get(pk=supplier_id)  # 404 khi người bán không có
    qs = Plot.objects.filter(supplier_id=supplier_id).select_related("area__parent")
    if status:
        qs = qs.filter(status=status)
    return qs.order_by("-is_default", "pk")


def get_plot(supplier_id: int, plot_id: int) -> Plot:
    return Plot.objects.select_related("area__parent").get(pk=plot_id, supplier_id=supplier_id)


def _check_photos(urls: list[str]) -> None:
    if len(urls) > MAX_PHOTOS:
        raise ApiError(
            "PHOTO_LIMIT", f"Tối đa {MAX_PHOTOS} ảnh mỗi đồi", status=400, field="photo_urls"
        )
    for url in urls:
        try:
            require_photo_url(url)
        except ValueError as exc:
            raise ApiError("PHOTO_URL_INVALID", str(exc), status=400, field="photo_urls") from exc


def _check_coordinates(lat: Decimal | None, lng: Decimal | None) -> None:
    if (lat is None) != (lng is None):
        raise ApiError(
            "COORDINATES_INCOMPLETE",
            "Toạ độ phải có đủ vĩ độ và kinh độ",
            status=400,
            field="lat" if lat is None else "lng",
        )


def _demote_other_defaults(supplier: Supplier, keep_pk: int | None, actor: Actor) -> None:
    others = supplier.plots.select_for_update().filter(is_default=True)
    if keep_pk is not None:
        others = others.exclude(pk=keep_pk)
    for other in others:
        before = audit.snapshot(other)
        other.is_default = False
        other.save(update_fields=["is_default", "updated_at"])
        audit.record(actor, other, "UPDATE", before=before)


@transaction.atomic
def create_plot(*, supplier_id: int, data: PlotCreate, actor: Actor) -> Plot:
    """Đồi đang dùng đầu tiên tự là mặc định; `is_default=true` chuyển mặc định sang đồi này."""
    supplier = Supplier.objects.select_for_update().get(pk=supplier_id)
    area = _load_area(data.area_id)
    _check_photos(data.photo_urls)
    _check_coordinates(data.lat, data.lng)
    plot = Plot(
        code="D-TMP",  # mã thật cấp sau khi hợp lệ
        supplier=supplier,
        area=area,
        area_ha=data.area_ha,
        planted_year=data.planted_year,
        lat=data.lat,
        lng=data.lng,
        photo_urls=data.photo_urls,
        is_default=False,
        status=ActiveStatus.ACTIVE,
    )
    _full_clean(plot)
    make_default = data.is_default or not supplier.plots.filter(status=ActiveStatus.ACTIVE).exists()
    if make_default:
        _demote_other_defaults(supplier, None, actor)  # phải hạ trước: partial UNIQUE 1 mặc định
    plot.is_default = make_default
    plot.code = codes.plot_code(*_split_supplier_code(supplier.code))
    plot.save()
    audit.record(actor, plot, "CREATE")
    return get_plot(supplier_id, plot.pk)


@transaction.atomic
def update_plot(*, supplier_id: int, plot_id: int, data: PlotUpdate, actor: Actor) -> Plot:
    supplier = Supplier.objects.select_for_update().get(pk=supplier_id)
    plot = Plot.objects.select_for_update().get(pk=plot_id, supplier_id=supplier_id)
    changes: dict[str, Any] = {
        f.name: getattr(data, f.name)
        for f in dataclasses.fields(data)
        if getattr(data, f.name) is not UNSET
    }
    changes = {k: v for k, v in changes.items() if getattr(plot, k) != v}
    if not changes:
        return get_plot(supplier_id, plot_id)

    before = audit.snapshot(plot)
    if "area_id" in changes:
        plot.area = _load_area(changes.pop("area_id"))
    if "photo_urls" in changes:
        _check_photos(changes["photo_urls"])
    for name, value in changes.items():
        setattr(plot, name, value)
    _check_coordinates(plot.lat, plot.lng)
    _full_clean(plot)

    other_active = supplier.plots.filter(status=ActiveStatus.ACTIVE).exclude(pk=plot.pk)
    promote: Plot | None = None
    if plot.status == ActiveStatus.INACTIVE:
        if changes.get("is_default") is True:
            raise ApiError(
                "PLOT_INACTIVE_DEFAULT",
                "Đồi đã ngừng dùng không làm đồi mặc định được",
                status=400,
                field="is_default",
            )
        if "status" in changes:  # vừa chuyển sang ngừng dùng
            if supplier.stream == SupplierStream.CONTROLLED and not other_active.exists():
                raise ApiError(
                    "STREAM_NEEDS_PLOT",
                    "Người bán luồng kiểm soát phải còn ít nhất 1 đồi đang dùng",
                    status=409,
                    field="status",
                )
            if before["is_default"]:
                promote = other_active.order_by("pk").first()
        plot.is_default = False
    else:
        reactivated = "status" in changes
        if changes.get("is_default") is False and before["is_default"] and not reactivated:
            raise ApiError(
                "DEFAULT_PLOT_REQUIRED",
                "Phải có đúng 1 đồi mặc định: hãy chọn đồi khác làm mặc định",
                status=409,
                field="is_default",
            )
        if reactivated and not other_active.exists():
            plot.is_default = True  # đồi duy nhất đang dùng thì là đồi mặc định
        if plot.is_default and not before["is_default"]:
            _demote_other_defaults(supplier, plot.pk, actor)

    plot.save()
    audit.record(actor, plot, "UPDATE", before=before)
    if promote is not None:
        promoted_before = audit.snapshot(promote)
        promote.is_default = True
        promote.save(update_fields=["is_default", "updated_at"])
        audit.record(actor, promote, "UPDATE", before=promoted_before)
    return get_plot(supplier_id, plot_id)
