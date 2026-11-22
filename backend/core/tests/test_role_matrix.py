"""Ma trận vai x route của `api_v1` (backend.md 4.3).

`ROUTE_ROLES` ghi vai được phép của từng route theo mục 2 và mục 9 của thiết kế chi tiết. Test
duyệt MỌI route lấy từ OpenAPI của `api_v1` nên thêm route mới mà quên khai vào bảng thì đỏ.

Quy ước vai:
  OWNER      chỉ chủ doanh nghiệp (mặc định của api_v1)
  ANY_STAFF  OWNER và WORKSHOP
  PUBLIC     không cần đăng nhập
"""

from __future__ import annotations

import importlib
import re
from typing import Any

import pytest
from django.test import Client
from ninja import NinjaAPI

pytestmark = pytest.mark.django_db

OWNER = "OWNER"
ANY_STAFF = "ANY_STAFF"
PUBLIC = "PUBLIC"

ROUTE_ROLES: dict[str, str] = {
    # accounts (backend.md 4.1, 4.2)
    "GET /api/v1/auth/csrf": PUBLIC,
    "POST /api/v1/auth/login": PUBLIC,
    "POST /api/v1/auth/logout": ANY_STAFF,
    "GET /api/v1/auth/me": ANY_STAFF,
    # catalog: GET cả hai vai, ghi chỉ OWNER (TK mục 9, dòng "Danh mục")
    "GET /api/v1/products": ANY_STAFF,
    "POST /api/v1/products": OWNER,
    "GET /api/v1/products/{product_id}": ANY_STAFF,
    "PATCH /api/v1/products/{product_id}": OWNER,
}

# Chưa đăng nhập thì 401, đăng nhập nhưng sai vai thì 403 (core/permissions.py).
DENIED = {401, 403}


def all_routes() -> list[str]:
    # import động: core không được import config (cấu trúc phân lớp), nhưng test cần api_v1 thật
    api_v1: NinjaAPI = importlib.import_module("config.api").api_v1
    paths: dict[str, dict[str, Any]] = api_v1.get_openapi_schema()["paths"]
    return sorted(
        f"{method.upper()} {path}" for path, operations in paths.items() for method in operations
    )


def call(client: Client, route: str) -> int:
    method, template = route.split(" ", 1)
    url = re.sub(r"\{[^}]+\}", "1", template)
    response = getattr(client, method.lower())(url, {}, content_type="application/json")
    return int(response.status_code)


def test_every_route_is_declared_and_no_stale_entry() -> None:
    routes = set(all_routes())
    undeclared = routes - ROUTE_ROLES.keys()
    stale = ROUTE_ROLES.keys() - routes
    assert not undeclared, f"Route chưa khai vai trong ROUTE_ROLES: {sorted(undeclared)}"
    assert not stale, f"ROUTE_ROLES có route không còn tồn tại: {sorted(stale)}"
    assert set(ROUTE_ROLES.values()) <= {OWNER, ANY_STAFF, PUBLIC}


@pytest.mark.parametrize("route", sorted(ROUTE_ROLES))
def test_anonymous(client: Client, route: str) -> None:
    status = call(client, route)
    if ROUTE_ROLES[route] == PUBLIC:
        assert status not in DENIED, f"{route}: route công khai trả {status}"
    else:
        assert status == 401, f"{route}: chưa đăng nhập phải 401, nhận {status}"


@pytest.mark.parametrize("route", sorted(ROUTE_ROLES))
def test_workshop(workshop_client: Client, route: str) -> None:
    status = call(workshop_client, route)
    if ROUTE_ROLES[route] == OWNER:
        assert status == 403, f"{route}: WORKSHOP phải 403, nhận {status}"
    else:
        assert status not in DENIED, f"{route}: WORKSHOP được phép nhưng nhận {status}"


@pytest.mark.parametrize("route", sorted(ROUTE_ROLES))
def test_owner(owner_client: Client, route: str) -> None:
    status = call(owner_client, route)
    assert status not in DENIED, f"{route}: OWNER phải vào được, nhận {status}"
