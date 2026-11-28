"""API công thức: phiên bản, kích hoạt, scale, khoá bản đã dùng, vòng lặp bán thành phẩm (BR-26)."""

from __future__ import annotations

import json
from typing import Any

import pytest
from django.test import Client

from catalog.models import Ingredient, Recipe, RecipeItem
from catalog.services import recipes as recipes_service
from core.models import AuditLog

pytestmark = pytest.mark.django_db

URL = "/api/v1/recipes"


def post(client: Client, payload: dict[str, Any] | None = None, url: str = URL) -> Any:
    return client.post(url, payload or {}, content_type="application/json")


def patch(client: Client, recipe_id: int, payload: dict[str, Any]) -> Any:
    return client.patch(f"{URL}/{recipe_id}", payload, content_type="application/json")


def put_items(client: Client, recipe_id: int, items: list[dict[str, Any]]) -> Any:
    return client.put(f"{URL}/{recipe_id}/items", {"items": items}, content_type="application/json")


def action(client: Client, recipe_id: int, name: str) -> Any:
    return client.post(f"{URL}/{recipe_id}/{name}", {}, content_type="application/json")


def body(response: Any) -> Any:
    return json.loads(response.content)


def ing(code: str, **overrides: Any) -> Ingredient:
    """Lấy phụ liệu seed theo mã, hoặc tạo mới nếu chưa có."""
    fields: dict[str, Any] = {"name": f"PL {code}", "kind": "OTHER"}
    fields.update(overrides)
    obj, _ = Ingredient.objects.get_or_create(code=code, defaults=fields)
    return obj


def line(code: str, qty: str, **extra: Any) -> dict[str, Any]:
    return {"ingredient_id": ing(code).pk, "qty_g": qty, **extra}


def rid(code: str, version: int = 1) -> int:
    return Recipe.objects.get(code=code, version=version).pk


def new_recipe(client: Client, code: str = "ZR1", **overrides: Any) -> Any:
    data: dict[str, Any] = {
        "code": code,
        "name": f"CT {code}",
        "output_kind": "PRODUCT",
        "items": [line("TTV", "30.00"), line("Q", "10.00")],
    }
    data.update(overrides)
    return post(client, data)


def inter(client: Client, code: str, out: str, uses: list[str], **extra: Any) -> Any:
    """Tạo công thức bán thành phẩm `code` làm ra phụ liệu `out` từ các phụ liệu `uses`."""
    return new_recipe(
        client,
        code,
        output_kind="INTERMEDIATE",
        output_ingredient_id=ing(out).pk,
        items=[line(u, "10.00") for u in uses],
        **extra,
    )


@pytest.fixture
def order_hooks(monkeypatch: pytest.MonkeyPatch) -> dict[str, set[int]]:
    """Giả lập hook đợt 2: id công thức đã có lệnh (`used`), còn lệnh DRAFT/CURING (`open`)."""
    state: dict[str, set[int]] = {"used": set(), "open": set()}
    monkeypatch.setattr(recipes_service, "_used_checks", [lambda r: r in state["used"]])
    monkeypatch.setattr(recipes_service, "_open_order_checks", [lambda r: r in state["open"]])
    return state


# ------------------------------------------------------------------ phân quyền


def test_anonymous_gets_401(client: Client) -> None:
    assert client.get(URL).status_code == 401
    assert post(client, {}).status_code == 401


def test_workshop_reads_but_cannot_write(workshop_client: Client) -> None:
    qc1 = rid("QC1")
    assert workshop_client.get(URL).status_code == 200
    assert workshop_client.get(f"{URL}/{qc1}").status_code == 200
    assert workshop_client.get(f"{URL}/{qc1}/scale", {"batch_g": "100"}).status_code == 200
    assert new_recipe(workshop_client).status_code == 403
    assert patch(workshop_client, qc1, {"name": "X"}).status_code == 403
    assert put_items(workshop_client, qc1, []).status_code == 403
    for name in ("new-version", "activate", "retire"):
        assert action(workshop_client, qc1, name).status_code == 403
    assert Recipe.objects.filter(code="QC1").count() == 1
    assert not AuditLog.objects.filter(entity="recipe").exists()


# ------------------------------------------------------------------ đọc


