"""Router `/api/public`: chỉ GET, không auth, DTO theo BR-17 (backend.md 8).

Không dùng `from __future__ import annotations` ở file này: `@throttle` bọc hàm nên Ninja phải
đọc được kiểu tham số thật, không phải chuỗi.
"""

from typing import Any

from django.http import Http404, HttpRequest
from ninja import Query, Router

from core.throttle import throttle
from website import services
from website.api.schemas.public import PublicPageOut, PublicProductOut

router = Router(tags=["Công khai"])

# 300 lượt/phút mỗi IP cho trang nội dung: Googlebot/AdsBot duyệt nhanh hơn 60 trang/phút (5.2).
CONTENT_LIMIT = 300


@router.get("/products", response=list[PublicProductOut], summary="Danh sách sản phẩm đã đăng")
@throttle("content", limit=CONTENT_LIMIT)
def list_products(
    request: HttpRequest,
    goods_type: str | None = None,
    featured: bool = False,
    limit: int = Query(services.DEFAULT_LIMIT, ge=1, le=services.MAX_LIMIT),
) -> list[dict[str, Any]]:
    return services.list_public_products(goods_type=goods_type, featured=featured, limit=limit)


@router.get("/products/{slug}", response=PublicProductOut, summary="Một sản phẩm theo slug")
@throttle("content", limit=CONTENT_LIMIT)
def get_product(request: HttpRequest, slug: str) -> dict[str, Any]:
    product = services.get_public_product(slug)
    if product is None:
        raise Http404
    return product


@router.get("/pages", response=list[PublicPageOut], summary="Trang tĩnh đã đăng (cho sitemap)")
@throttle("content", limit=CONTENT_LIMIT)
def list_pages(request: HttpRequest) -> list[dict[str, Any]]:
    return services.list_public_pages()
