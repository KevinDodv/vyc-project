"""Service công thức và thành phần (TK mục 5 «Công thức», BR-21, BR-26).

Một dòng `recipe` là một phiên bản của `code`. Quy tắc chính:

- Chỉ sửa trực tiếp bản DRAFT chưa có lệnh dùng; bản đã ACTIVE/RETIRED hoặc đã có lệnh thì
  «Tạo phiên bản mới» (BR-26b). Trả 409 `RECIPE_IN_USE` / `RECIPE_NOT_DRAFT`.
- Mỗi code tối đa một bản ACTIVE; kích hoạt bản mới thì bản cũ → RETIRED (BR-26a).
- `base_batch_g` = Σ qty_g, mỗi nhóm lựa chọn (alt_group) tính một phương án (BR-26c).
- Công thức bán thành phẩm không tự chứa chính nó, trực tiếp hay qua công thức khác (BR-26d).

Bảng lệnh sản xuất (`production_order`) thuộc app `operations` (đợt 2), mà `catalog` không được
import ngược lên `operations`, nên việc hỏi «công thức có lệnh dùng chưa» đi qua hai hook,
`operations` đăng ký trong `AppConfig.ready()`; chưa ai đăng ký thì coi như chưa có lệnh nào:

- `register_recipe_used_check(fn)`: `fn(recipe_id) -> bool`, True khi bản này đã có lệnh dùng
  (mọi trạng thái). Khoá sửa trực tiếp.
- `register_recipe_open_order_check(fn)`: `fn(recipe_id) -> bool`, True khi còn lệnh DRAFT hoặc
  CURING. Chặn ngừng dùng (BR-21).
"""

from __future__ import annotations

import dataclasses
from collections import defaultdict
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal
from typing import Final

from django.db import IntegrityError, transaction
from django.db.models import Max, Prefetch

from accounts.models import User
from catalog.models import (
    ActiveStatus,
    Ingredient,
    Recipe,
    RecipeItem,
    RecipeOutputKind,
    RecipeStatus,
)
from catalog.services.products import UNSET, _Unset
from core import audit
from core.errors import ApiError, BusinessError

RecipeCheck = Callable[[int], bool]
_used_checks: list[RecipeCheck] = []
_open_order_checks: list[RecipeCheck] = []

# Công thức sơ chế: đầu vào là lô quế, không có dòng phụ liệu nên ACTIVE được khi rỗng.
CODES_WITHOUT_ITEMS: Final = frozenset({"SC-VQH"})
# Mẻ danh nghĩa của công thức chưa có dòng nào (cột base_batch_g NOT NULL, > 0).
NOMINAL_BATCH_G: Final = Decimal("100.00")
MAX_BATCH_G: Final = Decimal("99999999.99")  # numeric(10,2)
CENT: Final = Decimal("0.01")


def register_recipe_used_check(check: RecipeCheck) -> None:
    """Đợt 2 nối vào: `check(recipe_id)` True khi bản đã có lệnh dùng. Đăng ký lặp thì bỏ qua."""
    if check not in _used_checks:
        _used_checks.append(check)


def register_recipe_open_order_check(check: RecipeCheck) -> None:
    """Đợt 2 nối vào: `check(recipe_id)` True khi còn lệnh DRAFT/CURING. Đăng ký lặp thì bỏ qua."""
    if check not in _open_order_checks:
        _open_order_checks.append(check)


def recipe_in_use(recipe_id: int) -> bool:
    return any(check(recipe_id) for check in _used_checks)


def recipe_has_open_orders(recipe_id: int) -> bool:
    return any(check(recipe_id) for check in _open_order_checks)


def is_editable(recipe: Recipe) -> bool:
    return recipe.status == RecipeStatus.DRAFT and not recipe_in_use(recipe.pk)


@dataclass(frozen=True)
class RecipeItemInput:
    ingredient_id: int
    qty_g: Decimal
    alt_group: int | None = None
    is_optional: bool = False
    note: str | None = None


@dataclass(frozen=True)
class RecipeCreate:
    code: str
    name: str
    output_kind: str
    output_ingredient_id: int | None = None
    base_batch_g: Decimal | None = None  # chỉ dùng khi không có dòng nào; có dòng thì máy cộng
    base_label: str | None = None
    cure_min_days: int = 0
    cure_max_days: int | None = None
    retain_months: int | None = None
    note: str | None = None
    items: list[RecipeItemInput] = field(default_factory=list)