def test_list_and_filters(owner_client: Client) -> None:
    assert len(body(owner_client.get(URL))) == 15
    assert [r["code"] for r in body(owner_client.get(URL, {"code": "QC1"}))] == ["QC1"]
    inters = body(owner_client.get(URL, {"output_kind": "INTERMEDIATE", "status": "ACTIVE"}))
    assert {r["code"] for r in inters} == {"TT1", "TT2", "DDT", "U-Q", "SC-VQH"}
    assert body(owner_client.get(URL, {"status": "DRAFT"})) == []
    assert owner_client.get(URL, {"status": "NOPE"}).status_code == 400
    assert owner_client.get(URL, {"output_kind": "NOPE"}).status_code == 400


def test_detail_has_items_with_pct(owner_client: Client) -> None:
    data = body(owner_client.get(f"{URL}/{rid('QC1')}"))
    assert (data["code"], data["version"], data["status"]) == ("QC1", 1, "ACTIVE")
    assert data["base_batch_g"] == "89.72"
    by_code = {i["ingredient_code"]: i for i in data["items"]}
    assert [i["line_no"] for i in data["items"]] == [1, 2, 3]
    assert (by_code["TTV"]["qty_g"], by_code["TTV"]["pct"]) == ("31.40", "35.00")
    assert by_code["CAM"]["pct"] == "55.00"
    assert data["editable"] is False  # đã ACTIVE
    assert owner_client.get(f"{URL}/99999999").status_code == 404


def test_detail_of_intermediate_has_output_ingredient(owner_client: Client) -> None:
    data = body(owner_client.get(f"{URL}/{rid('DDT')}"))
    assert data["output_kind"] == "INTERMEDIATE"
    assert data["output_ingredient_code"] == "DDT"
    groups = {i["ingredient_code"]: i["alt_group"] for i in data["items"]}
    assert groups == {"DPG": None, "TT1": 1, "TT2": 1}


# ------------------------------------------------------------------ scale


def test_scale_matches_ac25(owner_client: Client) -> None:
    r = owner_client.get(f"{URL}/{rid('QC1')}/scale", {"batch_g": "897.2"})
    assert r.status_code == 200
    data = body(r)
    assert (data["code"], data["base_batch_g"], data["batch_g"]) == ("QC1", "89.72", "897.20")
    suggested = {i["ingredient_code"]: i["suggested_g"] for i in data["items"]}
    assert suggested == {"TTV": "314.00", "Q": "89.70", "CAM": "493.50"}


def test_scale_rounds_half_up_to_2_digits(owner_client: Client) -> None:
    data = body(owner_client.get(f"{URL}/{rid('QC1')}/scale", {"batch_g": "100"}))
    suggested = {i["ingredient_code"]: i["suggested_g"] for i in data["items"]}
    assert suggested["TTV"] == "35.00"
    assert suggested["Q"] == "10.00"  # 8,97 * 100 / 89,72 = 9,9977
    assert suggested["CAM"] == "55.00"


@pytest.mark.parametrize("batch", ["0", "-5", "abc", ""])
def test_scale_rejects_bad_batch(owner_client: Client, batch: str) -> None:
    assert owner_client.get(f"{URL}/{rid('QC1')}/scale", {"batch_g": batch}).status_code == 400


def test_scale_requires_batch_and_known_recipe(owner_client: Client) -> None:
    assert owner_client.get(f"{URL}/{rid('QC1')}/scale").status_code == 400
    assert owner_client.get(f"{URL}/99999999/scale", {"batch_g": "10"}).status_code == 404


def test_scale_of_empty_recipe_has_no_lines(owner_client: Client) -> None:
    data = body(owner_client.get(f"{URL}/{rid('SC-VQH')}/scale", {"batch_g": "500"}))
    assert data["items"] == []


# ------------------------------------------------------------------ tạo


def test_create_draft_computes_batch_and_audits(owner_client: Client, owner: Any) -> None:
    r = new_recipe(
        owner_client,
        cure_min_days=14,
        cure_max_days=21,
        retain_months=12,
        base_label="mẻ thử",
    )
    assert r.status_code == 201, r.content
    data = body(r)
    assert (data["version"], data["status"], data["base_batch_g"]) == (1, "DRAFT", "40.00")
    assert [i["qty_g"] for i in data["items"]] == ["30.00", "10.00"]
    assert [i["pct"] for i in data["items"]] == ["75.00", "25.00"]
    assert data["editable"] is True
    recipe = Recipe.objects.get(pk=data["id"])
    log = AuditLog.objects.get(entity="recipe", entity_id=recipe.pk)
    assert (log.action, log.user_id) == ("CREATE", owner.pk)
    assert AuditLog.objects.filter(entity="recipe_item", action="CREATE").count() == 2


