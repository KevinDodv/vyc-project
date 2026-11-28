"""Router `/api/v1/areas` (TK mục 9: GET cả hai vai, ghi chỉ OWNER; INACTIVE = ngừng dùng).

Route ghi không khai `auth` nên rơi về `OWNER_ONLY` mặc định của `api_v1`.
"""

from __future__ import annotations

from typing import cast

from django.http import HttpRequest
from ninja import Router, Status

from accounts.models import User
from catalog.api.schemas.areas import AreaIn, AreaNode, AreaOut, AreaPatch
from catalog.models import Area
from catalog.services import areas as service
from core.permissions import ANY_STAFF

router = Router(tags=["Địa bàn"])


def _actor(request: HttpRequest) -> User:
    return cast(User, request.user)  # RoleAuth đã chắc chắn là người dùng đăng nhập


def _node(tree_node: service.AreaTreeNode) -> AreaNode:
    base = AreaOut.model_validate(tree_node.area)
    return AreaNode(**base.model_dump(), children=[_node(c) for c in tree_node.children])


@router.get("", auth=ANY_STAFF, response=list[AreaNode], summary="Cây địa bàn Tỉnh > Xã > Thôn")
def list_areas(request: HttpRequest) -> list[AreaNode]:
    return [_node(n) for n in service.list_tree()]


@router.get("/{area_id}", auth=ANY_STAFF, response=AreaOut, summary="Chi tiết địa bàn")
def get_area(request: HttpRequest, area_id: int) -> Area:
    return service.get_area(area_id)


@router.post("", response={201: AreaOut}, summary="Tạo địa bàn")
def create_area(request: HttpRequest, payload: AreaIn) -> Status:
    data = service.AreaCreate(**payload.model_dump())
    area = service.create_area(data=data, actor=_actor(request))
    return Status(201, AreaOut.model_validate(area))


@router.patch("/{area_id}", response=AreaOut, summary="Sửa địa bàn")
def update_area(request: HttpRequest, area_id: int, payload: AreaPatch) -> Area:
    data = service.AreaUpdate(**payload.patch_fields())
    return service.update_area(area_id=area_id, data=data, actor=_actor(request))
