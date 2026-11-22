"""Đăng nhập, khoá đăng nhập và đăng xuất (backend.md 4.1, 5.2).

Khoá đếm lần **sai** bằng `core.throttle` (cửa sổ trượt 15 phút):
- `login:u:<sha256(username)>|<ip_hash>`: 5 lần sai thì khoá cặp tài khoản + IP đó;
- `login:ip:<ip_hash>`: 20 lần sai với mọi username thì khoá IP đó.
Phiên sống 12 giờ kể từ lúc đăng nhập (`SESSION_COOKIE_AGE`, không kéo dài theo thao tác).
"""

from __future__ import annotations

import hashlib
import logging

from django.contrib.auth import authenticate, login, logout
from django.http import HttpRequest

from accounts.models import User
from core import throttle
from core.clientip import get_client_ip, ip_hash
from core.errors import ApiError

logger = logging.getLogger("vyc.accounts")

USERNAME_MAX_LENGTH = 150
LOGIN_USER_LIMIT = 5
LOGIN_IP_LIMIT = 20
LOGIN_WINDOW_MINUTES = 15


def _user_key(username: str, ip: str | None) -> str:
    digest = hashlib.sha256(username.lower()[:USERNAME_MAX_LENGTH].encode()).hexdigest()
    return f"login:u:{digest}|{ip_hash(ip) if ip else 'none'}"


def login_keys(username: str, ip: str | None) -> tuple[str, str | None]:
    """(khoá theo tài khoản + IP, khoá theo IP). Không có IP thì chỉ còn khoá đầu."""
    return _user_key(username, ip), (f"login:ip:{ip_hash(ip)}" if ip else None)


def login_user(request: HttpRequest, username: str, password: str) -> User:
    """Kiểm khoá, xác thực, mở phiên. Sai thì cộng lần sai vào cả hai khoá rồi 401.

    Khoá kiểm **trước** mật khẩu nên đã bị khoá thì mật khẩu đúng cũng nhận 429.
    """
    ip = get_client_ip(request)
    user_key, ip_key = login_keys(username, ip)
    if ip_key is None:
        logger.warning("client_ip_missing")
    throttle.check(
        user_key, limit=LOGIN_USER_LIMIT, minutes=LOGIN_WINDOW_MINUTES, code="LOGIN_LOCKED"
    )
    if ip_key is not None:
        throttle.check(
            ip_key, limit=LOGIN_IP_LIMIT, minutes=LOGIN_WINDOW_MINUTES, code="LOGIN_LOCKED"
        )

    user = authenticate(request, username=username, password=password)
    if not isinstance(user, User):
        throttle.hit(user_key)
        if ip_key is not None:
            throttle.hit(ip_key)
        # Cùng một thông báo cho tài khoản không có, bị ngừng dùng và sai mật khẩu.
        raise ApiError("INVALID_CREDENTIALS", "Sai tên đăng nhập hoặc mật khẩu", status=401)

    login(request, user)  # đổi khoá phiên, quay CSRF token; hạn phiên lấy từ SESSION_COOKIE_AGE
    throttle.reset(user_key)
    return user


def logout_user(request: HttpRequest) -> None:
    logout(request)
