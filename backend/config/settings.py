"""Cấu hình Django. Một file, đọc biến môi trường (docs/kien-truc/van-hanh.md mục 4)."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def env_list(name: str, default: str = "") -> list[str]:
    raw = os.environ.get(name, default)
    return [part.strip() for part in raw.split(",") if part.strip()]


def database_from_env() -> dict[str, Any]:
    """`DATABASE_URL` nếu có, không thì `POSTGRES_*` (tên mặc định cho dev trên máy)."""
    url = os.environ.get("DATABASE_URL", "").strip()
    if url:
        parts = urlsplit(url)
        name, user, password = parts.path.lstrip("/"), parts.username, parts.password
        host, port = parts.hostname, parts.port
        cfg: dict[str, Any] = {
            "NAME": unquote(name),
            "USER": unquote(user) if user else "",
            "PASSWORD": unquote(password) if password else "",
            "HOST": host or "",
            "PORT": str(port) if port else "",
        }
    else:
        cfg = {
            "NAME": os.environ.get("POSTGRES_DB", "vyc"),
            "USER": os.environ.get("POSTGRES_USER", "vyc"),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "vyc"),
            "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        }
    return {
        "ENGINE": "django.db.backends.postgresql",
        "CONN_MAX_AGE": 60,
        **cfg,
    }


# Tiền tố khoá giả (deploy/env/dev-defaults và mặc định dev bên dưới).
DEV_SECRET_PREFIX = "dev-only"  # noqa: S105


def require_secret(name: str, value: str, *, dev: bool, dev_default: str) -> str:
    """Khoá giả chỉ dùng được khi ENVIRONMENT=dev.

    Ngoài dev: thiếu biến, hoặc giá trị mang tiền tố `dev-only` (lỡ nạp dev-defaults cho
    staging/prod) thì không cho khởi động.
    """
    if dev:
        return value or dev_default
    if not value:
        raise ImproperlyConfigured(f"Thiếu {name} (bắt buộc ngoài môi trường dev)")
    if value.startswith(DEV_SECRET_PREFIX):
        raise ImproperlyConfigured(
            f"{name} đang là khoá dev ('{DEV_SECRET_PREFIX}...'); "
            "ngoài môi trường dev phải đặt giá trị thật"
        )
    return value


ENVIRONMENT = os.environ.get("ENVIRONMENT", "prod")  # thiếu biến thì coi là prod
_DEV = ENVIRONMENT == "dev"  # máy dev, CI chạy lint và test: được dùng khoá giả
DEBUG = env_bool("DJANGO_DEBUG", False)

SECRET_KEY = require_secret(
    "DJANGO_SECRET_KEY",
    os.environ.get("DJANGO_SECRET_KEY", ""),
    dev=_DEV,
    dev_default="dev-only-insecure-key",
)

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1" if DEBUG or _DEV else "")
SITE_ORIGIN = os.environ.get("SITE_ORIGIN", "").rstrip("/")
CSRF_TRUSTED_ORIGINS = [SITE_ORIGIN] if SITE_ORIGIN else []

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "ninja",
    "core",
    "accounts",
    "catalog",
    "operations",
    "website",
]

APPEND_SLASH = False

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "core.clientip.ClientIPMiddleware",
    "core.handlers.ApiMethodNotAllowedMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {"default": database_from_env()}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "accounts.User"
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
]
AUTH_PASSWORD_VALIDATORS: list[dict[str, str]] = []

LANGUAGE_CODE = "vi"
TIME_ZONE = "Asia/Ho_Chi_Minh"
USE_I18N = False
USE_TZ = True

# Phiên: lưu DB, hết hạn 12 giờ sau đăng nhập (backend.md 4.1).
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 12 * 3600
SESSION_SAVE_EVERY_REQUEST = False
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_HTTPONLY = False  # JS của trình duyệt đọc để gửi X-CSRFToken

_SECURE = ENVIRONMENT != "dev"  # cookie Secure chỉ khi không phải dev (van-hanh.md 4)
SESSION_COOKIE_SECURE = _SECURE
CSRF_COOKIE_SECURE = _SECURE
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# IP khách (backend.md 5.1): trống thì không tin header nào.
TRUSTED_PROXY_CIDRS = env_list("TRUSTED_PROXY_CIDRS")
IP_HASH_SALT = require_secret(
    "IP_HASH_SALT",
    os.environ.get("IP_HASH_SALT", ""),
    dev=_DEV,
    dev_default="dev-only-salt",
)

MEDIA_ROOT = Path(os.environ.get("MEDIA_ROOT", BASE_DIR / "var" / "media"))
MEDIA_PRIVATE_ROOT = Path(os.environ.get("MEDIA_PRIVATE_ROOT", BASE_DIR / "var" / "private"))
MEDIA_URL = "/media/"

ERROR_WEBHOOK_URL = os.environ.get("ERROR_WEBHOOK_URL", "")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"json": {"()": "core.logging.JsonFormatter"}},
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "json"},
        "webhook": {"class": "core.logging.WebhookHandler", "level": "ERROR"},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django.request": {
            "handlers": ["console", "webhook"],
            "level": "WARNING",
            "propagate": False,
        },
        "vyc": {"handlers": ["console", "webhook"], "level": "INFO", "propagate": False},
    },
}
