"""Service loại hàng hóa (TK mục 5, dòng «Loại hàng hóa»).

Quy tắc: không đổi nhóm (nguyên liệu, thành phẩm) khi đã có sản phẩm hay nguyên liệu dùng loại này.
Ngừng dùng chỉ đổi `status`; loại hàng không bị xoá (BR-19).
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass

from django.db import IntegrityError, transaction

from accounts.models import User
from catalog.models import GoodsType, Material, Product
from catalog.services.products import UNSET, _Unset
from core import audit
from core.errors import ApiError


@dataclass(frozen=True)
class GoodsTypeCreate:
    code: str
    name: str
    grp: str
    is_food: bool = False


@dataclass(frozen=True)
class GoodsTypeUpdate:
    """Mã (`code`) không đổi được sau khi tạo."""

    name: str | _Unset = UNSET
    grp: str | _Unset = UNSET
    is_food: bool | _Unset = UNSET
    status: str | _Unset = UNSET


def _check_code_free(code: str) -> None:
    if GoodsType.objects.filter(code=code).exists():
        raise ApiError(
            "GOODS_TYPE_CODE_TAKEN", f"Mã loại hàng {code} đã có", status=409, field="code"
        )


def list_goods_types(*, status: str | None = None, grp: str | None = None) -> list[GoodsType]:
    qs = GoodsType.objects.order_by("grp", "name", "id")
    if status:
        qs = qs.filter(status=status)
    if grp:
        qs = qs.filter(grp=grp)
    return list(qs)


def get_goods_type(goods_type_id: int) -> GoodsType:
    return GoodsType.objects.get(pk=goods_type_id)


@transaction.atomic
def create_goods_type(*, data: GoodsTypeCreate, actor: User) -> GoodsType:
    _check_code_free(data.code)
    goods_type = GoodsType(**dataclasses.asdict(data))
    try:
        # savepoint: hai request tạo trùng cùng lúc không làm hỏng giao dịch ngoài
        with transaction.atomic():
            goods_type.save()
    except IntegrityError:
        _check_code_free(data.code)
        raise
    audit.record(actor, goods_type, "CREATE")
    return goods_type


def _group_user(goods_type: GoodsType) -> str | None:
    if Product.objects.filter(goods_type=goods_type).exists():
        return "sản phẩm"
    if Material.objects.filter(goods_type=goods_type).exists():
        return "nguyên liệu"
    return None


@transaction.atomic
def update_goods_type(*, goods_type_id: int, data: GoodsTypeUpdate, actor: User) -> GoodsType:
    """Sửa một phần; `status = INACTIVE` là ngừng dùng. Không đổi gì thì không ghi audit_log."""
    goods_type = GoodsType.objects.select_for_update().get(pk=goods_type_id)
    changes = {
        f.name: getattr(data, f.name)
        for f in dataclasses.fields(data)
        if getattr(data, f.name) is not UNSET
    }
    changes = {k: v for k, v in changes.items() if getattr(goods_type, k) != v}
    if not changes:
        return goods_type

    before = audit.snapshot(goods_type)
    if "grp" in changes:
        used_by = _group_user(goods_type)
        if used_by is not None:
            raise ApiError(
                "GOODS_TYPE_GROUP_LOCKED",
                f"Loại hàng «{goods_type.name}» đã có {used_by} dùng, không đổi nhóm được",
                status=409,
                field="grp",
            )
    for name, value in changes.items():
        setattr(goods_type, name, value)
    goods_type.save()
    audit.record(actor, goods_type, "UPDATE", before=before)
    return goods_type
