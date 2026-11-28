"""Router `/api/v1/ingredients` (TK mục 9: GET cả hai vai, ghi chỉ OWNER).

Danh sách nhỏ cố định (19 phụ liệu) nên trả mảng thường, không phân trang (backend.md 3.3).
"""

from __future__ import annotations

from typing import Literal, cast

from django.http import HttpRequest
from ninja import Router, Status

from accounts.models import User
from catalog.api.schemas.ingredients import IngredientIn, IngredientOut, IngredientPatch
from catalog.models import Ingredient
from catalog.services import ingredients as service
from core.permissions import ANY_STAFF

router = Router(tags=["Phụ liệu"])

KindFilter = Literal["ESSENTIAL_OIL", "SOLVENT", "WAX", "MINERAL", "BOTANICAL", "BLEND", "OTHER"]


def _actor(request: HttpRequest) -> User:
    return cast(User, request.user)  # RoleAuth đã chắc chắn là người dùng đăng nhập


@router.get("", auth=ANY_STAFF, response=list[IngredientOut], summary="Danh sách phụ liệu")
def list_ingredients(
    request: HttpRequest,
    status: Literal["ACTIVE", "INACTIVE"] | None = None,
    kind: KindFilter | None = None,
) -> list[Ingredient]:
    return service.list_ingredients(status=status, kind=kind)


@router.get("/{ingredient_id}", auth=ANY_STAFF, response=IngredientOut, summary="Chi tiết phụ liệu")
def get_ingredient(request: HttpRequest, ingredient_id: int) -> Ingredient:
    return Ingredient.objects.get(pk=ingredient_id)


@router.post("", response={201: IngredientOut}, summary="Tạo phụ liệu")
def create_ingredient(request: HttpRequest, payload: IngredientIn) -> Status:
    data = service.IngredientCreate(**payload.model_dump())
    ingredient = service.create_ingredient(data=data, actor=_actor(request))
    return Status(201, IngredientOut.model_validate(ingredient))


@router.patch("/{ingredient_id}", response=IngredientOut, summary="Sửa hoặc ngừng dùng phụ liệu")
def update_ingredient(
    request: HttpRequest, ingredient_id: int, payload: IngredientPatch
) -> Ingredient:
    data = service.IngredientUpdate(**payload.patch_fields())
    return service.update_ingredient(ingredient_id=ingredient_id, data=data, actor=_actor(request))
