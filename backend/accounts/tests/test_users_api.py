"""API tài khoản: chỉ OWNER, mật khẩu ≥ 8, không tự ngừng dùng, không lộ hash, audit_log."""

from __future__ import annotations

import json
from typing import Any

import pytest
from django.test import Client

from accounts.models import User
from core.models import AuditLog
from core.roles import Role

pytestmark = pytest.mark.django_db

URL = "/api/v1/users"
HASH_MARKERS = ("argon2", "pbkdf2", "password")


def post(client: Client, payload: dict[str, Any]) -> Any:
    return client.post(URL, payload, content_type="application/json")


def patch(client: Client, user_id: int, payload: dict[str, Any]) -> Any:
    return client.patch(f"{URL}/{user_id}", payload, content_type="application/json")


def body(response: Any) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(response.content)
    return data


def new_user(**overrides: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        "username": "kho1",
        "full_name": "Thủ kho",
        "role": "WORKSHOP",
        "password": "mat-khau-1",
    }
    data.update(overrides)
    return data


def assert_no_secret(text: str) -> None:
    lowered = text.lower()
    for marker in HASH_MARKERS:
        assert marker not in lowered, marker


# ------------------------------------------------------------------ phân quyền


def test_anonymous_gets_401(client: Client) -> None:
    assert client.get(URL).status_code == 401
    assert post(client, new_user()).status_code == 401


def test_workshop_gets_403_everywhere(workshop_client: Client, workshop: User, owner: User) -> None:
    assert workshop_client.get(URL).status_code == 403
    assert workshop_client.get(f"{URL}/{owner.pk}").status_code == 403
    assert post(workshop_client, new_user()).status_code == 403
    r = patch(workshop_client, workshop.pk, {"role": "OWNER"})  # tự nâng quyền
    assert r.status_code == 403
    assert body(r)["code"] == "FORBIDDEN"
    workshop.refresh_from_db()
    assert workshop.role == Role.WORKSHOP
    assert User.objects.filter(username="kho1").count() == 0


# ------------------------------------------------------------------ tạo


def test_owner_creates_user_and_new_user_can_log_in(owner_client: Client) -> None:
    r = post(owner_client, new_user())
    assert r.status_code == 201, r.content
    out = body(r)
    assert out["username"] == "kho1"
    assert out["role"] == "WORKSHOP"
    assert out["status"] == "ACTIVE"
    assert out["last_login_at"] is None
    assert set(out) == {"id", "username", "full_name", "role", "status", "last_login_at"}
    assert_no_secret(r.content.decode())

    user = User.objects.get(username="kho1")
    assert user.password != "mat-khau-1"  # lưu hash, không lưu chữ thường
    assert user.check_password("mat-khau-1")
    assert Client().login(username="kho1", password="mat-khau-1")


def test_create_writes_audit_without_hash(owner_client: Client, owner: User) -> None:
    out = body(post(owner_client, new_user()))
    log = AuditLog.objects.get(entity="app_user", entity_id=out["id"])
    assert (log.action, log.user_id, log.before) == ("CREATE", owner.pk, None)
    assert log.after is not None
    assert log.after["username"] == "kho1"
    assert_no_secret(json.dumps(log.after))


@pytest.mark.parametrize("password", ["1234567", "", "a" * 257])
def test_rejects_bad_password(owner_client: Client, password: str) -> None:
    r = post(owner_client, new_user(password=password))
    assert r.status_code == 400
    assert body(r)["code"] == "VALIDATION_ERROR"
    assert not User.objects.filter(username="kho1").exists()


def test_accepts_exactly_8_char_password(owner_client: Client) -> None:
    assert post(owner_client, new_user(password="12345678")).status_code == 201


@pytest.mark.parametrize("username", ["ab", "co khoang trang", "a/b", "x" * 51, ""])
def test_rejects_bad_username(owner_client: Client, username: str) -> None:
    assert post(owner_client, new_user(username=username)).status_code == 400


