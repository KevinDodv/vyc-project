"""API quản lý sản phẩm: phân quyền, featured_rank, PATCH một phần, đổi slug, audit_log."""

from __future__ import annotations

import json
from typing import Any

import pytest
from django.db import IntegrityError, transaction
from django.test import Client

from catalog.models import GoodsType, Product, ProductStatus, Recipe, RecipeStatus, SlugRedirect
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


# ------------------------------------------------------------------ nối công thức (PH1, BR-26)


def _retire(code: str) -> None:
    Recipe.objects.filter(code=code).update(status=RecipeStatus.RETIRED)


def test_create_with_recipe_shelf_life_and_retention(
    owner_client: Client, goods_type: GoodsType
) -> None:
    payload = product_payload(
        goods_type, recipe_code="QC1", shelf_life_months=24, requires_retention_sample=True
    )
    r = post(owner_client, payload)
    assert r.status_code == 201, r.content
    data = body(r)
    assert (data["recipe_code"], data["shelf_life_months"]) == ("QC1", 24)
    assert data["requires_retention_sample"] is True
    assert data["warnings"] == []
    assert Product.objects.get(pk=data["id"]).recipe_code == "QC1"


@pytest.mark.parametrize(
    ("code", "error"),
    [
        ("NOPE", "RECIPE_NOT_ACTIVE"),  # không có công thức
        ("TT1", "RECIPE_NOT_PRODUCT"),  # bán thành phẩm
    ],
)
def test_create_rejects_bad_recipe_code(
    owner_client: Client, goods_type: GoodsType, code: str, error: str
) -> None:
    r = post(owner_client, product_payload(goods_type, recipe_code=code))
    assert (r.status_code, body(r)["code"]) == (400, error)
    assert body(r)["details"]["field"] == "recipe_code"
    assert not Product.objects.exists()


def test_recipe_code_needs_active_version(owner_client: Client, goods_type: GoodsType) -> None:
    Recipe.objects.filter(code="QC2").update(status=RecipeStatus.DRAFT)
    r = post(owner_client, product_payload(goods_type, recipe_code="QC2"))
    assert (r.status_code, body(r)["code"]) == (400, "RECIPE_NOT_ACTIVE")
    _retire("QC1")
    r = post(owner_client, product_payload(goods_type, recipe_code="QC1"))
    assert (r.status_code, body(r)["code"]) == (400, "RECIPE_NOT_ACTIVE")


def test_patch_recipe_code_set_change_and_clear(
    owner_client: Client, goods_type: GoodsType
) -> None:
    pid = make_product(goods_type, status=ProductStatus.DRAFT).pk
    r = patch(owner_client, pid, {"recipe_code": "NOPE"})
    assert (r.status_code, body(r)["code"]) == (400, "RECIPE_NOT_ACTIVE")
    assert Product.objects.get(pk=pid).recipe_code is None
    assert patch(owner_client, pid, {"recipe_code": "QC1"}).status_code == 200
    assert patch(owner_client, pid, {"recipe_code": "QC2"}).status_code == 200
    r = patch(owner_client, pid, {"recipe_code": None})
    assert (r.status_code, body(r)["recipe_code"]) == (200, None)


def test_patch_other_fields_ignores_retired_recipe(
    owner_client: Client, goods_type: GoodsType
) -> None:
    pid = make_product(goods_type, recipe_code="QC1").pk
    _retire("QC1")
    r = patch(owner_client, pid, {"shelf_life_months": 12, "requires_retention_sample": True})
    assert r.status_code == 200, r.content
    assert (body(r)["shelf_life_months"], body(r)["requires_retention_sample"]) == (12, True)
    # gửi lại đúng recipe_code hiện tại không bị coi là đổi nên cũng không bị chặn
    assert patch(owner_client, pid, {"recipe_code": "QC1", "name": "Tên mới"}).status_code == 200


def test_published_product_warns_when_recipe_loses_active_version(
    owner_client: Client, workshop_client: Client, goods_type: GoodsType
) -> None:
    pid = make_product(goods_type, recipe_code="QC1", status=ProductStatus.PUBLISHED).pk
    ok = body(owner_client.get(f"{URL}/{pid}"))
    assert ok["warnings"] == []

    _retire("QC1")
    for client in (owner_client, workshop_client):
        data = body(client.get(f"{URL}/{pid}"))
        assert [w["code"] for w in data["warnings"]] == ["RECIPE_NOT_ACTIVE"]
        assert data["warnings"][0]["field"] == "recipe_code"
        assert "QC1" in data["warnings"][0]["message"]
        listed = body(client.get(URL))["items"][0]
        assert [w["code"] for w in listed["warnings"]] == ["RECIPE_NOT_ACTIVE"]

    # cảnh báo, không chặn: vẫn sửa và vẫn PUBLISHED
    r = patch(owner_client, pid, {"name": "Tên khác"})
    assert (r.status_code, body(r)["status"]) == (200, "PUBLISHED")
    assert [w["code"] for w in body(r)["warnings"]] == ["RECIPE_NOT_ACTIVE"]


def test_publish_with_retired_recipe_is_allowed_with_warning(
    owner_client: Client, goods_type: GoodsType
) -> None:
    pid = make_product(goods_type, recipe_code="QC1", status=ProductStatus.DRAFT).pk
    _retire("QC1")
    r = patch(owner_client, pid, {"status": "PUBLISHED"})
    assert (r.status_code, body(r)["status"]) == (200, "PUBLISHED")
    assert [w["code"] for w in body(r)["warnings"]] == ["RECIPE_NOT_ACTIVE"]


def test_no_warning_for_draft_hidden_or_without_recipe(
    owner_client: Client, goods_type: GoodsType
) -> None:
    draft = make_product(goods_type, sku="A", slug="a", recipe_code="QC1", status="DRAFT")
    hidden = make_product(goods_type, sku="B", slug="b", recipe_code="QC1", status="HIDDEN")
    bare = make_product(goods_type, sku="C", slug="c", status=ProductStatus.PUBLISHED)
    _retire("QC1")
    for product in (draft, hidden, bare):
        assert body(owner_client.get(f"{URL}/{product.pk}"))["warnings"] == []


def test_active_new_version_clears_warning(owner_client: Client, goods_type: GoodsType) -> None:
    pid = make_product(goods_type, recipe_code="QC1", status=ProductStatus.PUBLISHED).pk
    r = owner_client.post(f"/api/v1/recipes/{Recipe.objects.get(code='QC1').pk}/new-version", {})
    assert r.status_code == 201
    new_id = body(r)["id"]
    assert owner_client.post(f"/api/v1/recipes/{new_id}/activate", {}).status_code == 200
    assert body(owner_client.get(f"{URL}/{pid}"))["warnings"] == []
