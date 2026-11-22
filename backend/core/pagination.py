"""Phân trang tự viết mỏng (backend.md 3.3). Query `?page=1&page_size=50`, tối đa 200."""

from __future__ import annotations

from django.db.models import Model, QuerySet
from ninja import Schema

DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 200


class Page[T](Schema):
    items: list[T]
    total: int
    page: int
    page_size: int


def paginate[M: Model](
    qs: QuerySet[M], page: int = 1, page_size: int = DEFAULT_PAGE_SIZE
) -> tuple[list[M], int]:
    """Trả (các dòng của trang, tổng số dòng). `page` < 1 thành 1; `page_size` kẹp trong 1..200."""
    page = max(page, 1)
    page_size = min(max(page_size, 1), MAX_PAGE_SIZE)
    total = qs.count()
    start = (page - 1) * page_size
    return list(qs[start : start + page_size]), total
