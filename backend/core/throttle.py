"""Giới hạn tần suất bằng bảng `throttle_hit` (backend.md 5.2).

Các hàm chạy bằng cursor riêng, không mở giao dịch: gọi ngoài giao dịch nghiệp vụ, vì `hit()`
trong giao dịch bị rollback thì lần sai cũng biến mất.
"""

from __future__ import annotations

import functools
import logging
import time
from collections.abc import Callable
from datetime import timedelta
from typing import Any

from django.db import connection
from django.http import HttpRequest
from django.utils import timezone

from core.clientip import get_client_ip, ip_hash
from core.errors import Throttled

logger = logging.getLogger("vyc.throttle")

DEFAULT_MESSAGES = {
    "RATE_LIMITED": "Bạn thao tác quá nhanh, thử lại sau ít phút",
    "LOGIN_LOCKED": "Sai mật khẩu 5 lần, thử lại sau 15 phút",
}

_last_missing_log = 0.0


def hit(key: str) -> None:
    """Cộng 1 vào dòng của phút hiện tại."""
    with connection.cursor() as cur:
        cur.execute(
            """INSERT INTO throttle_hit (key, window_start, hits)
               VALUES (%s, date_trunc('minute', now()), 1)
               ON CONFLICT (key, window_start)
               DO UPDATE SET hits = throttle_hit.hits + 1""",
            [key],
        )


def count(key: str, minutes: int) -> int:
    """Tổng lượt của `key` trong `minutes` phút gần nhất (cửa sổ trượt theo dòng phút)."""
    with connection.cursor() as cur:
        cur.execute(
            """SELECT COALESCE(SUM(hits), 0) FROM throttle_hit
               WHERE key = %s AND window_start > now() - make_interval(mins => %s)""",
            [key, minutes],
        )
        row = cur.fetchone()
    return int(row[0]) if row else 0


def _retry_after(minutes: int) -> int:
    if minutes <= 1:
        return 60 - timezone.now().second
    return minutes * 60


def check(
    key: str, *, limit: int, minutes: int, code: str = "RATE_LIMITED", message: str | None = None
) -> None:
    """Raise `Throttled` (429) nếu `count(key, minutes) >= limit`."""
    if count(key, minutes) >= limit:
        raise Throttled(
            code,
            message or DEFAULT_MESSAGES.get(code, DEFAULT_MESSAGES["RATE_LIMITED"]),
            retry_after=_retry_after(minutes),
        )


def reset(key: str) -> None:
    """Xoá mọi dòng của `key` (đăng nhập đúng thì xoá khoá `login:u:`)."""
    with connection.cursor() as cur:
        cur.execute("DELETE FROM throttle_hit WHERE key = %s", [key])


def purge(*, older_than: timedelta = timedelta(days=1)) -> int:
    """Xoá dòng cũ hơn `older_than`. Trả số dòng đã xoá (lệnh `manage.py purge_throttle`)."""
    with connection.cursor() as cur:
        cur.execute(
            "DELETE FROM throttle_hit WHERE window_start < %s", [timezone.now() - older_than]
        )
        return cur.rowcount


def _warn_client_ip_missing() -> None:
    """Gộp: tối đa một dòng WARNING mỗi phút."""
    global _last_missing_log
    now = time.monotonic()
    if now - _last_missing_log >= 60:
        _last_missing_log = now
        logger.warning("client_ip_missing")


def throttle[**P, R](
    scope: str, *, limit: int, minutes: int = 1
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator cho route `/api/public`: khoá `<scope>:<ip_hash>`, `check` rồi `hit`.

    `client_ip is None` (Astro quên gửi X-Forwarded-For) thì bỏ qua throttle và ghi log, vì lấy
    IP container làm khoá sẽ gộp mọi khách vào một khoá (backend.md 5.2).
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            request: Any = args[0] if args else kwargs.get("request")
            if isinstance(request, HttpRequest):
                ip = get_client_ip(request)
                if ip is None:
                    _warn_client_ip_missing()
                else:
                    key = f"{scope}:{ip_hash(ip)}"
                    check(key, limit=limit, minutes=minutes)
                    hit(key)
            return func(*args, **kwargs)

        return wrapper

    return decorator