@dataclass(frozen=True)
class RecipeUpdate:
    """Mỗi trường mặc định UNSET: chỉ trường được gửi mới đổi. `None` nghĩa là xoá giá trị."""

    name: str | _Unset = UNSET
    output_kind: str | _Unset = UNSET
    output_ingredient_id: int | _Unset | None = UNSET
    base_label: str | _Unset | None = UNSET
    cure_min_days: int | _Unset = UNSET
    cure_max_days: int | _Unset | None = UNSET
    retain_months: int | _Unset | None = UNSET
    note: str | _Unset | None = UNSET


@dataclass(frozen=True)
class ScaledLine:
    item: RecipeItem
    suggested_g: Decimal


# ------------------------------------------------------------------ đọc


def _with_items() -> Prefetch:
    items = RecipeItem.objects.select_related("ingredient").order_by("line_no")
    return Prefetch("items", queryset=items)


def list_recipes(
    *, code: str | None = None, status: str | None = None, output_kind: str | None = None
) -> list[Recipe]:
    qs = Recipe.objects.select_related("output_ingredient").order_by("code", "-version")
    if code:
        qs = qs.filter(code=code)
    if status:
        qs = qs.filter(status=status)
    if output_kind:
        qs = qs.filter(output_kind=output_kind)
    return list(qs)


def get_recipe(recipe_id: int) -> Recipe:
    return (
        Recipe.objects.select_related("output_ingredient")
        .prefetch_related(_with_items())
        .get(pk=recipe_id)
    )


def item_pct(qty_g: Decimal, base_batch_g: Decimal) -> Decimal:
    """% khối lượng của một dòng trên mẻ chuẩn, 2 số lẻ."""
    return (qty_g * 100 / base_batch_g).quantize(CENT, rounding=ROUND_HALF_UP)


def scale_recipe(*, recipe_id: int, batch_g: Decimal) -> tuple[Recipe, list[ScaledLine]]:
    """Lượng cân gợi ý từng dòng = qty_g * batch_g / base_batch_g, làm tròn 2 số lẻ (BR-26f)."""
    recipe = get_recipe(recipe_id)
    lines = [
        ScaledLine(
            item=item,
            suggested_g=(item.qty_g * batch_g / recipe.base_batch_g).quantize(
                CENT, rounding=ROUND_HALF_UP
            ),
        )
        for item in recipe.items.all()
    ]
    return recipe, lines


# ------------------------------------------------------------------ kiểm tra dùng chung


def compute_base_batch(items: Iterable[RecipeItemInput]) -> Decimal:
    """Σ qty_g; mỗi nhóm lựa chọn tính một phương án (lấy phương án nặng nhất)."""
    total = Decimal(0)
    groups: dict[int, Decimal] = {}
    for item in items:
        if item.alt_group is None:
            total += item.qty_g
        else:
            groups[item.alt_group] = max(groups.get(item.alt_group, Decimal(0)), item.qty_g)
    return (total + sum(groups.values(), Decimal(0))).quantize(CENT)


def _check_cure(cure_min: int, cure_max: int | None) -> None:
    if cure_max is not None and cure_max < cure_min:
        raise ApiError(
            "CURE_RANGE_INVALID",
            "Ngày ủ tối đa không được nhỏ hơn ngày ủ tối thiểu",
            field="cure_max_days",
        )


def _check_output(output_kind: str, output_ingredient_id: int | None) -> None:
    if output_kind == RecipeOutputKind.PRODUCT:
        if output_ingredient_id is not None:
            raise ApiError(
                "RECIPE_OUTPUT_FORBIDDEN",
                "Công thức thành phẩm không chọn phụ liệu làm ra",
                field="output_ingredient_id",
            )
        return
    if output_ingredient_id is None:
        raise ApiError(
            "RECIPE_OUTPUT_REQUIRED",
            "Công thức bán thành phẩm phải chọn phụ liệu làm ra",
            field="output_ingredient_id",
        )
    ingredient = Ingredient.objects.filter(pk=output_ingredient_id).first()
    if ingredient is None or ingredient.status != ActiveStatus.ACTIVE:
        raise ApiError(
            "INGREDIENT_INVALID",
            "Phụ liệu làm ra không có hoặc đã ngừng dùng",
            field="output_ingredient_id",
        )


