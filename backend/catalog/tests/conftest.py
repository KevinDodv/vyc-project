"""Fixture và hàm dựng dữ liệu sản phẩm cho test catalog (và website, qua import)."""

from __future__ import annotations

from typing import Any

import pytest

from catalog.models import GoodsType, Product, ProductStatus

IMAGE = {
    "url": "/media/img/3f/3fa9abc1-1440.webp",
    "alt": "Tinh dầu quế 10 ml",
    "key": "3f/3fa9abc1",
    "w": 1440,
    "h": 1080,
    "widths": [480, 960, 1440],
}


@pytest.fixture
def goods_type(db: None) -> GoodsType:
    """Loại hàng seed bởi migration 0002."""
    return GoodsType.objects.get(code="TINH_DAU")


def product_payload(goods_type: GoodsType, **overrides: Any) -> dict[str, Any]:
    """Body hợp lệ của POST /api/v1/products."""
    payload: dict[str, Any] = {
        "sku": "TD10",
        "name": "Tinh dầu quế Văn Yên 10 ml",
        "slug": "tinh-dau-que-van-yen-10ml",
        "goods_type_id": goods_type.pk,
        "size_label": "10 ml",
        "unit": "chai",
        "retail_price": 250000,
    }
    payload.update(overrides)
    return payload


def make_product(goods_type: GoodsType, **overrides: Any) -> Product:
    """Tạo thẳng bằng ORM (bỏ qua service) để dựng dữ liệu cho test đọc."""
    fields: dict[str, Any] = {
        "sku": "TD10",
        "name": "Tinh dầu quế Văn Yên 10 ml",
        "slug": "tinh-dau-que-van-yen-10ml",
        "goods_type": goods_type,
        "size_label": "10 ml",
        "unit": "chai",
        "retail_price": 250000,
        "status": ProductStatus.PUBLISHED,
    }
    fields.update(overrides)
    return Product.objects.create(**fields)