def test_rejects_unknown_role_and_blank_name(owner_client: Client) -> None:
    assert post(owner_client, new_user(role="ADMIN")).status_code == 400
    assert post(owner_client, new_user(full_name="  ")).status_code == 400


def test_duplicate_username_is_409_case_insensitive(owner_client: Client) -> None:
    assert post(owner_client, new_user()).status_code == 201
    for name in ("kho1", "KHO1"):
        r = post(owner_client, new_user(username=name))
        assert r.status_code == 409
        assert body(r)["code"] == "USERNAME_TAKEN"
        assert body(r)["details"]["field"] == "username"
    assert User.objects.filter(username__iexact="kho1").count() == 1


# ------------------------------------------------------------------ đọc


def test_list_and_detail_never_expose_hash(owner_client: Client, workshop: User) -> None:
    r = owner_client.get(URL)
    assert r.status_code == 200
    data = body(r)
    assert data["total"] == 2
    assert [u["username"] for u in data["items"]] == ["owner", "xuong"]
    assert_no_secret(r.content.decode())

    r = owner_client.get(f"{URL}/{workshop.pk}")
    assert r.status_code == 200
    assert_no_secret(r.content.decode())
    assert body(r)["full_name"] == "Nhân viên xưởng"


def test_list_filters(owner_client: Client, workshop: User) -> None:
    workshop.status = "INACTIVE"
    workshop.save()
    assert [u["username"] for u in body(owner_client.get(f"{URL}?status=INACTIVE"))["items"]] == [
        "xuong"
    ]
    assert [u["username"] for u in body(owner_client.get(f"{URL}?role=OWNER"))["items"]] == [
        "owner"
    ]
    assert body(owner_client.get(f"{URL}?q=xuong"))["total"] == 1
    assert body(owner_client.get(f"{URL}?q=Chủ"))["total"] == 1
    assert owner_client.get(f"{URL}?role=ADMIN").status_code == 400


def test_unknown_user_is_404(owner_client: Client) -> None:
    assert owner_client.get(f"{URL}/999999").status_code == 404
    assert patch(owner_client, 999_999, {"full_name": "X"}).status_code == 404


# ------------------------------------------------------------------ sửa


def test_patch_updates_name_and_role_with_audit(
    owner_client: Client, workshop: User, owner: User
) -> None:
    r = patch(owner_client, workshop.pk, {"full_name": "Tổ trưởng", "role": "OWNER"})
    assert r.status_code == 200, r.content
    assert body(r)["role"] == "OWNER"
    workshop.refresh_from_db()
    assert (workshop.full_name, workshop.role) == ("Tổ trưởng", Role.OWNER)

    log = AuditLog.objects.get(entity="app_user", entity_id=workshop.pk, action="UPDATE")
    assert log.user_id == owner.pk
    assert log.before is not None and log.after is not None
    assert log.before["role"] == "WORKSHOP"
    assert log.after["role"] == "OWNER"
    assert_no_secret(json.dumps(log.before) + json.dumps(log.after))


def test_username_cannot_change(owner_client: Client, workshop: User) -> None:
    r = patch(owner_client, workshop.pk, {"username": "khac", "full_name": "Tên mới"})
    assert r.status_code == 200
    workshop.refresh_from_db()
    assert workshop.username == "xuong"
    assert workshop.full_name == "Tên mới"


def test_owner_resets_password_and_old_one_stops_working(
    owner_client: Client, workshop: User
) -> None:
    before_hash = workshop.password
    r = patch(owner_client, workshop.pk, {"password": "mat-khau-moi"})
    assert r.status_code == 200
    assert_no_secret(r.content.decode())
    workshop.refresh_from_db()
    assert workshop.password != before_hash
    assert workshop.check_password("mat-khau-moi")
    assert not Client().login(username="xuong", password="pw-xuong-123")
    assert Client().login(username="xuong", password="mat-khau-moi")

    log = AuditLog.objects.get(entity="app_user", entity_id=workshop.pk, action="UPDATE")
    assert log.reason == "Đặt lại mật khẩu"
    assert_no_secret(json.dumps(log.before) + json.dumps(log.after))
    assert log.before == log.after  # hash không nằm trong snapshot


