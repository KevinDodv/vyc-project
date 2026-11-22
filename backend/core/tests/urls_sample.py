"""URLconf chỉ dùng cho test: một NinjaAPI nhỏ có đủ kiểu route để thử handler và phân quyền."""

from __future__ import annotations

from django.http import HttpRequest
from django.urls import path
from ninja import NinjaAPI, Query, Schema
from pydantic import Field

from core.errors import ApiError, BusinessError
from core.handlers import register_handlers
from core.pagination import Page, paginate
from core.permissions import ANY_STAFF, OWNER_ONLY
from core.throttle import throttle

sample_api = NinjaAPI(urls_namespace="sample_api", auth=OWNER_ONLY, docs_url=None)
register_handlers(sample_api)


class ItemIn(Schema):
    name: str = Field(min_length=1)
    qty: int = Field(ge=1)


@sample_api.get("/owner")
def owner_route(request: HttpRequest) -> dict[str, str]:
    return {"ok": "owner"}


@sample_api.get("/staff", auth=ANY_STAFF)
def staff_route(request: HttpRequest) -> dict[str, str]:
    return {"ok": "staff"}


@sample_api.post("/items", auth=ANY_STAFF)
def create_item(request: HttpRequest, payload: ItemIn) -> dict[str, str]:
    return {"name": payload.name}


@sample_api.get("/search", auth=None)
def search(request: HttpRequest, q: int = Query(...)) -> dict[str, int]:
    return {"q": q}


@sample_api.get("/business", auth=None)
def business(request: HttpRequest) -> None:
    raise BusinessError(
        "LOT_GENERAL_STREAM", "Lô hàng chung", rule="BR-08", lot_code="NL-2611-0045"
    )


@sample_api.get("/api-error", auth=None)
def api_error(request: HttpRequest) -> None:
    raise ApiError("SLUG_TAKEN", "Slug đã dùng", status=409)


@sample_api.get("/boom", auth=None)
def boom(request: HttpRequest) -> None:
    raise RuntimeError("chi tiết nội bộ không được lộ")


@sample_api.get("/throttled", auth=None)
@throttle("sample", limit=2)
def throttled_route(request: HttpRequest) -> dict[str, str]:
    return {"ok": "yes"}


@sample_api.get("/page", auth=None, response=Page[int])
def page_route(request: HttpRequest, page: int = 1, page_size: int = 2) -> dict[str, object]:
    from core.models import Setting

    rows, total = paginate(Setting.objects.order_by("key"), page, page_size)
    return {
        "items": [len(r.key) for r in rows],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


handler404 = "core.handlers.not_found"
urlpatterns = [path("api/sample/", sample_api.urls)]
