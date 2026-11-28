"""API phụ liệu: phân quyền, mã chữ hoa, khoá khi đã có lô (hook), BR-21, audit_log."""

from __future__ import annotations

import json
from typing import Any

import pytest
from django.test import Client

from catalog.models import Ingredient, Recipe, RecipeStatus
from catalog.services import ingredients as ingredients_service
from core.models import AuditLog

pytestmark = pytest.mark.django_db

URL = "/api/v1/ingredients"


def post(client: Client, payload: dict[str, Any]) -> Any:
    return client.post(URL, payload, content_type="application/json")


def patch(client: Client, ingredient_id: int, payload: dict[str, Any]) -> Any:
    return client.patch(f"{URL}/{ingredient_id}", payload, content_type="application/json")


def body(response: Any) -> Any:
    return json.loads(response.content)


def payload(**overrides: Any) -> dict[str, Any]:
    data: dict[str, Any] = {"code": "ZA1", "name": "Phụ liệu thử", "kind": "OTHER"}
    data.update(overrides)
    return data


def make(code: str = "ZA1", **overrides: Any) -> Ingredient:
    fields: dict[str, Any] = {"code": code, "name": f"PL {code}", "kind": "OTHER"}
    fields.update(overrides)
    return Ingredient.objects.create(**fields)


@pytest.fixture
def lot_hooks(monkeypatch: pytest.MonkeyPatch) -> dict[str, set[int]]:
    """Giả lập hook của đợt 2: id phụ liệu đã có lô (`any`) và còn lô IN_STOCK (`stock`)."""
    state: dict[str, set[int]] = {"any": set(), "stock": set()}
    monkeypatch.setattr(ingredients_service, "_lot_checks", [lambda i: i in state["any"]])
    monkeypatch.setattr(ingredients_service, "_stock_checks", [lambda i: i in state["stock"]])
    return state


# ------------------------------------------------------------------ phân quyền


def test_anonymous_gets_401(client: Client) -> None:
    assert client.get(URL).status_code == 401
    assert post(client, payload()).status_code == 401


def test_workshop_reads_but_cannot_write(workshop_client: Client) -> None:
    ing = make()
    assert workshop_client.get(URL).status_code == 200
    assert workshop_client.get(f"{URL}/{ing.pk}").status_code == 200
    assert post(workshop_client, payload(code="ZA2")).status_code == 403
    assert patch(workshop_client, ing.pk, {"name": "Đổi"}).status_code == 403
    ing.refresh_from_db()
    assert ing.name == "PL ZA1"
    assert not AuditLog.objects.filter(entity="ingredient").exists()


# ------------------------------------------------------------------ đọc


def test_list_has_seed_and_filters(owner_client: Client) -> None:
    rows = body(owner_client.get(URL))
    assert len(rows) == 19
    oils = body(owner_client.get(URL, {"kind": "ESSENTIAL_OIL"}))
    assert oils and {r["kind"] for r in oils} == {"ESSENTIAL_OIL"}
    make("ZA1", status="INACTIVE")
    assert [r["code"] for r in body(owner_client.get(URL, {"status": "INACTIVE"}))] == ["ZA1"]
    assert owner_client.get(URL, {"kind": "XX"}).status_code == 400


def test_detail_and_unknown_is_404(owner_client: Client) -> None:
    ing = Ingredient.objects.get(code="TTV")
    data = body(owner_client.get(f"{URL}/{ing.pk}"))
    assert data["code"] == "TTV"
    assert owner_client.get(f"{URL}/99999999").status_code == 404


# ------------------------------------------------------------------ tạo


def test_owner_creates_and_audit_logged(owner_client: Client, owner: Any) -> None:
    r = post(owner_client, payload(density_g_ml="0.915", shelf_life_months=24, requires_coa=True))
    assert r.status_code == 201, r.content
    data = body(r)
    assert (data["code"], data["status"], data["track_stock"]) == ("ZA1", "ACTIVE", True)
    assert data["requires_coa"] is True
    log = AuditLog.objects.get(entity="ingredient", entity_id=data["id"])
    assert (log.action, log.user_id) == ("CREATE", owner.pk)


@pytest.mark.parametrize("code", ["za1", "ABCDEFG", "", "A-1", "A B", "Ư1"])
def test_code_must_be_upper_1_to_6(owner_client: Client, code: str) -> None:
    r = post(owner_client, payload(code=code))
    assert r.status_code == 400
    assert not Ingredient.objects.filter(name="Phụ liệu thử").exists()


def test_duplicate_code_is_409(owner_client: Client) -> None:
    r = post(owner_client, payload(code="TTV"))
    assert (r.status_code, body(r)["code"]) == (409, "INGREDIENT_CODE_TAKEN")


@pytest.mark.parametrize(
    "extra",
    [
        {"kind": "NOPE"},
        {"density_g_ml": "0"},
        {"density_g_ml": "-1"},
        {"shelf_life_months": 0},
        {"name": "  "},
    ],
)
def test_invalid_body_is_400(owner_client: Client, extra: dict[str, Any]) -> None:
    assert post(owner_client, payload(**extra)).status_code == 400


