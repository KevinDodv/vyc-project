"""Nơi duy nhất render Markdown lấy từ DB (backend.md 8); frontend chỉ dùng `set:html`."""

from __future__ import annotations

import markdown as _markdown
import nh3

ALLOWED_TAGS = {"p", "br", "ul", "ol", "li", "strong", "em", "a", "h2", "h3", "blockquote"}
ALLOWED_ATTRIBUTES = {"a": {"href", "title"}}
URL_SCHEMES = {"http", "https", "mailto", "tel"}
# Bỏ cả nội dung bên trong các thẻ này, không chỉ bỏ thẻ.
CLEAN_CONTENT_TAGS = {"script", "style", "iframe", "object", "embed", "noscript", "template"}


def render_public_markdown(src: str | None) -> str | None:
    """Markdown → HTML đã làm sạch bằng nh3. Rỗng hoặc chỉ khoảng trắng thì `None`.

    Không cho `<img>`: ảnh sản phẩm đi qua `images` (đã qua `store_image`).
    """
    if src is None or not src.strip():
        return None
    html = _markdown.markdown(src)
    return nh3.clean(
        html,
        tags=ALLOWED_TAGS,
        clean_content_tags=CLEAN_CONTENT_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        url_schemes=URL_SCHEMES,
        link_rel="nofollow noopener noreferrer",
        strip_comments=True,
    )
