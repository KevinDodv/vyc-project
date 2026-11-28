"""Router `/api/v1/recipes` (TK mục 9: GET cả hai vai, ghi chỉ OWNER; BR-26).

Route ghi không khai `auth` nên rơi về `OWNER_ONLY` mặc định của `api_v1`.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated, Literal, cast

from django.http import HttpRequest
from ninja import Query, Router, Status

from accounts.models import User
from catalog.api.schemas.recipes import (
    RecipeDetailOut,
    RecipeIn,
    RecipeItemIn,
    RecipeItemOut,
    RecipeItemsPut,
    RecipeOut,
    RecipePatch,
    ScaleItemOut,
    ScaleOut,
)
from catalog.models import Recipe
from catalog.services import recipes as service
from core.permissions import ANY_STAFF

router = Router(tags=["Công thức"])

BatchG = Annotated[Decimal, Query(gt=0, max_digits=12, decimal_places=2)]


def _actor(request: HttpRequest) -> User:
    return cast(User, request.user)  # RoleAuth đã chắc chắn là người dùng đăng nhập


def _items(items: list[RecipeItemIn]) -> list[service.RecipeItemInput]:
    return [service.RecipeItemInput(**i.model_dump()) for i in items]


def _out(recipe: Recipe) -> RecipeOut:
    out = recipe.output_ingredient
    return RecipeOut(
        id=recipe.pk,
        code=recipe.code,
        version=recipe.version,
        name=recipe.name,
        output_kind=recipe.output_kind,
        output_ingredient_id=recipe.output_ingredient_id,
        output_ingredient_code=out.code if out else None,
        base_batch_g=recipe.base_batch_g,
        base_label=recipe.base_label,
        cure_min_days=recipe.cure_min_days,
        cure_max_days=recipe.cure_max_days,
        retain_months=recipe.retain_months,
        status=recipe.status,
        note=recipe.note,
        created_at=recipe.created_at,
        updated_at=recipe.updated_at,
    )


def _detail(recipe: Recipe) -> RecipeDetailOut:
    items = [
        RecipeItemOut(
            id=i.pk,
            line_no=i.line_no,
            ingredient_id=i.ingredient_id,
            ingredient_code=i.ingredient.code,
            ingredient_name=i.ingredient.name,
            qty_g=i.qty_g,
            pct=service.item_pct(i.qty_g, recipe.base_batch_g),
            alt_group=i.alt_group,
            is_optional=i.is_optional,
            note=i.note,
        )
        for i in recipe.items.all()
    ]
    return RecipeDetailOut(
        **_out(recipe).model_dump(), items=items, editable=service.is_editable(recipe)
    )


@router.get("", auth=ANY_STAFF, response=list[RecipeOut], summary="Danh sách công thức")
def list_recipes(
    request: HttpRequest,
    code: str | None = Query(None, max_length=40),
    status: Literal["DRAFT", "ACTIVE", "RETIRED"] | None = None,
    output_kind: Literal["PRODUCT", "INTERMEDIATE"] | None = None,
) -> list[RecipeOut]:
    rows = service.list_recipes(code=code, status=status, output_kind=output_kind)
    return [_out(r) for r in rows]


@router.get("/{recipe_id}", auth=ANY_STAFF, response=RecipeDetailOut, summary="Chi tiết công thức")
def get_recipe(request: HttpRequest, recipe_id: int) -> RecipeDetailOut:
    return _detail(service.get_recipe(recipe_id))


@router.get(
    "/{recipe_id}/scale",
    auth=ANY_STAFF,
    response=ScaleOut,
    summary="Lượng cân gợi ý theo mẻ mong muốn",
)
def scale_recipe(request: HttpRequest, recipe_id: int, batch_g: BatchG) -> ScaleOut:
    recipe, lines = service.scale_recipe(recipe_id=recipe_id, batch_g=batch_g)
    items = [
        ScaleItemOut(
            line_no=ln.item.line_no,
            ingredient_id=ln.item.ingredient_id,
            ingredient_code=ln.item.ingredient.code,
            ingredient_name=ln.item.ingredient.name,
            qty_g=ln.item.qty_g,
            suggested_g=ln.suggested_g,
            alt_group=ln.item.alt_group,
            is_optional=ln.item.is_optional,
        )
        for ln in lines
    ]
    return ScaleOut(
        recipe_id=recipe.pk,
        code=recipe.code,
        version=recipe.version,
        base_batch_g=recipe.base_batch_g,
        batch_g=batch_g.quantize(service.CENT),
        items=items,
    )


@router.post("", response={201: RecipeDetailOut}, summary="Tạo công thức (version 1, DRAFT)")
def create_recipe(request: HttpRequest, payload: RecipeIn) -> Status:
    data = service.RecipeCreate(
        **payload.model_dump(exclude={"items"}), items=_items(payload.items)
    )
    recipe = service.create_recipe(data=data, actor=_actor(request))
    return Status(201, _detail(recipe))


@router.patch("/{recipe_id}", response=RecipeDetailOut, summary="Sửa công thức (chỉ bản DRAFT)")
def update_recipe(request: HttpRequest, recipe_id: int, payload: RecipePatch) -> RecipeDetailOut:
    data = service.RecipeUpdate(**payload.patch_fields())
    return _detail(service.update_recipe(recipe_id=recipe_id, data=data, actor=_actor(request)))


@router.put(
    "/{recipe_id}/items",
    response=RecipeDetailOut,
    summary="Thay toàn bộ dòng thành phần (chỉ bản DRAFT)",
)
def put_items(request: HttpRequest, recipe_id: int, payload: RecipeItemsPut) -> RecipeDetailOut:
    recipe = service.replace_items(
        recipe_id=recipe_id, items=_items(payload.items), actor=_actor(request)
    )
    return _detail(recipe)


@router.post(
    "/{recipe_id}/new-version",
    response={201: RecipeDetailOut},
    summary="Tạo phiên bản mới (sao chép, version + 1, DRAFT)",
)
def new_version(request: HttpRequest, recipe_id: int) -> Status:
    recipe = service.new_version(recipe_id=recipe_id, actor=_actor(request))
    return Status(201, _detail(recipe))


@router.post(
    "/{recipe_id}/activate",
    response=RecipeDetailOut,
    summary="Kích hoạt bản DRAFT (bản ACTIVE cũ → RETIRED)",
)
def activate(request: HttpRequest, recipe_id: int) -> RecipeDetailOut:
    return _detail(service.activate(recipe_id=recipe_id, actor=_actor(request)))


@router.post("/{recipe_id}/retire", response=RecipeDetailOut, summary="Ngừng dùng bản ACTIVE")
def retire(request: HttpRequest, recipe_id: int) -> RecipeDetailOut:
    return _detail(service.retire(recipe_id=recipe_id, actor=_actor(request)))
