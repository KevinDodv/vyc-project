"""Fixture chung. Tài khoản dựng bằng `User.objects.create_user`, đăng nhập bằng `force_login`."""

from __future__ import annotations

import pytest
from django.test import Client

from accounts.models import User
from core.roles import Role


@pytest.fixture
def owner(db: None) -> User:
    return User.objects.create_user(
        "owner", "pw-owner-123", full_name="Chủ doanh nghiệp", role=Role.OWNER
    )


@pytest.fixture
def workshop(db: None) -> User:
    return User.objects.create_user(
        "xuong", "pw-xuong-123", full_name="Nhân viên xưởng", role=Role.WORKSHOP
    )


@pytest.fixture
def owner_client(owner: User) -> Client:
    client = Client()
    client.force_login(owner)
    return client


@pytest.fixture
def workshop_client(workshop: User) -> Client:
    client = Client()
    client.force_login(workshop)
    return client
