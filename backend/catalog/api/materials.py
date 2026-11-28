"""Router `/api/v1/materials` kèm hạng (TK mục 9: GET cả hai vai, ghi chỉ OWNER).

Danh sách nhỏ cố định (2 nguyên liệu) nên trả mảng thường, không phân trang (backend.md 3.3).
"""

from __future__ import annotations

from typing import Literal, cast

from django.http import HttpRequest
from ninja import Router, Status

from accounts.models import User
from catalog.api.schemas.materials import GradeIn, MaterialIn, MaterialOut, MaterialPatch
from catalog.models import Material
from catalog.services import materials as service
from core.permissions import ANY_STAFF

router = Router(tags=["Nguyên vật liệu"])


def _actor(request: HttpRequest) -> User:
    return cast(User, request.user)  # RoleAuth đã chắc chắn là người dùng đăng nhập


def _grades(items: list[GradeIn]) -> list[service.GradeInput]:
    return [service.GradeInput(**g.model_dump()) for g in items]


@router.get(
    "", auth=ANY_STAFF, response=list[MaterialOut], summary="Danh sách nguyên liệu kèm hạng"
)
def list_materials(
    request: HttpRequest, status: Literal["ACTIVE", "INACTIVE"] | None = None
) -> list[Material]:
    return service.list_materials(status=status)


@router.get("/{material_id}", auth=ANY_STAFF, response=MaterialOut, summary="Chi tiết nguyên liệu")
def get_material(request: HttpRequest, material_id: int) -> Material:
    return service.get_material(material_id)


@router.post("", response={201: MaterialOut}, summary="Tạo nguyên liệu (kèm hạng)")
def create_material(request: HttpRequest, payload: MaterialIn) -> Status:
    data = service.MaterialCreate(
        **payload.model_dump(exclude={"grades"}), grades=_grades(payload.grades)
    )
    material = service.create_material(data=data, actor=_actor(request))
    return Status(201, MaterialOut.model_validate(material))


@router.patch("/{material_id}", response=MaterialOut, summary="Sửa nguyên liệu và hạng")
def update_material(request: HttpRequest, material_id: int, payload: MaterialPatch) -> Material:
    fields = payload.patch_fields()
    if payload.grades is not None:
        fields["grades"] = _grades(payload.grades)
    data = service.MaterialUpdate(**fields)
    return service.update_material(material_id=material_id, data=data, actor=_actor(request))
