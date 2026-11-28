"""API loại hàng hóa và nguyên liệu kèm hạng: phân quyền, quy tắc khoá, hook lô, audit_log."""

from __future__ import annotations

import json
from typing import Any

import pytest
from django.test import Client

from catalog.models import GoodsType, Grade, Material
from catalog.services import materials as materials_service
from catalog.tests.conftest import make_product
from core.models import AuditLog

pytestmark = pytest.mark.django_db

GT_URL = "/api/v1/goods-types"
MAT_URL = "/api/v1/materials"


def post(client: Client, url: str, payload: dict[str, Any]) -> Any:
    return client.post(url, payload, content_type="application/json")


def patch(client: Client, url: str, payload: dict[str, Any]) -> Any:
    return client.patch(url, payload, content_type="application/json")


def body(response: Any) -> Any:
    return json.loads(response.content)


@pytest.fixture
def lot_hook(monkeypatch: pytest.MonkeyPatch) -> list[int]:
    """Giả lập hook của đợt 2: danh sách id hạng đang có lô trong kho (rỗng: không hạng nào)."""
    busy: list[int] = []
    monkeypatch.setattr(materials_service, "_grade_in_use_checks", [lambda gid: gid in busy])
    return busy


# ================================================================== /goods-types


def test_goods_types_anonymous_and_workshop(
    client: Client, workshop_client: Client, goods_type: GoodsType
) -> None:
    assert client.get(GT_URL).status_code == 401
    assert post(client, GT_URL, {"code": "X", "name": "X", "grp": "PRODUCT"}).status_code == 401

    assert workshop_client.get(GT_URL).status_code == 200
    assert workshop_client.get(f"{GT_URL}/{goods_type.pk}").status_code == 200
    r = post(workshop_client, GT_URL, {"code": "NEW", "name": "Mới", "grp": "PRODUCT"})
    assert r.status_code == 403
    assert body(r)["code"] == "FORBIDDEN"
    assert not GoodsType.objects.filter(code="NEW").exists()
    r = patch(workshop_client, f"{GT_URL}/{goods_type.pk}", {"name": "Đổi"})
    assert r.status_code == 403
    assert not AuditLog.objects.filter(entity="goods_type").exists()


def test_goods_types_list_and_filters(owner_client: Client, goods_type: GoodsType) -> None:
    rows = body(owner_client.get(GT_URL))
    assert {r["code"] for r in rows} >= {"TINH_DAU", "QUE_NL"}
    only_material = body(owner_client.get(f"{GT_URL}?grp=MATERIAL"))
    assert only_material
    assert {r["grp"] for r in only_material} == {"MATERIAL"}
    assert body(owner_client.get(f"{GT_URL}?status=INACTIVE")) == []


def test_goods_type_create_and_audit(owner_client: Client, owner: Any) -> None:
    r = post(
        owner_client,
        GT_URL,
        {"code": "TRA_DB", "name": "Trà đặc biệt", "grp": "PRODUCT", "is_food": True},
    )
    assert r.status_code == 201
    data = body(r)
    assert (data["is_food"], data["status"], data["grp"]) == (True, "ACTIVE", "PRODUCT")
    log = AuditLog.objects.get(entity="goods_type", entity_id=data["id"])
    assert log.action == "CREATE"
    assert log.after is not None and log.after["code"] == "TRA_DB"
    assert log.user_id == owner.pk


def test_goods_type_duplicate_code_is_409(owner_client: Client, goods_type: GoodsType) -> None:
    r = post(owner_client, GT_URL, {"code": "TINH_DAU", "name": "Trùng", "grp": "PRODUCT"})
    assert r.status_code == 409
    assert body(r)["code"] == "GOODS_TYPE_CODE_TAKEN"
    assert body(r)["message"] == "Mã loại hàng TINH_DAU đã có"
    assert GoodsType.objects.filter(code="TINH_DAU").count() == 1