def test_create_counts_one_alternative_per_group(owner_client: Client) -> None:
    items = [
        line("DPG", "65.00"),
        line("TT1", "35.00", alt_group=1),
        line("TT2", "35.00", alt_group=1),
    ]
    data = body(new_recipe(owner_client, "ZR2", items=items))
    assert data["base_batch_g"] == "100.00"
    assert [i["pct"] for i in data["items"]] == ["65.00", "35.00", "35.00"]


def test_create_without_items_uses_nominal_batch(owner_client: Client) -> None:
    data = body(new_recipe(owner_client, "ZR3", items=[]))
    assert (data["base_batch_g"], data["items"]) == ("100.00", [])
    data = body(new_recipe(owner_client, "ZR4", items=[], base_batch_g="250"))
    assert data["base_batch_g"] == "250.00"


def test_create_duplicate_code_is_409(owner_client: Client) -> None:
    r = new_recipe(owner_client, "QC1")
    assert (r.status_code, body(r)["code"]) == (409, "RECIPE_CODE_TAKEN")


@pytest.mark.parametrize("code", ["qc1", "", "A B", "-A", "A" * 41, "Ư1"])
def test_create_code_format_is_400(owner_client: Client, code: str) -> None:
    assert new_recipe(owner_client, code).status_code == 400


def test_create_output_rules(owner_client: Client) -> None:
    r = new_recipe(owner_client, "ZR5", output_kind="INTERMEDIATE")
    assert (r.status_code, body(r)["code"]) == (400, "RECIPE_OUTPUT_REQUIRED")
    r = new_recipe(owner_client, "ZR5", output_ingredient_id=ing("TTV").pk)
    assert (r.status_code, body(r)["code"]) == (400, "RECIPE_OUTPUT_FORBIDDEN")
    r = new_recipe(owner_client, "ZR5", output_kind="INTERMEDIATE", output_ingredient_id=99999999)
    assert (r.status_code, body(r)["code"]) == (400, "INGREDIENT_INVALID")
    assert not Recipe.objects.filter(code="ZR5").exists()


def test_create_rejects_bad_cure_range(owner_client: Client) -> None:
    r = new_recipe(owner_client, "ZR6", cure_min_days=10, cure_max_days=5)
    assert (r.status_code, body(r)["code"]) == (400, "CURE_RANGE_INVALID")


@pytest.mark.parametrize("qty", ["0", "-1", "0.001", "abc", "123456789012"])
def test_item_gram_must_be_positive(owner_client: Client, qty: str) -> None:
    r = new_recipe(owner_client, "ZR7", items=[line("TTV", qty)])
    assert r.status_code == 400
    assert not Recipe.objects.filter(code="ZR7").exists()


def test_item_rules(owner_client: Client) -> None:
    dup = [line("TTV", "1"), line("TTV", "2")]
    r = new_recipe(owner_client, "ZR8", items=dup)
    assert (r.status_code, body(r)["code"]) == (400, "RECIPE_ITEM_DUPLICATE")
    r = new_recipe(owner_client, "ZR8", items=[line("TTV", "1", alt_group=1), line("Q", "1")])
    assert (r.status_code, body(r)["code"]) == (400, "ALT_GROUP_SINGLE")
    r = new_recipe(owner_client, "ZR8", items=[{"ingredient_id": 99999999, "qty_g": "1"}])
    assert (r.status_code, body(r)["code"]) == (400, "INGREDIENT_INVALID")
    Ingredient.objects.filter(code="TTV").update(status="INACTIVE")
    r = new_recipe(owner_client, "ZR8", items=[line("TTV", "1")])
    assert (r.status_code, body(r)["code"]) == (400, "INGREDIENT_INVALID")
    assert not Recipe.objects.filter(code="ZR8").exists()


def test_create_rejects_too_many_items(owner_client: Client) -> None:
    items = [line("TTV", "1")] * 51
    assert new_recipe(owner_client, "ZR9", items=items).status_code == 400


# ------------------------------------------------------------------ PATCH và PUT items


