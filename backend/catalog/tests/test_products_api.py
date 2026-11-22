"""API quản lý sản phẩm: phân quyền, featured_rank, PATCH một phần, đổi slug, audit_log."""

from __future__ import annotations

import json
from typing import Any

import pytest
from django.db import IntegrityError, transaction
from django.test import Client

from catalog.models import GoodsType, Product, SlugRedirect
from catalog.tests.conftest import IMAGE, make_product, product_payload
from core.models import AuditLog

pytestmark = pytest.mark.django_db

URL = "/api/v1/products"


def post(client: Client, payload: dict[str, Any], url: str = URL) -> Any:
    return client.post(url, payload, content_type="application/json")


def patch(client: Client, product_id: int, payload: dict[str, Any]) -> Any:
    return client.patch(f"{URL}/{product_id}", payload, content_type="application/json")


def body(response: Any) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(response.content)
    return data


# ------------------------------------------------------------------ phân quyền


def test_anonymous_gets_401(client: Client, goods_type: GoodsType) -> None:
    assert post(client, product_payload(goods_type)).status_code == 401
    assert client.get(URL).status_code == 401


def test_workshop_cannot_create(workshop_client: Client, goods_type: GoodsType) -> None:
    r = post(workshop_client, product_payload(goods_type))
    assert r.status_code == 403
    assert body(r)["code"] == "FORBIDDEN"
    assert Product.objects.count() == 0


def test_workshop_cannot_patch_featured_rank(
    workshop_client: Client, goods_type: GoodsType
) -> None:
    product = make_product(goods_type, featured_rank=None)
    r = patch(workshop_client, product.pk, {"featured_rank": 1})
    assert r.status_code == 403
    product.refresh_from_db()
    assert product.featured_rank is None


def test_workshop_reads_without_price_owner_with_price(
    workshop_client: Client, owner_client: Client, goods_type: GoodsType
) -> None:
    product = make_product(goods_type)

    detail = body(workshop_client.get(f"{URL}/{product.pk}"))
    assert "retail_price" not in detail
    assert detail["sku"] == "TD10"
    listing = body(workshop_client.get(URL))
    assert listing["total"] == 1
    assert "retail_price" not in listing["items"][0]

    assert body(owner_client.get(f"{URL}/{product.pk}"))["retail_price"] == 250000
    assert body(owner_client.get(URL))["items"][0]["retail_price"] == 250000


# ------------------------------------------------------------------ tạo và audit_log


def test_owner_creates_draft_and_audit_logged(
    owner_client: Client, owner: Any, goods_type: GoodsType
) -> None:
    r = post(owner_client, product_payload(goods_type, images=[IMAGE]))
    assert r.status_code == 201, r.content
    data = body(r)
    assert data["status"] == "DRAFT"
    assert data["featured_rank"] is None
    assert data["images"][0]["key"] == "3f/3fa9abc1"

    log = AuditLog.objects.get(entity="product", entity_id=data["id"])
    assert (log.action, log.user_id) == ("CREATE", owner.pk)
    assert log.after is not None and log.after["sku"] == "TD10"


def test_publish_via_patch_writes_audit(owner_client: Client, goods_type: GoodsType) -> None:
    pid = body(post(owner_client, product_payload(goods_type)))["id"]
    r = patch(owner_client, pid, {"status": "PUBLISHED"})
    assert r.status_code == 200
    assert body(r)["status"] == "PUBLISHED"

    log = AuditLog.objects.filter(entity="product", entity_id=pid, action="UPDATE").get()
    assert log.before is not None and log.before["status"] == "DRAFT"
    assert log.after is not None and log.after["status"] == "PUBLISHED"


def test_noop_patch_writes_no_audit(owner_client: Client, goods_type: GoodsType) -> None:
    product = make_product(goods_type)
    r = patch(owner_client, product.pk, {"name": product.name})
    assert r.status_code == 200
    assert not AuditLog.objects.filter(entity="product", action="UPDATE").exists()


def test_create_rejects_unknown_goods_type_and_duplicate_sku(
    owner_client: Client, goods_type: GoodsType
) -> None:
    r = post(owner_client, product_payload(goods_type, goods_type_id=999999))
    assert (r.status_code, body(r)["code"]) == (400, "GOODS_TYPE_INVALID")

    assert post(owner_client, product_payload(goods_type)).status_code == 201
    r = post(owner_client, product_payload(goods_type, slug="slug-khac"))
    assert (r.status_code, body(r)["code"]) == (409, "SKU_TAKEN")


def test_unknown_product_is_404(owner_client: Client) -> None:
    assert owner_client.get(f"{URL}/999999").status_code == 404
    assert patch(owner_client, 999999, {"name": "x"}).status_code == 404


# ------------------------------------------------------------------ featured_rank


def test_featured_rank_zero_is_400_and_db_check(
    owner_client: Client, goods_type: GoodsType
) -> None:
    r = post(owner_client, product_payload(goods_type, featured_rank=0))
    assert (r.status_code, body(r)["code"]) == (400, "VALIDATION_ERROR")

    product = make_product(goods_type)
    r = patch(owner_client, product.pk, {"featured_rank": 0})
    assert (r.status_code, body(r)["code"]) == (400, "VALIDATION_ERROR")

    # CHECK ở DB: ghi thẳng 0 vẫn bị chặn.
    with pytest.raises(IntegrityError), transaction.atomic():
        Product.objects.filter(pk=product.pk).update(featured_rank=0)


