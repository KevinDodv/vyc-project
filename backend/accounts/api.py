"""Router `/api/v1/auth` (backend.md 4.1, 4.2): csrf, login, logout, me."""

from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.middleware.csrf import CsrfViewMiddleware, get_token
from ninja import Field, Router, Schema, Status
from ninja.utils import check_csrf

from accounts import services
from accounts.models import User
from core.errors import ApiError
from core.permissions import ANY_STAFF

router = Router(tags=["Tài khoản"])


class LoginIn(Schema):
    username: str = Field(min_length=1, max_length=services.USERNAME_MAX_LENGTH)
    # Chặn mật khẩu khổng lồ: argon2 băm mất thời gian theo độ dài.
    password: str = Field(min_length=1, max_length=256)


class MeOut(Schema):
    id: int
    username: str
    full_name: str
    role: str


def _require_csrf(request: HttpRequest) -> None:
    """Login không có auth nên Ninja không kiểm CSRF; kiểm tay để chống login CSRF (4.2)."""
    if check_csrf(request) is not None:
        raise ApiError("CSRF_FAILED", "Phiên làm việc đã cũ, tải lại trang rồi thử lại", status=403)


def _write_csrf_cookie(request: HttpRequest, response: HttpResponse) -> None:
    """Dự án không bật CsrfViewMiddleware (chỉ kiểm trong RoleAuth), nên không ai đặt cookie
    `csrftoken` sau `get_token()` hay `login()`. Gọi `process_response` của Django để đặt."""
    CsrfViewMiddleware(lambda r: response).process_response(request, response)


@router.get("/csrf", auth=None, response={204: None})
def csrf(request: HttpRequest, response: HttpResponse) -> Status:
    """Đặt cookie `csrftoken` (JS đọc được, gửi lại bằng header X-CSRFToken)."""
    get_token(request)
    _write_csrf_cookie(request, response)
    return Status(204, None)


@router.post("/login", auth=None, response=MeOut)
def login(request: HttpRequest, response: HttpResponse, payload: LoginIn) -> User:
    _require_csrf(request)
    user = services.login_user(request, payload.username, payload.password)
    _write_csrf_cookie(request, response)  # login() đã quay token
    return user


@router.post("/logout", auth=ANY_STAFF, response={204: None})
def logout(request: HttpRequest, response: HttpResponse) -> Status:
    services.logout_user(request)
    _write_csrf_cookie(request, response)
    return Status(204, None)


@router.get("/me", auth=ANY_STAFF, response=MeOut)
def me(request: HttpRequest) -> User:
    user: User = request.user  # type: ignore[assignment]  # RoleAuth đã bảo đảm đã đăng nhập
    return user
