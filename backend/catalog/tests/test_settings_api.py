"""API cấu hình: seed mặc định (TK mục 13), GET cả hai vai, PATCH chỉ OWNER, audit_log."""

from __future__ import annotations

import json
from typing import Any

import pytest
from django.test import Client

from catalog.api.schemas.settings import SettingsOut, SettingsPatch
from catalog.services import settings as service
from core.models import AuditLog, Setting

pytestmark = pytest.mark.django_db

URL = "/api/v1/settings"
DEFAULTS = {
    "scan_warning_threshold": 20,
    "price_deviation_pct": 20,
    "label_size": {"width_mm": 40, "height_mm": 30},
    "print_format": "A5",
    "retain_default_months": 12,
}


def patch(client: Client, payload: dict[str, Any]) -> Any:
    return client.patch(URL, payload, content_type="application/json")


def body(response: Any) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(response.content)
    return data


def test_migration_seeds_defaults() -> None:
    assert {s.key: s.value for s in Setting.objects.all()} == DEFAULTS


def test_schemas_cover_the_same_keys_as_defaults() -> None:
    assert set(service.DEFAULTS) == set(DEFAULTS)
    assert set(SettingsOut.model_fields) == set(DEFAULTS)
    assert set(SettingsPatch.model_fields) == set(DEFAULTS)


def test_anonymous_gets_401(client: Client) -> None:
    assert client.get(URL).status_code == 401
    assert patch(client, {"scan_warning_threshold": 5}).status_code == 401


def test_both_roles_read(owner_client: Client, workshop_client: Client) -> None:
    for client in (owner_client, workshop_client):
        r = client.get(URL)
        assert r.status_code == 200
        assert body(r) == DEFAULTS


def test_get_falls_back_to_defaults_when_row_missing(owner_client: Client) -> None:
    Setting.objects.all().delete()
    assert body(owner_client.get(URL)) == DEFAULTS
    assert service.get_value("scan_warning_threshold") == 20


def test_workshop_cannot_patch(workshop_client: Client) -> None:
    r = patch(workshop_client, {"scan_warning_threshold": 5})
    assert r.status_code == 403
    assert body(r)["code"] == "FORBIDDEN"
    assert Setting.objects.get(key="scan_warning_threshold").value == 20
    assert AuditLog.objects.count() == 0


def test_owner_patches_partially_and_audits(owner_client: Client) -> None:
    r = patch(owner_client, {"scan_warning_threshold": 35, "print_format": "THERMAL_80"})
    assert r.status_code == 200, r.content
    assert body(r) == DEFAULTS | {"scan_warning_threshold": 35, "print_format": "THERMAL_80"}
    assert Setting.objects.get(key="scan_warning_threshold").value == 35
    assert Setting.objects.get(key="price_deviation_pct").value == 20  # khoá khác giữ nguyên
    assert body(owner_client.get(URL))["scan_warning_threshold"] == 35

    logs = {log.before and next(iter(log.before)): log for log in AuditLog.objects.all()}
    assert set(logs) == {"scan_warning_threshold", "print_format"}
    log = logs["scan_warning_threshold"]
    assert (log.entity, log.action) == ("setting", "UPDATE")
    assert log.before == {"scan_warning_threshold": 20}
    assert log.after == {"scan_warning_threshold": 35}
    assert log.entity_id == 1


def test_patch_label_size(owner_client: Client) -> None:
    r = patch(owner_client, {"label_size": {"width_mm": 50, "height_mm": 30}})
    assert r.status_code == 200
    assert body(r)["label_size"] == {"width_mm": 50, "height_mm": 30}


def test_patch_creates_row_when_missing(owner_client: Client) -> None:
    Setting.objects.filter(key="retain_default_months").delete()
    r = patch(owner_client, {"retain_default_months": 24})
    assert r.status_code == 200
    assert Setting.objects.get(key="retain_default_months").value == 24


def test_unchanged_value_writes_no_audit(owner_client: Client) -> None:
    assert patch(owner_client, {"scan_warning_threshold": 20}).status_code == 200
    assert patch(owner_client, {}).status_code == 200
    assert AuditLog.objects.count() == 0


@pytest.mark.parametrize(
    "payload",
    [
        {"scan_warning_threshold": 0},
        {"scan_warning_threshold": "abc"},
        {"scan_warning_threshold": None},
        {"price_deviation_pct": 101},
        {"price_deviation_pct": 0},
        {"retain_default_months": 0},
        {"print_format": "A4"},
        {"label_size": {"width_mm": 5, "height_mm": 30}},
        {"label_size": {"width_mm": 40}},
        {"label_size": None},
        {"unknown_key": 1},  # khoá lạ không lọt vào bảng setting
    ],
)
def test_rejects_invalid(owner_client: Client, payload: dict[str, Any]) -> None:
    r = patch(owner_client, payload)
    assert r.status_code == 400, payload
    assert body(r)["code"] == "VALIDATION_ERROR"
    assert {s.key: s.value for s in Setting.objects.all()} == DEFAULTS
    assert AuditLog.objects.count() == 0


def test_service_rejects_unknown_key(owner: Any) -> None:
    from core.errors import ApiError

    with pytest.raises(ApiError) as exc:
        service.update_settings(changes={"nope": 1}, actor=owner)
    assert exc.value.code == "SETTING_UNKNOWN"
    assert not Setting.objects.filter(key="nope").exists()
