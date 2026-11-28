"""Schema vào/ra của `/api/v1/materials` (backend.md 8, TK mục 5 «Nguyên vật liệu»).

Hạng (`grades`) đi cùng nguyên liệu: POST gửi danh sách hạng đầu tiên; PATCH gửi hạng mới (không
`id`) hoặc hạng cần sửa (có `id`, đổi được tên và trạng thái, không đổi được bậc).
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any, ClassVar, Literal

from ninja import Schema
from pydantic import Field, StringConstraints, model_validator

from core.schemas import SafeMediaPath

Code = Annotated[str, StringConstraints(pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]*$", max_length=40)]
Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
ActiveStatusLiteral = Literal["ACTIVE", "INACTIVE"]


class GradeIn(Schema):
    id: int | None = None  # không có: hạng mới
    rank: int  # 1-9, kiểm ở service để báo tiếng Việt
    name: Text
    status: ActiveStatusLiteral | None = None


class MaterialIn(Schema):
    code: Code
    name: Text
    goods_type_id: int
    image_url: SafeMediaPath | None = None
    sort_order: int = Field(0, ge=0, le=9999)
    grades: list[GradeIn] = Field(default_factory=list, max_length=9)


class MaterialPatch(Schema):
    """Chỉ đổi trường có trong body. Mã không đổi được. `status: INACTIVE` là ngừng dùng."""

    name: Text | None = None
    goods_type_id: int | None = None
    image_url: SafeMediaPath | None = None
    sort_order: int | None = Field(None, ge=0, le=9999)
    status: ActiveStatusLiteral | None = None
    grades: list[GradeIn] | None = Field(None, max_length=9)
    # Cột NOT NULL (image_url cho phép null: bỏ ảnh).
    _NOT_NULL: ClassVar[frozenset[str]] = frozenset(
        {"name", "goods_type_id", "sort_order", "status", "grades"}
    )

    @model_validator(mode="after")
    def _reject_null_for_required(self) -> MaterialPatch:
        for name in self._NOT_NULL & self.model_fields_set:
            if getattr(self, name) is None:
                raise ValueError(f"{name} không được để trống")
        return self

    def patch_fields(self) -> dict[str, Any]:
        """Các trường client thật sự gửi, đã đổi schema con thành dict."""
        return self.model_dump(exclude_unset=True)


class GradeOut(Schema):
    id: int
    material_id: int
    rank: int
    name: str
    status: str


class MaterialOut(Schema):
    id: int
    code: str
    name: str
    goods_type_id: int
    image_url: str | None
    sort_order: int
    status: str
    grades: list[GradeOut]
    created_at: datetime
    updated_at: datetime
