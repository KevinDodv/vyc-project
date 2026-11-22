"""Kiểu dùng chung cho URL và đường dẫn ảnh trong schema (backend.md 8).

URL trong DTO không đi qua nh3 nên kiểm ở đây: lúc ghi thì lỗi thành 400 VALIDATION_ERROR, lúc đọc
(DTO công khai) service gọi cùng hai hàm `require_*` để bỏ phần tử sai.
"""

from __future__ import annotations

from typing import Annotated, Literal
from urllib.parse import unquote, urlsplit

from ninja import Schema
from pydantic import AfterValidator

MEDIA_PREFIX = "/media/"
MAX_DECODE_ROUNDS = 5


def _has_control_chars(value: str) -> bool:
    return any(ord(ch) < 32 or ord(ch) == 127 for ch in value)


def require_http_url(value: str) -> str:
    """Chỉ nhận `http(s)://host/...`. `javascript:`, `data:`, `//evil.com`, `/path` đều sai."""
    if _has_control_chars(value) or value != value.strip() or " " in value:
        raise ValueError("URL không được chứa khoảng trắng hay ký tự điều khiển")
    parts = urlsplit(value)
    if parts.scheme not in {"http", "https"}:
        raise ValueError("URL phải bắt đầu bằng http:// hoặc https://")
    if not parts.netloc or not parts.hostname:
        raise ValueError("URL thiếu tên miền")
    return value


def require_media_path(value: str) -> str:
    """Đường dẫn ảnh nội bộ, dạng `/media/...`.

    Giải mã %XX lặp tới khi chuỗi không đổi (tối đa 5 vòng, còn đổi thì coi là sai), rồi mới kiểm
    trên chuỗi đã giải mã: bắt đầu bằng `/media/`, không có `..`, `//`, `\\`, ký tự điều khiển.
    Trả lại `value` gốc.
    """
    if not value.startswith(MEDIA_PREFIX) or _has_control_chars(value):
        raise ValueError("Đường dẫn ảnh phải bắt đầu bằng /media/")
    decoded = value
    for _ in range(MAX_DECODE_ROUNDS):
        step = unquote(decoded)
        if step == decoded:
            break
        decoded = step
    else:
        raise ValueError("Đường dẫn ảnh mã hoá quá nhiều lớp")
    if (
        not decoded.startswith(MEDIA_PREFIX)
        or ".." in decoded
        or "//" in decoded
        or "\\" in decoded
        or _has_control_chars(decoded)
    ):
        raise ValueError("Đường dẫn ảnh không hợp lệ")
    return value


SafeHttpUrl = Annotated[str, AfterValidator(require_http_url)]
SafeMediaPath = Annotated[str, AfterValidator(require_media_path)]


class ImageVariant(Schema):
    width: int
    format: Literal["avif", "webp", "jpeg"]
    url: SafeMediaPath


class ImageRef(Schema):
    alt: str
    width: int
    height: int
    variants: list[ImageVariant]


class BuyLink(Schema):
    channel: Literal["shopee", "tiktok", "zalo", "other"]
    url: SafeHttpUrl
