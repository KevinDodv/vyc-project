"""API địa bàn: phân quyền, cây Tỉnh > Xã > Thôn, cha đúng cấp, không trùng tên, audit_log."""

from __future__ import annotations

import json
from typing import Any

import pytest
from django.test import Client

from catalog.models import Area, AreaLevel
from core.models import AuditLog

pytestmark = pytest.mark.django_db

URL = "/api/v1/areas"


def post(client: Client, payload: dict[str, Any]) -> Any:
    return client.post(URL, payload, content_type="application/json")


def patch(client: Client, area_id: int, payload: dict[str, Any]) -> Any:
    return client.patch(f"{URL}/{area_id}", payload, content_type="application/json")


def body(response: Any) -> Any:
    return json.loads(response.content)


def node(client: Client, code: str) -> dict[str, Any]:
    """Nút gốc theo mã trong cây (DB test đã có sẵn tỉnh LC từ migration seed)."""
    found: dict[str, Any] = next(n for n in body(client.get(URL)) if n["code"] == code)
    return found


def make_area(code: str, level: str, name: str, parent: Area | None = None, **extra: Any) -> Area:
    return Area.objects.create(code=code, level=level, name=name, parent=parent, **extra)


@pytest.fixture
def province() -> Area:
    return make_area("T-A", AreaLevel.PROVINCE, "Tỉnh A")


@pytest.fixture
def commune(province: Area) -> Area:
    return make_area("X-A1", AreaLevel.COMMUNE, "Xã A1", province)


# ------------------------------------------------------------------ phân quyền


def test_anonymous_gets_401(client: Client, province: Area) -> None:
    assert client.get(URL).status_code == 401
    assert client.get(f"{URL}/{province.pk}").status_code == 401
    r = post(client, {"code": "X", "level": "PROVINCE", "name": "X"})
    assert r.status_code == 401
    assert patch(client, province.pk, {"name": "Y"}).status_code == 401


def test_workshop_reads_but_cannot_write(workshop_client: Client, province: Area) -> None:
    assert workshop_client.get(URL).status_code == 200
    assert workshop_client.get(f"{URL}/{province.pk}").status_code == 200

    r = post(workshop_client, {"code": "T-B", "level": "PROVINCE", "name": "Tỉnh B"})
    assert r.status_code == 403
    assert body(r)["code"] == "FORBIDDEN"
    assert Area.objects.filter(code="T-B").count() == 0

    r = patch(workshop_client, province.pk, {"name": "Đổi tên"})
    assert r.status_code == 403
    province.refresh_from_db()
    assert province.name == "Tỉnh A"
    assert not AuditLog.objects.filter(entity="area").exists()


# ------------------------------------------------------------------ đọc dạng cây


def test_list_returns_tree(owner_client: Client, province: Area, commune: Area) -> None:
    make_area("V-A1-3", AreaLevel.VILLAGE, "Thôn 3", commune)
    make_area("V-A1-1", AreaLevel.VILLAGE, "Thôn 1", commune)
    make_area("X-A2", AreaLevel.COMMUNE, "Xã A2", province)
    make_area("T-B", AreaLevel.PROVINCE, "Tỉnh B")

    r = owner_client.get(URL)
    assert r.status_code == 200
    roots = [n for n in body(r) if n["code"].startswith("T-")]
    assert [n["name"] for n in roots] == ["Tỉnh A", "Tỉnh B"]
    assert "LC" in {n["code"] for n in body(r)}  # tỉnh seed vẫn có trong cây
    assert [c["name"] for c in roots[0]["children"]] == ["Xã A1", "Xã A2"]
    villages = roots[0]["children"][0]["children"]
    assert [v["name"] for v in villages] == ["Thôn 1", "Thôn 3"]
    assert villages[0]["children"] == []
    assert roots[1]["children"] == []
    assert roots[0]["parent_id"] is None
    assert roots[0]["children"][0]["parent_id"] == province.pk


def test_list_keeps_inactive_nodes_with_status(owner_client: Client, province: Area) -> None:
    make_area("X-OLD", AreaLevel.COMMUNE, "Xã cũ", province, status="INACTIVE")
    child = node(owner_client, "T-A")["children"][0]
    assert child["status"] == "INACTIVE"


def test_detail_and_not_found(workshop_client: Client, commune: Area) -> None:
    r = workshop_client.get(f"{URL}/{commune.pk}")
    assert body(r)["code"] == "X-A1"
    assert body(r)["level"] == "COMMUNE"
    assert workshop_client.get(f"{URL}/999999").status_code == 404


# ------------------------------------------------------------------ tạo và audit_log


