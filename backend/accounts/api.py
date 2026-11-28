"""Router `/api/v1/auth` (backend.md 4.1, 4.2: csrf, login, logout, me) và `/api/v1/users`."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any, ClassVar, Literal

from django.contrib.auth import update_session_auth_hash
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.middleware.csrf import CsrfViewMiddleware, get_token
from ninja import Field, Query, Router, Schema, Status
from ninja.utils import check_csrf
from pydantic import AliasChoices, StringConstraints, model_validator

from accounts import services
from accounts.models import User
from core.errors import ApiError
from core.pagination import DEFAULT_PAGE_SIZE, Page, paginate
from core.permissions import ANY_STAFF

router = Router(tags=["Tài khoản"])
# `/users` (quản lý tài khoản): mọi route chỉ OWNER, nhờ `OWNER_ONLY` mặc định của `api_v1`.
users_router = Router(tags=["Tài khoản"])


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


# ---------------------------------------------------------------------------- /users (OWNER)

Username = Annotated[str, StringConstraints(pattern=r"^[A-Za-z0-9._-]{3,50}$")]
FullName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
# Chặn mật khẩu khổng lồ như LoginIn: argon2 băm mất thời gian theo độ dài.
NewPassword = Annotated[str, Field(min_length=services.PASSWORD_MIN_LENGTH, max_length=256)]
RoleLiteral = Literal["OWNER", "WORKSHOP"]
StatusLiteral = Literal["ACTIVE", "INACTIVE"]


class UserIn(Schema):
    username: Username
    full_name: FullName
    role: RoleLiteral
    password: NewPassword


class UserPatch(Schema):
    """Không có `username`: tên đăng nhập không đổi được. Gửi `null` cho trường nào cũng sai."""

    full_name: FullName | None = None
    role: RoleLiteral | None = None
    status: StatusLiteral | None = None
    password: NewPassword | None = None
    _FIELDS: ClassVar[tuple[str, ...]] = ("full_name", "role", "status", "password")

    @model_validator(mode="after")
    def _reject_null(self) -> UserPatch:
        for name in self._FIELDS:
            if name in self.model_fields_set and getattr(self, name) is None:
                raise ValueError(f"{name} không được để trống")
        return self

    def patch_fields(self) -> dict[str, Any]:
        return self.model_dump(exclude_unset=True)


class UserOut(Schema):
    """Không có hash mật khẩu và không có trường `password` nào."""

    id: int
    username: str
    full_name: str
    role: str
    status: str
    # Model đặt tên thuộc tính là `last_login` (cột DB là last_login_at); nhận cả hai tên để
    # Page[UserOut] dựng lại từ UserOut không vỡ.
    last_login_at: datetime | None = Field(
        None, validation_alias=AliasChoices("last_login_at", "last_login")
    )


@users_router.get("", response=Page[UserOut], summary="Danh sách tài khoản")
def list_users(
    request: HttpRequest,
    page: int = Query(1, ge=1),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=200),
    role: RoleLiteral | None = None,
    status: StatusLiteral | None = None,
    q: str | None = None,
) -> Page[UserOut]:
    qs = User.objects.order_by("username", "id")
    if role:
        qs = qs.filter(role=role)
    if status:
        qs = qs.filter(status=status)
    if q:
        qs = qs.filter(Q(username__icontains=q) | Q(full_name__icontains=q))
    rows, total = paginate(qs, page, page_size)
    items = [UserOut.model_validate(u) for u in rows]
    return Page[UserOut](items=items, total=total, page=page, page_size=page_size)


@users_router.get("/{user_id}", response=UserOut, summary="Chi tiết tài khoản")
def get_user(request: HttpRequest, user_id: int) -> UserOut:
    return UserOut.model_validate(User.objects.get(pk=user_id))


@users_router.post("", response={201: UserOut}, summary="Tạo tài khoản")
def create_user(request: HttpRequest, payload: UserIn) -> Status:
    user = services.create_user(**payload.model_dump(), actor=_actor(request))
    return Status(201, UserOut.model_validate(user))


@users_router.patch("/{user_id}", response=UserOut, summary="Sửa tài khoản, đặt lại mật khẩu")
def update_user(request: HttpRequest, user_id: int, payload: UserPatch) -> UserOut:
    actor = _actor(request)
    user, password_changed = services.update_user(
        user_id=user_id, changes=payload.patch_fields(), actor=actor
    )
    if password_changed and user.pk == actor.pk:
        update_session_auth_hash(request, user)  # đổi mật khẩu của chính mình không bị văng phiên
    return UserOut.model_validate(user)


def _actor(request: HttpRequest) -> User:
    user: User = request.user  # type: ignore[assignment]  # RoleAuth đã bảo đảm đã đăng nhập
    return user
