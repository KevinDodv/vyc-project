"""Đăng nhập, CSRF, khoá đăng nhập, phiên 12 giờ, đăng xuất (backend.md 4.1, 4.2, 5.2)."""

from __future__ import annotations

import json
from datetime import timedelta
from io import StringIO
from typing import Any

import pytest
from django.contrib.sessions.models import Session
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import Client, override_settings
from django.utils import timezone

from accounts.models import User, UserStatus
from core.roles import Role

pytestmark = pytest.mark.django_db

BASE = "/api/v1/auth"
OWNER_PW = "pw-owner-123"


class Browser:
    """Trình duyệt giả: kiểm CSRF thật, tự gửi lại `X-CSRFToken` từ cookie như frontend."""

    def __init__(self, **extra: Any) -> None:
        self.client = Client(enforce_csrf_checks=True, **extra)

    def token(self) -> str:
        return self.client.cookies["csrftoken"].value

    def fetch_csrf(self) -> Any:
        return self.client.get(f"{BASE}/csrf")

    def post(self, path: str, data: dict[str, Any] | None = None, *, csrf: bool = True) -> Any:
        if csrf and "csrftoken" not in self.client.cookies:
            self.fetch_csrf()
        headers = {"X-CSRFToken": self.token()} if csrf else {}
        return self.client.post(
            f"{BASE}{path}", data or {}, content_type="application/json", headers=headers
        )

    def login(self, username: str = "owner", password: str = OWNER_PW) -> Any:
        return self.post("/login", {"username": username, "password": password})

    def me(self) -> Any:
        return self.client.get(f"{BASE}/me")


def body(response: Any) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(response.content)
    return data


@pytest.fixture
def browser() -> Browser:
    return Browser()


# ------------------------------------------------------------------ csrf / me


def test_csrf_sets_readable_cookie(browser: Browser) -> None:
    r = browser.fetch_csrf()
    assert r.status_code == 204
    cookie = r.cookies["csrftoken"]
    assert cookie.value
    assert not cookie["httponly"]  # JS phải đọc được để gửi X-CSRFToken


def test_me_requires_login(browser: Browser) -> None:
    r = browser.me()
    assert r.status_code == 401
    assert body(r)["code"] == "UNAUTHENTICATED"


def test_login_requires_csrf(owner: User, browser: Browser) -> None:
    r = browser.post("/login", {"username": "owner", "password": OWNER_PW}, csrf=False)
    assert r.status_code == 403
    assert body(r)["code"] == "CSRF_FAILED"
    assert browser.me().status_code == 401


# ---------------------------------------------------------------------- login


def test_login_ok_returns_owner_and_opens_session(owner: User, browser: Browser) -> None:
    r = browser.login()
    assert r.status_code == 200
    assert body(r) == {
        "id": owner.pk,
        "username": "owner",
        "full_name": "Chủ doanh nghiệp",
        "role": "OWNER",
    }
    session = r.cookies["sessionid"]
    assert session["httponly"]
    assert session["samesite"] == "Lax"
    assert "csrftoken" in r.cookies  # token quay sau đăng nhập, cookie mới về trình duyệt

    me = browser.me()
    assert me.status_code == 200
    assert body(me) == body(r)


def test_me_returns_workshop_role(workshop: User, browser: Browser) -> None:
    browser.login("xuong", "pw-xuong-123")
    assert body(browser.me())["role"] == "WORKSHOP"


def test_login_updates_last_login(owner: User, browser: Browser) -> None:
    assert owner.last_login is None
    browser.login()
    owner.refresh_from_db()
    assert owner.last_login is not None


@pytest.mark.parametrize(
    ("username", "password"),
    [("owner", "sai-mat-khau"), ("khong-co-tai-khoan", OWNER_PW)],
)
def test_bad_credentials_same_message(
    owner: User, browser: Browser, username: str, password: str
) -> None:
    r = browser.login(username, password)
    assert r.status_code == 401
    assert body(r) == {
        "code": "INVALID_CREDENTIALS",
        "message": "Sai tên đăng nhập hoặc mật khẩu",
        "details": {},
    }
    assert browser.me().status_code == 401


def test_inactive_user_cannot_login(owner: User, browser: Browser) -> None:
    owner.status = UserStatus.INACTIVE
    owner.save()
    r = browser.login()
    assert r.status_code == 401
    assert body(r)["code"] == "INVALID_CREDENTIALS"


def test_overlong_username_is_400_and_not_counted(owner: User, browser: Browser) -> None:
    r = browser.login("a" * 151, "x")
    assert r.status_code == 400
    assert body(r)["code"] == "VALIDATION_ERROR"
    # Không tính vào khoá: 5 lần sai kế tiếp vẫn là 401 chứ không phải 429.
    for _ in range(5):
        assert browser.login("owner", "sai").status_code == 401


# ------------------------------------------------------------------- khoá 429


def test_five_wrong_logins_lock_the_pair(owner: User, browser: Browser) -> None:
    for _ in range(5):
        assert browser.login(password="sai").status_code == 401
    r = browser.login(password="sai")
    assert r.status_code == 429
    assert body(r)["code"] == "LOGIN_LOCKED"
    assert body(r)["message"] == "Sai mật khẩu 5 lần, thử lại sau 15 phút"
    assert r["Retry-After"] == "900"
    # Đã khoá thì mật khẩu đúng cũng không vào được.
    assert browser.login().status_code == 429
    assert browser.me().status_code == 401