def test_owner_creates_province_commune_village_and_audit(owner_client: Client, owner: Any) -> None:
    r = post(
        owner_client,
        {"code": "T-N", "level": "PROVINCE", "name": "Tỉnh N", "former_name": "tỉnh cũ"},
    )
    assert r.status_code == 201
    province_id = body(r)["id"]
    assert body(r)["status"] == "ACTIVE"
    assert body(r)["valid_from"] == "2025-07-01"
    assert body(r)["former_name"] == "tỉnh cũ"

    r = post(
        owner_client,
        {"code": "X-N1", "level": "COMMUNE", "name": "Xã N1", "parent_id": province_id},
    )
    assert r.status_code == 201
    commune_id = body(r)["id"]
    r = post(
        owner_client,
        {
            "code": "V-N1-1",
            "level": "VILLAGE",
            "name": "Thôn 1",
            "parent_id": commune_id,
            "valid_from": "2026-01-01",
        },
    )
    assert r.status_code == 201
    assert body(r)["valid_from"] == "2026-01-01"

    log = AuditLog.objects.get(entity="area", entity_id=commune_id)
    assert log.action == "CREATE"
    assert log.before is None
    assert log.after is not None and log.after["name"] == "Xã N1"
    assert log.after["parent_id"] == province_id
    assert log.user_id == owner.pk
    assert AuditLog.objects.filter(entity="area").count() == 3


@pytest.mark.parametrize(
    ("level", "parent_of", "message"),
    [
        ("COMMUNE", "commune", "Cấp trên của Xã phải là Tỉnh"),
        ("COMMUNE", None, "Phải chọn cấp trên"),
        ("VILLAGE", "province", "Cấp trên của Thôn phải là Xã"),
        ("VILLAGE", None, "Phải chọn cấp trên"),
        ("PROVINCE", "province", "Tỉnh không có cấp trên"),
    ],
)
def test_wrong_parent_level_is_400(
    owner_client: Client,
    province: Area,
    commune: Area,
    level: str,
    parent_of: str | None,
    message: str,
) -> None:
    parent = {"province": province, "commune": commune}.get(parent_of or "")
    payload: dict[str, Any] = {"code": "Z-1", "level": level, "name": "Z"}
    if parent is not None:
        payload["parent_id"] = parent.pk
    before = Area.objects.count()

    r = post(owner_client, payload)
    assert r.status_code == 400
    assert body(r)["code"] == "AREA_INVALID"
    assert body(r)["message"] == message
    assert body(r)["details"]["field"] == "parent_id"
    assert Area.objects.count() == before
    assert not AuditLog.objects.filter(entity="area").exists()


def test_unknown_or_inactive_parent_is_400(owner_client: Client, province: Area) -> None:
    r = post(owner_client, {"code": "X-9", "level": "COMMUNE", "name": "Xã 9", "parent_id": 999999})
    assert r.status_code == 400
    assert body(r)["code"] == "AREA_PARENT_INVALID"
    assert body(r)["message"] == "Cấp trên không có"

    province.status = "INACTIVE"
    province.save()
    r = post(
        owner_client,
        {"code": "X-9", "level": "COMMUNE", "name": "Xã 9", "parent_id": province.pk},
    )
    assert r.status_code == 400
    assert body(r)["code"] == "AREA_PARENT_INACTIVE"
    assert body(r)["message"] == "Cấp trên đã ngừng dùng"


def test_duplicate_name_in_same_parent_is_409(
    owner_client: Client, province: Area, commune: Area
) -> None:
    r = post(
        owner_client,
        {"code": "X-NEW", "level": "COMMUNE", "name": "Xã A1", "parent_id": province.pk},
    )
    assert r.status_code == 409
    assert body(r)["code"] == "AREA_NAME_TAKEN"
    assert body(r)["message"] == "Tên «Xã A1» đã có trong cùng cấp trên"
    assert body(r)["details"]["field"] == "name"
    assert Area.objects.filter(name="Xã A1").count() == 1


def test_same_name_in_different_parent_is_ok(owner_client: Client, commune: Area) -> None:
    other = make_area("X-A2", AreaLevel.COMMUNE, "Xã A2", commune.parent)
    make_area("V-1", AreaLevel.VILLAGE, "Thôn 1", commune)
    r = post(
        owner_client,
        {"code": "V-2", "level": "VILLAGE", "name": "Thôn 1", "parent_id": other.pk},
    )
    assert r.status_code == 201


def test_duplicate_province_name_and_code_are_409(owner_client: Client, province: Area) -> None:
    r = post(owner_client, {"code": "T-NEW", "level": "PROVINCE", "name": "Tỉnh A"})
    assert r.status_code == 409
    assert body(r)["code"] == "AREA_NAME_TAKEN"
    assert body(r)["message"] == "Tên «Tỉnh A» đã có giữa các tỉnh"

    r = post(owner_client, {"code": "T-A", "level": "PROVINCE", "name": "Tỉnh khác"})
    assert r.status_code == 409
    assert body(r)["code"] == "AREA_CODE_TAKEN"
    assert body(r)["message"] == "Mã địa bàn T-A đã có"
    assert body(r)["details"]["field"] == "code"