def test_patch_draft_header(owner_client: Client) -> None:
    pid = body(new_recipe(owner_client))["id"]
    r = patch(owner_client, pid, {"name": "Tên mới", "cure_min_days": 7, "note": "bước 1"})
    assert r.status_code == 200, r.content
    assert (body(r)["name"], body(r)["cure_min_days"], body(r)["note"]) == ("Tên mới", 7, "bước 1")
    log = AuditLog.objects.filter(entity="recipe", entity_id=pid, action="UPDATE").get()
    assert log.before is not None and log.before["name"] == "CT ZR1"
    # không đổi gì thì không ghi thêm
    assert patch(owner_client, pid, {"name": "Tên mới"}).status_code == 200
    assert AuditLog.objects.filter(entity="recipe", entity_id=pid, action="UPDATE").count() == 1


def test_patch_validation(owner_client: Client) -> None:
    pid = body(new_recipe(owner_client))["id"]
    assert patch(owner_client, pid, {"cure_min_days": 9, "cure_max_days": 3}).status_code == 400
    for name in ("name", "output_kind", "cure_min_days"):
        assert patch(owner_client, pid, {name: None}).status_code == 400
    assert patch(owner_client, pid, {"code": "OTHER"}).status_code == 200  # trường lạ bị bỏ qua
    assert Recipe.objects.get(pk=pid).code == "ZR1"


def test_patch_output_on_single_version_draft(owner_client: Client) -> None:
    pid = body(new_recipe(owner_client))["id"]
    r = patch(owner_client, pid, {"output_kind": "INTERMEDIATE"})
    assert (r.status_code, body(r)["code"]) == (400, "RECIPE_OUTPUT_REQUIRED")
    r = patch(
        owner_client,
        pid,
        {"output_kind": "INTERMEDIATE", "output_ingredient_id": ing("ZOUT").pk},
    )
    assert r.status_code == 200, r.content
    assert body(r)["output_ingredient_code"] == "ZOUT"
    r = patch(owner_client, pid, {"output_kind": "PRODUCT"})
    assert r.status_code == 200
    assert body(r)["output_ingredient_id"] is None


def test_patch_output_locked_when_code_has_several_versions(owner_client: Client) -> None:
    old = body(inter(owner_client, "ZI1", "ZOUT1", ["TTV"]))["id"]
    assert action(owner_client, old, "activate").status_code == 200
    v2 = body(action(owner_client, old, "new-version"))["id"]
    r = patch(owner_client, v2, {"output_ingredient_id": ing("ZOUT2").pk})
    assert (r.status_code, body(r)["code"]) == (409, "RECIPE_OUTPUT_LOCKED")


def test_put_items_replaces_and_recomputes(owner_client: Client) -> None:
    pid = body(new_recipe(owner_client))["id"]  # TTV 30 + Q 10
    r = put_items(owner_client, pid, [line("TTV", "30.00"), line("CAM", "60.00")])
    assert r.status_code == 200, r.content
    data = body(r)
    assert data["base_batch_g"] == "90.00"
    assert [(i["line_no"], i["ingredient_code"]) for i in data["items"]] == [(1, "TTV"), (2, "CAM")]
    assert RecipeItem.objects.filter(recipe_id=pid).count() == 2
    # đổi Q → CAM ở dòng 2 là UPDATE dòng; bớt dòng 3 nếu có sẽ là DELETE_LINE
    r = put_items(owner_client, pid, [line("TTV", "30.00")])
    assert body(r)["base_batch_g"] == "30.00"
    assert AuditLog.objects.filter(entity="recipe_item", action="DELETE_LINE").count() == 1
    assert RecipeItem.objects.filter(recipe_id=pid).count() == 1


def test_put_same_items_writes_no_audit(owner_client: Client) -> None:
    pid = body(new_recipe(owner_client))["id"]
    before = AuditLog.objects.count()
    r = put_items(owner_client, pid, [line("TTV", "30.00"), line("Q", "10.00")])
    assert r.status_code == 200
    assert AuditLog.objects.count() == before


def test_put_empty_keeps_current_batch(owner_client: Client) -> None:
    pid = body(new_recipe(owner_client))["id"]
    data = body(put_items(owner_client, pid, []))
    assert (data["items"], data["base_batch_g"]) == ([], "40.00")