def test_goods_type_group_locked_when_products_use_it(
    owner_client: Client, goods_type: GoodsType
) -> None:
    make_product(goods_type)
    r = patch(owner_client, f"{GT_URL}/{goods_type.pk}", {"grp": "MATERIAL"})
    assert r.status_code == 409
    assert body(r)["code"] == "GOODS_TYPE_GROUP_LOCKED"
    assert "đã có sản phẩm dùng, không đổi nhóm được" in body(r)["message"]
    assert body(r)["details"]["field"] == "grp"
    goods_type.refresh_from_db()
    assert goods_type.grp == "PRODUCT"
    assert not AuditLog.objects.filter(entity="goods_type").exists()

    # Đổi trường khác vẫn được; gửi lại đúng nhóm hiện tại không tính là đổi nhóm.
    r = patch(owner_client, f"{GT_URL}/{goods_type.pk}", {"grp": "PRODUCT", "name": "Tinh dầu 2"})
    assert r.status_code == 200
    assert body(r)["name"] == "Tinh dầu 2"


def test_goods_type_group_locked_when_materials_use_it(owner_client: Client, db: None) -> None:
    que_nl = GoodsType.objects.get(code="QUE_NL")
    assert Material.objects.filter(goods_type=que_nl).exists()
    r = patch(owner_client, f"{GT_URL}/{que_nl.pk}", {"grp": "PRODUCT"})
    assert r.status_code == 409
    assert "đã có nguyên liệu dùng" in body(r)["message"]


def test_goods_type_group_changes_when_unused_and_audits(owner_client: Client, owner: Any) -> None:
    gt = GoodsType.objects.create(code="TMP", name="Tạm", grp="PRODUCT")
    r = patch(owner_client, f"{GT_URL}/{gt.pk}", {"grp": "MATERIAL", "is_food": True})
    assert r.status_code == 200
    assert body(r)["grp"] == "MATERIAL"
    log = AuditLog.objects.get(entity="goods_type", entity_id=gt.pk)
    assert log.action == "UPDATE"
    assert log.before is not None and log.before["grp"] == "PRODUCT"
    assert log.after is not None and log.after["grp"] == "MATERIAL"
    assert log.user_id == owner.pk


def test_goods_type_inactive_and_no_op(owner_client: Client, goods_type: GoodsType) -> None:
    url = f"{GT_URL}/{goods_type.pk}"
    r = patch(owner_client, url, {"name": goods_type.name})
    assert r.status_code == 200
    assert not AuditLog.objects.filter(entity="goods_type").exists()

    r = patch(owner_client, url, {"status": "INACTIVE"})
    assert r.status_code == 200
    assert body(r)["status"] == "INACTIVE"
    assert AuditLog.objects.filter(entity="goods_type", action="UPDATE").count() == 1
    assert body(owner_client.get(f"{GT_URL}?status=ACTIVE")) != []
    assert goods_type.pk not in {r["id"] for r in body(owner_client.get(f"{GT_URL}?status=ACTIVE"))}


def test_goods_type_invalid_body_is_400(owner_client: Client, goods_type: GoodsType) -> None:
    r = post(owner_client, GT_URL, {"code": "OK", "name": "Tên", "grp": "OTHER"})
    assert r.status_code == 400
    assert body(r)["code"] == "VALIDATION_ERROR"
    r = patch(owner_client, f"{GT_URL}/{goods_type.pk}", {"name": None})
    assert r.status_code == 400
    assert patch(owner_client, f"{GT_URL}/999999", {"name": "X"}).status_code == 404


# ================================================================== /materials


