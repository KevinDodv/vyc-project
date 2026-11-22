"""Router `/api/v1/products` (backend.md 8, TK mục 9: GET cả hai vai, ghi chỉ OWNER).

Route ghi không khai `auth` nên rơi về `OWNER_ONLY` mặc định của `api_v1`.
"""

from __future__ import annotations

from typing import cast

from django.db.models import Q
from django.http import HttpRequest
from ninja import Query, Router, Status

from accounts.models import User
from catalog.api.schemas.products import (
    ProductIn,
    ProductOut,
    ProductOwnerOut,
    ProductPatch,
)
from catalog.models import Product
from catalog.services import products as service
from core.pagination import DEFAULT_PAGE_SIZE, Page, paginate
from core.permissions import ANY_STAFF, pick_out
from core.roles import Role

router = Router(tags=["Danh mục"])


def _actor(request: HttpRequest) -> User:
    return cast(User, request.user)  # RoleAuth đã chắc chắn là người dùng đăng nhập


def _out(actor: User, product: Product) -> ProductOut:
    return pick_out(actor, ProductOwnerOut, ProductOut, product)


@router.get(
    "",
    auth=ANY_STAFF,
    response=Page[ProductOwnerOut] | Page[ProductOut],
    summary="Danh sách sản phẩm",
)
def list_products(
    request: HttpRequest,
    page: int = Query(1, ge=1),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=200),
    status: str | None = None,
    goods_type_id: int | None = None,
    q: str | None = None,
) -> Page[ProductOwnerOut] | Page[ProductOut]:
    actor = _actor(request)
    qs = Product.objects.order_by("name", "id")
    if status:
        qs = qs.filter(status=status)
    if goods_type_id is not None:
        qs = qs.filter(goods_type_id=goods_type_id)
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(sku__icontains=q))
    rows, total = paginate(qs, page, page_size)
    if actor.role == Role.OWNER:
        owner_items = [ProductOwnerOut.model_validate(p) for p in rows]
        return Page[ProductOwnerOut](items=owner_items, total=total, page=page, page_size=page_size)
    items = [ProductOut.model_validate(p) for p in rows]
    return Page[ProductOut](items=items, total=total, page=page, page_size=page_size)


@router.get(
    "/{product_id}",
    auth=ANY_STAFF,
    response=ProductOwnerOut | ProductOut,
    summary="Chi tiết sản phẩm",
)
def get_product(request: HttpRequest, product_id: int) -> ProductOut:
    return _out(_actor(request), Product.objects.get(pk=product_id))


@router.post("", response={201: ProductOwnerOut}, summary="Tạo sản phẩm (DRAFT)")
def create_product(request: HttpRequest, payload: ProductIn) -> Status:
    data = service.ProductCreate(**payload.model_dump())  # schema con đã thành dict
    product = service.create_product(data=data, actor=_actor(request))
    return Status(201, ProductOwnerOut.model_validate(product))


@router.patch("/{product_id}", response=ProductOwnerOut, summary="Sửa sản phẩm")
def update_product(request: HttpRequest, product_id: int, payload: ProductPatch) -> ProductOwnerOut:
    data = service.ProductUpdate(**payload.patch_fields())
    product = service.update_product(product_id=product_id, data=data, actor=_actor(request))
    return ProductOwnerOut.model_validate(product)