def test_put_item_validation_leaves_old_items(owner_client: Client) -> None:
    pid = body(new_recipe(owner_client))["id"]
    assert put_items(owner_client, pid, [line("TTV", "0")]).status_code == 400
    r = put_items(owner_client, pid, [line("TTV", "1"), line("TTV", "2")])
    assert (r.status_code, body(r)["code"]) == (400, "RECIPE_ITEM_DUPLICATE")
    assert [str(i.qty_g) for i in RecipeItem.objects.filter(recipe_id=pid).order_by("line_no")] == [
        "30.00",
        "10.00",
    ]


# ------------------------------------------------------------------ BR-26: khoá bản đã dùng


def test_active_recipe_cannot_be_edited_directly(owner_client: Client) -> None:
    qc1 = rid("QC1")
    r = patch(owner_client, qc1, {"name": "Đổi"})
    assert (r.status_code, body(r)["code"]) == (409, "RECIPE_NOT_DRAFT")
    assert body(r)["details"]["rule"] == "BR-26"
    r = put_items(owner_client, qc1, [line("TTV", "50")])
    assert (r.status_code, body(r)["code"]) == (409, "RECIPE_NOT_DRAFT")
    assert Recipe.objects.get(pk=qc1).name == "Quế Cam, dầu nhẹ"
    assert str(RecipeItem.objects.get(recipe_id=qc1, line_no=1).qty_g) == "31.40"


def test_recipe_with_orders_is_immutable(
    owner_client: Client, order_hooks: dict[str, set[int]]
) -> None:
    pid = body(new_recipe(owner_client))["id"]
    order_hooks["used"].add(pid)
    r = patch(owner_client, pid, {"name": "Đổi"})
    assert (r.status_code, body(r)["code"]) == (409, "RECIPE_IN_USE")
    r = put_items(owner_client, pid, [line("TTV", "50")])
    assert (r.status_code, body(r)["code"]) == (409, "RECIPE_IN_USE")
    assert body(owner_client.get(f"{URL}/{pid}"))["editable"] is False


# ------------------------------------------------------------------ phiên bản, kích hoạt


def test_new_version_copies_into_draft(owner_client: Client, owner: Any) -> None:
    qc1 = rid("QC1")
    r = action(owner_client, qc1, "new-version")
    assert r.status_code == 201, r.content
    data = body(r)
    assert (data["code"], data["version"], data["status"]) == ("QC1", 2, "DRAFT")
    assert data["editable"] is True
    assert [(i["ingredient_code"], i["qty_g"]) for i in data["items"]] == [
        ("TTV", "31.40"),
        ("Q", "8.97"),
        ("CAM", "49.35"),
    ]
    assert data["base_batch_g"] == "89.72"
    assert Recipe.objects.get(pk=qc1).status == "ACTIVE"  # bản cũ giữ nguyên
    log = AuditLog.objects.get(entity="recipe", entity_id=data["id"])
    assert (log.action, log.reason) == ("CREATE", "Sao chép từ v1")


def test_second_new_version_is_409_while_draft_exists(owner_client: Client) -> None:
    qc1 = rid("QC1")
    assert action(owner_client, qc1, "new-version").status_code == 201
    r = action(owner_client, qc1, "new-version")
    assert (r.status_code, body(r)["code"]) == (409, "RECIPE_DRAFT_EXISTS")
    assert Recipe.objects.filter(code="QC1").count() == 2


def test_ac37_new_version_edit_activate_retires_old(
    owner_client: Client, order_hooks: dict[str, set[int]]
) -> None:
    qc1 = rid("QC1")
    order_hooks["used"].add(qc1)
    # (a) sửa gram dòng của v1 đã có lệnh: 409, v1 giữ nguyên
    r = put_items(owner_client, qc1, [line("TTV", "50")])
    assert (r.status_code, body(r)["code"]) == (409, "RECIPE_IN_USE")
    # (b) tạo v2, sửa, kích hoạt
    v2 = body(action(owner_client, qc1, "new-version"))["id"]
    r = put_items(
        owner_client, v2, [line("TTV", "30.00"), line("Q", "10.00"), line("CAM", "50.00")]
    )
    assert body(r)["base_batch_g"] == "90.00"
    r = action(owner_client, v2, "activate")
    assert r.status_code == 200, r.content
    assert body(r)["status"] == "ACTIVE"
    statuses = dict(Recipe.objects.filter(code="QC1").values_list("version", "status"))
    assert statuses == {1: "RETIRED", 2: "ACTIVE"}
    assert str(RecipeItem.objects.get(recipe_id=qc1, line_no=1).qty_g) == "31.40"
    old_log = AuditLog.objects.filter(entity="recipe", entity_id=qc1, action="UPDATE").get()
    assert old_log.reason == "Thay bằng v2"


