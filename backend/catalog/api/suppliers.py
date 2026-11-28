"""Router `/api/v1/suppliers` (TK mục 9).

GET cả hai vai (WORKSHOP cần chọn người bán và đồi trên phiếu nhập). POST người bán cả hai vai
(WORKSHOP thêm nhanh: chờ duyệt). Mọi route còn lại không khai `auth` nên rơi về `OWNER_ONLY`.
"""

from __future__ import annotations

from typing import Any, cast

from django.http import HttpRequest
from ninja import Query, Router, Schema, Status

from accounts.models import User
from catalog.api.schemas.suppliers import (
    NoticeOut,
    PlotIn,
    PlotOut,
    PlotPatch,
    SupplierIn,
    SupplierOut,
    SupplierPatch,
    SupplierSavedOut,
)
from catalog.models import Plot, Supplier
from catalog.services import suppliers as service
from core.pagination import DEFAULT_PAGE_SIZE, Page, paginate
from core.permissions import ANY_STAFF

router = Router(tags=["Người bán"])


def _actor(request: HttpRequest) -> User:
    return cast(User, request.user)  # RoleAuth đã chắc chắn là người dùng đăng nhập


def _fields(obj: Any, schema: type[Schema]) -> dict[str, Any]:
    """Các cột của `obj` mà `schema` khai, kèm `area_name` (tên thôn, xã) cho nút bấm."""
    values = {name: getattr(obj, name) for name in schema.model_fields if name != "area_name"}
    values["area_name"] = service.area_label(obj.area)
    return values


def _supplier_out(supplier: Supplier) -> SupplierOut:
    return SupplierOut(**_fields(supplier, SupplierOut))


def _plot_out(plot: Plot) -> PlotOut:
    return PlotOut(**_fields(plot, PlotOut))


def _saved(result: service.SupplierSaved) -> SupplierSavedOut:
    values = _fields(result.supplier, SupplierOut)
    notices = [
        NoticeOut(code=n.code, message=n.message, supplier_ids=n.supplier_ids)
        for n in result.notices
    ]
    return SupplierSavedOut(**values, notices=notices)


@router.get("", auth=ANY_STAFF, response=Page[SupplierOut], summary="Danh sách người bán")
def list_suppliers(
    request: HttpRequest,
    page: int = Query(1, ge=1),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=200),
    q: str | None = None,
    recent: int | None = Query(None, ge=1, le=50),
    status: str | None = None,
    approved: bool | None = None,
    kind: str | None = None,
    stream: str | None = None,
    area_id: int | None = None,
) -> Page[SupplierOut]:
    """`q` tìm không phân biệt dấu (tên, mã, SĐT, thôn). `recent=12`: lưới nút gần đây."""
    qs = service.list_suppliers(
        q=q,
        recent=recent,
        status=status,
        approved=approved,
        kind=kind,
        stream=stream,
        area_id=area_id,
    )
    rows, total = paginate(qs, page, page_size)
    items = [_supplier_out(s) for s in rows]
    return Page[SupplierOut](items=items, total=total, page=page, page_size=page_size)


@router.get("/{supplier_id}", auth=ANY_STAFF, response=SupplierOut, summary="Chi tiết người bán")
def get_supplier(request: HttpRequest, supplier_id: int) -> SupplierOut:
    return _supplier_out(service.get_supplier(supplier_id))


@router.post(
    "",
    auth=ANY_STAFF,
    response={201: SupplierSavedOut},
    summary="Tạo người bán (WORKSHOP: thêm nhanh, chờ duyệt)",
)
def create_supplier(request: HttpRequest, payload: SupplierIn) -> Status:
    data = service.SupplierCreate(**payload.model_dump())
    result = service.create_supplier(data=data, actor=_actor(request))
    return Status(201, _saved(result))


@router.patch("/{supplier_id}", response=SupplierSavedOut, summary="Sửa hoặc ngừng dùng người bán")
def update_supplier(
    request: HttpRequest, supplier_id: int, payload: SupplierPatch
) -> SupplierSavedOut:
    data = service.SupplierUpdate(**payload.patch_fields())
    result = service.update_supplier(supplier_id=supplier_id, data=data, actor=_actor(request))
    return _saved(result)


@router.post("/{supplier_id}/approve", response=SupplierOut, summary="Duyệt người bán thêm nhanh")
def approve_supplier(request: HttpRequest, supplier_id: int) -> SupplierOut:
    supplier = service.approve_supplier(supplier_id=supplier_id, actor=_actor(request))
    return _supplier_out(supplier)


@router.get(
    "/{supplier_id}/plots",
    auth=ANY_STAFF,
    response=list[PlotOut],
    summary="Đồi quế của người bán (đồi mặc định xếp đầu)",
)
def list_plots(request: HttpRequest, supplier_id: int, status: str | None = None) -> list[PlotOut]:
    return [_plot_out(p) for p in service.list_plots(supplier_id, status=status)]


@router.post(
    "/{supplier_id}/plots",
    response={201: PlotOut},
    summary="Thêm đồi quế (mã D-<xã>-<số NCC>-<stt> tự sinh)",
)
def create_plot(request: HttpRequest, supplier_id: int, payload: PlotIn) -> Status:
    data = service.PlotCreate(**payload.model_dump(exclude={"coordinates"}))
    plot = service.create_plot(supplier_id=supplier_id, data=data, actor=_actor(request))
    return Status(201, _plot_out(plot))


@router.patch("/{supplier_id}/plots/{plot_id}", response=PlotOut, summary="Sửa hoặc ngừng dùng đồi")
def update_plot(
    request: HttpRequest, supplier_id: int, plot_id: int, payload: PlotPatch
) -> PlotOut:
    data = service.PlotUpdate(**payload.patch_fields())
    plot = service.update_plot(
        supplier_id=supplier_id, plot_id=plot_id, data=data, actor=_actor(request)
    )
    return _plot_out(plot)