def test_lock_is_per_account_and_ip(owner: User, workshop: User) -> None:
    attacker = Browser(REMOTE_ADDR="203.0.113.9")
    for _ in range(5):
        attacker.login(password="sai")
    assert attacker.login().status_code == 429

    # OWNER ở xưởng (IP khác) không bị người ngoài khoá.
    at_workshop = Browser(REMOTE_ADDR="198.51.100.7")
    assert at_workshop.login().status_code == 200
    # Cùng IP kẻ dò nhưng tài khoản khác: khoá theo cặp nên chưa bị chặn.
    assert attacker.login("xuong", "pw-xuong-123").status_code == 200


def test_ip_lock_after_twenty_wrong_across_usernames(owner: User) -> None:
    attacker = Browser(REMOTE_ADDR="203.0.113.9")
    for name in ("a", "b", "c", "d"):
        for _ in range(5):
            assert attacker.login(name, "sai").status_code == 401
    r = attacker.login("e", "sai")
    assert r.status_code == 429
    assert body(r)["code"] == "LOGIN_LOCKED"
    assert attacker.login().status_code == 429  # cả tài khoản thật, vì IP đã bị khoá
    assert Browser(REMOTE_ADDR="198.51.100.7").login().status_code == 200


def test_successful_login_resets_account_counter(owner: User, browser: Browser) -> None:
    for _ in range(4):
        browser.login(password="sai")
    assert browser.login().status_code == 200
    browser.post("/logout")
    for _ in range(5):
        assert browser.login(password="sai").status_code == 401
    assert browser.login(password="sai").status_code == 429


@override_settings(TRUSTED_PROXY_CIDRS=["127.0.0.0/8"])
def test_lock_still_works_when_client_ip_is_missing(owner: User, browser: Browser) -> None:
    # REMOTE_ADDR thuộc dải tin cậy mà không có X-Forwarded-For → client_ip None (backend.md 5.1).
    for _ in range(5):
        assert browser.login(password="sai").status_code == 401
    assert browser.login().status_code == 429


# ----------------------------------------------------------------- phiên 12 giờ


def test_session_lasts_twelve_hours(owner: User, browser: Browser) -> None:
    r = browser.login()
    assert r.cookies["sessionid"]["max-age"] == 12 * 3600

    session = Session.objects.get()
    remaining = session.expire_date - timezone.now()
    assert timedelta(hours=11, minutes=59) < remaining <= timedelta(hours=12)

    # Thao tác sau đó không kéo dài phiên (SESSION_SAVE_EVERY_REQUEST = False).
    session.expire_date = timezone.now() + timedelta(hours=1)
    session.save()
    assert browser.me().status_code == 200
    assert Session.objects.get().expire_date - timezone.now() <= timedelta(hours=1)


def test_expired_session_is_401(owner: User, browser: Browser) -> None:
    browser.login()
    Session.objects.update(expire_date=timezone.now() - timedelta(seconds=1))
    r = browser.me()
    assert r.status_code == 401
    assert body(r)["code"] == "UNAUTHENTICATED"


# --------------------------------------------------------------------- logout


def test_logout_ends_session(owner: User, browser: Browser) -> None:
    browser.login()
    assert browser.me().status_code == 200
    r = browser.post("/logout")
    assert r.status_code == 204
    assert browser.me().status_code == 401
    assert Session.objects.count() == 0


def test_logout_requires_login_and_csrf(owner: User, browser: Browser) -> None:
    assert browser.post("/logout").status_code == 401
    browser.login()
    r = browser.post("/logout", csrf=False)
    assert r.status_code == 403
    assert body(r)["code"] == "CSRF_FAILED"
    assert browser.me().status_code == 200


# ----------------------------------------------------------------- create_owner


def run_create_owner(*args: str) -> str:
    out = StringIO()
    call_command("create_owner", *args, stdout=out)
    return out.getvalue()


def test_create_owner_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OWNER_PASSWORD", "mat-khau-dai-123")
    run_create_owner("--username", "chu", "--full-name", "Nguyễn Văn A")
    user = User.objects.get(username="chu")
    assert user.role == Role.OWNER
    assert user.full_name == "Nguyễn Văn A"
    assert user.status == UserStatus.ACTIVE
    assert user.check_password("mat-khau-dai-123")
    assert user.password.startswith("argon2$")

    browser = Browser()
    assert body(browser.login("chu", "mat-khau-dai-123"))["role"] == "OWNER"


def test_create_owner_custom_env_name(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MY_PW", "mat-khau-dai-123")
    run_create_owner("--username", "chu", "--password-env", "MY_PW")
    assert User.objects.get(username="chu").check_password("mat-khau-dai-123")


def test_create_owner_prompts_when_no_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OWNER_PASSWORD", raising=False)
    monkeypatch.setattr("getpass.getpass", lambda prompt="": "mat-khau-nhap-tay")
    run_create_owner("--username", "chu")
    assert User.objects.get(username="chu").check_password("mat-khau-nhap-tay")


def test_create_owner_prompt_mismatch(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OWNER_PASSWORD", raising=False)
    answers = iter(["mat-khau-nhap-tay", "go-nham-roi"])
    monkeypatch.setattr("getpass.getpass", lambda prompt="": next(answers))
    with pytest.raises(CommandError, match="không khớp"):
        run_create_owner("--username", "chu")
    assert not User.objects.exists()


def test_create_owner_rejects_short_password(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OWNER_PASSWORD", "ngan")
    with pytest.raises(CommandError, match="8 ký tự"):
        run_create_owner("--username", "chu")
    assert not User.objects.exists()


def test_create_owner_rejects_existing_username(
    owner: User, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("OWNER_PASSWORD", "mat-khau-dai-123")
    with pytest.raises(CommandError, match="đã tồn tại"):
        run_create_owner("--username", "owner")
    assert User.objects.get(username="owner").check_password(OWNER_PW)
