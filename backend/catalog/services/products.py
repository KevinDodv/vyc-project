"""Service sản phẩm: tạo, sửa, đổi slug (backend.md 8).

Không biết tới request hay schema Ninja; api chuyển schema sang dataclass ở file này.
BR-14 (sản phẩm is_food cần giấy tờ ATTP mới được PUBLISHED) làm ở GĐ3 cùng màn chứng nhận.

`recipe_code` phải trỏ tới công thức thành phẩm đang có bản ACTIVE (kiểm khi gán hoặc đổi). Sau
đó công thức hết bản ACTIVE thì sản phẩm PUBLISHED chỉ nhận cảnh báo (`product_warnings`),
không bị chặn.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any, Final

from django.db import IntegrityError, transaction

from accounts.models import User
from catalog.models import (
    GoodsType,
    GoodsTypeStatus,
    Product,
    ProductStatus,
    Recipe,
    RecipeOutputKind,
    RecipeStatus,
    SlugRedirect,
)
from core import audit
from core.errors import ApiError


class _Unset:
    """Dấu «không gửi trường này», khác với `None` («gửi null, xoá giá trị»)."""

    _instance: _Unset | None = None

    def __new__(cls) -> _Unset:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return "UNSET"

    def __bool__(self) -> bool:
        return False


UNSET: Final = _Unset()


@dataclass(frozen=True)
class ProductCreate:
    sku: str
    name: str
    slug: str
    goods_type_id: int
    size_label: str
    unit: str
    shelf_life_months: int | None = None
    requires_retention_sample: bool = False
    recipe_code: str | None = None
    retail_price: int | None = None
    featured_rank: int | None = None
    short_desc: str | None = None
    story_md: str | None = None
    usage_md: str | None = None
    seo_title: str | None = None
    seo_description: str | None = None
    images: list[dict[str, Any]] = field(default_factory=list)
    buy_links: list[dict[str, Any]] = field(default_factory=list)
    serial_tracked: bool = True


@dataclass(frozen=True)
class ProductUpdate:
    """Mỗi trường mặc định UNSET: chỉ trường được gửi mới đổi. `None` nghĩa là xoá giá trị."""

    sku: str | _Unset = UNSET
    name: str | _Unset = UNSET
    slug: str | _Unset = UNSET
    goods_type_id: int | _Unset = UNSET
    size_label: str | _Unset = UNSET
    unit: str | _Unset = UNSET
    shelf_life_months: int | _Unset | None = UNSET
    requires_retention_sample: bool | _Unset = UNSET
    recipe_code: str | _Unset | None = UNSET
    retail_price: int | _Unset | None = UNSET
    featured_rank: int | _Unset | None = UNSET
    short_desc: str | _Unset | None = UNSET
    story_md: str | _Unset | None = UNSET
    usage_md: str | _Unset | None = UNSET
    seo_title: str | _Unset | None = UNSET
    seo_description: str | _Unset | None = UNSET
    images: list[dict[str, Any]] | _Unset = UNSET
    buy_links: list[dict[str, Any]] | _Unset = UNSET
    serial_tracked: bool | _Unset = UNSET
    status: str | _Unset = UNSET


def _check_recipe_code(recipe_code: str | None) -> None:
    if recipe_code is None:
        return
    recipe = Recipe.objects.filter(code=recipe_code, status=RecipeStatus.ACTIVE).first()
    if recipe is None:
        raise ApiError(
            "RECIPE_NOT_ACTIVE",
            f"Công thức {recipe_code} không có hoặc chưa có bản đang dùng",
            status=400,
            field="recipe_code",
        )
    if recipe.output_kind != RecipeOutputKind.PRODUCT:
        raise ApiError(
            "RECIPE_NOT_PRODUCT",
            f"Công thức {recipe_code} là bán thành phẩm, sản phẩm chỉ nối công thức thành phẩm",
            status=400,
            field="recipe_code",
        )


def product_warnings(products: Iterable[Product]) -> dict[int, list[dict[str, str]]]:
    """Cảnh báo không chặn: sản phẩm PUBLISHED mà công thức nối vào hết bản ACTIVE."""
    watched = [p for p in products if p.status == ProductStatus.PUBLISHED and p.recipe_code]
    if not watched:
        return {}
    codes = {p.recipe_code for p in watched}
    active = set(
        Recipe.objects.filter(status=RecipeStatus.ACTIVE, code__in=codes).values_list(
            "code", flat=True
        )
    )
    return {
        p.pk: [
            {
                "code": "RECIPE_NOT_ACTIVE",
                "message": f"Công thức {p.recipe_code} hiện không có bản đang dùng",
                "field": "recipe_code",
            }
        ]
        for p in watched
        if p.recipe_code not in active
    }


def _other_than(product_id: int | None) -> int:
    """Id để `.exclude(...)`: tạo mới (None) thì không loại dòng nào (bigserial bắt đầu từ 1)."""
    return product_id if product_id is not None else 0


def _slug_taken(slug: str, *, product_id: int | None) -> bool:
    """Slug đã là slug hiện hành hoặc slug cũ của sản phẩm KHÁC."""
    if Product.objects.filter(slug=slug).exclude(pk=_other_than(product_id)).exists():
        return True
    return (
        SlugRedirect.objects.filter(old_slug=slug)
        .exclude(product_id=_other_than(product_id))
        .exists()
    )


def _check_unique(*, sku: str | None, slug: str | None, product_id: int | None) -> None:
    if (
        sku is not None
        and Product.objects.filter(sku=sku).exclude(pk=_other_than(product_id)).exists()
    ):
        raise ApiError("SKU_TAKEN", f"Mã SKU {sku} đã có sản phẩm khác dùng", status=409)
    if slug is not None and _slug_taken(slug, product_id=product_id):
        raise ApiError("SLUG_TAKEN", f"Đường dẫn «{slug}» đã có sản phẩm khác dùng", status=409)


def _get_goods_type(goods_type_id: int) -> GoodsType:
    goods_type = GoodsType.objects.filter(pk=goods_type_id).first()
    if goods_type is None or goods_type.status != GoodsTypeStatus.ACTIVE:
        raise ApiError("GOODS_TYPE_INVALID", "Loại hàng không có hoặc đã ngừng dùng", status=400)
    return goods_type


@transaction.atomic
def create_product(*, data: ProductCreate, actor: User) -> Product:
    """Tạo sản phẩm ở trạng thái DRAFT (đăng bán qua `update_product`)."""
    _get_goods_type(data.goods_type_id)
    _check_recipe_code(data.recipe_code)
    _check_unique(sku=data.sku, slug=data.slug, product_id=None)
    values = {f.name: getattr(data, f.name) for f in dataclasses.fields(data)}
    product = Product(status=ProductStatus.DRAFT, **values)
    try:
        # savepoint: IntegrityError do hai request tạo trùng cùng lúc không làm hỏng giao dịch ngoài
        with transaction.atomic():
            product.save()
    except IntegrityError:
        _check_unique(sku=data.sku, slug=data.slug, product_id=None)
        raise
    audit.record(actor, product, "CREATE")
    return product


@transaction.atomic
def update_product(*, product_id: int, data: ProductUpdate, actor: User) -> Product:
    """Sửa một phần: chỉ trường khác UNSET mới đổi. Đổi slug thì giữ slug cũ trong slug_redirect."""
    product = Product.objects.select_for_update().get(pk=product_id)
    changes = {
        f.name: getattr(data, f.name)
        for f in dataclasses.fields(data)
        if getattr(data, f.name) is not UNSET
    }
    # Chỉ giữ trường thật sự khác giá trị hiện tại: không đổi gì thì không ghi audit_log.
    changes = {k: v for k, v in changes.items() if getattr(product, k) != v}
    if not changes:
        return product

    before = audit.snapshot(product)
    if "goods_type_id" in changes:
        _get_goods_type(changes["goods_type_id"])
    if "recipe_code" in changes:
        _check_recipe_code(changes["recipe_code"])
    _check_unique(sku=changes.get("sku"), slug=changes.get("slug"), product_id=product.pk)

    old_slug = product.slug
    for name, value in changes.items():
        setattr(product, name, value)
    try:
        with transaction.atomic():
            product.save()
            new_slug = changes.get("slug")
            if new_slug is not None:
                # Đổi tên rồi đổi lại: slug mới từng là slug cũ của chính sản phẩm này.
                SlugRedirect.objects.filter(old_slug=new_slug, product_id=product.pk).delete()
                SlugRedirect.objects.create(old_slug=old_slug, product=product)
    except IntegrityError:
        _check_unique(sku=changes.get("sku"), slug=changes.get("slug"), product_id=product.pk)
        raise
    audit.record(actor, product, "UPDATE", before=before)
    return product