def _prepare_items(items: Sequence[RecipeItemInput]) -> list[RecipeItemInput]:
    """Kiểm từng dòng (gram, phụ liệu còn dùng, trùng, nhóm lựa chọn). Trả lại danh sách đã kiểm."""
    ids = [i.ingredient_id for i in items]
    if len(set(ids)) != len(ids):
        raise ApiError("RECIPE_ITEM_DUPLICATE", "Một phụ liệu chỉ nằm trên một dòng", field="items")
    found = Ingredient.objects.in_bulk(ids)
    for item in items:
        if item.qty_g <= 0:
            raise ApiError("QTY_INVALID", "Gram mỗi dòng phải lớn hơn 0", field="items")
        ingredient = found.get(item.ingredient_id)
        if ingredient is None or ingredient.status != ActiveStatus.ACTIVE:
            raise ApiError(
                "INGREDIENT_INVALID",
                f"Phụ liệu #{item.ingredient_id} không có hoặc đã ngừng dùng",
                field="items",
            )
    sizes: dict[int, int] = defaultdict(int)
    for item in items:
        if item.alt_group is not None:
            sizes[item.alt_group] += 1
    single = sorted(g for g, n in sizes.items() if n == 1)
    if single:
        raise ApiError(
            "ALT_GROUP_SINGLE",
            f"Nhóm lựa chọn {single[0]} chỉ có một dòng; cần từ hai dòng trở lên",
            field="items",
        )
    base = compute_base_batch(items)
    if base > MAX_BATCH_G:
        raise ApiError("BATCH_TOO_LARGE", "Mẻ chuẩn quá lớn", field="items")
    return list(items)


def _find_cycle(
    *, code: str, output_ingredient_id: int | None, item_ingredient_ids: Iterable[int]
) -> list[int] | None:
    """Đường đi quay về chính nó: output → thành phần → … → output. Không có vòng thì None.

    Đồ thị là các cạnh «phụ liệu làm ra → phụ liệu thành phần» của công thức bán thành phẩm chưa
    RETIRED, trừ mọi phiên bản của `code` (đang được thay bằng `item_ingredient_ids`).
    """
    if output_ingredient_id is None:
        return None
    adjacency: dict[int, set[int]] = defaultdict(set)
    rows = (
        RecipeItem.objects.filter(
            recipe__output_ingredient__isnull=False,
            recipe__status__in=[RecipeStatus.ACTIVE, RecipeStatus.DRAFT],
        )
        .exclude(recipe__code=code)
        .values_list("recipe__output_ingredient_id", "ingredient_id")
    )
    for made, used in rows:
        adjacency[made].add(used)
    adjacency[output_ingredient_id] = set(item_ingredient_ids)

    seen: set[int] = set()
    stack = [(output_ingredient_id, [output_ingredient_id])]
    while stack:
        node, path = stack.pop()
        for nxt in sorted(adjacency.get(node, ())):
            if nxt == output_ingredient_id:
                return [*path, nxt]
            if nxt not in seen:
                seen.add(nxt)
                stack.append((nxt, [*path, nxt]))
    return None


def _lock_graph() -> None:
    """Khoá các công thức bán thành phẩm (theo thứ tự id) để hai lần lưu không cùng tạo vòng."""
    list(
        Recipe.objects.select_for_update()
        .filter(output_kind=RecipeOutputKind.INTERMEDIATE)
        .order_by("pk")
        .values_list("pk", flat=True)
    )


def _check_no_cycle(
    *, code: str, output_ingredient_id: int | None, item_ingredient_ids: Iterable[int]
) -> None:
    path = _find_cycle(
        code=code,
        output_ingredient_id=output_ingredient_id,
        item_ingredient_ids=item_ingredient_ids,
    )
    if path is None:
        return
    names = Ingredient.objects.in_bulk(path)
    chain = " → ".join(names[i].code for i in path)
    raise BusinessError(
        "RECIPE_CYCLE",
        f"Công thức không được tự chứa chính nó, trực tiếp hay gián tiếp: {chain}",
        rule="BR-26",
        field="items",
        path=[names[i].code for i in path],
    )


