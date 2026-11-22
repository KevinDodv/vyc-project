"""Vai trò và kiểu người dùng. Ở core để core dùng được mà không import ngược accounts."""

from __future__ import annotations

from typing import Any, Protocol

from django.db import models


class Role(models.TextChoices):
    OWNER = "OWNER", "Chủ doanh nghiệp"
    WORKSHOP = "WORKSHOP", "Xưởng"


class Actor(Protocol):
    """Người thực hiện thao tác. `accounts.User` thoả Protocol này."""

    @property
    def pk(self) -> Any: ...

    @property
    def role(self) -> str: ...

    @property
    def is_authenticated(self) -> bool: ...