def test_activate_requires_draft(owner_client: Client) -> None:
    r = action(owner_client, rid("QC1"), "activate")
    assert (r.status_code, body(r)["code"]) == (409, "RECIPE_NOT_DRAFT")


def test_activate_needs_items_except_sc_vqh(owner_client: Client) -> None:
    pid = body(new_recipe(owner_client, "ZR1", items=[]))["id"]
    r = action(owner_client, pid, "activate")
    assert (r.status_code, body(r)["code"]) == (409, "RECIPE_EMPTY")
    assert Recipe.objects.get(pk=pid).status == "DRAFT"

    sc = rid("SC-VQH")
    v2 = body(action(owner_client, sc, "new-version"))["id"]
    r = action(owner_client, v2, "activate")
    assert r.status_code == 200, r.content
    assert dict(Recipe.objects.filter(code="SC-VQH").values_list("version", "status")) == {
        1: "RETIRED",
        2: "ACTIVE",
    }


def test_activate_rejects_inactive_ingredient(owner_client: Client) -> None:
    pid = body(new_recipe(owner_client))["id"]
    Ingredient.objects.filter(code="Q").update(status="INACTIVE")
    r = action(owner_client, pid, "activate")
    assert (r.status_code, body(r)["code"]) == (409, "INGREDIENT_INVALID")
    assert Recipe.objects.get(pk=pid).status == "DRAFT"


def test_only_one_active_per_code(owner_client: Client) -> None:
    pid = body(new_recipe(owner_client))["id"]
    assert action(owner_client, pid, "activate").status_code == 200
    v2 = body(action(owner_client, pid, "new-version"))["id"]
    assert action(owner_client, v2, "activate").status_code == 200
    v3 = body(action(owner_client, v2, "new-version"))["id"]
    assert action(owner_client, v3, "activate").status_code == 200
    assert Recipe.objects.filter(code="ZR1", status="ACTIVE").count() == 1
    assert dict(Recipe.objects.filter(code="ZR1").values_list("version", "status")) == {
        1: "RETIRED",
        2: "RETIRED",
        3: "ACTIVE",
    }


def test_retire(owner_client: Client, order_hooks: dict[str, set[int]]) -> None:
    qc1 = rid("QC1")
    order_hooks["open"].add(qc1)
    r = action(owner_client, qc1, "retire")
    assert (r.status_code, body(r)["code"]) == (409, "RECIPE_HAS_OPEN_ORDERS")
    assert body(r)["details"]["rule"] == "BR-21"
    order_hooks["open"].clear()
    r = action(owner_client, qc1, "retire")
    assert (r.status_code, body(r)["code"] if r.status_code != 200 else "") == (200, "")
    assert body(r)["status"] == "RETIRED"
    r = action(owner_client, qc1, "retire")
    assert (r.status_code, body(r)["code"]) == (409, "RECIPE_NOT_ACTIVE")
    # bản RETIRED vẫn sao chép được ra bản nháp mới
    assert action(owner_client, qc1, "new-version").status_code == 201


def test_unknown_recipe_is_404_for_actions(owner_client: Client) -> None:
    for name in ("new-version", "activate", "retire"):
        assert action(owner_client, 99999999, name).status_code == 404
    assert patch(owner_client, 99999999, {"name": "X"}).status_code == 404
    assert put_items(owner_client, 99999999, []).status_code == 404


# ------------------------------------------------------------------ BR-26d: vòng lặp bán thành phẩm


def test_direct_self_reference_is_rejected(owner_client: Client) -> None:
    tt1 = rid("TT1")
    v2 = body(action(owner_client, tt1, "new-version"))["id"]
    r = put_items(owner_client, v2, [line("HH", "10"), line("TT1", "5")])
    assert (r.status_code, body(r)["code"]) == (409, "RECIPE_CYCLE")
    assert body(r)["details"]["rule"] == "BR-26"
    assert body(r)["details"]["path"] == ["TT1", "TT1"]
    assert RecipeItem.objects.filter(recipe_id=v2).count() == 4  # dòng sao chép còn nguyên


