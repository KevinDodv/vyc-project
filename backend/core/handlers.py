"""Exception handler cho cả hai NinjaAPI: mọi lỗi trả `{code, message, details}` (3.2)."""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.views.defaults import page_not_found
from ninja import NinjaAPI
from ninja.errors import AuthenticationError, AuthorizationError, HttpError, ValidationError

from core.errors import ApiError

logger = logging.getLogger("vyc.errors")

# Nguồn của tham số trong `loc` của Ninja, không phải tên trường.
_SOURCES = {"body", "query", "path", "header", "cookie", "form", "file"}
_VALUE_ERROR_PREFIX = "Value error, "


def error_body(code: str, message: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"code": code, "message": message, "details": details or {}}


def _respond(
    api: NinjaAPI,
    request: HttpRequest,
    status: int,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> HttpResponse:
    response = api.create_response(request, error_body(code, message, details), status=status)
    for name, value in (headers or {}).items():
        response[name] = value
    return response


def _field_name(loc: list[Any] | tuple[Any, ...]) -> str:
    parts = [str(p) for p in loc]
    if parts and parts[0] in _SOURCES:
        source, parts = parts[0], parts[1:]
        # Body một schema: Ninja đặt tên tham số (vd "payload") trước tên trường.
        if source == "body" and len(parts) > 1:
            parts = parts[1:]
    return ".".join(parts)


def _validation_details(exc: ValidationError) -> list[dict[str, str]]:
    errors = []
    for err in exc.errors:
        message = str(err.get("msg", ""))
        message = message.removeprefix(_VALUE_ERROR_PREFIX)
        errors.append({"field": _field_name(err.get("loc", ())), "message": message})
    return errors


def register_handlers(api: NinjaAPI) -> None:
    """Gắn handler vào `api`. Ninja tra theo MRO nên lớp con thắng lớp cha."""

    @api.exception_handler(ApiError)
    def on_api_error(request: HttpRequest, exc: ApiError) -> HttpResponse:
        return _respond(api, request, exc.status, exc.code, exc.message, exc.details, exc.headers)

    @api.exception_handler(ValidationError)
    def on_validation_error(request: HttpRequest, exc: ValidationError) -> HttpResponse:
        return _respond(
            api,
            request,
            400,
            "VALIDATION_ERROR",
            "Dữ liệu gửi lên không hợp lệ",
            {"errors": _validation_details(exc)},
        )

    @api.exception_handler(AuthenticationError)
    def on_unauthenticated(request: HttpRequest, exc: AuthenticationError) -> HttpResponse:
        return _respond(api, request, 401, "UNAUTHENTICATED", "Bạn chưa đăng nhập")

    @api.exception_handler(AuthorizationError)
    def on_authorization_error(request: HttpRequest, exc: AuthorizationError) -> HttpResponse:
        return _respond(api, request, 403, "FORBIDDEN", "Bạn không có quyền thực hiện thao tác này")

    @api.exception_handler(PermissionDenied)
    def on_permission_denied(request: HttpRequest, exc: PermissionDenied) -> HttpResponse:
        return _respond(api, request, 403, "FORBIDDEN", "Bạn không có quyền thực hiện thao tác này")

    @api.exception_handler(Http404)
    @api.exception_handler(ObjectDoesNotExist)
    def on_not_found(request: HttpRequest, exc: Exception) -> HttpResponse:
        return _respond(api, request, 404, "NOT_FOUND", "Không tìm thấy")

    @api.exception_handler(HttpError)
    def on_http_error(request: HttpRequest, exc: HttpError) -> HttpResponse:
        return _respond(api, request, exc.status_code, f"HTTP_{exc.status_code}", str(exc))

    @api.exception_handler(Exception)
    def on_unexpected(request: HttpRequest, exc: Exception) -> HttpResponse:
        logger.error("unhandled_exception", exc_info=exc, extra={"path": request.path})
        return _respond(
            api, request, 500, "INTERNAL_ERROR", "Hệ thống gặp lỗi, vui lòng thử lại sau"
        )


def not_found(request: HttpRequest, exception: Exception | None = None) -> HttpResponse:
    """`handler404` của URLconf: đường dẫn `/api/...` không khớp route nào cũng trả JSON mục 3.2."""
    if request.path.startswith("/api/"):
        return JsonResponse(error_body("NOT_FOUND", "Không tìm thấy"), status=404)
    return page_not_found(request, exception or Http404())


class ApiMethodNotAllowedMiddleware:
    """Ninja trả 405 là một HttpResponse chữ thường, không raise nên handler không bắt được.
    Đổi sang JSON mục 3.2 cho đường dẫn `/api/...` (giữ header `Allow`)."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        if response.status_code == 405 and request.path.startswith("/api/"):
            replaced = JsonResponse(
                error_body("HTTP_405", "Phương thức không được hỗ trợ"), status=405
            )
            if "Allow" in response:
                replaced["Allow"] = response["Allow"]
            return replaced
        return response
