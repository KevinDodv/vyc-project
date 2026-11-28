"""Router `/api/v1/customers` (TK mục 9: GET cả hai vai, ghi chỉ OWNER).

Route ghi không khai `auth` nên rơi về `OWNER_ONLY` mặc định của `api_v1`.
"""

from __future__ import annotations

from typing import cast

from django.http import HttpRequest
from ninja import Query, Router, Status

from accounts.models import User
from catalog.api.schemas.customers import CustomerIn, CustomerOut, CustomerPatch
from catalog.services import customers as service
from core.pagination import DEFAULT_PAGE_SIZE, Page, paginate
from core.permissions import ANY_STAFF

router = Router(tags=["Danh mục"])


def _actor(request: HttpRequest) -> User:
    return cast(User, request.user)  # RoleAuth đã chắc chắn là người dùng đăng nhập


@router.get("", auth=ANY_STAFF, response=Page[CustomerOut], summary="Danh sách khách hàng")
def list_customers(
    request: HttpRequest,
    page: int = Query(1, ge=1),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=200),
    q: str | None = None,
    kind: str | None = None,
    status: str | None = None,
) -> Page[CustomerOut]:
    rows, total = paginate(service.list_customers(q=q, kind=kind, status=status), page, page_size)
    items = [CustomerOut.model_validate(c) for c in rows]
    return Page[CustomerOut](items=items, total=total, page=page, page_size=page_size)


@router.get("/{customer_id}", auth=ANY_STAFF, response=CustomerOut, summary="Chi tiết khách hàng")
def get_customer(request: HttpRequest, customer_id: int) -> CustomerOut:
    return CustomerOut.model_validate(service.get_customer(customer_id))


@router.post("", response={201: CustomerOut}, summary="Tạo khách hàng (mã KH-NNNN tự sinh)")
def create_customer(request: HttpRequest, payload: CustomerIn) -> Status:
    data = service.CustomerCreate(**payload.model_dump())
    customer = service.create_customer(data=data, actor=_actor(request))
    return Status(201, CustomerOut.model_validate(customer))


@router.patch("/{customer_id}", response=CustomerOut, summary="Sửa hoặc ngừng dùng khách hàng")
def update_customer(request: HttpRequest, customer_id: int, payload: CustomerPatch) -> CustomerOut:
    data = service.CustomerUpdate(**payload.patch_fields())
    customer = service.update_customer(customer_id=customer_id, data=data, actor=_actor(request))
    return CustomerOut.model_validate(customer)