def test_valid_to_before_valid_from_is_400(owner_client: Client) -> None:
    r = post(
        owner_client,
        {
            "code": "T-R",
            "level": "PROVINCE",
            "name": "Tỉnh R",
            "valid_from": "2026-05-01",
            "valid_to": "2026-04-30",
        },
    )
    assert r.status_code == 400
    assert body(r)["code"] == "AREA_RANGE_INVALID"
    assert body(r)["message"] == "Ngày hết hiệu lực phải sau ngày bắt đầu"


def test_invalid_body_is_400(owner_client: Client) -> None:
    r = post(owner_client, {"code": "bad code", "level": "REGION", "name": " "})
    assert r.status_code == 400
    assert body(r)["code"] == "VALIDATION_ERROR"
    fields = {e["field"] for e in body(r)["details"]["errors"]}
    assert {"code", "level", "name"} <= fields


# ------------------------------------------------------------------ sửa, ngừng dùng


def test_patch_renames_and_audits_before_after(
    owner_client: Client, owner: Any, commune: Area
) -> None:
    r = patch(owner_client, commune.pk, {"name": "Xã Mới", "former_name": "xã cũ"})
    assert r.status_code == 200
    assert body(r)["name"] == "Xã Mới"
    assert body(r)["former_name"] == "xã cũ"
    assert body(r)["code"] == "X-A1"  # không đổi

    log = AuditLog.objects.get(entity="area", entity_id=commune.pk)
    assert log.action == "UPDATE"
    assert log.before is not None and log.before["name"] == "Xã A1"
    assert log.after is not None and log.after["name"] == "Xã Mới"
    assert log.user_id == owner.pk


def test_patch_without_change_writes_no_audit(owner_client: Client, commune: Area) -> None:
    r = patch(owner_client, commune.pk, {"name": "Xã A1"})
    assert r.status_code == 200
    assert not AuditLog.objects.filter(entity="area").exists()


def test_patch_inactive_means_discontinued(owner_client: Client, commune: Area) -> None:
    r = patch(owner_client, commune.pk, {"status": "INACTIVE"})
    assert r.status_code == 200
    assert body(r)["status"] == "INACTIVE"
    commune.refresh_from_db()
    assert commune.status == "INACTIVE"
    assert AuditLog.objects.filter(entity="area", action="UPDATE").count() == 1
    # Không xoá cứng (BR-19): dòng vẫn còn và vẫn hiện trong cây.
    assert node(owner_client, "T-A")["children"][0]["status"] == "INACTIVE"


def test_patch_to_name_taken_in_same_parent_is_409(owner_client: Client, commune: Area) -> None:
    other = make_area("X-A2", AreaLevel.COMMUNE, "Xã A2", commune.parent)
    r = patch(owner_client, other.pk, {"name": "Xã A1"})
    assert r.status_code == 409
    assert body(r)["code"] == "AREA_NAME_TAKEN"
    other.refresh_from_db()
    assert other.name == "Xã A2"
    assert not AuditLog.objects.filter(entity="area").exists()


def test_patch_parent_must_keep_right_level(owner_client: Client, province: Area) -> None:
    commune = make_area("X-A1", AreaLevel.COMMUNE, "Xã A1", province)
    village = make_area("V-1", AreaLevel.VILLAGE, "Thôn 1", commune)
    new_commune = make_area("X-A2", AreaLevel.COMMUNE, "Xã A2", province)

    r = patch(owner_client, village.pk, {"parent_id": province.pk})
    assert r.status_code == 400
    assert body(r)["message"] == "Cấp trên của Thôn phải là Xã"
    assert body(r)["details"]["field"] == "parent_id"
    village.refresh_from_db()
    assert village.parent_id == commune.pk

    r = patch(owner_client, village.pk, {"parent_id": new_commune.pk})
    assert r.status_code == 200
    assert body(r)["parent_id"] == new_commune.pk

    r = patch(owner_client, village.pk, {"parent_id": None})
    assert r.status_code == 400
    assert body(r)["message"] == "Phải chọn cấp trên"


def test_patch_level_and_code_are_ignored(owner_client: Client, commune: Area) -> None:
    r = patch(owner_client, commune.pk, {"code": "KHAC", "level": "VILLAGE"})
    assert r.status_code == 200
    commune.refresh_from_db()
    assert (commune.code, commune.level) == ("X-A1", "COMMUNE")


def test_patch_null_for_required_field_is_400(owner_client: Client, commune: Area) -> None:
    r = patch(owner_client, commune.pk, {"name": None})
    assert r.status_code == 400
    assert body(r)["code"] == "VALIDATION_ERROR"
    r = patch(owner_client, commune.pk, {"status": "DELETED"})
    assert r.status_code == 400


def test_patch_valid_range_checked_against_stored_value(
    owner_client: Client, commune: Area
) -> None:
    r = patch(
        owner_client, commune.pk, {"valid_to": "2025-06-30"}
    )  # valid_from mặc định 2025-07-01
    assert r.status_code == 400
    assert body(r)["code"] == "AREA_RANGE_INVALID"


def test_patch_not_found(owner_client: Client) -> None:
    assert patch(owner_client, 999999, {"name": "X"}).status_code == 404
