"""Tài khoản (bảng app_user, TK mục 4). Service, API, đăng nhập: việc của t3."""

from __future__ import annotations

from typing import Any

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from django.db.models import Q

from core.roles import Role


class UserStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Đang dùng"
    INACTIVE = "INACTIVE", "Ngừng dùng"


class UserManager(BaseUserManager["User"]):
    def create_user(self, username: str, password: str | None = None, **extra: Any) -> User:
        if not username:
            raise ValueError("username là bắt buộc")
        extra.setdefault("role", Role.WORKSHOP)
        user = self.model(username=username, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    username = models.TextField(unique=True)
    full_name = models.TextField()
    # Giữ đúng tên cột của TK mục 4.
    password = models.CharField(max_length=128, db_column="password_hash")
    last_login = models.DateTimeField(null=True, blank=True, db_column="last_login_at")
    role = models.TextField(choices=Role.choices)
    status = models.TextField(choices=UserStatus.choices, default=UserStatus.ACTIVE)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["full_name", "role"]

    class Meta:
        db_table = "app_user"
        constraints = [
            models.CheckConstraint(condition=Q(role__in=Role.values), name="app_user_role_valid"),
        ]

    @property
    def is_active(self) -> bool:  # type: ignore[override]
        return self.status == UserStatus.ACTIVE

    def __str__(self) -> str:
        return self.username
