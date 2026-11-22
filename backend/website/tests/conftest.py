"""Fixture cho test website: dùng lại dữ liệu mẫu của catalog."""

from __future__ import annotations

import pytest

from catalog.models import GoodsType


@pytest.fixture
def goods_type(db: None) -> GoodsType:
    """Loại hàng seed bởi catalog migration 0002."""
    return GoodsType.objects.get(code="TINH_DAU")
