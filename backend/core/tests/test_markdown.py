"""render_public_markdown: các ca XSS ở backend.md mục 8."""

from __future__ import annotations

import pytest

from core.markdown import render_public_markdown


def render(src: str) -> str:
    out = render_public_markdown(src)
    assert out is not None
    return out


def test_blank_gives_none() -> None:
    assert render_public_markdown(None) is None
    assert render_public_markdown("") is None
    assert render_public_markdown("  \n ") is None


def test_basic_markdown_survives() -> None:
    html = render("## Tiêu đề\n\nQuế **Văn Yên** và *tinh dầu*.\n\n- một\n- hai\n\n> trích")
    for tag in ("<h2>", "<strong>Văn Yên</strong>", "<em>tinh dầu</em>", "<ul>", "<li>một</li>"):
        assert tag in html
    assert "<blockquote>" in html


def test_javascript_href_is_dropped() -> None:
    html = render("[x](javascript:alert(1))")
    assert "<a" in html
    assert "href" not in html
    assert "javascript" not in html


@pytest.mark.parametrize(
    "src",
    [
        "[x](data:text/html;base64,PHNjcmlwdD4=)",
        "[x](vbscript:msgbox(1))",
        "[x](JaVaScRiPt:alert(1))",
        '<a href="javascript:alert(1)">x</a>',
        '<a href="&#106;avascript:alert(1)">x</a>',
    ],
)
def test_dangerous_schemes_are_dropped(src: str) -> None:
    html = render(src)
    assert "href" not in html
    assert "script:" not in html.lower()


def test_safe_links_keep_href_and_get_rel() -> None:
    html = render("[a](https://example.com) [b](mailto:a@example.com) [c](tel:0123456789)")
    assert 'href="https://example.com"' in html
    assert 'href="mailto:a@example.com"' in html
    assert 'href="tel:0123456789"' in html
    assert 'rel="nofollow noopener noreferrer"' in html


def test_img_and_onerror_are_removed() -> None:
    html = render("<img src=x onerror=alert(1)>")
    assert "<img" not in html
    assert "onerror" not in html


def test_markdown_image_is_removed() -> None:
    assert "<img" not in render("![alt](/media/img/a.webp)")


def test_onclick_is_removed() -> None:
    html = render('<a href="#" onclick="alert(1)">x</a>')
    assert "onclick" not in html


@pytest.mark.parametrize("tag", ["script", "iframe", "style"])
def test_raw_dangerous_tags_are_removed_with_content(tag: str) -> None:
    html = render(f"Trước\n\n<{tag}>alert(1)</{tag}>\n\nSau")
    assert tag not in html
    assert "alert(1)" not in html
    assert "Trước" in html
    assert "Sau" in html


def test_other_attributes_are_removed() -> None:
    html = render('<p style="color:red" class="x" id="y" onmouseover="alert(1)">t</p>')
    assert "style" not in html
    assert "class" not in html
    assert "onmouseover" not in html


def test_comments_are_stripped() -> None:
    assert "<!--" not in render("a <!-- bí mật --> b")


def test_disallowed_headings_are_flattened() -> None:
    assert "<h1" not in render("# H1\n\n<h1>x</h1>")


def test_target_attribute_is_not_allowed() -> None:
    html = render('<a href="https://example.com" target="_blank">x</a>')
    assert "target" not in html
