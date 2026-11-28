"""Schema vào/ra của `/api/v1/ingredients` (TK mục 5 «Phụ liệu», mục 9).

Mã chữ hoa hoặc số, 1-6 ký tự (BR-20). `PATCH {status: "INACTIVE"}` là ngừng dùng (BR-21).
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Annotated, Any, ClassVar, Literal

from ninja import Schema
from pydantic import Field, StringConstraints, model_validator

Code = Annotated[str, StringConstraints(pattern=r"^[A-Z0-9]{1,6}$")]
Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
KindLiteral = Literal["ESSENTIAL_OIL", "SOLVENT", "WAX", "MINERAL", "BOTANICAL", "BLEND", "OTHER"]
ActiveStatusLiteral = Literal["ACTIVE", "INACTIVE"]


class IngredientIn(Schema):
    code: Code
    name: Text
    kind: KindLiteral
    density_g_ml: Decimal | None = Field(None, gt=0, lt=100, max_digits=5, decimal_places=3)
    track_stock: bool = True
    requires_coa: bool = False
    shelf_life_months: int | None = Field(None, ge=1, le=240)


class IngredientPatch(Schema):
    """Chỉ đổi trường có trong body. Đã có lô thì không đổi `code` hay bật `track_stock`."""

    code: Code | None = None
    name: Text | None = None
    kind: KindLiteral | None = None
    density_g_ml: Decimal | None = Field(None, gt=0, lt=100, max_digits=5, decimal_places=3)
    track_stock: bool | None = None
    requires_coa: bool | None = None
    shelf_life_months: int | None = Field(None, ge=1, le=240)
    status: ActiveStatusLiteral | None = None
    # density_g_ml và shelf_life_months cho phép null (xoá giá trị); còn lại là cột NOT NULL.
    _NOT_NULL: ClassVar[frozenset[str]] = frozenset(
        {"code", "name", "kind", "track_stock", "requires_coa", "status"}
    )

    @model_validator(mode="after")
    def _reject_null_for_required(self) -> IngredientPatch:
        for name in self._NOT_NULL & self.model_fields_set:
            if getattr(self, name) is None:
                raise ValueError(f"{name} không được để trống")
        return self

    def patch_fields(self) -> dict[str, Any]:
        return self.model_dump(exclude_unset=True)


class IngredientOut(Schema):
    id: int
    code: str
    name: str
    kind: str
    density_g_ml: Decimal | None
    track_stock: bool
    requires_coa: bool
    shelf_life_months: int | None
    status: str
    created_at: datetime
    updated_at: datetime
