"""Luồng mẫu end-to-end qua HTTP, bước 1-3 của backend.md mục 8.

1. OWNER đăng nhập: GET /auth/csrf → POST /auth/login → GET /auth/me.
2. Tạo sản phẩm DRAFT → PATCH PUBLISHED; mỗi bước ghi audit_log.
3. GET /api/public/products/{slug} trả DTO công khai; DRAFT và slug sai trả 404.

Client kiểm CSRF thật và tự gửi lại `X-CSRFToken` từ cookie như frontend. Test mở rộng thêm
đổi slug (slug cũ vẫn tra ra sản phẩm mới) và đăng xuất để chứng minh phiên bị huỷ.
"""

from __future__ import annotations

import json
from typing import Any

import pytest
from django.test import Client

from accounts.models import User
from catalog.models import GoodsType
from catalog.tests.conftest import product_payload
from core.models import AuditLog

pytestmark = pytest.mark.django_db

AUTH = "/api/v1/auth"
PRODUCTS = "/api/v1/products"
PUBLIC = "/api/public/products"
SLUG = "tinh-dau-que-van-yen-10ml"
NEW_SLUG = "tinh-dau-que-van-yen-10-ml"


def body(response: Any) -> Any:
    return json.loads(response.content)


class Browser:
    """Trình duyệt giả có kiểm CSRF."""

    def __init__(self) -> None:
        self.client = Client(enforce_csrf_checks=True)

    def _headers(self) -> dict[str, str]:
        return {"X-CSRFToken": self.client.cookies["csrftoken"].value}

    def get(self, url: str) -> Any:
        return self.client.get(url)

    def send(self, method: str, url: str, data: dict[str, Any] | None = None) -> Any:
        return getattr(self.client, method)(
            url, data or {}, content_type="application/json", headers=self._headers()
        )


@pytest.fixture
def goods_type(db: None) -> GoodsType:
    """Loại hàng seed bởi migration 0002."""
    return GoodsType.objects.get(code="TINH_DAU")


@pytest.fixture
def browser(owner: User) -> Browser:
    return Browser()


def test_sample_flow_login_create_publish_read(browser: Browser, goods_type: GoodsType) -> None:
    # --- Bước 1: đăng nhập. Chưa đăng nhập thì /me 401.
    assert browser.get(f"{AUTH}/me").status_code == 401
    assert browser.get(f"{AUTH}/csrf").status_code == 204
    assert "csrftoken" in browser.client.cookies

    login = browser.send("post", f"{AUTH}/login", {"username": "owner", "password": "pw-owner-123"})
    assert login.status_code == 200, login.content
    me = browser.get(f"{AUTH}/me")
    assert me.status_code == 200
    assert body(me)["role"] == "OWNER"

    # --- Bước 2: tạo DRAFT, chưa lộ ra công khai.
    created = browser.send("post", PRODUCTS, product_payload(goods_type))
    assert created.status_code == 201, created.content
    product = body(created)
    assert product["status"] == "DRAFT"
    assert browser.get(f"{PUBLIC}/{SLUG}").status_code == 404

    # --- Đăng: PATCH PUBLISHED.
    published = browser.send("patch", f"{PRODUCTS}/{product['id']}", {"status": "PUBLISHED"})
    assert published.status_code == 200, published.content
    assert body(published)["status"] == "PUBLISHED"

    actions = list(
        AuditLog.objects.filter(entity="product", entity_id=product["id"])
        .order_by("id")
        .values_list("action", flat=True)
    )
    assert actions == ["CREATE", "UPDATE"]

    # --- Bước 3: DTO công khai; slug sai 404.
    public = browser.get(f"{PUBLIC}/{SLUG}")
    assert public.status_code == 200
    dto = body(public)
    assert dto["slug"] == SLUG
    assert dto["name"] == "Tinh dầu quế Văn Yên 10 ml"
    assert dto["retail_price"] == 250000
    assert "status" not in dto
    assert "id" not in dto
    assert browser.get(f"{PUBLIC}/khong-co-slug-nay").status_code == 404

    listing = body(browser.get(PUBLIC))
    assert [item["slug"] for item in listing] == [SLUG]


def test_sample_flow_slug_change_keeps_old_url_and_logout_ends_session(
    browser: Browser, goods_type: GoodsType
) -> None:
    browser.get(f"{AUTH}/csrf")
    browser.send("post", f"{AUTH}/login", {"username": "owner", "password": "pw-owner-123"})
    pid = body(browser.send("post", PRODUCTS, product_payload(goods_type)))["id"]
    browser.send("patch", f"{PRODUCTS}/{pid}", {"status": "PUBLISHED"})

    renamed = browser.send("patch", f"{PRODUCTS}/{pid}", {"slug": NEW_SLUG})
    assert renamed.status_code == 200, renamed.content

    # Slug cũ vẫn tra ra sản phẩm, trả slug mới để frontend 301.
    old = browser.get(f"{PUBLIC}/{SLUG}")
    assert old.status_code == 200
    assert body(old)["slug"] == NEW_SLUG
    assert browser.get(f"{PUBLIC}/{NEW_SLUG}").status_code == 200

    # Đăng xuất: phiên bị huỷ, ghi tiếp bị 401.
    assert browser.send("post", f"{AUTH}/logout").status_code == 204
    assert browser.get(f"{AUTH}/me").status_code == 401
    assert browser.client.get(PRODUCTS).status_code == 401