def _require_editable(recipe: Recipe) -> None:
    if recipe_in_use(recipe.pk):
        raise BusinessError(
            "RECIPE_IN_USE",
            f"{recipe.code} v{recipe.version} đã có lệnh sản xuất dùng, "
            "không sửa trực tiếp; hãy tạo phiên bản mới",
            rule="BR-26",
        )
    if recipe.status != RecipeStatus.DRAFT:
        raise BusinessError(
            "RECIPE_NOT_DRAFT",
            f"{recipe.code} v{recipe.version} không còn ở trạng thái nháp, "
            "không sửa trực tiếp; hãy tạo phiên bản mới",
            rule="BR-26",
        )


def _write_items(recipe: Recipe, items: Sequence[RecipeItemInput], actor: User) -> bool:
    """Ghi danh sách dòng tại chỗ theo line_no (1..n). True nếu có gì đổi."""
    existing = {i.line_no: i for i in RecipeItem.objects.select_for_update().filter(recipe=recipe)}
    changed = False
    for line_no, spec in enumerate(items, start=1):
        row = existing.pop(line_no, None)
        if row is None:
            row = RecipeItem.objects.create(
                recipe=recipe,
                line_no=line_no,
                ingredient_id=spec.ingredient_id,
                qty_g=spec.qty_g,
                alt_group=spec.alt_group,
                is_optional=spec.is_optional,
                note=spec.note,
            )
            audit.record(actor, row, "CREATE")
            changed = True
            continue
        new_values = {
            "ingredient_id": spec.ingredient_id,
            "qty_g": spec.qty_g,
            "alt_group": spec.alt_group,
            "is_optional": spec.is_optional,
            "note": spec.note,
        }
        if all(getattr(row, k) == v for k, v in new_values.items()):
            continue
        before = audit.snapshot(row)
        for k, v in new_values.items():
            setattr(row, k, v)
        row.save()
        audit.record(actor, row, "UPDATE", before=before)
        changed = True
    for row in existing.values():  # dòng thừa so với danh sách mới
        audit.record(actor, row, "DELETE_LINE")
        row.delete()
        changed = True
    return changed


# ------------------------------------------------------------------ ghi


@transaction.atomic
def create_recipe(*, data: RecipeCreate, actor: User) -> Recipe:
    """Tạo công thức mới: version 1, DRAFT. Mã đã có thì dùng «Tạo phiên bản mới»."""
    _check_cure(data.cure_min_days, data.cure_max_days)
    _check_output(data.output_kind, data.output_ingredient_id)
    if Recipe.objects.filter(code=data.code).exists():
        raise ApiError(
            "RECIPE_CODE_TAKEN",
            f"Mã công thức {data.code} đã có; dùng «Tạo phiên bản mới» để đổi công thức",
            status=409,
            field="code",
        )
    _lock_graph()
    items = _prepare_items(data.items)
    _check_no_cycle(
        code=data.code,
        output_ingredient_id=data.output_ingredient_id,
        item_ingredient_ids=[i.ingredient_id for i in items],
    )
    base = compute_base_batch(items) if items else (data.base_batch_g or NOMINAL_BATCH_G)
    recipe = Recipe(
        code=data.code,
        version=1,
        name=data.name,
        output_kind=data.output_kind,
        output_ingredient_id=data.output_ingredient_id,
        base_batch_g=base,
        base_label=data.base_label,
        cure_min_days=data.cure_min_days,
        cure_max_days=data.cure_max_days,
        retain_months=data.retain_months,
        status=RecipeStatus.DRAFT,
        note=data.note,
    )
    try:
        with transaction.atomic():
            recipe.save()
    except IntegrityError:
        if Recipe.objects.filter(code=data.code).exists():
            raise ApiError(
                "RECIPE_CODE_TAKEN", f"Mã công thức {data.code} đã có", status=409, field="code"
            ) from None
        raise
    audit.record(actor, recipe, "CREATE")
    _write_items(recipe, items, actor)
    return get_recipe(recipe.pk)


