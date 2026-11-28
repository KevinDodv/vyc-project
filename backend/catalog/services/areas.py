"""Service địa bàn: tạo, sửa, ngừng dùng, dựng cây Tỉnh > Xã > Thôn (TK mục 5, dòng «Địa bàn»).

Cha đúng cấp (Xã → Tỉnh, Thôn → Xã) chỉ kiểm được ở `Area.clean()`, nên mọi lần ghi đi qua
`full_clean()` ở đây. Không trùng tên trong cùng cha và không trùng mã: kiểm trước để báo 409 tiếng
Việt; DB vẫn có UNIQUE làm chốt chặn khi hai request chạy cùng lúc.
"""

from __future__ import annotations

import dataclasses
import datetime
from dataclasses import dataclass

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from accounts.models import User
from catalog.models import ActiveStatus, Area
from catalog.services.products import UNSET, _Unset
from core import audit
from core.errors import ApiError

# Tên trường của model → tên trường ở API (khoá ngoại đi theo `<tên>_id`).
_FIELD_ALIASES = {"parent": "parent_id", "__all__": "__all__"}


@dataclass(frozen=True)
class AreaCreate:
    code: str
    level: str
    name: str
    parent_id: int | None = None
    former_name: str | None = None
    valid_from: datetime.date | None = None  # None: lấy mặc định của model
    valid_to: datetime.date | None = None


@dataclass(frozen=True)
class AreaUpdate:
    """Cấp (`level`) và mã (`code`) không đổi được sau khi tạo."""

    name: str | _Unset = UNSET
    parent_id: int | _Unset | None = UNSET
    former_name: str | _Unset | None = UNSET
    valid_from: datetime.date | _Unset = UNSET
    valid_to: datetime.date | _Unset | None = UNSET
    status: str | _Unset = UNSET


@dataclass
class AreaTreeNode:
    area: Area
    children: list[AreaTreeNode] = dataclasses.field(default_factory=list)


def _other_than(area_id: int | None) -> int:
    """Id để `.exclude(...)`: tạo mới (None) thì không loại dòng nào (bigserial bắt đầu từ 1)."""
    return area_id if area_id is not None else 0


def _check_unique(
    *, code: str | None, name: str, parent_id: int | None, area_id: int | None
) -> None:
    others = Area.objects.exclude(pk=_other_than(area_id))
    if code is not None and others.filter(code=code).exists():
        raise ApiError("AREA_CODE_TAKEN", f"Mã địa bàn {code} đã có", status=409, field="code")
    if others.filter(parent_id=parent_id, name=name).exists():
        where = "trong cùng cấp trên" if parent_id is not None else "giữa các tỉnh"
        raise ApiError("AREA_NAME_TAKEN", f"Tên «{name}» đã có {where}", status=409, field="name")


def _full_clean(area: Area) -> None:
    """Chạy `full_clean()` rồi đổi lỗi đầu tiên thành 400 theo trường (`details.field`)."""
    try:
        area.full_clean(validate_unique=False, validate_constraints=False)
    except ValidationError as exc:
        field, messages = next(iter(exc.message_dict.items()))
        raise ApiError(
            "AREA_INVALID", messages[0], status=400, field=_FIELD_ALIASES.get(field, field)
        ) from exc


def _check_parent_usable(parent_id: int | None) -> None:
    if parent_id is None:
        return
    parent = Area.objects.filter(pk=parent_id).first()
    if parent is None:
        raise ApiError("AREA_PARENT_INVALID", "Cấp trên không có", status=400, field="parent_id")
    if parent.status != ActiveStatus.ACTIVE:
        raise ApiError(
            "AREA_PARENT_INACTIVE", "Cấp trên đã ngừng dùng", status=400, field="parent_id"
        )


def _check_range(valid_from: datetime.date, valid_to: datetime.date | None) -> None:
    if valid_to is not None and valid_to < valid_from:
        raise ApiError(
            "AREA_RANGE_INVALID", "Ngày hết hiệu lực phải sau ngày bắt đầu", status=400,
            field="valid_to",
        )  # fmt: skip


def list_tree() -> list[AreaTreeNode]:
    """Cả bảng địa bàn thành cây, anh em xếp theo tên. Bảng chỉ vài chục dòng nên đọc một lần."""
    rows = list(Area.objects.order_by("name", "id"))
    nodes = {a.pk: AreaTreeNode(a) for a in rows}
    roots: list[AreaTreeNode] = []
    for area in rows:
        parent = nodes.get(area.parent_id) if area.parent_id is not None else None
        (parent.children if parent is not None else roots).append(nodes[area.pk])
    return roots


def get_area(area_id: int) -> Area:
    return Area.objects.get(pk=area_id)


@transaction.atomic
def create_area(*, data: AreaCreate, actor: User) -> Area:
    _check_parent_usable(data.parent_id)
    _check_unique(code=data.code, name=data.name, parent_id=data.parent_id, area_id=None)
    area = Area(
        code=data.code,
        level=data.level,
        name=data.name,
        parent_id=data.parent_id,
        former_name=data.former_name,
        valid_to=data.valid_to,
    )
    if data.valid_from is not None:
        area.valid_from = data.valid_from
    _check_range(area.valid_from, area.valid_to)
    _full_clean(area)
    try:
        with (
            transaction.atomic()
        ):  # savepoint: hai request tạo trùng không làm hỏng giao dịch ngoài
            area.save()
    except IntegrityError:
        _check_unique(code=data.code, name=data.name, parent_id=data.parent_id, area_id=None)
        raise
    audit.record(actor, area, "CREATE")
    return area


@transaction.atomic
def update_area(*, area_id: int, data: AreaUpdate, actor: User) -> Area:
    """Sửa một phần; `status = INACTIVE` là ngừng dùng. Không đổi gì thì không ghi audit_log."""
    area = Area.objects.select_for_update().get(pk=area_id)
    changes = {
        f.name: getattr(data, f.name)
        for f in dataclasses.fields(data)
        if getattr(data, f.name) is not UNSET
    }
    changes = {k: v for k, v in changes.items() if getattr(area, k) != v}
    if not changes:
        return area

    before = audit.snapshot(area)
    if "parent_id" in changes:
        _check_parent_usable(changes["parent_id"])
    for name, value in changes.items():
        setattr(area, name, value)
    _check_unique(code=None, name=area.name, parent_id=area.parent_id, area_id=area.pk)
    _check_range(area.valid_from, area.valid_to)
    _full_clean(area)
    try:
        with transaction.atomic():
            area.save()
    except IntegrityError:
        _check_unique(code=None, name=area.name, parent_id=area.parent_id, area_id=area.pk)
        raise
    audit.record(actor, area, "UPDATE", before=before)
    return area