def test_materials_anonymous_and_workshop(
    client: Client, workshop_client: Client, owner: Any
) -> None:
    vq = Material.objects.get(code="VQ")
    assert client.get(MAT_URL).status_code == 401
    assert client.get(f"{MAT_URL}/{vq.pk}").status_code == 401

    assert workshop_client.get(MAT_URL).status_code == 200
    assert workshop_client.get(f"{MAT_URL}/{vq.pk}").status_code == 200
    que_nl = GoodsType.objects.get(code="QUE_NL")
    r = post(workshop_client, MAT_URL, {"code": "NEW", "name": "Mới", "goods_type_id": que_nl.pk})
    assert r.status_code == 403
    assert body(r)["code"] == "FORBIDDEN"
    r = patch(workshop_client, f"{MAT_URL}/{vq.pk}", {"name": "Đổi"})
    assert r.status_code == 403
    r = patch(workshop_client, f"{MAT_URL}/{vq.pk}", {"grades": [{"rank": 4, "name": "Loại 4"}]})
    assert r.status_code == 403
    assert Material.objects.filter(code="NEW").count() == 0
    assert not AuditLog.objects.filter(entity__in=["material", "grade"]).exists()


def test_list_materials_with_grades(workshop_client: Client, db: None) -> None:
    rows = body(workshop_client.get(MAT_URL))
    assert [m["code"] for m in rows] == ["VQ", "QV"]
    assert all([g["rank"] for g in m["grades"]] == [1, 2, 3] for m in rows)
    assert rows[0]["grades"][0]["name"] == "Loại 1"
    assert rows[0]["grades"][0]["material_id"] == rows[0]["id"]

    detail = body(workshop_client.get(f"{MAT_URL}/{rows[1]['id']}"))
    assert detail["code"] == "QV"
    assert len(detail["grades"]) == 3
    assert workshop_client.get(f"{MAT_URL}/999999").status_code == 404


def test_create_material_with_grades_and_audit(owner_client: Client, owner: Any) -> None:
    que_nl = GoodsType.objects.get(code="QUE_NL")
    r = post(
        owner_client,
        MAT_URL,
        {
            "code": "QC",
            "name": "Quế cành",
            "goods_type_id": que_nl.pk,
            "image_url": "/media/img/3f/3fa9abc1-1440.webp",
            "sort_order": 3,
            "grades": [{"rank": 1, "name": "Loại 1"}, {"rank": 2, "name": "Loại 2"}],
        },
    )
    assert r.status_code == 201
    data = body(r)
    assert data["status"] == "ACTIVE"
    assert [(g["rank"], g["name"], g["status"]) for g in data["grades"]] == [
        (1, "Loại 1", "ACTIVE"),
        (2, "Loại 2", "ACTIVE"),
    ]
    assert AuditLog.objects.filter(
        entity="material", entity_id=data["id"], action="CREATE"
    ).exists()
    grade_logs = AuditLog.objects.filter(entity="grade", action="CREATE", user_id=owner.pk)
    assert grade_logs.count() == 2


def test_create_material_errors(owner_client: Client, db: None) -> None:
    que_nl = GoodsType.objects.get(code="QUE_NL")
    base = {"code": "QC", "name": "Quế cành", "goods_type_id": que_nl.pk}

    r = post(owner_client, MAT_URL, {**base, "code": "VQ"})
    assert r.status_code == 409
    assert body(r)["code"] == "MATERIAL_CODE_TAKEN"
    assert body(r)["message"] == "Mã nguyên liệu VQ đã có"

    product_type = GoodsType.objects.get(code="TINH_DAU")
    r = post(owner_client, MAT_URL, {**base, "goods_type_id": product_type.pk})
    assert r.status_code == 400
    assert body(r)["code"] == "GOODS_TYPE_INVALID"
    assert "không thuộc nhóm nguyên liệu" in body(r)["message"]

    r = post(owner_client, MAT_URL, {**base, "goods_type_id": 999999})
    assert r.status_code == 400
    assert body(r)["code"] == "GOODS_TYPE_INVALID"

    que_nl.status = "INACTIVE"
    que_nl.save()
    r = post(owner_client, MAT_URL, base)
    assert r.status_code == 400
    assert body(r)["code"] == "GOODS_TYPE_INVALID"
    assert body(r)["details"]["field"] == "goods_type_id"

    assert Material.objects.filter(code="QC").count() == 0
    assert not AuditLog.objects.filter(entity="material").exists()


