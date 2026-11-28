"""Đăng nhập, khoá đăng nhập, đăng xuất (backend.md 4.1, 5.2); quản lý tài khoản (TK mục 5).

Khoá đếm lần **sai** bằng `core.throttle` (cửa sổ trượt 15 phút):
- `login:u:<sha256(username)>|<ip_hash>`: 5 lần sai thì khoá cặp tài khoản + IP đó;
- `login:ip:<ip_hash>`: 20 lần sai với mọi username thì khoá IP đó.
Phiên sống 12 giờ kể từ lúc đăng nhập (`SESSION_COOKIE_AGE`, không kéo dài theo thao tác).
"""

from __future__ import annotations

import hashlib
import logging
from typing import Any

from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError, transaction
from django.http import HttpRequest

from accounts.models import User, UserStatus
from core import audit, throttle
from core.clientip import get_client_ip, ip_hash
from core.errors import ApiError
from core.roles import Actor, Role

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


# ------------------------------------------------------------------ quản lý tài khoản (OWNER)

PASSWORD_MIN_LENGTH = 8  # TK mục 5
USER_UPDATABLE_FIELDS = frozenset({"full_name", "role", "status", "password"})


@transaction.atomic
def create_user(*, username: str, full_name: str, role: str, password: str, actor: Actor) -> User:
    """Tạo tài khoản ACTIVE. Tên đăng nhập trùng (không phân biệt hoa thường) thì 409."""
    if User.objects.filter(username__iexact=username).exists():
        raise ApiError(
            "USERNAME_TAKEN",
            f"Tên đăng nhập «{username}» đã có người dùng",
            status=409,
            field="username",
        )
    try:
        with transaction.atomic():  # savepoint: hai request tạo trùng cùng lúc
            user = User.objects.create_user(
                username, password, full_name=full_name, role=role, status=UserStatus.ACTIVE
            )
    except IntegrityError:
        raise ApiError(
            "USERNAME_TAKEN",
            f"Tên đăng nhập «{username}» đã có người dùng",
            status=409,
            field="username",
        ) from None
    audit.record(actor, user, "CREATE")  # snapshot bỏ cột password
    return user


@transaction.atomic
def update_user(*, user_id: int, changes: dict[str, Any], actor: Actor) -> tuple[User, bool]:
    """Sửa họ tên, vai, trạng thái hoặc đặt lại mật khẩu (không đổi tên đăng nhập).

    Trả (người dùng, đã đổi mật khẩu). Chặn: tự ngừng dùng chính mình; để hệ thống không còn
    OWNER đang dùng. Mật khẩu đổi thì audit_log chỉ ghi lý do, không bao giờ ghi hash.
    """
    unknown = set(changes) - USER_UPDATABLE_FIELDS
    if unknown:
        raise ValueError(f"trường không sửa được: {sorted(unknown)}")
    user = User.objects.select_for_update().get(pk=user_id)
    new_password = changes.pop("password", None)
    changes = {k: v for k, v in changes.items() if getattr(user, k) != v}
    if not changes and new_password is None:
        return user, False

    if changes.get("status") == UserStatus.INACTIVE and user.pk == actor.pk:
        raise ApiError(
            "CANNOT_DEACTIVATE_SELF",
            "Không tự ngừng dùng chính tài khoản của mình",
            status=409,
            field="status",
        )
    after_role = changes.get("role", user.role)
    after_status = changes.get("status", user.status)
    if user.role == Role.OWNER and (after_role != Role.OWNER or after_status != UserStatus.ACTIVE):
        # Khoá các OWNER đang dùng khác để hai người không cùng hạ nhau xuống.
        others = (
            User.objects.select_for_update()
            .filter(role=Role.OWNER, status=UserStatus.ACTIVE)
            .exclude(pk=user.pk)
        )
        if not others.exists():
            raise ApiError(
                "LAST_OWNER",
                "Phải còn ít nhất một chủ doanh nghiệp đang dùng",
                status=409,
                field="role" if after_role != Role.OWNER else "status",
            )

    before = audit.snapshot(user)
    for name, value in changes.items():
        setattr(user, name, value)
    if new_password is not None:
        user.set_password(new_password)
    user.save()
    audit.record(
        actor,
        user,
        "UPDATE",
        before=before,
        reason="Đặt lại mật khẩu" if new_password is not None else None,
    )
    return user, new_password is not None