def test_short_password_on_patch_rejected(owner_client: Client, workshop: User) -> None:
    r = patch(owner_client, workshop.pk, {"password": "short"})
    assert r.status_code == 400
    workshop.refresh_from_db()
    assert workshop.check_password("pw-xuong-123")


def test_owner_changing_own_password_keeps_session(owner_client: Client, owner: User) -> None:
    assert patch(owner_client, owner.pk, {"password": "owner-moi-123"}).status_code == 200
    assert owner_client.get(URL).status_code == 200  # phiên hiện tại không bị văng
    owner.refresh_from_db()
    assert owner.check_password("owner-moi-123")


def test_reset_password_logs_out_other_sessions(owner_client: Client, workshop: User) -> None:
    other = Client()
    other.force_login(workshop)
    assert other.get("/api/v1/auth/me").status_code == 200
    patch(owner_client, workshop.pk, {"password": "mat-khau-moi"})
    assert other.get("/api/v1/auth/me").status_code == 401


def test_patch_null_rejected(owner_client: Client, workshop: User) -> None:
    for name in ("full_name", "role", "status", "password"):
        r = patch(owner_client, workshop.pk, {name: None})
        assert r.status_code == 400, name
        assert body(r)["code"] == "VALIDATION_ERROR"


def test_noop_patch_writes_no_audit(owner_client: Client, workshop: User) -> None:
    assert patch(owner_client, workshop.pk, {"full_name": workshop.full_name}).status_code == 200
    assert patch(owner_client, workshop.pk, {}).status_code == 200
    assert AuditLog.objects.count() == 0


# ------------------------------------------------------------------ ngừng dùng


def test_cannot_deactivate_self(owner_client: Client, owner: User) -> None:
    r = patch(owner_client, owner.pk, {"status": "INACTIVE"})
    assert r.status_code == 409
    assert body(r)["code"] == "CANNOT_DEACTIVATE_SELF"
    assert body(r)["details"]["field"] == "status"
    owner.refresh_from_db()
    assert owner.status == "ACTIVE"
    assert AuditLog.objects.count() == 0


def test_owner_deactivates_another_user_who_is_then_locked_out(
    owner_client: Client, workshop: User, workshop_client: Client
) -> None:
    assert workshop_client.get("/api/v1/auth/me").status_code == 200
    r = patch(owner_client, workshop.pk, {"status": "INACTIVE"})
    assert r.status_code == 200
    assert body(r)["status"] == "INACTIVE"
    assert workshop_client.get("/api/v1/auth/me").status_code == 401  # phiên đang mở cũng mất
    assert not Client().login(username="xuong", password="pw-xuong-123")
    # bật lại được
    assert patch(owner_client, workshop.pk, {"status": "ACTIVE"}).status_code == 200
    assert Client().login(username="xuong", password="pw-xuong-123")


def test_cannot_leave_system_without_active_owner(owner_client: Client, owner: User) -> None:
    r = patch(owner_client, owner.pk, {"role": "WORKSHOP"})  # owner là OWNER duy nhất
    assert r.status_code == 409
    assert body(r)["code"] == "LAST_OWNER"
    owner.refresh_from_db()
    assert owner.role == Role.OWNER


def test_owner_can_demote_self_when_another_active_owner_exists(
    owner_client: Client, owner: User
) -> None:
    User.objects.create_user("owner2", "pw-owner2-123", full_name="Chủ 2", role=Role.OWNER)
    assert patch(owner_client, owner.pk, {"role": "WORKSHOP"}).status_code == 200


def test_inactive_owner_does_not_count_as_active(owner_client: Client, owner: User) -> None:
    User.objects.create_user(
        "owner2", "pw-owner2-123", full_name="Chủ 2", role=Role.OWNER, status="INACTIVE"
    )
    r = patch(owner_client, owner.pk, {"role": "WORKSHOP"})
    assert (r.status_code, body(r)["code"]) == (409, "LAST_OWNER")