def test_owner_sets_featured_rank(owner_client: Client, goods_type: GoodsType) -> None:
    product = make_product(goods_type)
    r = patch(owner_client, product.pk, {"featured_rank": 2})
    assert r.status_code == 200
    assert body(r)["featured_rank"] == 2
    log = AuditLog.objects.filter(entity="product", action="UPDATE").get()
    assert log.before is not None and log.before["featured_rank"] is None
    assert log.after is not None and log.after["featured_rank"] == 2


# ------------------------------------------------------------------ #781: không gửi ≠ gửi null


def test_patch_name_only_keeps_featured_rank(owner_client: Client, goods_type: GoodsType) -> None:
    product = make_product(goods_type, featured_rank=3, retail_price=250000, short_desc="Mô tả")
    r = patch(owner_client, product.pk, {"name": "Tên mới"})
    assert r.status_code == 200
    product.refresh_from_db()
    assert product.name == "Tên mới"
    assert product.featured_rank == 3
    assert product.retail_price == 250000
    assert product.short_desc == "Mô tả"


def test_patch_null_featured_rank_clears_it(owner_client: Client, goods_type: GoodsType) -> None:
    product = make_product(goods_type, featured_rank=3)
    r = patch(owner_client, product.pk, {"featured_rank": None})
    assert r.status_code == 200
    assert body(r)["featured_rank"] is None
    product.refresh_from_db()
    assert product.featured_rank is None


def test_patch_null_clears_optional_but_rejects_required(
    owner_client: Client, goods_type: GoodsType
) -> None:
    product = make_product(goods_type, short_desc="Mô tả", retail_price=1000)
    r = patch(owner_client, product.pk, {"short_desc": None, "retail_price": None})
    assert r.status_code == 200
    product.refresh_from_db()
    assert product.short_desc is None and product.retail_price is None

    for field in ("name", "slug", "sku", "status", "images", "serial_tracked"):
        r = patch(owner_client, product.pk, {field: None})
        assert (r.status_code, body(r)["code"]) == (400, "VALIDATION_ERROR"), field


# ------------------------------------------------------------------ URL và ảnh


@pytest.mark.parametrize("url", ["javascript:alert(1)", "//evil.com", "data:text/html,x"])
def test_unsafe_buy_link_is_400(owner_client: Client, goods_type: GoodsType, url: str) -> None:
    link = [{"channel": "shopee", "url": url}]
    r = post(owner_client, product_payload(goods_type, buy_links=link))
    assert (r.status_code, body(r)["code"]) == (400, "VALIDATION_ERROR")

    product = make_product(goods_type)
    r = patch(owner_client, product.pk, {"buy_links": link})
    assert (r.status_code, body(r)["code"]) == (400, "VALIDATION_ERROR")


@pytest.mark.parametrize(
    "url", ["https://evil.com/a.webp", "/media/../x", "/media/%2e%2e/x", "/media/%252e%252e/x"]
)
def test_unsafe_image_url_is_400(owner_client: Client, goods_type: GoodsType, url: str) -> None:
    r = post(owner_client, product_payload(goods_type, images=[{**IMAGE, "url": url}]))
    assert (r.status_code, body(r)["code"]) == (400, "VALIDATION_ERROR")


def test_image_without_alt_is_400(owner_client: Client, goods_type: GoodsType) -> None:
    r = post(owner_client, product_payload(goods_type, images=[{**IMAGE, "alt": ""}]))
    assert (r.status_code, body(r)["code"]) == (400, "VALIDATION_ERROR")


# ------------------------------------------------------------------ đổi slug


def test_slug_change_adds_redirect(owner_client: Client, goods_type: GoodsType) -> None:
    product = make_product(goods_type, slug="slug-cu")
    r = patch(owner_client, product.pk, {"slug": "slug-moi"})
    assert r.status_code == 200
    assert body(r)["slug"] == "slug-moi"
    assert list(SlugRedirect.objects.values_list("old_slug", "product_id")) == [
        ("slug-cu", product.pk)
    ]


def test_slug_taken_by_other_product_is_409(owner_client: Client, goods_type: GoodsType) -> None:
    make_product(goods_type, sku="A", slug="slug-a")
    b = make_product(goods_type, sku="B", slug="slug-b")
    r = patch(owner_client, b.pk, {"slug": "slug-a"})
    assert (r.status_code, body(r)["code"]) == (409, "SLUG_TAKEN")
    b.refresh_from_db()
    assert b.slug == "slug-b"
    assert not SlugRedirect.objects.exists()


def test_old_slug_of_other_product_is_409(owner_client: Client, goods_type: GoodsType) -> None:
    a = make_product(goods_type, sku="A", slug="slug-a")
    b = make_product(goods_type, sku="B", slug="slug-b")
    assert patch(owner_client, a.pk, {"slug": "slug-a2"}).status_code == 200  # redirect slug-a
    r = patch(owner_client, b.pk, {"slug": "slug-a"})
    assert (r.status_code, body(r)["code"]) == (409, "SLUG_TAKEN")
    r = post(owner_client, product_payload(goods_type, sku="C", slug="slug-a"))
    assert (r.status_code, body(r)["code"]) == (409, "SLUG_TAKEN")


def test_slug_changed_back_removes_its_own_redirect(
    owner_client: Client, goods_type: GoodsType
) -> None:
    product = make_product(goods_type, slug="slug-a")
    assert patch(owner_client, product.pk, {"slug": "slug-b"}).status_code == 200
    assert patch(owner_client, product.pk, {"slug": "slug-a"}).status_code == 200
    assert list(SlugRedirect.objects.values_list("old_slug", flat=True)) == ["slug-b"]