# ------------------------------------------------------------------ sửa


def test_patch_updates_and_noop_writes_no_audit(owner_client: Client) -> None:
    ing = make()
    r = patch(owner_client, ing.pk, {"name": "Tên mới", "requires_coa": True})
    assert r.status_code == 200
    assert (body(r)["name"], body(r)["requires_coa"]) == ("Tên mới", True)
    log = AuditLog.objects.filter(entity="ingredient", entity_id=ing.pk, action="UPDATE").get()
    assert log.before is not None and log.before["name"] == "PL ZA1"

    assert patch(owner_client, ing.pk, {"name": "Tên mới"}).status_code == 200
    assert AuditLog.objects.filter(entity="ingredient", entity_id=ing.pk).count() == 1


def test_patch_null_clears_optional_but_rejects_required(owner_client: Client) -> None:
    ing = make(shelf_life_months=12, density_g_ml="0.9")
    r = patch(owner_client, ing.pk, {"shelf_life_months": None, "density_g_ml": None})
    assert r.status_code == 200
    assert (body(r)["shelf_life_months"], body(r)["density_g_ml"]) == (None, None)
    for name in ("name", "kind", "code", "status", "track_stock"):
        assert patch(owner_client, ing.pk, {name: None}).status_code == 400


def test_code_change_without_lots_is_allowed(owner_client: Client) -> None:
    ing = make()
    r = patch(owner_client, ing.pk, {"code": "ZB2"})
    assert (r.status_code, body(r)["code"]) == (200, "ZB2")
    r = patch(owner_client, ing.pk, {"code": "TTV"})
    assert (r.status_code, body(r)["code"]) == (409, "INGREDIENT_CODE_TAKEN")


def test_code_and_track_stock_locked_when_has_lots(
    owner_client: Client, lot_hooks: dict[str, set[int]]
) -> None:
    ing = make(track_stock=False)
    lot_hooks["any"].add(ing.pk)
    r = patch(owner_client, ing.pk, {"code": "ZB2"})
    assert (r.status_code, body(r)["code"]) == (409, "INGREDIENT_CODE_LOCKED")
    r = patch(owner_client, ing.pk, {"track_stock": True})
    assert (r.status_code, body(r)["code"]) == (409, "INGREDIENT_TRACK_STOCK_LOCKED")
    # gửi lại đúng mã hiện tại, đổi tên, hay tắt theo dõi tồn thì không bị khoá
    assert patch(owner_client, ing.pk, {"code": "ZA1", "name": "Đổi tên"}).status_code == 200
    ing.refresh_from_db()
    assert (ing.code, ing.track_stock) == ("ZA1", False)
    other = make("ZC3", track_stock=True)
    lot_hooks["any"].add(other.pk)
    assert patch(owner_client, other.pk, {"track_stock": False}).status_code == 200


# ------------------------------------------------------------------ BR-21 ngừng dùng


def test_deactivate_blocked_when_stock_left(
    owner_client: Client, lot_hooks: dict[str, set[int]]
) -> None:
    ing = make()
    lot_hooks["stock"].add(ing.pk)
    r = patch(owner_client, ing.pk, {"status": "INACTIVE"})
    assert (r.status_code, body(r)["code"]) == (409, "INGREDIENT_HAS_LOTS")
    assert body(r)["details"]["rule"] == "BR-21"
    lot_hooks["stock"].clear()
    assert patch(owner_client, ing.pk, {"status": "INACTIVE"}).status_code == 200


def test_deactivate_blocked_by_active_recipe(owner_client: Client) -> None:
    ttv = Ingredient.objects.get(code="TTV")  # nằm trong QC1 (ACTIVE)
    r = patch(owner_client, ttv.pk, {"status": "INACTIVE"})
    assert (r.status_code, body(r)["code"]) == (409, "INGREDIENT_IN_ACTIVE_RECIPE")
    assert "QC1" in body(r)["details"]["recipes"]
    ttv.refresh_from_db()
    assert ttv.status == "ACTIVE"


def test_deactivate_blocked_when_output_of_active_recipe(owner_client: Client) -> None:
    vqh = Ingredient.objects.get(code="VQH")  # đầu ra của SC-VQH, còn trong TUI
    Recipe.objects.filter(code="TUI").update(status=RecipeStatus.RETIRED)
    r = patch(owner_client, vqh.pk, {"status": "INACTIVE"})
    assert (r.status_code, body(r)["code"]) == (409, "INGREDIENT_IN_ACTIVE_RECIPE")
    assert body(r)["details"]["recipes"] == ["SC-VQH"]


def test_deactivate_allowed_when_only_retired_recipes_use_it(owner_client: Client) -> None:
    bm = Ingredient.objects.get(code="BM")  # chỉ nằm trong VTC
    Recipe.objects.filter(code="VTC").update(status=RecipeStatus.RETIRED)
    assert patch(owner_client, bm.pk, {"status": "INACTIVE"}).status_code == 200
    assert patch(owner_client, bm.pk, {"status": "ACTIVE"}).status_code == 200
