"""Router `/api/v1/certificates` (TK mục 9: GET cả hai vai, ghi chỉ OWNER).

Route ghi không khai `auth` nên rơi về `OWNER_ONLY` mặc định của `api_v1`. Không có xoá: chứng
nhận sai thì sửa, không muốn công khai thì tắt `is_public`.
"""

from __future__ import annotations

from typing import cast

from django.db.models import Q
from django.http import HttpRequest
from ninja import Query, Router, Status

from accounts.models import User
from catalog.api.schemas.certificates import CertificateIn, CertificateOut, CertificatePatch
from catalog.models import Certificate
from catalog.services import certificates as service
from core.pagination import DEFAULT_PAGE_SIZE, Page, paginate
from core.permissions import ANY_STAFF

router = Router(tags=["Chứng nhận"])


def _actor(request: HttpRequest) -> User:
    return cast(User, request.user)  # RoleAuth đã chắc chắn là người dùng đăng nhập


@router.get("", auth=ANY_STAFF, response=Page[CertificateOut], summary="Danh sách chứng nhận")
def list_certificates(
    request: HttpRequest,
    page: int = Query(1, ge=1),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=200),
    kind: str | None = None,
    product_id: int | None = None,
    plot_id: int | None = None,
    is_public: bool | None = None,
    active: bool | None = None,
    q: str | None = None,
) -> Page[CertificateOut]:
    """`active=true`: còn hiệu lực; `active=false`: đã hết hạn."""
    qs = Certificate.objects.order_by("kind", "number", "id")
    if kind:
        qs = qs.filter(kind=kind)
    if product_id is not None:
        qs = qs.filter(product_id=product_id)
    if plot_id is not None:
        qs = qs.filter(plot_id=plot_id)
    if is_public is not None:
        qs = qs.filter(is_public=is_public)
    if active is True:
        qs = qs.filter(service.valid_on())
    elif active is False:
        qs = qs.exclude(service.valid_on())
    if q:
        qs = qs.filter(Q(number__icontains=q) | Q(issuer__icontains=q))
    rows, total = paginate(qs, page, page_size)
    items = [CertificateOut.model_validate(c) for c in rows]
    return Page[CertificateOut](items=items, total=total, page=page, page_size=page_size)


@router.get(
    "/{certificate_id}", auth=ANY_STAFF, response=CertificateOut, summary="Chi tiết chứng nhận"
)
def get_certificate(request: HttpRequest, certificate_id: int) -> CertificateOut:
    return CertificateOut.model_validate(Certificate.objects.get(pk=certificate_id))


@router.post("", response={201: CertificateOut}, summary="Thêm chứng nhận")
def create_certificate(request: HttpRequest, payload: CertificateIn) -> Status:
    data = service.CertificateCreate(**payload.model_dump())
    certificate = service.create_certificate(data=data, actor=_actor(request))
    return Status(201, CertificateOut.model_validate(certificate))


@router.patch("/{certificate_id}", response=CertificateOut, summary="Sửa chứng nhận")
def update_certificate(
    request: HttpRequest, certificate_id: int, payload: CertificatePatch
) -> CertificateOut:
    certificate = service.update_certificate(
        certificate_id=certificate_id, changes=payload.patch_fields(), actor=_actor(request)
    )
    return CertificateOut.model_validate(certificate)