@transaction.atomic
def update_recipe(*, recipe_id: int, data: RecipeUpdate, actor: User) -> Recipe:
    """Sửa phần đầu công thức (không đụng dòng thành phần). Chỉ bản DRAFT chưa có lệnh dùng."""
    recipe = Recipe.objects.select_for_update().get(pk=recipe_id)
    _require_editable(recipe)
    changes = {
        f.name: getattr(data, f.name)
        for f in dataclasses.fields(data)
        if getattr(data, f.name) is not UNSET
    }
    changes = {k: v for k, v in changes.items() if getattr(recipe, k) != v}
    if not changes:
        return get_recipe(recipe.pk)

    cure_min = changes.get("cure_min_days", recipe.cure_min_days)
    cure_max = changes.get("cure_max_days", recipe.cure_max_days)
    _check_cure(int(cure_min), None if cure_max is None else int(cure_max))

    if "output_kind" in changes or "output_ingredient_id" in changes:
        kind = str(changes.get("output_kind", recipe.output_kind))
        out_id = changes.get("output_ingredient_id", recipe.output_ingredient_id)
        if (
            "output_kind" in changes
            and kind == RecipeOutputKind.PRODUCT
            and ("output_ingredient_id" not in changes)
        ):
            out_id = None  # đổi sang thành phẩm thì tự bỏ phụ liệu làm ra
            changes["output_ingredient_id"] = None
        if Recipe.objects.filter(code=recipe.code).exclude(pk=recipe.pk).exists():
            raise ApiError(
                "RECIPE_OUTPUT_LOCKED",
                f"{recipe.code} có nhiều phiên bản, không đổi đầu ra được",
                status=409,
                field="output_ingredient_id",
            )
        _check_output(kind, out_id)
        _lock_graph()
        _check_no_cycle(
            code=recipe.code,
            output_ingredient_id=out_id,
            item_ingredient_ids=RecipeItem.objects.filter(recipe=recipe).values_list(
                "ingredient_id", flat=True
            ),
        )

    before = audit.snapshot(recipe)
    for name, value in changes.items():
        setattr(recipe, name, value)
    recipe.save()
    audit.record(actor, recipe, "UPDATE", before=before)
    return get_recipe(recipe.pk)


@transaction.atomic
def replace_items(*, recipe_id: int, items: Sequence[RecipeItemInput], actor: User) -> Recipe:
    """Thay toàn bộ dòng thành phần; máy cộng lại mẻ chuẩn (không dòng nào thì giữ mẻ hiện có)."""
    recipe = Recipe.objects.select_for_update().get(pk=recipe_id)
    _require_editable(recipe)
    prepared = _prepare_items(items)
    _lock_graph()
    _check_no_cycle(
        code=recipe.code,
        output_ingredient_id=recipe.output_ingredient_id,
        item_ingredient_ids=[i.ingredient_id for i in prepared],
    )
    before = audit.snapshot(recipe)
    changed = _write_items(recipe, prepared, actor)
    if prepared:
        base = compute_base_batch(prepared)
        if base != recipe.base_batch_g:
            recipe.base_batch_g = base
            recipe.save()
            audit.record(actor, recipe, "UPDATE", before=before)
        elif changed:
            audit.record(actor, recipe, "UPDATE", before=before)
    elif changed:
        audit.record(actor, recipe, "UPDATE", before=before)
    return get_recipe(recipe.pk)


@transaction.atomic
def new_version(*, recipe_id: int, actor: User) -> Recipe:
    """Sao chép một phiên bản thành version = lớn nhất + 1, ở DRAFT, kèm các dòng thành phần."""
    source = Recipe.objects.get(pk=recipe_id)
    siblings = list(Recipe.objects.select_for_update().filter(code=source.code).order_by("pk"))
    draft = next((r for r in siblings if r.status == RecipeStatus.DRAFT), None)
    if draft is not None:
        raise BusinessError(
            "RECIPE_DRAFT_EXISTS",
            f"{source.code} đã có bản nháp v{draft.version}; sửa bản đó hoặc kích hoạt nó trước",
            rule="BR-26",
        )
    top = Recipe.objects.filter(code=source.code).aggregate(top=Max("version"))["top"]
    copy = Recipe(
        code=source.code,
        version=int(top) + 1,
        name=source.name,
        output_kind=source.output_kind,
        output_ingredient_id=source.output_ingredient_id,
        base_batch_g=source.base_batch_g,
        base_label=source.base_label,
        cure_min_days=source.cure_min_days,
        cure_max_days=source.cure_max_days,
        retain_months=source.retain_months,
        status=RecipeStatus.DRAFT,
        note=source.note,
    )
    copy.save()
    audit.record(actor, copy, "CREATE", reason=f"Sao chép từ v{source.version}")
    for row in RecipeItem.objects.filter(recipe=source).order_by("line_no"):
        clone = RecipeItem.objects.create(
            recipe=copy,
            line_no=row.line_no,
            ingredient_id=row.ingredient_id,
            qty_g=row.qty_g,
            alt_group=row.alt_group,
            is_optional=row.is_optional,
            note=row.note,
        )
        audit.record(actor, clone, "CREATE")
    return get_recipe(copy.pk)


