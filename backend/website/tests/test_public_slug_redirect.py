"""Slug cũ (TK mục 8, AC-19): API công khai trả 200 kèm slug mới, Astro tự 301."""

from __future__ import annotations

import json
from typing import Any

import pytest
from django.test import Client

from accounts.models import User
from catalog.models import GoodsType, ProductStatus, SlugRedirect
from catalog.services.products import ProductUpdate, update_product
from catalog.tests.conftest import make_product

pytestmark = pytest.mark.django_db


def get(client: Client, slug: str) -> Any:
    return client.get(f"/api/public/products/{slug}")


def test_old_slug_returns_200_with_new_slug(
    client: Client, owner: User, goods_type: GoodsType
) -> None:
    product = make_product(goods_type, slug="slug-cu")
    update_product(product_id=product.pk, data=ProductUpdate(slug="slug-moi"), actor=owner)

    r = get(client, "slug-cu")
    assert r.status_code == 200
    assert json.loads(r.content)["slug"] == "slug-moi"
    r = get(client, "slug-moi")
    assert (r.status_code, json.loads(r.content)["slug"]) == (200, "slug-moi")


def test_two_renames_keep_both_old_slugs(
    client: Client, owner: User, goods_type: GoodsType
) -> None:
    product = make_product(goods_type, slug="a")
    update_product(product_id=product.pk, data=ProductUpdate(slug="b"), actor=owner)
    update_product(product_id=product.pk, data=ProductUpdate(slug="c"), actor=owner)
    for old in ("a", "b", "c"):
        assert json.loads(get(client, old).content)["slug"] == "c"


def test_rename_back_serves_original_slug(
    client: Client, owner: User, goods_type: GoodsType
) -> None:
    product = make_product(goods_type, slug="a")
    update_product(product_id=product.pk, data=ProductUpdate(slug="b"), actor=owner)
    update_product(product_id=product.pk, data=ProductUpdate(slug="a"), actor=owner)
    assert json.loads(get(client, "a").content)["slug"] == "a"
    assert json.loads(get(client, "b").content)["slug"] == "a"
    assert not SlugRedirect.objects.filter(old_slug="a").exists()


def test_old_slug_of_unpublished_product_is_404(
    client: Client, owner: User, goods_type: GoodsType
) -> None:
    product = make_product(goods_type, slug="slug-cu")
    update_product(product_id=product.pk, data=ProductUpdate(slug="slug-moi"), actor=owner)
    update_product(
        product_id=product.pk, data=ProductUpdate(status=ProductStatus.HIDDEN), actor=owner
    )
    for slug in ("slug-cu", "slug-moi"):
        r = get(client, slug)
        assert (r.status_code, json.loads(r.content)["code"]) == (404, "NOT_FOUND"), slug


def test_unknown_slug_is_404(client: Client, goods_type: GoodsType) -> None:
    make_product(goods_type, slug="co")
    assert get(client, "khong-co").status_code == 404


def test_current_slug_wins_over_redirect_row(client: Client, goods_type: GoodsType) -> None:
    """Dữ liệu sửa tay: slug hiện hành của sản phẩm A trùng old_slug của B thì A thắng."""
    a = make_product(goods_type, sku="A", slug="chung")
    b = make_product(goods_type, sku="B", slug="b")
    SlugRedirect.objects.create(old_slug="chung", product=b)
    assert json.loads(get(client, "chung").content)["sku"] == a.sku
