"""Schema vào/ra của `/api/v1/areas` (backend.md 8, TK mục 5 «Địa bàn»).

`AreaNode` là nút của cây Tỉnh > Xã > Thôn: `children` lồng nhau theo cấp.
`AreaPatch` phân biệt «không gửi» với «gửi null» bằng `model_fields_set` (xem `patch_fields`).
"""

from __future__ import annotations

from datetime import date
from typing import Annotated, Any, ClassVar, Literal

from ninja import Schema
from pydantic import Field, StringConstraints, model_validator

Code = Annotated[str, StringConstraints(pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]*$", max_length=40)]
Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
AreaLevelLiteral = Literal["PROVINCE", "COMMUNE", "VILLAGE"]
ActiveStatusLiteral = Literal["ACTIVE", "INACTIVE"]


class AreaIn(Schema):
    code: Code
    level: AreaLevelLiteral
    name: Text
    parent_id: int | None = None  # bắt buộc với xã, thôn; tỉnh thì để trống
    former_name: str | None = Field(None, max_length=200)
    valid_from: date | None = None  # mặc định 01/07/2025
    valid_to: date | None = None


class AreaPatch(Schema):
    """Chỉ đổi trường có trong body. Cấp và mã không đổi được. `status: INACTIVE` là ngừng dùng."""

    name: Text | None = None
    parent_id: int | None = None
    former_name: str | None = Field(None, max_length=200)
    valid_from: date | None = None
    valid_to: date | None = None
    status: ActiveStatusLiteral | None = None
    # Cột NOT NULL: gửi `null` là sai (khác parent_id, former_name, valid_to cho phép null).
    _NOT_NULL: ClassVar[frozenset[str]] = frozenset({"name", "valid_from", "status"})

    @model_validator(mode="after")
    def _reject_null_for_required(self) -> AreaPatch:
        for name in self._NOT_NULL & self.model_fields_set:
            if getattr(self, name) is None:
                raise ValueError(f"{name} không được để trống")
        return self

    def patch_fields(self) -> dict[str, Any]:
        """Các trường client thật sự gửi."""
        return self.model_dump(exclude_unset=True)


class AreaOut(Schema):
    id: int
    code: str
    level: str
    name: str
    parent_id: int | None
    former_name: str | None
    valid_from: date
    valid_to: date | None
    status: str


class AreaNode(AreaOut):
    children: list[AreaNode] = Field(default_factory=list)


AreaNode.model_rebuild()
