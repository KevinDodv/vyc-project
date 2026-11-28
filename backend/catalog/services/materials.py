"""Service nguyên vật liệu và hạng (TK mục 5, dòng «Nguyên vật liệu»).

Quy tắc: không ngừng dùng hạng đang có lô trong kho. Bảng lô (`material_lot`) thuộc app
`operations` (đợt 2), mà `catalog` không được import ngược lên `operations`, nên kiểm tra đi qua
một hook: app `operations` gọi `register_grade_in_use_check(fn)` trong `AppConfig.ready()` với
`fn(grade_id) -> bool` trả True khi hạng đó còn lô IN_STOCK hoặc RESERVED. Chưa ai đăng ký thì
không hạng nào bị coi là đang có lô. Ngừng dùng cả nguyên liệu cũng đi qua kiểm tra này cho mọi
hạng đang dùng của nó.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Callable
from dataclasses import dataclass, field

from django.db import IntegrityError, transaction
from django.db.models import Prefetch

from accounts.models import User
from catalog.models import ActiveStatus, GoodsGroup, GoodsType, GoodsTypeStatus, Grade, Material
from catalog.services.products import UNSET, _Unset
from core import audit
from core.errors import ApiError

GradeInUseCheck = Callable[[int], bool]
_grade_in_use_checks: list[GradeInUseCheck] = []


def register_grade_in_use_check(check: GradeInUseCheck) -> None:
    """Đợt 2 nối vào: `check(grade_id)` True khi hạng còn lô trong kho. Đăng ký lặp thì bỏ qua."""
    if check not in _grade_in_use_checks:
        _grade_in_use_checks.append(check)


def grade_has_lots(grade_id: int) -> bool:
    return any(check(grade_id) for check in _grade_in_use_checks)


@dataclass(frozen=True)
class GradeInput:
    """Một hạng trong body. `id` None: hạng mới; có `id`: sửa hạng đó (bậc không đổi được)."""

    rank: int
    name: str
    id: int | None = None
    status: str | None = None  # None: giữ nguyên (hạng mới thì ACTIVE)


@dataclass(frozen=True)
class MaterialCreate:
    code: str
    name: str
    goods_type_id: int
    image_url: str | None = None
    sort_order: int = 0
    grades: list[GradeInput] = field(default_factory=list)


@dataclass(frozen=True)
class MaterialUpdate:
    """Mã (`code`) không đổi được sau khi tạo. `grades`: thêm hạng mới hoặc sửa hạng có `id`."""

    name: str | _Unset = UNSET
    goods_type_id: int | _Unset = UNSET
    image_url: str | _Unset | None = UNSET
    sort_order: int | _Unset = UNSET
    status: str | _Unset = UNSET
    grades: list[GradeInput] | _Unset = UNSET


def _with_grades() -> Prefetch:
    return Prefetch("grades", queryset=Grade.objects.order_by("rank"))


def list_materials(*, status: str | None = None) -> list[Material]:
    qs = Material.objects.prefetch_related(_with_grades()).order_by("sort_order", "id")
    if status:
        qs = qs.filter(status=status)
    return list(qs)


def get_material(material_id: int) -> Material:
    return Material.objects.prefetch_related(_with_grades()).get(pk=material_id)


def _check_goods_type(goods_type_id: int) -> None:
    goods_type = GoodsType.objects.filter(pk=goods_type_id).first()
    if (
        goods_type is None
        or goods_type.status != GoodsTypeStatus.ACTIVE
        or goods_type.grp != GoodsGroup.MATERIAL
    ):
        raise ApiError(
            "GOODS_TYPE_INVALID",
            "Loại hàng không có, đã ngừng dùng hoặc không thuộc nhóm nguyên liệu",
            status=400,
            field="goods_type_id",
        )


def _check_code_free(code: str) -> None:
    if Material.objects.filter(code=code).exists():
        raise ApiError(
            "MATERIAL_CODE_TAKEN", f"Mã nguyên liệu {code} đã có", status=409, field="code"
        )


def _check_grade_inputs(items: list[GradeInput]) -> None:
    for item in items:
        if not 1 <= item.rank <= 9:
            raise ApiError("GRADE_RANK_INVALID", "Bậc của hạng phải từ 1 đến 9", field="grades")
        if not item.name.strip():
            raise ApiError("GRADE_NAME_REQUIRED", "Tên hạng không được để trống", field="grades")
    ranks = [g.rank for g in items]
    if len(set(ranks)) != len(ranks):
        raise ApiError("GRADE_RANK_DUPLICATE", "Hai hạng không được cùng một bậc", field="grades")
    ids = [g.id for g in items if g.id is not None]
    if len(set(ids)) != len(ids):
        raise ApiError("GRADE_DUPLICATE", "Một hạng xuất hiện hai lần", field="grades")


def _guard_grade_deactivation(grade: Grade) -> None:
    if grade_has_lots(grade.pk):
        raise ApiError(
            "GRADE_HAS_LOTS",
            f"Hạng «{grade.name}» đang có lô trong kho, không ngừng dùng được",
            status=409,
            field="grades",
        )


def _create_grade(
    material: Material, item: GradeInput, taken: dict[int, Grade], actor: User
) -> None:
    clash = taken.get(item.rank)
    if clash is not None:
        raise ApiError(
            "GRADE_RANK_TAKEN",
            f"Bậc {item.rank} đã có hạng «{clash.name}»",
            status=409,
            field="grades",
        )
    grade = Grade(
        material=material,
        rank=item.rank,
        name=item.name.strip(),
        status=item.status or ActiveStatus.ACTIVE,
    )
    grade.save()
    taken[grade.rank] = grade
    audit.record(actor, grade, "CREATE")


def _update_grade(grade: Grade, item: GradeInput, actor: User) -> None:
    if grade.rank != item.rank:
        raise ApiError(
            "GRADE_RANK_LOCKED",
            f"Không đổi bậc của hạng «{grade.name}»; thêm hạng mới nếu cần",
            status=409,
            field="grades",
        )
    new_name = item.name.strip()
    new_status = item.status or grade.status
    if new_name == grade.name and new_status == grade.status:
        return
    if new_status == ActiveStatus.INACTIVE and grade.status != ActiveStatus.INACTIVE:
        _guard_grade_deactivation(grade)
    before = audit.snapshot(grade)
    grade.name = new_name
    grade.status = new_status
    grade.save()
    audit.record(actor, grade, "UPDATE", before=before)


def _apply_grades(material: Material, items: list[GradeInput], actor: User) -> None:
    _check_grade_inputs(items)
    existing = {g.pk: g for g in Grade.objects.select_for_update().filter(material=material)}
    taken = {g.rank: g for g in existing.values()}
    for item in items:
        if item.id is None:
            _create_grade(material, item, taken, actor)
            continue
        grade = existing.get(item.id)
        if grade is None:
            raise ApiError(
                "GRADE_NOT_FOUND", "Hạng không thuộc nguyên liệu này", status=400, field="grades"
            )
        _update_grade(grade, item, actor)


@transaction.atomic
def create_material(*, data: MaterialCreate, actor: User) -> Material:
    _check_goods_type(data.goods_type_id)
    _check_code_free(data.code)
    material = Material(
        code=data.code,
        name=data.name,
        goods_type_id=data.goods_type_id,
        image_url=data.image_url,
        sort_order=data.sort_order,
    )
    try:
        with transaction.atomic():
            material.save()
    except IntegrityError:
        _check_code_free(data.code)
        raise
    audit.record(actor, material, "CREATE")
    _apply_grades(material, data.grades, actor)
    return get_material(material.pk)


def _guard_material_deactivation(material: Material) -> None:
    for grade in Grade.objects.filter(material=material, status=ActiveStatus.ACTIVE):
        if grade_has_lots(grade.pk):
            raise ApiError(
                "MATERIAL_HAS_LOTS",
                f"Hạng «{grade.name}» của {material.name} đang có lô trong kho, "
                "không ngừng dùng nguyên liệu được",
                status=409,
                field="status",
            )


@transaction.atomic
def update_material(*, material_id: int, data: MaterialUpdate, actor: User) -> Material:
    """Sửa nguyên liệu và/hoặc hạng. Không đổi gì thì không ghi audit_log."""
    material = Material.objects.select_for_update().get(pk=material_id)
    changes = {
        f.name: getattr(data, f.name)
        for f in dataclasses.fields(data)
        if f.name != "grades" and getattr(data, f.name) is not UNSET
    }
    changes = {k: v for k, v in changes.items() if getattr(material, k) != v}

    if changes:
        before = audit.snapshot(material)
        if "goods_type_id" in changes:
            _check_goods_type(changes["goods_type_id"])
        if changes.get("status") == ActiveStatus.INACTIVE:
            _guard_material_deactivation(material)
        for name, value in changes.items():
            setattr(material, name, value)
        material.save()
        audit.record(actor, material, "UPDATE", before=before)

    if not isinstance(data.grades, _Unset):
        _apply_grades(material, data.grades, actor)
    return get_material(material.pk)
