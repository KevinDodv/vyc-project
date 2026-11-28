"""`/media/` do Django phục vụ chỉ khi DEBUG (`config.urls`); staging và prod do Caddy phục vụ."""

from pathlib import Path
from typing import Any

import pytest
from django.test import Client

from config import urls


@pytest.fixture
def media_root(settings: Any, tmp_path: Path) -> Path:
    root = tmp_path / "media"
    (root / "img").mkdir(parents=True)
    (root / "img" / "a.webp").write_bytes(b"anh")
    (tmp_path / "secret.txt").write_bytes(b"bi mat")
    settings.MEDIA_ROOT = root
    return root


def use_media_urls(settings: Any, *, debug: bool) -> None:
    """URLconf chỉ gồm phần `/media/`, dựng lại theo DEBUG của từng ca."""
    settings.DEBUG = debug
    settings.ROOT_URLCONF = type("MediaUrls", (), {"urlpatterns": urls.media_urlpatterns()})


def test_debug_phuc_vu_file_trong_media_root(settings: Any, media_root: Path) -> None:
    use_media_urls(settings, debug=True)
    response = Client().get("/media/img/a.webp")
    assert response.status_code == 200
    assert b"".join(response.streaming_content) == b"anh"  # type: ignore[attr-defined]
    assert response["Content-Type"] == "image/webp"


def test_debug_khong_doc_duoc_file_ngoai_media_root(settings: Any, media_root: Path) -> None:
    use_media_urls(settings, debug=True)
    for url in ("/media/../secret.txt", "/media/img/%2e%2e/%2e%2e/secret.txt"):
        assert Client().get(url).status_code in (400, 404)


def test_khong_debug_thi_khong_co_route(settings: Any, media_root: Path) -> None:
    use_media_urls(settings, debug=False)
    assert urls.media_urlpatterns() == []
    assert Client().get("/media/img/a.webp").status_code == 404
