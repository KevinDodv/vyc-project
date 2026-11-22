"""`?featured=1`, `limit`, `goods_type` của GET /api/public/products; throttle 300/phút."""

from __future__ import annotations

import json
from datetime import timedelta
from typing import Any

import pytest
from django.test import Client
from django.utils import timezone

from catalog.models import GoodsType, Product, ProductStatus
from catalog.tests.conftest import make_product
from core.clientip import ip_hash
from core.models import ThrottleHit

pytestmark = pytest.mark.django_db

URL = "/api/public/products"


def skus(client: Client, query: str = "") -> list[str]:
    r = client.get(f"{URL}{query}")
    assert r.status_code == 200, r.content
    items: list[dict[str, Any]] = json.loads(r.content)
    return [i["sku"] for i in items]


def make(goods_type: GoodsType, sku: str, *, age_days: int = 0, **kw: Any) -> Product:
    """`age_days` càng lớn càng cũ (updated_at do auto_now nên ghi đè bằng update())."""
    product = make_product(goods_type, sku=sku, slug=sku.lower(), name=sku, **kw)
    Product.objects.filter(pk=product.pk).update(
        updated_at=timezone.now() - timedelta(days=age_days)
    )
    return product


def test_featured_filters_and_excludes_unpublished(client: Client, goods_type: GoodsType) -> None:
    make(goods_type, "A", featured_rank=1)
    make(goods_type, "B")  # PUBLISHED nhưng không nổi bật
    make(goods_type, "C", featured_rank=2, status=ProductStatus.DRAFT)
    make(goods_type, "D", featured_rank=3, status=ProductStatus.HIDDEN)
    assert skus(client, "?featured=1") == ["A"]


def test_featured_order_by_rank_not_updated_at(client: Client, goods_type: GoodsType) -> None:
    make(goods_type, "R3", featured_rank=3, age_days=0)  # mới nhất nhưng hạng thấp nhất
    make(goods_type, "R1", featured_rank=1, age_days=20)
    make(goods_type, "R2", featured_rank=2, age_days=10)
    assert skus(client, "?featured=1") == ["R1", "R2", "R3"]


def test_same_rank_newer_first_then_id(client: Client, goods_type: GoodsType) -> None:
    make(goods_type, "OLD", featured_rank=1, age_days=5)
    make(goods_type, "NEW", featured_rank=1, age_days=1)
    assert skus(client, "?featured=1") == ["NEW", "OLD"]


def test_limit_cuts_featured(client: Client, goods_type: GoodsType) -> None:
    for rank, sku in enumerate(["A", "B", "C"], start=1):
        make(goods_type, sku, featured_rank=rank)
    assert skus(client, "?featured=1&limit=2") == ["A", "B"]


def test_without_featured_order_is_updated_at_desc(client: Client, goods_type: GoodsType) -> None:
    make(goods_type, "OLD", featured_rank=1, age_days=30)
    make(goods_type, "MID", age_days=10)
    make(goods_type, "NEW", featured_rank=5, age_days=1)
    assert skus(client) == ["NEW", "MID", "OLD"]
    assert skus(client, "?limit=2") == ["NEW", "MID"]


@pytest.mark.parametrize("value", ["1", "true", "True"])
def test_ninja_accepts_featured_as_bool(client: Client, goods_type: GoodsType, value: str) -> None:
    make(goods_type, "A", featured_rank=1)
    make(goods_type, "B")
    assert skus(client, f"?featured={value}") == ["A"]


@pytest.mark.parametrize("value", ["0", "false"])
def test_featured_false_values_do_not_filter(
    client: Client, goods_type: GoodsType, value: str
) -> None:
    make(goods_type, "A", featured_rank=1)
    make(goods_type, "B")
    assert sorted(skus(client, f"?featured={value}")) == ["A", "B"]


def test_featured_garbage_is_400(client: Client) -> None:
    r = client.get(f"{URL}?featured=maybe")
    assert r.status_code == 400
    assert json.loads(r.content)["code"] == "VALIDATION_ERROR"


@pytest.mark.parametrize("query", ["?limit=0", "?limit=101", "?limit=abc"])
def test_limit_out_of_range_is_400(client: Client, query: str) -> None:
    assert client.get(f"{URL}{query}").status_code == 400


def test_limit_default_50_max_100(client: Client, goods_type: GoodsType) -> None:
    Product.objects.bulk_create(
        Product(
            sku=f"S{i}",
            slug=f"s{i}",
            name=f"S{i}",
            goods_type=goods_type,
            size_label="1",
            unit="chai",
            status=ProductStatus.PUBLISHED,
        )
        for i in range(105)
    )
    assert len(skus(client)) == 50
    assert len(skus(client, "?limit=100")) == 100


def test_goods_type_filter(client: Client, goods_type: GoodsType) -> None:
    tra = GoodsType.objects.get(code="TRA")
    make(goods_type, "OIL")
    make(tra, "TEA")
    assert skus(client, "?goods_type=TRA") == ["TEA"]
    assert skus(client, "?goods_type=TINH_DAU") == ["OIL"]
    assert skus(client, "?goods_type=KHONG_CO") == []
    assert sorted(skus(client)) == ["OIL", "TEA"]


def test_throttle_300_per_minute(client: Client, goods_type: GoodsType) -> None:
    make(goods_type, "A")
    # Test client có REMOTE_ADDR 127.0.0.1 (ngoài dải proxy tin cậy) nên khoá theo IP đó.
    window = timezone.now().replace(second=0, microsecond=0)
    ThrottleHit.objects.create(key=f"content:{ip_hash('127.0.0.1')}", window_start=window, hits=299)
    assert client.get(URL).status_code == 200  # lượt thứ 300
    r = client.get(URL)
    assert r.status_code == 429
    assert json.loads(r.content)["code"] == "RATE_LIMITED"
    assert "Retry-After" in r
    # Trang chi tiết và danh sách trang dùng chung một khoá.
    assert client.get(f"{URL}/a").status_code == 429
    assert client.get("/api/public/pages").status_code == 429
