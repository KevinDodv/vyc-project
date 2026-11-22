"""Phân quyền theo vai (backend.md 4.3). Mặc định từ chối: `api_v1` khai `auth=OWNER_ONLY`."""

from __future__ import annotations

from typing import Any

from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from ninja import Schema
from ninja.security import SessionAuth
from ninja.utils import check_csrf

from core.errors import ApiError
from core.roles import Actor, Role

SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "TRACE"})


class RoleAuth(SessionAuth):
    """Phiên Django + vai. Chưa đăng nhập: 401. Sai vai: 403. Ghi mà thiếu CSRF: 403 CSRF_FAILED."""

    def __init__(self, *roles: Role) -> None:
        # CSRF tự kiểm ở `authenticate` để người chưa đăng nhập vẫn nhận 401, không phải 403.
        super().__init__(csrf=False)
        self.roles = frozenset(role.value for role in roles)

    def authenticate(self, request: HttpRequest, key: str | None) -> Actor | None:
        user = request.user
        if not user.is_authenticated:
            return None
        if request.method not in SAFE_METHODS and check_csrf(request) is not None:
            raise ApiError(
                "CSRF_FAILED", "Phiên làm việc đã cũ, tải lại trang rồi thử lại", status=403
            )
        if getattr(user, "role", None) not in self.roles:
            raise PermissionDenied
        return user


OWNER_ONLY = RoleAuth(Role.OWNER)
ANY_STAFF = RoleAuth(Role.OWNER, Role.WORKSHOP)


def pick_out[S: Schema](
    actor: Actor, owner: type[S], workshop: type[S], obj: Any, *, own_draft: bool = False
) -> S:
    """Chọn schema output theo vai: OWNER (hoặc `own_draft`, phiếu WORKSHOP đang lập) thấy giá."""
    schema = owner if actor.role == Role.OWNER or own_draft else workshop
    return schema.model_validate(obj)
