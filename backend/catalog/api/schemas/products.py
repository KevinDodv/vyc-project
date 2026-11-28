"""Schema vào/ra của `/api/v1/products` (backend.md 8).

`ProductOut` (WORKSHOP) không có giá; `ProductOwnerOut` (OWNER) thêm `retail_price` (mục 4.3).
`ProductPatch` phân biệt «không gửi» với «gửi null» bằng `model_fields_set` (xem `patch_fields`).
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any, ClassVar, Literal

from ninja import Schema
from pydantic import Field, StringConstraints, model_validator

from core.schemas import BuyLink, SafeMediaPath

Slug = Annotated[str, StringConstraints(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=120)]
Sku = Annotated[str, StringConstraints(pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]*$", max_length=40)]
Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
ProductStatusLiteral = Literal["DRAFT", "PUBLISHED", "HIDDEN"]


class ProductImage(Schema):
    """Ảnh của sản phẩm, đúng dạng `core.images.store_image` trả (backend.md 6.5)."""

    url: SafeMediaPath
    alt: str = Field(min_length=1, max_length=200)  # mỗi ảnh bắt buộc có alt (mục 4)
    key: str = Field(pattern=r"^[0-9a-f]{2}/[0-9a-f]{8,64}$")
    w: int = Field(ge=1, le=10000)
    h: int = Field(ge=1, le=10000)
    widths: list[int] = Field(min_length=1, max_length=3)


class ProductIn(Schema):
    sku: Sku
    name: Text
    slug: Slug
    goods_type_id: int
    size_label: Text
    unit: Text
    shelf_life_months: int | None = Field(None, ge=1, le=240)
    requires_retention_sample: bool = False
    recipe_code: str | None = Field(None, max_length=40)
    retail_price: int | None = Field(None, ge=0)
    featured_rank: int | None = Field(None, ge=1, le=999)
    short_desc: str | None = Field(None, max_length=500)
    story_md: str | None = Field(None, max_length=20000)
    usage_md: str | None = Field(None, max_length=20000)
    seo_title: str | None = Field(None, max_length=70)
    seo_description: str | None = Field(None, max_length=170)
    images: list[ProductImage] = Field(default_factory=list, max_length=20)
    buy_links: list[BuyLink] = Field(default_factory=list, max_length=10)
    serial_tracked: bool = True


class ProductPatch(Schema):
    """Chỉ đổi trường có trong body. `featured_rank: null` là bỏ nổi bật; không gửi thì giữ nguyên.

    Trường cột NOT NULL (`_NOT_NULL`) mà gửi `null` thì 400 thay vì lọt xuống DB.
    """

    sku: Sku | None = None
    name: Text | None = None
    slug: Slug | None = None
    goods_type_id: int | None = None
    size_label: Text | None = None
    unit: Text | None = None
    shelf_life_months: int | None = Field(None, ge=1, le=240)
    requires_retention_sample: bool | None = None
    recipe_code: str | None = Field(None, max_length=40)
    retail_price: int | None = Field(None, ge=0)
    featured_rank: int | None = Field(None, ge=1, le=999)
    short_desc: str | None = Field(None, max_length=500)
    story_md: str | None = Field(None, max_length=20000)
    usage_md: str | None = Field(None, max_length=20000)
    seo_title: str | None = Field(None, max_length=70)
    seo_description: str | None = Field(None, max_length=170)
    images: list[ProductImage] | None = Field(None, max_length=20)
    buy_links: list[BuyLink] | None = Field(None, max_length=10)
    serial_tracked: bool | None = None
    status: ProductStatusLiteral | None = None
    # Cột NOT NULL: gửi `null` là sai (khác featured_rank, nơi null có nghĩa «bỏ nổi bật»).
    _NOT_NULL: ClassVar[frozenset[str]] = frozenset(
        {
            "sku",
            "name",
            "slug",
            "goods_type_id",
            "size_label",
            "unit",
            "requires_retention_sample",
            "images",
            "buy_links",
            "serial_tracked",
            "status",
        }
    )

    @model_validator(mode="after")
    def _reject_null_for_required(self) -> ProductPatch:
        for name in self._NOT_NULL & self.model_fields_set:
            if getattr(self, name) is None:
                raise ValueError(f"{name} không được để trống")
        return self

    def patch_fields(self) -> dict[str, Any]:
        """Các trường client thật sự gửi, đã đổi schema con thành dict."""
        return self.model_dump(exclude_unset=True)


class ProductWarning(Schema):
    """Cảnh báo không chặn, ví dụ công thức nối vào đã hết bản ACTIVE."""

    code: str
    message: str
    field: str | None = None


class ProductOut(Schema):
    """Cho WORKSHOP: không có giá bán lẻ. `warnings` rỗng khi sản phẩm không có vấn đề."""

    id: int
    sku: str
    name: str
    slug: str
    goods_type_id: int
    size_label: str
    unit: str
    shelf_life_months: int | None
    requires_retention_sample: bool
    recipe_code: str | None
    featured_rank: int | None
    short_desc: str | None
    story_md: str | None
    usage_md: str | None
    seo_title: str | None
    seo_description: str | None
    images: list[dict[str, Any]]
    buy_links: list[dict[str, Any]]
    serial_tracked: bool
    status: str
    created_at: datetime
    updated_at: datetime
    warnings: list[ProductWarning] = Field(default_factory=list)


class ProductOwnerOut(ProductOut):
    retail_price: int | None
