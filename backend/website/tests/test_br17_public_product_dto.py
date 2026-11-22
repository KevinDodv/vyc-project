"""BR-17: DTO công khai chỉ gồm trường được phép; DRAFT/HIDDEN không lộ; dữ liệu bẩn bị lọc."""

from __future__ import annotations

import json
import logging
from typing import Any

import pytest
from django.test import Client

from catalog.models import GoodsType, ProductStatus
from catalog.tests.conftest import IMAGE, make_product

pytestmark = pytest.mark.django_db

ALLOWED_KEYS = {
    "slug",
    "sku",
    "name",
    "spec",
    "unit",
    "retail_price",
    "availability",
    "short_description",
    "story_html",
    "usage_html",
    "images",
    "og_image",
    "buy_links",
    "seo_title",
    "seo_description",
    "updated_at",
    "origin",
}
ALLOWED_IMAGE_KEYS = {"url", "alt", "key", "w", "h", "widths"}
FORBIDDEN_KEYS = {
    "id",
    "status",
    "featured_rank",
    "recipe_code",
    "requires_retention_sample",
    "serial_tracked",
    "shelf_life_months",
    "goods_type_id",
    "goods_type",
    "story_md",
    "usage_md",
    "short_desc",
    "size_label",
    "created_at",
}


def get(client: Client, url: str) -> Any:
    return client.get(url)


def data(response: Any) -> Any:
    return json.loads(response.content)


def test_dto_key_set_is_exactly_the_whitelist(client: Client, goods_type: GoodsType) -> None:
    make_product(
        goods_type,
        short_desc="Mô tả ngắn",
        story_md="**Câu chuyện**",
        featured_rank=1,
        recipe_code="Q100",
        requires_retention_sample=True,
        shelf_life_months=24,
        images=[IMAGE],
        buy_links=[{"channel": "shopee", "url": "https://shopee.vn/x"}],
        seo_title="Tiêu đề",
    )
    r = get(client, "/api/public/products/tinh-dau-que-van-yen-10ml")
    assert r.status_code == 200
    dto = data(r)
    assert set(dto) == ALLOWED_KEYS
    assert not FORBIDDEN_KEYS & set(dto)
    assert set(dto["images"][0]) == ALLOWED_IMAGE_KEYS
    assert dto["spec"] == "10 ml"
    assert dto["short_description"] == "Mô tả ngắn"
    assert dto["story_html"] == "<p><strong>Câu chuyện</strong></p>"
    assert dto["retail_price"] == 250000
    assert dto["og_image"] == "/media/img/3f/3fa9abc1-og.jpg"
    assert dto["origin"] is None
    assert dto["buy_links"] == [{"channel": "shopee", "url": "https://shopee.vn/x"}]
    assert dto["updated_at"].endswith("Z") or "+" in dto["updated_at"]


def test_list_dto_has_same_key_set(client: Client, goods_type: GoodsType) -> None:
    make_product(goods_type, featured_rank=1)
    items = data(get(client, "/api/public/products"))
    assert len(items) == 1
    assert set(items[0]) == ALLOWED_KEYS


def test_availability(client: Client, goods_type: GoodsType) -> None:
    make_product(goods_type, sku="A", slug="a", serial_tracked=False)
    assert data(get(client, "/api/public/products/a"))["availability"] == "in_stock"


@pytest.mark.parametrize("status", [ProductStatus.DRAFT, ProductStatus.HIDDEN])
def test_unpublished_is_404_and_not_listed(
    client: Client, goods_type: GoodsType, status: ProductStatus
) -> None:
    make_product(goods_type, status=status)
    r = get(client, "/api/public/products/tinh-dau-que-van-yen-10ml")
    assert r.status_code == 404
    assert data(r)["code"] == "NOT_FOUND"
    assert data(get(client, "/api/public/products")) == []


def test_unknown_slug_is_404(client: Client) -> None:
    r = get(client, "/api/public/products/khong-co")
    assert (r.status_code, data(r)["code"]) == (404, "NOT_FOUND")


def test_story_markdown_is_sanitized(client: Client, goods_type: GoodsType) -> None:
    make_product(
        goods_type,
        story_md=(
            "[x](javascript:alert(1))\n\n<script>alert(1)</script>\n\n"
            '<img src=x onerror=alert(1)>\n\n<a href="#" onclick="evil()">y</a>'
        ),
        usage_md="<iframe src='https://evil.com'></iframe>Dùng vài giọt",
    )
    dto = data(get(client, "/api/public/products/tinh-dau-que-van-yen-10ml"))
    for html in (dto["story_html"], dto["usage_html"]):
        for bad in ("<script", "<iframe", "<img", "onerror", "onclick", "javascript:", "alert(1)"):
            assert bad not in html
    assert "Dùng vài giọt" in dto["usage_html"]


def test_unsafe_urls_already_in_db_are_dropped_not_500(
    client: Client, goods_type: GoodsType, caplog: pytest.LogCaptureFixture
) -> None:
    make_product(
        goods_type,
        images=[
            IMAGE,
            {**IMAGE, "url": "https://evil.com/a.webp"},
            {**IMAGE, "url": "/media/%2e%2e/x"},
            {"url": "/media/ok.webp"},  # thiếu khoá
            "không phải dict",
        ],
        buy_links=[
            {"channel": "shopee", "url": "javascript:alert(1)"},
            {"channel": "zalo", "url": "//evil.com"},
            {"channel": "tiktok", "url": "https://shop.tiktok.com/x"},
            {"channel": "khac", "url": "https://ok.vn"},
        ],
    )
    with caplog.at_level(logging.WARNING, logger="vyc.website"):
        r = get(client, "/api/public/products/tinh-dau-que-van-yen-10ml")
    assert r.status_code == 200
    dto = data(r)
    assert [i["url"] for i in dto["images"]] == [IMAGE["url"]]
    assert dto["buy_links"] == [{"channel": "tiktok", "url": "https://shop.tiktok.com/x"}]
    assert sum(rec.message == "unsafe_url_dropped" for rec in caplog.records) == 7


def test_image_extra_keys_are_not_leaked(client: Client, goods_type: GoodsType) -> None:
    make_product(goods_type, images=[{**IMAGE, "internal_path": "D:/secret", "exif": {"gps": 1}}])
    dto = data(get(client, "/api/public/products/tinh-dau-que-van-yen-10ml"))
    assert set(dto["images"][0]) == ALLOWED_IMAGE_KEYS


def test_no_images_means_no_og_image(client: Client, goods_type: GoodsType) -> None:
    make_product(goods_type)
    dto = data(get(client, "/api/public/products/tinh-dau-que-van-yen-10ml"))
    assert dto["images"] == [] and dto["og_image"] is None
    assert dto["story_html"] is None


def test_public_api_is_get_only(client: Client, goods_type: GoodsType) -> None:
    make_product(goods_type)
    for method in (client.post, client.patch, client.put, client.delete):
        r = method("/api/public/products/tinh-dau-que-van-yen-10ml")
        assert r.status_code == 405, method


def test_pages_lists_only_published(client: Client) -> None:
    from website.models import PageStatus, SitePage

    SitePage.objects.create(
        slug="cau-chuyen", title="Câu chuyện", body_md="x", status=PageStatus.PUBLISHED
    )
    SitePage.objects.create(slug="nhap", title="Nháp", body_md="x", status=PageStatus.DRAFT)
    items = data(get(client, "/api/public/pages"))
    assert [(p["slug"], p["title"]) for p in items] == [("cau-chuyen", "Câu chuyện")]
    assert set(items[0]) == {"slug", "title", "updated_at"}
