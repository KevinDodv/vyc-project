"""Ghi audit_log (BR-19): `snapshot()` chụp trạng thái, `record()` ghi một dòng."""

from __future__ import annotations

import datetime as dt
import uuid
from collections.abc import Iterable
from decimal import Decimal
from typing import Any

from django.db import models

from core.models import AuditAction, AuditLog
from core.roles import Actor

# Không bao giờ chụp vào audit_log.
SENSITIVE_FIELDS = frozenset({"password"})


def _jsonable(value: Any) -> Any:
    if value is None or isinstance(value, bool | int | float | str):
        return value
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, dt.datetime | dt.date | dt.time):
        return value.isoformat()
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, list | tuple | set | frozenset):
        return [_jsonable(v) for v in value]
    return str(value)


def snapshot(obj: models.Model, fields: Iterable[str] | None = None) -> dict[str, Any]:
    """Chụp các cột của `obj` (khoá ngoại ghi theo `<tên>_id`), Decimal và ngày giờ thành chuỗi."""
    wanted = set(fields) if fields is not None else None
    data: dict[str, Any] = {}
    for field in obj._meta.concrete_fields:
        if field.name in SENSITIVE_FIELDS:
            continue
        if wanted is not None and field.name not in wanted and field.attname not in wanted:
            continue
        data[field.attname] = _jsonable(getattr(obj, field.attname))
    return data


def record(
    actor: Actor,
    obj: models.Model,
    action: AuditAction | str,
    *,
    before: dict[str, Any] | None = None,
    reason: str | None = None,
) -> AuditLog:
    """Ghi một dòng audit_log cho `obj`. Gọi trong `transaction.atomic` của service.

    `after` tự lấy từ `snapshot(obj)`, trừ DELETE_LINE: `after = null`, và nếu chưa có `before`
    thì chụp `obj` làm `before`.
    """
    action = AuditAction(action)
    after: dict[str, Any] | None
    if action == AuditAction.DELETE_LINE:
        after = None
        if before is None:
            before = snapshot(obj)
    else:
        after = snapshot(obj)
    return AuditLog.objects.create(
        entity=obj._meta.db_table,
        entity_id=obj.pk,
        action=action.value,
        before=before,
        after=after,
        reason=reason,
        user_id=actor.pk,
    )
