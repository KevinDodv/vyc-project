"""Lỗi API: hình dạng `{code, message, details}` (backend.md 3.2)."""

from __future__ import annotations

from typing import Any


class ApiError(Exception):
    status = 400

    def __init__(
        self, code: str, message: str, *, status: int | None = None, **details: Any
    ) -> None:
        super().__init__(code, message)
        self.code = code
        self.message = message
        if status is not None:
            self.status = status
        self.details: dict[str, Any] = details
        self.headers: dict[str, str] = {}

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"


class BusinessError(ApiError):
    """Vi phạm BR hoặc sai trạng thái. `rule` là mã BR, vào `details.rule`."""

    status = 409

    def __init__(
        self, code: str, message: str, *, rule: str, status: int = 409, **details: Any
    ) -> None:
        super().__init__(code, message, status=status, rule=rule, **details)


class Throttled(ApiError):
    """Vượt ngưỡng tần suất: 429 kèm `Retry-After`."""

    status = 429

    def __init__(self, code: str, message: str, *, retry_after: int) -> None:
        super().__init__(code, message)
        self.retry_after = retry_after
        self.headers = {"Retry-After": str(retry_after)}
