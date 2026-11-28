"""Schema vào/ra của `/api/v1/customers` (TK mục 5, 9)."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any, ClassVar, Literal

from ninja import Schema
from pydantic import StringConstraints, model_validator

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
Phone = Annotated[str, StringConstraints(strip_whitespace=True, max_length=30)]
Address = Annotated[str, StringConstraints(strip_whitespace=True, max_length=500)]
CustomerKindLiteral = Literal["EXPORTER", "AGENT", "CORPORATE", "RETAIL", "MARKETPLACE"]
ActiveStatusLiteral = Literal["ACTIVE", "INACTIVE"]


class CustomerIn(Schema):
    name: Name
    kind: CustomerKindLiteral
    phone: Phone | None = None
    address: Address | None = None


class CustomerPatch(Schema):
    """Chỉ đổi trường có trong body. `phone`/`address` gửi `null` là xoá giá trị."""

    name: Name | None = None
    kind: CustomerKindLiteral | None = None
    phone: Phone | None = None
    address: Address | None = None
    status: ActiveStatusLiteral | None = None
    # Cột NOT NULL: gửi `null` là sai (khác phone/address, nơi null có nghĩa «xoá»).
    _NOT_NULL: ClassVar[frozenset[str]] = frozenset({"name", "kind", "status"})

    @model_validator(mode="after")
    def _reject_null_for_required(self) -> CustomerPatch:
        for name in self._NOT_NULL & self.model_fields_set:
            if getattr(self, name) is None:
                raise ValueError(f"{name} không được để trống")
        return self

    def patch_fields(self) -> dict[str, Any]:
        """Các trường client thật sự gửi."""
        return self.model_dump(exclude_unset=True)


class CustomerOut(Schema):
    id: int
    code: str
    name: str
    kind: str
    phone: str | None
    address: str | None
    status: str
    created_at: datetime
    updated_at: datetime