@transaction.atomic
def activate(*, recipe_id: int, actor: User) -> Recipe:
    """DRAFT → ACTIVE; bản ACTIVE cũ của cùng code → RETIRED (BR-26a)."""
    recipe = Recipe.objects.get(pk=recipe_id)
    siblings = list(Recipe.objects.select_for_update().filter(code=recipe.code).order_by("pk"))
    recipe = next(r for r in siblings if r.pk == recipe_id)
    if recipe.status != RecipeStatus.DRAFT:
        raise BusinessError(
            "RECIPE_NOT_DRAFT",
            f"{recipe.code} v{recipe.version} không phải bản nháp nên không kích hoạt được",
            rule="BR-26",
        )
    rows = list(RecipeItem.objects.select_related("ingredient").filter(recipe=recipe))
    if not rows and recipe.code not in CODES_WITHOUT_ITEMS:
        raise BusinessError(
            "RECIPE_EMPTY",
            f"{recipe.code} v{recipe.version} chưa có dòng thành phần nào",
            rule="BR-26",
        )
    retired = [r.ingredient.code for r in rows if r.ingredient.status != ActiveStatus.ACTIVE]
    if retired:
        raise ApiError(
            "INGREDIENT_INVALID",
            f"Phụ liệu đã ngừng dùng: {', '.join(retired)}",
            status=409,
            field="items",
        )
    if recipe.output_kind == RecipeOutputKind.INTERMEDIATE:
        _check_output(recipe.output_kind, recipe.output_ingredient_id)
        _lock_graph()
        _check_no_cycle(
            code=recipe.code,
            output_ingredient_id=recipe.output_ingredient_id,
            item_ingredient_ids=[r.ingredient_id for r in rows],
        )
    for old in siblings:
        if old.status == RecipeStatus.ACTIVE:
            before = audit.snapshot(old)
            old.status = RecipeStatus.RETIRED
            old.save()
            audit.record(actor, old, "UPDATE", before=before, reason=f"Thay bằng v{recipe.version}")
    before = audit.snapshot(recipe)
    recipe.status = RecipeStatus.ACTIVE
    recipe.save()
    audit.record(actor, recipe, "UPDATE", before=before, reason="Kích hoạt")
    return get_recipe(recipe.pk)


@transaction.atomic
def retire(*, recipe_id: int, actor: User) -> Recipe:
    """ACTIVE → RETIRED. Còn lệnh DRAFT/CURING dùng bản này thì 409 (BR-21)."""
    recipe = Recipe.objects.select_for_update().get(pk=recipe_id)
    if recipe.status != RecipeStatus.ACTIVE:
        raise BusinessError(
            "RECIPE_NOT_ACTIVE",
            f"{recipe.code} v{recipe.version} không ở trạng thái đang dùng",
            rule="BR-26",
        )
    if recipe_has_open_orders(recipe.pk):
        raise BusinessError(
            "RECIPE_HAS_OPEN_ORDERS",
            f"{recipe.code} v{recipe.version} còn lệnh sản xuất chưa xong, không ngừng dùng được",
            rule="BR-21",
        )
    before = audit.snapshot(recipe)
    recipe.status = RecipeStatus.RETIRED
    recipe.save()
    audit.record(actor, recipe, "UPDATE", before=before, reason="Ngừng dùng")
    return get_recipe(recipe.pk)
