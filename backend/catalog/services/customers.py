"""Service khách hàng (người mua): tạo, sửa, ngừng dùng (TK mục 5, dòng «Khách hàng»).

Mã `KH-NNNN` sinh ở đây qua `core.codes.customer_code` (BR-20), không đếm lại. Model gọi
`full_clean()` trước khi lưu; lỗi thành 400 VALIDATION_ERROR kèm `details.field`.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import Any

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q, QuerySet

from catalog.models import ActiveStatus, Customer
from catalog.services.products import UNSET, _Unset
from core import audit, codes
from core.errors import ApiError
from core.roles import Actor


@dataclass(frozen=True)
class CustomerCreate:
    name: str
    kind: str
    phone: str | None = None
    address: str | None = None


@dataclass(frozen=True)
class CustomerUpdate:
    """Mỗi trường mặc định UNSET: chỉ trường được gửi mới đổi. `None` nghĩa là xoá giá trị."""

    name: str | _Unset = UNSET
    kind: str | _Unset = UNSET
    phone: str | _Unset | None = UNSET
    address: str | _Unset | None = UNSET
    status: str | _Unset = UNSET


def full_clean(obj: Customer) -> None:
    """`full_clean()` của model; lỗi thành 400 VALIDATION_ERROR theo trường (`details.field`)."""
    try:
        obj.full_clean(validate_unique=False, validate_constraints=False)
    except ValidationError as exc:
        errors = [
            {"field": field, "message": message}
            for field, messages in exc.message_dict.items()
            for message in messages
        ]
        first = errors[0]
        raise ApiError(
            "VALIDATION_ERROR", first["message"], status=400, field=first["field"], errors=errors
        ) from exc


def list_customers(
    *, q: str | None = None, kind: str | None = None, status: str | None = None
) -> QuerySet[Customer]:
    qs = Customer.objects.order_by("name", "id")
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(code__icontains=q) | Q(phone__icontains=q))
    if kind:
        qs = qs.filter(kind=kind)
    if status:
        qs = qs.filter(status=status)
    return qs


def get_customer(customer_id: int) -> Customer:
    return Customer.objects.get(pk=customer_id)


@transaction.atomic
def create_customer(*, data: CustomerCreate, actor: Actor) -> Customer:
    customer = Customer(
        code="KH-TMP",  # mã thật cấp sau khi dữ liệu hợp lệ, để lỗi nhập liệu không đốt số
        name=data.name,
        kind=data.kind,
        phone=data.phone,
        address=data.address,
        status=ActiveStatus.ACTIVE,
    )
    full_clean(customer)
    customer.code = codes.customer_code()
    customer.save()
    audit.record(actor, customer, "CREATE")
    return customer


@transaction.atomic
def update_customer(*, customer_id: int, data: CustomerUpdate, actor: Actor) -> Customer:
    """Sửa một phần. Không đổi gì thì không ghi audit_log."""
    customer = Customer.objects.select_for_update().get(pk=customer_id)
    changes: dict[str, Any] = {
        f.name: getattr(data, f.name)
        for f in dataclasses.fields(data)
        if getattr(data, f.name) is not UNSET
    }
    changes = {k: v for k, v in changes.items() if getattr(customer, k) != v}
    if not changes:
        return customer
    before = audit.snapshot(customer)
    for name, value in changes.items():
        setattr(customer, name, value)
    full_clean(customer)
    customer.save()
    audit.record(actor, customer, "UPDATE", before=before)
    return customer