def test_create_material_rejects_unsafe_image_url(owner_client: Client, db: None) -> None:
    que_nl = GoodsType.objects.get(code="QUE_NL")
    for bad in ("javascript:alert(1)", "data:text/html,x", "https://evil.example/x.png"):
        r = post(
            owner_client,
            MAT_URL,
            {"code": "QC", "name": "Quế cành", "goods_type_id": que_nl.pk, "image_url": bad},
        )
        assert r.status_code == 400, bad
        assert body(r)["code"] == "VALIDATION_ERROR"
    assert Material.objects.filter(code="QC").count() == 0


def test_create_material_grade_rules_roll_back_everything(owner_client: Client, db: None) -> None:
    que_nl = GoodsType.objects.get(code="QUE_NL")
    base = {"code": "QC", "name": "Quế cành", "goods_type_id": que_nl.pk}
    cases = [
        ([{"rank": 1, "name": "A"}, {"rank": 1, "name": "B"}], "GRADE_RANK_DUPLICATE"),
        ([{"rank": 0, "name": "A"}], "GRADE_RANK_INVALID"),
        ([{"rank": 10, "name": "A"}], "GRADE_RANK_INVALID"),
        ([{"rank": 1, "name": "   "}], "VALIDATION_ERROR"),
    ]
    for grades, code in cases:
        r = post(owner_client, MAT_URL, {**base, "grades": grades})
        assert r.status_code == 400, grades
        assert body(r)["code"] == code
    # Lỗi ở hạng thì nguyên liệu cũng không được tạo (cùng một giao dịch).
    assert Material.objects.filter(code="QC").count() == 0
    assert not AuditLog.objects.filter(entity__in=["material", "grade"]).exists()


def test_patch_material_fields_and_audit(owner_client: Client, owner: Any) -> None:
    vq = Material.objects.get(code="VQ")
    r = patch(
        owner_client,
        f"{MAT_URL}/{vq.pk}",
        {
            "name": "Vỏ quế loại tốt",
            "sort_order": 5,
            "image_url": "/media/img/aa/aabbccdd-480.webp",
        },
    )
    assert r.status_code == 200
    assert body(r)["name"] == "Vỏ quế loại tốt"
    assert body(r)["sort_order"] == 5
    log = AuditLog.objects.get(entity="material", entity_id=vq.pk)
    assert log.action == "UPDATE"
    assert log.before is not None and log.before["name"] == "Vỏ quế"
    assert log.after is not None and log.after["name"] == "Vỏ quế loại tốt"
    assert log.user_id == owner.pk

    r = patch(owner_client, f"{MAT_URL}/{vq.pk}", {"image_url": None})
    assert r.status_code == 200
    assert body(r)["image_url"] is None

    # Không đổi gì: không thêm dòng audit.
    count = AuditLog.objects.count()
    patch(owner_client, f"{MAT_URL}/{vq.pk}", {"name": "Vỏ quế loại tốt"})
    assert AuditLog.objects.count() == count


def test_patch_material_goods_type_must_be_material_group(owner_client: Client, db: None) -> None:
    vq = Material.objects.get(code="VQ")
    product_type = GoodsType.objects.get(code="TINH_DAU")
    r = patch(owner_client, f"{MAT_URL}/{vq.pk}", {"goods_type_id": product_type.pk})
    assert r.status_code == 400
    assert body(r)["code"] == "GOODS_TYPE_INVALID"
    vq.refresh_from_db()
    assert vq.goods_type.code == "QUE_NL"


def test_patch_material_null_for_required_is_400(owner_client: Client, db: None) -> None:
    vq = Material.objects.get(code="VQ")
    for field in ("name", "goods_type_id", "status", "grades"):
        r = patch(owner_client, f"{MAT_URL}/{vq.pk}", {field: None})
        assert r.status_code == 400, field
        assert body(r)["code"] == "VALIDATION_ERROR"
    assert patch(owner_client, f"{MAT_URL}/999999", {"name": "X"}).status_code == 404


