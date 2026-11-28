"""Cấu hình hệ thống (bảng setting, TK mục 4 và 13).

Chỉ nhận các khoá trong `DEFAULTS`; khoá nào chưa có dòng trong DB thì dùng giá trị mặc định, nên
code khác đọc qua `get_value()` luôn có kết quả dù seed chưa chạy. Kiểu và khoảng giá trị kiểm ở
schema API (`catalog.api.schemas.settings`).
"""

from __future__ import annotations

from typing import Any

from django.db import transaction

from accounts.models import User
from core.errors import ApiError
from core.models import AuditAction, AuditLog, Setting

# Giá trị mặc định chờ chủ DN chốt (TK mục 13). Thêm khoá mới ở CUỐI để số hiệu audit không đổi,
# và thêm cả vào core/migrations/0002_seed_settings.py nếu muốn seed.
DEFAULTS: dict[str, Any] = {
    "scan_warning_threshold": 20,  # BR-18: quét quá số lần này thì hiện cảnh báo
    "price_deviation_pct": 20,  # % giá mua lệch bảng giá thì cảnh báo
    "label_size": {"width_mm": 40, "height_mm": 30},  # khổ tem serial và tem lô
    "print_format": "A5",  # A5 hoặc THERMAL_80
    "retain_default_months": 12,  # BR-29: số tháng lưu mẫu khi công thức để trống
}
KEYS: tuple[str, ...] = tuple(DEFAULTS)


def get_all() -> dict[str, Any]:
    """Mọi khoá đã biết: giá trị trong DB, thiếu thì mặc định."""
    stored = {s.key: s.value for s in Setting.objects.filter(key__in=KEYS)}
    return {key: stored.get(key, DEFAULTS[key]) for key in KEYS}


def get_value(key: str) -> Any:
    """Giá trị một khoá đã biết (KeyError nếu khoá lạ: lỗi của người gọi, không phải của client)."""
    default = DEFAULTS[key]
    row = Setting.objects.filter(key=key).first()
    return default if row is None else row.value


@transaction.atomic
def update_settings(*, changes: dict[str, Any], actor: User) -> dict[str, Any]:
    """Đổi các khoá trong `changes`. Khoá nào không đổi giá trị thì không ghi, không audit.

    `audit.record` cần khoá chính số mà setting có khoá chính chữ, nên ghi thẳng một dòng
    audit_log cho mỗi khoá đổi: `entity_id` = số thứ tự (từ 1) của khoá trong `KEYS`.
    """
    unknown = sorted(set(changes) - set(DEFAULTS))
    if unknown:
        raise ApiError("SETTING_UNKNOWN", f"Không có cấu hình «{unknown[0]}»", field=unknown[0])
    current = get_all()
    for key, value in changes.items():
        if current[key] == value:
            continue
        Setting.objects.update_or_create(key=key, defaults={"value": value})
        AuditLog.objects.create(
            entity="setting",
            entity_id=KEYS.index(key) + 1,
            action=AuditAction.UPDATE.value,
            before={key: current[key]},
            after={key: value},
            user_id=actor.pk,
        )
    return get_all()
