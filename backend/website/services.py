"""Dựng DTO công khai (BR-17). Trả dict dựng tay theo whitelist, không dump nguyên model.

Chỉ thêm trường vào đây khi đã xác nhận được phép lộ ra ngoài: test_br17_public_product_dto
khoá đúng tập khoá. Service không biết tới schema Ninja; api bọc dict thành `PublicProductOut`.
"""

from __future__ import annotations

import logging
from typing import Any

from django.db.models import QuerySet

from catalog.models import Product, ProductStatus, SlugRedirect
from core.markdown import render_public_markdown
from core.schemas import require_http_url, require_media_path
from website.models import PageStatus, SitePage

logger = logging.getLogger("vyc.website")

BUY_CHANNELS = frozenset({"shopee", "tiktok", "zalo", "other"})
DEFAULT_LIMIT = 50
MAX_LIMIT = 100


def _drop(kind: str, product: Product) -> None:
    """Dữ liệu cũ hoặc sửa tay trong DB không được lọt ra ngoài, cũng không làm trang 500."""
    logger.warning("unsafe_url_dropped", extra={"kind": kind, "product_id": product.pk})


def _public_images(product: Product) -> list[dict[str, Any]]:
    """Giữ đúng khoá của ImageRef (backend.md 6.5); phần tử sai hình dạng hay URL lạ thì bỏ."""
    out: list[dict[str, Any]] = []
    raw = product.images if isinstance(product.images, list) else []
    for item in raw:
        try:
            out.append(
                {
                    "url": require_media_path(str(item["url"])),
                    "alt": str(item.get("alt", "")),
                    "key": str(item["key"]),
                    "w": int(item["w"]),
                    "h": int(item["h"]),
                    "widths": [int(w) for w in item["widths"]],
                }
            )
        except (KeyError, TypeError, ValueError, AttributeError):
            _drop("image", product)
    return out


def _public_buy_links(product: Product) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    raw = product.buy_links if isinstance(product.buy_links, list) else []
    for item in raw:
        try:
            channel = str(item["channel"])
            if channel not in BUY_CHANNELS:
                raise ValueError(channel)
            out.append({"channel": channel, "url": require_http_url(str(item["url"]))})
        except (KeyError, TypeError, ValueError, AttributeError):
            _drop("buy_link", product)
    return out


def _og_image(images: list[dict[str, Any]]) -> str | None:
    """Bản JPEG 1200x630 của ảnh đầu: `/media/img/<key>-og.jpg` (backend.md 6.5)."""
    if not images:
        return None
    try:
        return require_media_path(f"/media/img/{images[0]['key']}-og.jpg")
    except ValueError:
        return None


def _availability(product: Product) -> str:
    """`serial_tracked = false` thì luôn còn hàng.

    Còn lại phải có serial IN_STOCK thuộc lô ACTIVE (backend.md 8). Bảng serial thuộc `operations`,
    chưa dựng ở khung này nên tạm coi là hết hàng; thay bằng một câu EXISTS khi có `operations`.
    """
    return "in_stock" if not product.serial_tracked else "out_of_stock"


def build_public_product(product: Product) -> dict[str, Any]:
    images = _public_images(product)
    return {
        "slug": product.slug,
        "sku": product.sku,
        "name": product.name,
        "spec": product.size_label,
        "unit": product.unit,
        "retail_price": product.retail_price,
        "availability": _availability(product),
        "short_description": product.short_desc,
        "story_html": render_public_markdown(product.story_md),
        "usage_html": render_public_markdown(product.usage_md),
        "images": images,
        "og_image": _og_image(images),
        "buy_links": _public_buy_links(product),
        "seo_title": product.seo_title,
        "seo_description": product.seo_description,
        "updated_at": product.updated_at,
        "origin": None,  # khối «Nguồn gốc»: làm ở GĐ3
    }


def _published() -> QuerySet[Product]:
    return Product.objects.filter(status=ProductStatus.PUBLISHED)


def list_public_products(
    *, goods_type: str | None = None, featured: bool = False, limit: int = DEFAULT_LIMIT
) -> list[dict[str, Any]]:
    """Sản phẩm PUBLISHED. Mặc định mới cập nhật trước; `featured` thì chỉ sản phẩm có hạng,
    hạng tăng dần, cùng hạng thì mới cập nhật trước rồi `id`."""
    qs = _published()
    if goods_type:
        qs = qs.filter(goods_type__code=goods_type)
    if featured:
        qs = qs.filter(featured_rank__isnull=False).order_by("featured_rank", "-updated_at", "id")
    else:
        qs = qs.order_by("-updated_at", "id")
    limit = min(max(limit, 1), MAX_LIMIT)
    return [build_public_product(p) for p in qs[:limit]]


def get_public_product(slug: str) -> dict[str, Any] | None:
    """Tra slug hiện hành, không thấy thì tra slug cũ. Không PUBLISHED hoặc không có: `None`.

    Gọi bằng slug cũ vẫn trả sản phẩm đích với slug mới; Astro so slug rồi tự 301.
    """
    product = _published().filter(slug=slug).first()
    if product is None:
        redirect = SlugRedirect.objects.filter(old_slug=slug).select_related("product").first()
        if redirect is not None and redirect.product.status == ProductStatus.PUBLISHED:
            product = redirect.product
    return build_public_product(product) if product is not None else None


def list_public_pages() -> list[dict[str, Any]]:
    """Trang tĩnh đã xuất bản, cho sitemap."""
    rows = SitePage.objects.filter(status=PageStatus.PUBLISHED).order_by("slug")
    return [{"slug": p.slug, "title": p.title, "updated_at": p.updated_at} for p in rows]
