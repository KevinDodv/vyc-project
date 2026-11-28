"""API khách hàng: phân quyền 2 vai, mã KH-<stt>, PATCH một phần, ngừng dùng, audit_log."""

from __future__ import annotations

import json
import re
from typing import Any

import pytest
from django.test import Client

from catalog.models import Customer
from core.models import AuditLog

pytestmark = pytest.mark.django_db

URL = "/api/v1/customers"


def post(client: Client, payload: dict[str, Any]) -> Any:
    return client.post(URL, payload, content_type="application/json")


def patch(client: Client, customer_id: int, payload: dict[str, Any]) -> Any:
    return client.patch(f"{URL}/{customer_id}", payload, content_type="application/json")


def body(response: Any) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(response.content)
    return data


def new_customer(client: Client, **overrides: Any) -> dict[str, Any]:
    payload = {"name": "Đại lý Hưng Phát", "kind": "AGENT", "phone": "0912345678"}
    payload.update(overrides)
    response = post(client, payload)
    assert response.status_code == 201, response.content
    return body(response)


def before_of(log: AuditLog) -> dict[str, Any]:
    assert log.before is not None
    return dict(log.before)


def after_of(log: AuditLog) -> dict[str, Any]:
    assert log.after is not None
    return dict(log.after)


def audit(customer_id: int, action: str) -> list[AuditLog]:
    return list(AuditLog.objects.filter(entity="customer", entity_id=customer_id, action=action))


# ------------------------------------------------------------------ phân quyền


def test_anonymous_gets_401(client: Client) -> None:
    assert client.get(URL).status_code == 401
    assert post(client, {"name": "A", "kind": "AGENT"}).status_code == 401


def test_workshop_reads_but_cannot_write(owner_client: Client, workshop_client: Client) -> None:
    created = new_customer(owner_client)
    assert workshop_client.get(URL).status_code == 200
    assert workshop_client.get(f"{URL}/{created['id']}").status_code == 200
    before = Customer.objects.count()

    r = post(workshop_client, {"name": "B", "kind": "AGENT"})
    assert r.status_code == 403
    assert body(r)["code"] == "FORBIDDEN"
    assert Customer.objects.count() == before
    assert patch(workshop_client, created["id"], {"name": "Đổi tên"}).status_code == 403
    assert Customer.objects.get(pk=created["id"]).name == "Đại lý Hưng Phát"


# ------------------------------------------------------------------ tạo


def test_create_generates_sequential_kh_code(owner_client: Client) -> None:
    first = new_customer(owner_client, name="Khách một")
    second = new_customer(owner_client, name="Khách hai")
    assert re.fullmatch(r"KH-\d{4}", first["code"])
    assert int(second["code"][3:]) == int(first["code"][3:]) + 1
    assert first["status"] == "ACTIVE"
    assert first["phone"] == "0912345678"
    assert first["address"] is None


def test_create_writes_audit_log(owner_client: Client, owner: Any) -> None:
    created = new_customer(owner_client)
    (log,) = audit(created["id"], "CREATE")
    assert log.user_id == owner.pk
    assert after_of(log)["code"] == created["code"]
    assert log.before is None


def test_create_rejects_bad_input_without_burning_a_code(owner_client: Client) -> None:
    for bad in (
        {"name": "", "kind": "AGENT"},
        {"name": "   ", "kind": "AGENT"},
        {"name": "A", "kind": "ALIEN"},
        {"kind": "AGENT"},
    ):
        r = post(owner_client, bad)
        assert r.status_code == 400, bad
        assert body(r)["code"] == "VALIDATION_ERROR"
    first = new_customer(owner_client)
    second = new_customer(owner_client)
    assert int(second["code"][3:]) == int(first["code"][3:]) + 1


def test_seed_customers_are_listed(workshop_client: Client) -> None:
    items = body(workshop_client.get(URL, {"q": "Khách lẻ"}))["items"]
    assert [c["kind"] for c in items] == ["RETAIL"]


# ------------------------------------------------------------------ sửa


def test_patch_updates_only_sent_fields_and_audits(owner_client: Client) -> None:
    created = new_customer(owner_client, address="12 Trần Phú")
    r = patch(owner_client, created["id"], {"phone": "0987654321"})
    assert r.status_code == 200
    data = body(r)
    assert data["phone"] == "0987654321"
    assert data["address"] == "12 Trần Phú"
    assert data["name"] == "Đại lý Hưng Phát"
    (log,) = audit(created["id"], "UPDATE")
    assert before_of(log)["phone"] == "0912345678"
    assert after_of(log)["phone"] == "0987654321"


def test_patch_null_clears_optional_fields(owner_client: Client) -> None:
    created = new_customer(owner_client, address="12 Trần Phú")
    data = body(patch(owner_client, created["id"], {"phone": None, "address": None}))
    assert data["phone"] is None
    assert data["address"] is None


def test_patch_null_on_required_field_is_400(owner_client: Client) -> None:
    created = new_customer(owner_client)
    for field in ("name", "kind", "status"):
        r = patch(owner_client, created["id"], {field: None})
        assert r.status_code == 400, field
        assert body(r)["code"] == "VALIDATION_ERROR"


def test_patch_without_change_writes_no_audit(owner_client: Client) -> None:
    created = new_customer(owner_client)
    assert patch(owner_client, created["id"], {"name": created["name"]}).status_code == 200
    assert audit(created["id"], "UPDATE") == []


def test_patch_status_inactive_and_back(owner_client: Client) -> None:
    created = new_customer(owner_client)
    assert body(patch(owner_client, created["id"], {"status": "INACTIVE"}))["status"] == "INACTIVE"
    assert body(patch(owner_client, created["id"], {"status": "ACTIVE"}))["status"] == "ACTIVE"
    assert len(audit(created["id"], "UPDATE")) == 2
    assert patch(owner_client, created["id"], {"status": "GONE"}).status_code == 400


def test_unknown_customer_is_404(owner_client: Client) -> None:
    assert owner_client.get(f"{URL}/999999").status_code == 404
    assert patch(owner_client, 999999, {"name": "X"}).status_code == 404


# ------------------------------------------------------------------ danh sách


def test_list_filters_and_pages(owner_client: Client) -> None:
    a = new_customer(owner_client, name="Zeta Export", kind="EXPORTER", phone="0900000001")
    new_customer(owner_client, name="Alpha Agent", kind="AGENT", phone="0900000002")
    patch(owner_client, a["id"], {"status": "INACTIVE"})

    by_kind = body(owner_client.get(URL, {"kind": "EXPORTER"}))
    assert [c["name"] for c in by_kind["items"]] == ["Zeta Export"]
    by_status = body(owner_client.get(URL, {"status": "INACTIVE"}))
    assert [c["id"] for c in by_status["items"]] == [a["id"]]
    by_phone = body(owner_client.get(URL, {"q": "0900000002"}))
    assert [c["name"] for c in by_phone["items"]] == ["Alpha Agent"]
    by_code = body(owner_client.get(URL, {"q": a["code"]}))
    assert [c["id"] for c in by_code["items"]] == [a["id"]]

    page = body(owner_client.get(URL, {"page_size": 2, "page": 1}))
    assert len(page["items"]) == 2
    assert page["total"] == Customer.objects.count()
    names = [c["name"] for c in page["items"]]
    assert names == sorted(names)
