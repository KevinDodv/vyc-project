"""Hình dạng lỗi (backend.md 3.2), phân quyền theo vai và CSRF (4.2, 4.3), throttle (5.2)."""

from __future__ import annotations

import json
from typing import Any

import pytest
from django.test import Client, override_settings

from core import throttle
from core.models import Setting

pytestmark = [pytest.mark.urls("core.tests.urls_sample"), pytest.mark.django_db]

BASE = "/api/sample"


def body(response: Any) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(response.content)
    return data


def test_anonymous_gets_401_in_error_shape(client: Client) -> None:
    r = client.get(f"{BASE}/owner")
    assert r.status_code == 401
    assert body(r) == {"code": "UNAUTHENTICATED", "message": "Bạn chưa đăng nhập", "details": {}}


def test_default_auth_is_owner_only(owner_client: Client, workshop_client: Client) -> None:
    assert owner_client.get(f"{BASE}/owner").status_code == 200
    r = workshop_client.get(f"{BASE}/owner")
    assert r.status_code == 403
    assert body(r)["code"] == "FORBIDDEN"


def test_any_staff_opens_route_for_workshop(workshop_client: Client, owner_client: Client) -> None:
    assert workshop_client.get(f"{BASE}/staff").status_code == 200
    assert owner_client.get(f"{BASE}/staff").status_code == 200


def test_csrf_required_on_write(owner: Any) -> None:
    client = Client(enforce_csrf_checks=True)
    client.force_login(owner)
    r = client.post(f"{BASE}/items", {"name": "a", "qty": 1}, content_type="application/json")
    assert r.status_code == 403
    assert body(r)["code"] == "CSRF_FAILED"
    # GET không cần CSRF.
    assert client.get(f"{BASE}/staff").status_code == 200


def test_csrf_ok_with_matching_cookie_and_header(owner: Any) -> None:
    client = Client(enforce_csrf_checks=True)
    client.force_login(owner)
    token = "a" * 32
    client.cookies["csrftoken"] = token
    r = client.post(
        f"{BASE}/items",
        {"name": "a", "qty": 1},
        content_type="application/json",
        headers={"X-CSRFToken": token},
    )
    assert r.status_code == 200, r.content


def test_anonymous_write_is_401_not_csrf(db: None) -> None:
    client = Client(enforce_csrf_checks=True)
    r = client.post(f"{BASE}/items", {"name": "a", "qty": 1}, content_type="application/json")
    assert r.status_code == 401


def test_validation_error_is_400_not_422(owner_client: Client) -> None:
    r = owner_client.post(f"{BASE}/items", {"name": "", "qty": 0}, content_type="application/json")
    assert r.status_code == 400
    data = body(r)
    assert data["code"] == "VALIDATION_ERROR"
    fields = {e["field"] for e in data["details"]["errors"]}
    assert fields == {"name", "qty"}


def test_validation_error_on_query(client: Client) -> None:
    r = client.get(f"{BASE}/search", {"q": "abc"})
    assert r.status_code == 400
    assert body(r)["details"]["errors"][0]["field"] == "q"


def test_business_error_has_rule_in_details(client: Client) -> None:
    r = client.get(f"{BASE}/business")
    assert r.status_code == 409
    assert body(r) == {
        "code": "LOT_GENERAL_STREAM",
        "message": "Lô hàng chung",
        "details": {"rule": "BR-08", "lot_code": "NL-2611-0045"},
    }


def test_api_error_custom_status(client: Client) -> None:
    r = client.get(f"{BASE}/api-error")
    assert r.status_code == 409
    assert body(r)["code"] == "SLUG_TAKEN"


def test_unknown_path_and_method_use_error_shape(client: Client) -> None:
    r = client.get(f"{BASE}/nope")
    assert r.status_code == 404
    assert body(r)["code"] == "NOT_FOUND"
    r = client.delete(f"{BASE}/search")
    assert r.status_code == 405
    assert body(r)["code"] == "HTTP_405"


def test_unexpected_exception_hides_details(client: Client) -> None:
    r = client.get(f"{BASE}/boom")
    assert r.status_code == 500
    data = body(r)
    assert data["code"] == "INTERNAL_ERROR"
    assert "nội bộ" not in json.dumps(data, ensure_ascii=False)


@override_settings(TRUSTED_PROXY_CIDRS=["127.0.0.1/32"])
def test_throttle_decorator_returns_429_with_retry_after(client: Client) -> None:
    headers = {"X-Forwarded-For": "203.0.113.9"}
    assert client.get(f"{BASE}/throttled", headers=headers).status_code == 200
    assert client.get(f"{BASE}/throttled", headers=headers).status_code == 200
    r = client.get(f"{BASE}/throttled", headers=headers)
    assert r.status_code == 429
    assert body(r)["code"] == "RATE_LIMITED"
    assert 1 <= int(r["Retry-After"]) <= 60
    # IP khác có khoá riêng.
    other = {"X-Forwarded-For": "203.0.113.10"}
    assert client.get(f"{BASE}/throttled", headers=other).status_code == 200


@override_settings(TRUSTED_PROXY_CIDRS=["127.0.0.1/32"])
def test_throttle_skipped_when_client_ip_missing(client: Client) -> None:
    for _ in range(5):
        assert client.get(f"{BASE}/throttled").status_code == 200  # không có X-Forwarded-For
    assert throttle.count("sample:anything", 1) == 0


def test_throttle_check_hit_count_reset() -> None:
    key = "login:u:abc|def"
    for _ in range(5):
        throttle.hit(key)
    assert throttle.count(key, 15) == 5
    with pytest.raises(throttle.Throttled) as exc:
        throttle.check(key, limit=5, minutes=15, code="LOGIN_LOCKED")
    assert exc.value.code == "LOGIN_LOCKED"
    assert exc.value.retry_after == 900
    throttle.check(key, limit=6, minutes=15)  # dưới ngưỡng thì qua
    throttle.reset(key)
    assert throttle.count(key, 15) == 0


def test_throttle_purge_removes_old_rows() -> None:
    from datetime import timedelta

    from django.db import connection

    throttle.hit("old")
    with connection.cursor() as cur:
        cur.execute("UPDATE throttle_hit SET window_start = now() - interval '2 days'")
    throttle.hit("new")
    assert throttle.purge(older_than=timedelta(days=1)) == 1
    assert throttle.count("new", 1) == 1


def test_pagination(client: Client) -> None:
    Setting.objects.all().delete()  # bỏ setting seed (core/migrations/0002) để đếm đúng 5
    for i in range(5):
        Setting.objects.create(key=f"k{i}" + "x" * i, value={})
    r = client.get(f"{BASE}/page", {"page": 2, "page_size": 2})
    assert r.status_code == 200
    assert body(r) == {"items": [4, 5], "total": 5, "page": 2, "page_size": 2}
