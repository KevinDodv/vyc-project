"""Schema vào/ra của `/api/v1/recipes` (TK mục 5 «Công thức», mục 9, BR-26).

Gram tính theo gram, không theo ml. `base_batch_g` do máy cộng từ các dòng (mỗi nhóm lựa chọn một
phương án); body chỉ gửi `base_batch_g` khi chưa có dòng nào (công thức sơ chế SC-VQH).
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Annotated, Any, ClassVar, Literal

from ninja import Schema
from pydantic import Field, StringConstraints, model_validator

Code = Annotated[str, StringConstraints(pattern=r"^[A-Z0-9][A-Z0-9-]{0,39}$")]
Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
OutputKindLiteral = Literal["PRODUCT", "INTERMEDIATE"]
RecipeStatusLiteral = Literal["DRAFT", "ACTIVE", "RETIRED"]
Grams = Annotated[Decimal, Field(gt=0, max_digits=10, decimal_places=2)]


class RecipeItemIn(Schema):
    ingredient_id: int = Field(ge=1, le=2147483647)
    qty_g: Grams
    alt_group: int | None = Field(None, ge=1, le=99)
    is_optional: bool = False
    note: str | None = Field(None, max_length=500)


class RecipeIn(Schema):
    code: Code
    name: Text
    output_kind: OutputKindLiteral
    output_ingredient_id: int | None = Field(None, ge=1, le=2147483647)
    base_batch_g: Grams | None = None
    base_label: str | None = Field(None, max_length=200)
    cure_min_days: int = Field(0, ge=0, le=365)
    cure_max_days: int | None = Field(None, ge=0, le=365)
    retain_months: int | None = Field(None, ge=1, le=120)
    note: str | None = Field(None, max_length=2000)
    items: list[RecipeItemIn] = Field(default_factory=list, max_length=50)


class RecipePatch(Schema):
    """Chỉ đổi trường có trong body. Mã và phiên bản không đổi được; dòng thành phần đi qua PUT."""

    name: Text | None = None
    output_kind: OutputKindLiteral | None = None
    output_ingredient_id: int | None = Field(None, ge=1, le=2147483647)
    base_label: str | None = Field(None, max_length=200)
    cure_min_days: int | None = Field(None, ge=0, le=365)
    cure_max_days: int | None = Field(None, ge=0, le=365)
    retain_months: int | None = Field(None, ge=1, le=120)
    note: str | None = Field(None, max_length=2000)
    _NOT_NULL: ClassVar[frozenset[str]] = frozenset({"name", "output_kind", "cure_min_days"})

    @model_validator(mode="after")
    def _reject_null_for_required(self) -> RecipePatch:
        for name in self._NOT_NULL & self.model_fields_set:
            if getattr(self, name) is None:
                raise ValueError(f"{name} không được để trống")
        return self

    def patch_fields(self) -> dict[str, Any]:
        return self.model_dump(exclude_unset=True)


class RecipeItemsPut(Schema):
    """Danh sách dòng mới thay toàn bộ dòng cũ; thứ tự trong mảng là `line_no` 1..n."""

    items: list[RecipeItemIn] = Field(max_length=50)


class RecipeItemOut(Schema):
    id: int
    line_no: int
    ingredient_id: int
    ingredient_code: str
    ingredient_name: str
    qty_g: Decimal
    pct: Decimal  # % khối lượng trên mẻ chuẩn
    alt_group: int | None
    is_optional: bool
    note: str | None


class RecipeOut(Schema):
    id: int
    code: str
    version: int
    name: str
    output_kind: str
    output_ingredient_id: int | None
    output_ingredient_code: str | None
    base_batch_g: Decimal
    base_label: str | None
    cure_min_days: int
    cure_max_days: int | None
    retain_months: int | None
    status: str
    note: str | None
    created_at: datetime
    updated_at: datetime


class RecipeDetailOut(RecipeOut):
    items: list[RecipeItemOut]
    editable: bool  # DRAFT và chưa có lệnh dùng: sửa trực tiếp được


class ScaleItemOut(Schema):
    line_no: int
    ingredient_id: int
    ingredient_code: str
    ingredient_name: str
    qty_g: Decimal
    suggested_g: Decimal
    alt_group: int | None
    is_optional: bool


class ScaleOut(Schema):
    recipe_id: int
    code: str
    version: int
    base_batch_g: Decimal
    batch_g: Decimal
    items: list[ScaleItemOut]