def test_two_tier_cycle_via_seed_ddt(owner_client: Client) -> None:
    """DDT dùng TT1 (seed); bản mới của TT1 mà dùng lại DDT thì TT1 → DDT → TT1."""
    v2 = body(action(owner_client, rid("TT1"), "new-version"))["id"]
    r = put_items(owner_client, v2, [line("HH", "10"), line("DDT", "5")])
    assert (r.status_code, body(r)["code"]) == (409, "RECIPE_CYCLE")
    assert body(r)["details"]["path"] == ["TT1", "DDT", "TT1"]


def test_three_tier_cycle_is_rejected_at_create(owner_client: Client) -> None:
    assert inter(owner_client, "RX", "ZX", ["ZY"]).status_code == 201
    assert inter(owner_client, "RY", "ZY", ["ZZ"]).status_code == 201
    r = inter(owner_client, "RZ", "ZZ", ["ZX", "TTV"])
    assert (r.status_code, body(r)["code"]) == (409, "RECIPE_CYCLE")
    assert body(r)["details"]["path"] == ["ZZ", "ZX", "ZY", "ZZ"]
    assert not Recipe.objects.filter(code="RZ").exists()


def test_three_tier_cycle_is_rejected_at_put_items(owner_client: Client) -> None:
    assert inter(owner_client, "RX", "ZX", ["ZY"]).status_code == 201
    assert inter(owner_client, "RY", "ZY", ["ZZ"]).status_code == 201
    rz = body(inter(owner_client, "RZ", "ZZ", ["TTV"]))["id"]
    r = put_items(owner_client, rz, [line("TTV", "5"), line("ZX", "5")])
    assert (r.status_code, body(r)["code"]) == (409, "RECIPE_CYCLE")
    assert [i.ingredient.code for i in RecipeItem.objects.filter(recipe_id=rz)] == ["TTV"]
    # bỏ dòng ZX thì lưu được; không vòng nào
    assert put_items(owner_client, rz, [line("TTV", "5"), line("Q", "5")]).status_code == 200


def test_three_tier_cycle_is_rejected_when_changing_output(owner_client: Client) -> None:
    assert inter(owner_client, "RX", "ZX", ["ZY"]).status_code == 201
    assert inter(owner_client, "RY", "ZY", ["ZZ"]).status_code == 201
    rz = body(new_recipe(owner_client, "RZ", items=[line("ZX", "5")]))["id"]  # thành phẩm
    r = patch(
        owner_client, rz, {"output_kind": "INTERMEDIATE", "output_ingredient_id": ing("ZZ").pk}
    )
    assert (r.status_code, body(r)["code"]) == (409, "RECIPE_CYCLE")
    assert Recipe.objects.get(pk=rz).output_kind == "PRODUCT"


def test_diamond_without_cycle_is_allowed(owner_client: Client) -> None:
    assert inter(owner_client, "RB", "ZB", ["ZD"]).status_code == 201
    assert inter(owner_client, "RC", "ZC", ["ZD"]).status_code == 201
    assert inter(owner_client, "RD", "ZD", ["TTV"]).status_code == 201
    assert inter(owner_client, "RA", "ZA", ["ZB", "ZC"]).status_code == 201


def test_retired_recipes_do_not_count_for_cycles(owner_client: Client) -> None:
    rx = body(inter(owner_client, "RX", "ZX", ["ZY"]))["id"]
    assert inter(owner_client, "RY", "ZY", ["TTV"]).status_code == 201
    Recipe.objects.filter(pk=rx).update(status="RETIRED")
    # RX đã RETIRED nên RY được phép dùng ZX
    ry = rid("RY")
    assert action(owner_client, ry, "activate").status_code == 200
    v2 = body(action(owner_client, ry, "new-version"))["id"]
    assert put_items(owner_client, v2, [line("ZX", "5")]).status_code == 200


def test_activate_rechecks_cycle(owner_client: Client) -> None:
    assert inter(owner_client, "RX", "ZX", ["ZY"]).status_code == 201
    ry = body(inter(owner_client, "RY", "ZY", ["TTV"]))["id"]
    # Dựng thẳng bằng ORM một bản nháp vòng (bỏ qua service) rồi kích hoạt: bị chặn lúc kích hoạt.
    RecipeItem.objects.filter(recipe_id=ry).update(ingredient=ing("ZX"))
    r = action(owner_client, ry, "activate")
    assert (r.status_code, body(r)["code"]) == (409, "RECIPE_CYCLE")
    assert Recipe.objects.get(pk=ry).status == "DRAFT"
