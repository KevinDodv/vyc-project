"""Router `/api/v1/goods-types` (TK mục 9: GET cả hai vai, ghi chỉ OWNER).

Schema đặt ngay trong file này (ít trường, chỉ router này dùng).
"""

from __future__ import annotations

from typing import Annotated, Any, ClassVar, Literal, cast

from django.http import HttpRequest
from ninja import Router, Schema, Status
from pydantic import StringConstraints, model_validator

from accounts.models import User
from catalog.models import GoodsType
from catalog.services import goods as service
from core.permissions import ANY_STAFF

router = Router(tags=["Loại hàng hóa"])

Code = Annotated[str, StringConstraints(pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]*$", max_length=40)]
Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
GroupLiteral = Literal["MATERIAL", "PRODUCT"]
StatusLiteral = Literal["ACTIVE", "INACTIVE"]


class GoodsTypeIn(Schema):
    code: Code
    name: Text
    grp: GroupLiteral
    is_food: bool = False


class GoodsTypePatch(Schema):
    """Chỉ đổi trường có trong body. Mã không đổi được. `status: INACTIVE` là ngừng dùng."""

    name: Text | None = None
    grp: GroupLiteral | None = None
    is_food: bool | None = None
    status: StatusLiteral | None = None
    _NOT_NULL: ClassVar[frozenset[str]] = frozenset({"name", "grp", "is_food", "status"})

    @model_validator(mode="after")
    def _reject_null_for_required(self) -> GoodsTypePatch:
        for name in self._NOT_NULL & self.model_fields_set:
            if getattr(self, name) is None:
                raise ValueError(f"{name} không được để trống")
        return self

    def patch_fields(self) -> dict[str, Any]:
        return self.model_dump(exclude_unset=True)


class GoodsTypeOut(Schema):
    id: int
    code: str
    name: str
    grp: str
    is_food: bool
    status: str


def _actor(request: HttpRequest) -> User:
    return cast(User, request.user)  # RoleAuth đã chắc chắn là người dùng đăng nhập


@router.get("", auth=ANY_STAFF, response=list[GoodsTypeOut], summary="Danh sách loại hàng hóa")
def list_goods_types(
    request: HttpRequest, status: StatusLiteral | None = None, grp: GroupLiteral | None = None
) -> list[GoodsType]:
    return service.list_goods_types(status=status, grp=grp)


@router.get("/{goods_type_id}", auth=ANY_STAFF, response=GoodsTypeOut, summary="Chi tiết loại hàng")
def get_goods_type(request: HttpRequest, goods_type_id: int) -> GoodsType:
    return service.get_goods_type(goods_type_id)


@router.post("", response={201: GoodsTypeOut}, summary="Tạo loại hàng hóa")
def create_goods_type(request: HttpRequest, payload: GoodsTypeIn) -> Status:
    data = service.GoodsTypeCreate(**payload.model_dump())
    goods_type = service.create_goods_type(data=data, actor=_actor(request))
    return Status(201, GoodsTypeOut.model_validate(goods_type))


@router.patch("/{goods_type_id}", response=GoodsTypeOut, summary="Sửa loại hàng hóa")
def update_goods_type(
    request: HttpRequest, goods_type_id: int, payload: GoodsTypePatch
) -> GoodsType:
    data = service.GoodsTypeUpdate(**payload.patch_fields())
    return service.update_goods_type(goods_type_id=goods_type_id, data=data, actor=_actor(request))