def test_patch_adds_new_grade_and_renames_existing(owner_client: Client, owner: Any) -> None:
    vq = Material.objects.get(code="VQ")
    grade1 = Grade.objects.get(material=vq, rank=1)
    r = patch(
        owner_client,
        f"{MAT_URL}/{vq.pk}",
        {
            "grades": [
                {"id": grade1.pk, "rank": 1, "name": "Loại đặc biệt"},
                {"rank": 4, "name": "Loại 4"},
            ]
        },
    )
    assert r.status_code == 200
    grades = body(r)["grades"]
    assert [(g["rank"], g["name"]) for g in grades] == [
        (1, "Loại đặc biệt"),
        (2, "Loại 2"),
        (3, "Loại 3"),
        (4, "Loại 4"),
    ]
    update = AuditLog.objects.get(entity="grade", entity_id=grade1.pk, action="UPDATE")
    assert update.before is not None and update.before["name"] == "Loại 1"
    assert update.after is not None and update.after["name"] == "Loại đặc biệt"
    new_id = grades[3]["id"]
    assert AuditLog.objects.filter(entity="grade", entity_id=new_id, action="CREATE").exists()
    assert not AuditLog.objects.filter(entity="material").exists()  # nguyên liệu không đổi


def test_patch_grade_rules(owner_client: Client, db: None) -> None:
    vq = Material.objects.get(code="VQ")
    qv = Material.objects.get(code="QV")
    g1 = Grade.objects.get(material=vq, rank=1)
    other = Grade.objects.get(material=qv, rank=1)
    url = f"{MAT_URL}/{vq.pk}"

    r = patch(owner_client, url, {"grades": [{"rank": 2, "name": "Trùng bậc"}]})
    assert r.status_code == 409
    assert body(r)["code"] == "GRADE_RANK_TAKEN"
    assert body(r)["message"] == "Bậc 2 đã có hạng «Loại 2»"

    r = patch(owner_client, url, {"grades": [{"id": g1.pk, "rank": 5, "name": "Loại 1"}]})
    assert r.status_code == 409
    assert body(r)["code"] == "GRADE_RANK_LOCKED"

    r = patch(
        owner_client, url, {"grades": [{"id": other.pk, "rank": 1, "name": "Của người khác"}]}
    )
    assert r.status_code == 400
    assert body(r)["code"] == "GRADE_NOT_FOUND"

    r = patch(owner_client, url, {"grades": [{"rank": 11, "name": "Quá bậc"}]})
    assert r.status_code == 400
    assert body(r)["code"] == "GRADE_RANK_INVALID"
    assert body(r)["message"] == "Bậc của hạng phải từ 1 đến 9"

    r = patch(owner_client, url, {"grades": [{"id": g1.pk, "rank": 1, "name": "A"}] * 2})
    assert r.status_code == 400
    assert body(r)["code"] in {"GRADE_RANK_DUPLICATE", "GRADE_DUPLICATE"}

    assert Grade.objects.filter(material=vq).count() == 3
    assert not AuditLog.objects.filter(entity="grade").exists()


def test_grade_can_be_deactivated_without_lots(owner_client: Client, lot_hook: list[int]) -> None:
    vq = Material.objects.get(code="VQ")
    g3 = Grade.objects.get(material=vq, rank=3)
    r = patch(
        owner_client,
        f"{MAT_URL}/{vq.pk}",
        {"grades": [{"id": g3.pk, "rank": 3, "name": "Loại 3", "status": "INACTIVE"}]},
    )
    assert r.status_code == 200
    g3.refresh_from_db()
    assert g3.status == "INACTIVE"
    assert AuditLog.objects.filter(entity="grade", entity_id=g3.pk, action="UPDATE").exists()
    # Hạng ngừng dùng vẫn nằm trong danh sách (để xem lại), có status.
    assert [g["status"] for g in body(r)["grades"]] == ["ACTIVE", "ACTIVE", "INACTIVE"]


