"""require_http_url, require_media_path (backend.md 8): giải mã lặp rồi mới kiểm."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from core.schemas import BuyLink, ImageRef, ImageVariant, require_http_url, require_media_path

GOOD_URLS = [
    "https://shopee.vn/quevanyen",
    "http://example.com",
    "https://example.com:8443/a/b?c=d#e",
]
BAD_URLS = [
    "javascript:alert(1)",
    "JaVaScRiPt:alert(1)",
    "data:text/html,<script>alert(1)</script>",
    "vbscript:msgbox(1)",
    "//evil.com",
    "/media/a.webp",
    "ftp://example.com/x",
    "https://",
    "https:///x",
    "",
    " https://example.com",
    "https://exa mple.com",
    "https://example.com/\nx",
]

GOOD_PATHS = ["/media/img/3f/3fa9-480.webp", "/media/img/3f/3fa9-1440.avif", "/media/a%20b.webp"]
BAD_PATHS = [
    "https://evil.com/a.webp",
    "//evil.com/media/a.webp",
    "/static/a.webp",
    "media/a.webp",
    "/media",
    "/media/../x",
    "/media/%2e%2e/x",  # mã hoá một lần
    "/media/%2E%2E/x",
    "/media/%252e%252e/x",  # mã hoá hai lần
    "/media/%25252e%25252e/x",  # ba lần
    "/media/a%2f%2fb",  # //
    "/media/a%252f%252fb",
    "/media//x",
    "/media/a\\b",
    "/media/a%5cb",
    "/media/a%00b",
    "/media/a\x00b",
    "/media/a\nb",
    "%2fmedia/x",
]


@pytest.mark.parametrize("url", GOOD_URLS)
def test_require_http_url_accepts(url: str) -> None:
    assert require_http_url(url) == url


@pytest.mark.parametrize("url", BAD_URLS)
def test_require_http_url_rejects(url: str) -> None:
    with pytest.raises(ValueError):
        require_http_url(url)


@pytest.mark.parametrize("path", GOOD_PATHS)
def test_require_media_path_accepts_and_returns_original(path: str) -> None:
    assert require_media_path(path) == path


@pytest.mark.parametrize("path", BAD_PATHS)
def test_require_media_path_rejects(path: str) -> None:
    with pytest.raises(ValueError):
        require_media_path(path)


def test_require_media_path_encoded_too_deep() -> None:
    # "a" mã hoá 6 lần: còn đổi sau 5 vòng giải mã thì coi là sai, dù bên trong vô hại.
    deep = "%61"
    for _ in range(5):
        deep = deep.replace("%", "%25")
    with pytest.raises(ValueError, match="quá nhiều lớp"):
        require_media_path("/media/" + deep)


def test_require_media_path_five_rounds_is_ok_when_it_settles() -> None:
    deep = "%61"  # "a" mã hoá hai lần: còn trong giới hạn
    path = "/media/" + deep.replace("%", "%25")
    assert require_media_path(path) == path


def test_image_ref_rejects_unsafe_variant_url() -> None:
    ok = ImageVariant(width=480, format="webp", url="/media/img/3f/3fa9-480.webp")
    assert ImageRef(alt="x", width=480, height=360, variants=[ok]).variants[0].url == ok.url
    with pytest.raises(ValidationError):
        ImageVariant(width=480, format="webp", url="/media/%252e%252e/x")


def test_buy_link_schema() -> None:
    assert BuyLink(channel="shopee", url="https://shopee.vn/x").url == "https://shopee.vn/x"
    for bad in ("javascript:alert(1)", "//evil.com"):
        with pytest.raises(ValidationError):
            BuyLink(channel="shopee", url=bad)
    with pytest.raises(ValidationError):
        BuyLink(channel="facebook", url="https://example.com")  # type: ignore[arg-type]
