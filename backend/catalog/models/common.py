"""Enum dùng chung cho các bảng danh mục có cột `status` ACTIVE / INACTIVE."""

from __future__ import annotations

from django.db import models


class ActiveStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Đang dùng"
    INACTIVE = "INACTIVE", "Ngừng dùng"