def test_grade_with_lots_cannot_be_deactivated(owner_client: Client, lot_hook: list[int]) -> None:
    vq = Material.objects.get(code="VQ")
    g2 = Grade.objects.get(material=vq, rank=2)
    lot_hook.append(g2.pk)

    r = patch(
        owner_client,
        f"{MAT_URL}/{vq.pk}",
        {"grades": [{"id": g2.pk, "rank": 2, "name": "Loại 2", "status": "INACTIVE"}]},
    )
    assert r.status_code == 409
    assert body(r)["code"] == "GRADE_HAS_LOTS"
    assert body(r)["message"] == "Hạng «Loại 2» đang có lô trong kho, không ngừng dùng được"
    g2.refresh_from_db()
    assert g2.status == "ACTIVE"
    assert not AuditLog.objects.filter(entity="grade").exists()

    # Đổi tên hạng đang có lô vẫn được; chỉ việc ngừng dùng bị chặn.
    r = patch(
        owner_client,
        f"{MAT_URL}/{vq.pk}",
        {"grades": [{"id": g2.pk, "rank": 2, "name": "Loại hai"}]},
    )
    assert r.status_code == 200
    # Hết lô thì ngừng dùng được.
    lot_hook.clear()
    r = patch(
        owner_client,
        f"{MAT_URL}/{vq.pk}",
        {"grades": [{"id": g2.pk, "rank": 2, "name": "Loại hai", "status": "INACTIVE"}]},
    )
    assert r.status_code == 200


def test_material_with_lots_cannot_be_deactivated(
    owner_client: Client, lot_hook: list[int]
) -> None:
    vq = Material.objects.get(code="VQ")
    lot_hook.append(Grade.objects.get(material=vq, rank=1).pk)

    r = patch(owner_client, f"{MAT_URL}/{vq.pk}", {"status": "INACTIVE"})
    assert r.status_code == 409
    assert body(r)["code"] == "MATERIAL_HAS_LOTS"
    assert "đang có lô trong kho, không ngừng dùng nguyên liệu được" in body(r)["message"]
    vq.refresh_from_db()
    assert vq.status == "ACTIVE"
    assert not AuditLog.objects.filter(entity="material").exists()

    # Nguyên liệu khác (không có lô) ngừng dùng được: PATCH {status: INACTIVE}.
    qv = Material.objects.get(code="QV")
    r = patch(owner_client, f"{MAT_URL}/{qv.pk}", {"status": "INACTIVE"})
    assert r.status_code == 200
    assert body(r)["status"] == "INACTIVE"
    assert AuditLog.objects.filter(entity="material", entity_id=qv.pk, action="UPDATE").exists()
    # Vẫn không xoá: danh sách còn thấy, lọc theo status được.
    assert [m["code"] for m in body(owner_client.get(f"{MAT_URL}?status=ACTIVE"))] == ["VQ"]
    assert len(body(owner_client.get(MAT_URL))) == 2


def test_deactivating_material_and_its_state_rolls_back_on_failed_grades(
    owner_client: Client, lot_hook: list[int]
) -> None:
    """Một request lỗi ở phần hạng thì phần sửa nguyên liệu cùng request cũng không được giữ."""
    vq = Material.objects.get(code="VQ")
    r = patch(
        owner_client,
        f"{MAT_URL}/{vq.pk}",
        {"name": "Tên mới", "grades": [{"rank": 1, "name": "Trùng bậc 1"}]},
    )
    assert r.status_code == 409
    vq.refresh_from_db()
    assert vq.name == "Vỏ quế"
    assert not AuditLog.objects.filter(entity__in=["material", "grade"]).exists()


def test_register_grade_in_use_check_hook(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(materials_service, "_grade_in_use_checks", [])
    assert materials_service.grade_has_lots(1) is False  # chưa ai đăng ký: không chặn

    def only_seven(grade_id: int) -> bool:
        return grade_id == 7

    materials_service.register_grade_in_use_check(only_seven)
    materials_service.register_grade_in_use_check(only_seven)  # đăng ký lặp bị bỏ qua
    assert materials_service.grade_has_lots(7) is True
    assert materials_service.grade_has_lots(8) is False
    assert len(materials_service._grade_in_use_checks) == 1
