"""DTO công khai (BR-17). Chỉ những trường trang sản phẩm cần; không có `status`, `featured_rank`,
`recipe_code`, `requires_retention_sample`, `serial_tracked` hay trường nội bộ khác.

Tên trường theo frontend-seo.md mục 11 (G5). Dựng tay trong `website.services`, không dump model.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from ninja import Schema

from core.schemas import BuyLink, SafeMediaPath


class ImageRef(Schema):
    """Ảnh đã xử lý ở backend (backend.md 6.5). Bản lớn nhất ở `url`, các bề rộng ở `widths`."""

    url: SafeMediaPath
    alt: str
    key: str
    w: int
    h: int
    widths: list[int]


class PublicOrigin(Schema):
    """Khối «Nguồn gốc» (mục 8.2). Khung để trống, làm ở GĐ3."""


class PublicProductOut(Schema):
    slug: str  # slug hiện hành; gọi bằng slug cũ thì vẫn 200 với slug mới ở đây
    sku: str
    name: str
    spec: str  # = product.size_label ("10 ml")
    unit: str
    retail_price: int | None
    availability: Literal["in_stock", "out_of_stock"]
    short_description: str | None
    story_html: str | None
    usage_html: str | None
    images: list[ImageRef]
    og_image: SafeMediaPath | None
    buy_links: list[BuyLink]
    seo_title: str | None
    seo_description: str | None
    updated_at: datetime
    origin: PublicOrigin | None


class PublicPageOut(Schema):
    slug: str
    title: str
    updated_at: datetime
