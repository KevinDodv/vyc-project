"""Khoá dev (`dev-only...`) không được dùng ngoài ENVIRONMENT=dev (#828, low #1 của Quan)."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest
from django.core.exceptions import ImproperlyConfigured

from config.settings import require_secret

BACKEND_DIR = Path(__file__).resolve().parent.parent
REAL_KEY = "k9Qz-real-secret-from-env-file"


class TestRequireSecret:
    def test_dev_falls_back_to_dev_default(self) -> None:
        got = require_secret("X", "", dev=True, dev_default="dev-only-x")
        assert got == "dev-only-x"

    def test_dev_accepts_dev_prefixed_value(self) -> None:
        got = require_secret("X", "dev-only-from-file", dev=True, dev_default="dev-only-x")
        assert got == "dev-only-from-file"

    def test_non_dev_accepts_real_value(self) -> None:
        assert require_secret("X", REAL_KEY, dev=False, dev_default="dev-only-x") == REAL_KEY

    def test_non_dev_rejects_missing(self) -> None:
        with pytest.raises(ImproperlyConfigured, match="Thiếu X"):
            require_secret("X", "", dev=False, dev_default="dev-only-x")

    @pytest.mark.parametrize(
        "value", ["dev-only-insecure-key-not-for-prod", "dev-only-salt-not-for-prod", "dev-only"]
    )
    def test_non_dev_rejects_dev_prefixed_value(self, value: str) -> None:
        with pytest.raises(ImproperlyConfigured, match="khoá dev"):
            require_secret("X", value, dev=False, dev_default="dev-only-x")


def _import_settings(
    code: str = "import config.settings", **overrides: str
) -> subprocess.CompletedProcess[str]:
    """Nạp config.settings trong tiến trình riêng với biến môi trường cho trước."""
    env = {
        k: v
        for k, v in os.environ.items()
        if k not in {"ENVIRONMENT", "DJANGO_SECRET_KEY", "IP_HASH_SALT", "DJANGO_DEBUG"}
    }
    env.update(overrides)
    return subprocess.run(  # noqa: S603  (code do test truyền, không phải đầu vào ngoài)
        [sys.executable, "-c", code],
        cwd=BACKEND_DIR,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )


@pytest.mark.parametrize(
    ("secret_key", "salt", "bad_name"),
    [
        ("dev-only-insecure-key-not-for-prod", "real-salt-123", "DJANGO_SECRET_KEY"),
        (REAL_KEY, "dev-only-salt-not-for-prod", "IP_HASH_SALT"),
    ],
)
def test_prod_refuses_to_start_with_dev_secret(secret_key: str, salt: str, bad_name: str) -> None:
    # DJANGO_DEBUG=1 cũng không mở được cửa: chỉ ENVIRONMENT=dev mới được khoá giả.
    proc = _import_settings(
        ENVIRONMENT="prod", DJANGO_SECRET_KEY=secret_key, IP_HASH_SALT=salt, DJANGO_DEBUG="1"
    )
    assert proc.returncode != 0
    assert "ImproperlyConfigured" in proc.stderr
    assert bad_name in proc.stderr


def test_prod_starts_with_real_secrets() -> None:
    proc = _import_settings(
        ENVIRONMENT="prod", DJANGO_SECRET_KEY=REAL_KEY, IP_HASH_SALT="real-salt-123"
    )
    assert proc.returncode == 0, proc.stderr


def test_dev_starts_without_secrets() -> None:
    proc = _import_settings(ENVIRONMENT="dev")
    assert proc.returncode == 0, proc.stderr


def test_missing_environment_defaults_to_prod_and_guard_blocks() -> None:
    # Quên đặt ENVIRONMENT: coi là prod nên khoá dev giả không được dùng, settings không nạp được.
    proc = _import_settings()
    assert proc.returncode != 0
    assert "ImproperlyConfigured" in proc.stderr


def test_missing_environment_is_prod_with_real_secrets() -> None:
    code = "import config.settings as s; print(s.ENVIRONMENT, s._SECURE)"
    proc = _import_settings(code, DJANGO_SECRET_KEY=REAL_KEY, IP_HASH_SALT="real-salt-123")
    assert proc.stdout.split() == ["prod", "True"], proc.stderr
