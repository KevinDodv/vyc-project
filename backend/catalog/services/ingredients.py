"""Service phụ liệu và bán thành phẩm (TK mục 5, dòng «Phụ liệu»; BR-21).

Bảng lô phụ liệu (`ingredient_lot`) thuộc app `operations` (đợt 2), mà `catalog` không được
import ngược lên `operations`, nên kiểm tra lô đi qua hai hook; `operations` đăng ký trong
`AppConfig.ready()`. Chưa ai đăng ký thì phụ liệu nào cũng coi như chưa có lô.

- `register_ingredient_lot_check(fn)`: `fn(ingredient_id) -> bool`, True khi phụ liệu đã có lô ở
  MỌI trạng thái. Khoá việc đổi mã và bật «theo dõi tồn».
- `register_ingredient_stock_check(fn)`: `fn(ingredient_id) -> bool`, True khi còn lô IN_STOCK.
  Chặn ngừng dùng (BR-21).
"""

from __future__ import annotations

import dataclasses
from collections.abc import Callable
from dataclasses import dataclass
from decimal import Decimal

from django.db import IntegrityError, transaction

from accounts.models import User
from catalog.models import ActiveStatus, Ingredient, Recipe, RecipeStatus
from catalog.services.products import UNSET, _Unset
from core import audit
from core.errors import ApiError, BusinessError

IngredientCheck = Callable[[int], bool]
_lot_checks: list[IngredientCheck] = []
_stock_checks: list[IngredientCheck] = []


def register_ingredient_lot_check(check: IngredientCheck) -> None:
    """Đợt 2 nối vào: `check(ingredient_id)` True khi phụ liệu đã có lô. Đăng ký lặp thì bỏ qua."""
    if check not in _lot_checks:
        _lot_checks.append(check)


def register_ingredient_stock_check(check: IngredientCheck) -> None:
    """Đợt 2 nối vào: `check(ingredient_id)` True khi còn lô IN_STOCK. Đăng ký lặp thì bỏ qua."""
    if check not in _stock_checks:
        _stock_checks.append(check)


def has_lots(ingredient_id: int) -> bool:
    return any(check(ingredient_id) for check in _lot_checks)


def has_stock(ingredient_id: int) -> bool:
    return any(check(ingredient_id) for check in _stock_checks)


@dataclass(frozen=True)
class IngredientCreate:
    code: str
    name: str
    kind: str
    density_g_ml: Decimal | None = None
    track_stock: bool = True
    requires_coa: bool = False
    shelf_life_months: int | None = None


@dataclass(frozen=True)
class IngredientUpdate:
    """Mỗi trường mặc định UNSET: chỉ trường được gửi mới đổi. `None` nghĩa là xoá giá trị."""

    code: str | _Unset = UNSET
    name: str | _Unset = UNSET
    kind: str | _Unset = UNSET
    density_g_ml: Decimal | _Unset | None = UNSET
    track_stock: bool | _Unset = UNSET
    requires_coa: bool | _Unset = UNSET
    shelf_life_months: int | _Unset | None = UNSET
    status: str | _Unset = UNSET


def list_ingredients(*, status: str | None = None, kind: str | None = None) -> list[Ingredient]:
    qs = Ingredient.objects.order_by("kind", "code")
    if status:
        qs = qs.filter(status=status)
    if kind:
        qs = qs.filter(kind=kind)
    return list(qs)


def _check_code_free(code: str, *, ingredient_id: int | None) -> None:
    qs = Ingredient.objects.filter(code=code)
    if ingredient_id is not None:
        qs = qs.exclude(pk=ingredient_id)
    if qs.exists():
        raise ApiError(
            "INGREDIENT_CODE_TAKEN", f"Mã phụ liệu {code} đã có", status=409, field="code"
        )


@transaction.atomic
def create_ingredient(*, data: IngredientCreate, actor: User) -> Ingredient:
    _check_code_free(data.code, ingredient_id=None)
    values = {f.name: getattr(data, f.name) for f in dataclasses.fields(data)}
    ingredient = Ingredient(**values)
    try:
        # savepoint: hai request tạo trùng cùng lúc không làm hỏng giao dịch ngoài
        with transaction.atomic():
            ingredient.save()
    except IntegrityError:
        _check_code_free(data.code, ingredient_id=None)
        raise
    audit.record(actor, ingredient, "CREATE")
    return ingredient


def _active_recipes_using(ingredient: Ingredient) -> list[str]:
    """Mã các công thức ACTIVE còn dùng phụ liệu: làm dòng thành phần hoặc làm đầu ra."""
    used = Recipe.objects.filter(status=RecipeStatus.ACTIVE, items__ingredient=ingredient)
    made = Recipe.objects.filter(status=RecipeStatus.ACTIVE, output_ingredient=ingredient)
    codes = set(used.values_list("code", flat=True)) | set(made.values_list("code", flat=True))
    return sorted(codes)


def _guard_changes(ingredient: Ingredient, changes: dict[str, object]) -> None:
    if "code" in changes and has_lots(ingredient.pk):
        raise ApiError(
            "INGREDIENT_CODE_LOCKED",
            f"Phụ liệu {ingredient.code} đã có lô, không đổi mã được",
            status=409,
            field="code",
        )
    if changes.get("track_stock") is True and has_lots(ingredient.pk):
        raise ApiError(
            "INGREDIENT_TRACK_STOCK_LOCKED",
            f"Phụ liệu {ingredient.code} đã có lô, không bật «theo dõi tồn» được",
            status=409,
            field="track_stock",
        )
    if changes.get("status") == ActiveStatus.INACTIVE:
        if has_stock(ingredient.pk):
            raise BusinessError(
                "INGREDIENT_HAS_LOTS",
                f"Phụ liệu {ingredient.code} còn lô trong kho, không ngừng dùng được",
                rule="BR-21",
                field="status",
            )
        recipes = _active_recipes_using(ingredient)
        if recipes:
            raise BusinessError(
                "INGREDIENT_IN_ACTIVE_RECIPE",
                f"Phụ liệu {ingredient.code} còn trong công thức đang dùng: {', '.join(recipes)}",
                rule="BR-21",
                field="status",
                recipes=recipes,
            )


@transaction.atomic
def update_ingredient(*, ingredient_id: int, data: IngredientUpdate, actor: User) -> Ingredient:
    """Sửa một phần: chỉ trường khác UNSET mới đổi. Không đổi gì thì không ghi audit_log."""
    ingredient = Ingredient.objects.select_for_update().get(pk=ingredient_id)
    changes = {
        f.name: getattr(data, f.name)
        for f in dataclasses.fields(data)
        if getattr(data, f.name) is not UNSET
    }
    changes = {k: v for k, v in changes.items() if getattr(ingredient, k) != v}
    if not changes:
        return ingredient

    if "code" in changes:
        _check_code_free(str(changes["code"]), ingredient_id=ingredient.pk)
    _guard_changes(ingredient, changes)
    before = audit.snapshot(ingredient)
    for name, value in changes.items():
        setattr(ingredient, name, value)
    try:
        with transaction.atomic():
            ingredient.save()
    except IntegrityError:
        if "code" in changes:
            _check_code_free(str(changes["code"]), ingredient_id=ingredient.pk)
        raise
    audit.record(actor, ingredient, "UPDATE", before=before)
    return ingredient
