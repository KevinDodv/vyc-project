"""API người bán và đồi quế: phân quyền 2 vai, luồng, duyệt, mã tự sinh, đồi mặc định, audit_log.

Địa bàn dựng riêng trong fixture (tỉnh > xã > thôn, mã `ZP`/`ZC`...), không dựa vào seed.
"""

from __future__ import annotations

import json
from typing import Any

import pytest
from django.test import Client

from catalog.models import ActiveStatus, Area, AreaLevel, Plot, Supplier
from catalog.services import suppliers as service
from core.models import AuditLog
from core.timeutil import today_vn

pytestmark = pytest.mark.django_db

URL = "/api/v1/suppliers"


# ---------------------------------------------------------------- dựng dữ liệu


def make_area(code: str, level: str, name: str, parent: Area | None = None) -> Area:
    return Area.objects.create(code=code, level=level, name=name, parent=parent)


@pytest.fixture
def province(db: None) -> Area:
    return make_area("ZP", AreaLevel.PROVINCE, "Tỉnh Thử")


@pytest.fixture
def commune(province: Area) -> Area:
    return make_area("ZC", AreaLevel.COMMUNE, "Xã Thử", province)


@pytest.fixture
def village(commune: Area) -> Area:
    return make_area("ZC-T1", AreaLevel.VILLAGE, "Thôn Một", commune)


@pytest.fixture
def village2(commune: Area) -> Area:
    return make_area("ZC-T2", AreaLevel.VILLAGE, "Thôn Hai", commune)


@pytest.fixture
def other_village(province: Area) -> Area:
    other = make_area("ZD", AreaLevel.COMMUNE, "Xã Khác Thử", province)
    return make_area("ZD-T1", AreaLevel.VILLAGE, "Thôn Một", other)


def post(client: Client, payload: dict[str, Any], url: str = URL) -> Any:
    return client.post(url, payload, content_type="application/json")


def patch(client: Client, url: str, payload: dict[str, Any]) -> Any:
    return client.patch(url, payload, content_type="application/json")


def body(response: Any) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(response.content)
    return data


def supplier_payload(area: Area, **overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "name": "Nguyễn Văn Hùng",
        "kind": "FARMER",
        "area_id": area.pk,
        "phone": "0912345678",
    }
    payload.update(overrides)
    return payload


def new_supplier(client: Client, area: Area, **overrides: Any) -> dict[str, Any]:
    r = post(client, supplier_payload(area, **overrides))
    assert r.status_code == 201, r.content
    return body(r)


def plots_url(supplier_id: int, plot_id: int | None = None) -> str:
    base = f"{URL}/{supplier_id}/plots"
    return base if plot_id is None else f"{base}/{plot_id}"


def new_plot(client: Client, supplier_id: int, area: Area, **overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {"area_id": area.pk, "area_ha": "1.5", "planted_year": 2015}
    payload.update(overrides)
    r = post(client, payload, plots_url(supplier_id))
    assert r.status_code == 201, r.content
    return body(r)


def before_of(log: AuditLog) -> dict[str, Any]:
    assert log.before is not None
    return dict(log.before)


def after_of(log: AuditLog) -> dict[str, Any]:
    assert log.after is not None
    return dict(log.after)


def audit(entity: str, entity_id: int, action: str | None = None) -> list[AuditLog]:
    qs = AuditLog.objects.filter(entity=entity, entity_id=entity_id)
    return list(qs.filter(action=action) if action else qs)


# ---------------------------------------------------------------- phân quyền


def test_anonymous_gets_401(client: Client, village: Area) -> None:
    assert client.get(URL).status_code == 401
    assert post(client, supplier_payload(village)).status_code == 401
    assert client.get(plots_url(1)).status_code == 401


def test_workshop_can_read_and_quick_add_but_not_the_rest(
    owner_client: Client, workshop_client: Client, village: Area
) -> None:
    owner_made = new_supplier(owner_client, village, name="Do chủ tạo")
    plot = new_plot(owner_client, owner_made["id"], village)
    assert workshop_client.get(URL).status_code == 200
    assert workshop_client.get(f"{URL}/{owner_made['id']}").status_code == 200
    assert workshop_client.get(plots_url(owner_made["id"])).status_code == 200
    assert post(workshop_client, supplier_payload(village, name="Xưởng thêm")).status_code == 201

    before = Supplier.objects.count()
    detail = f"{URL}/{owner_made['id']}"
    forbidden = [
        patch(workshop_client, detail, {"name": "Sửa lén"}),
        post(workshop_client, {}, f"{detail}/approve"),
        post(workshop_client, {"area_id": village.pk}, plots_url(owner_made["id"])),
        patch(workshop_client, plots_url(owner_made["id"], plot["id"]), {"area_ha": "9"}),
    ]
    for r in forbidden:
        assert r.status_code == 403, r.content
        assert body(r)["code"] == "FORBIDDEN"
    assert Supplier.objects.count() == before
    assert Supplier.objects.get(pk=owner_made["id"]).name == "Do chủ tạo"
    assert Plot.objects.get(pk=plot["id"]).area_ha is not None
    assert str(Plot.objects.get(pk=plot["id"]).area_ha) == "1.50"


# ---------------------------------------------------------------- tạo người bán


def test_owner_create_defaults(owner_client: Client, owner: Any, village: Area) -> None:
    data = new_supplier(owner_client, village)
    assert data["code"] == "NCC-ZC-001"
    assert data["approved"] is True
    assert data["stream"] == "GENERAL"
    assert data["public_consent"] is False  # mặc định không công khai tên
    assert data["status"] == "ACTIVE"
    assert data["plots_count"] == 0
    assert data["area_name"] == "Thôn Một, Xã Thử"
    assert data["notices"] == []
    (log,) = audit("supplier", data["id"], "CREATE")
    assert log.user_id == owner.pk
    assert after_of(log)["code"] == "NCC-ZC-001"


def test_supplier_code_counts_per_commune(
    owner_client: Client, village: Area, village2: Area, other_village: Area
) -> None:
    assert new_supplier(owner_client, village, name="A")["code"] == "NCC-ZC-001"
    assert new_supplier(owner_client, village2, name="B")["code"] == "NCC-ZC-002"  # cùng xã
    assert new_supplier(owner_client, other_village, name="C")["code"] == "NCC-ZD-001"


def test_owner_can_set_public_consent(owner_client: Client, village: Area) -> None:
    data = new_supplier(owner_client, village, public_consent=True)
    assert data["public_consent"] is True


def test_workshop_quick_add_is_pending_and_general(
    workshop_client: Client, workshop: Any, village: Area
) -> None:
    data = new_supplier(
        workshop_client, village, stream="CONTROLLED", public_consent=True, name="Hộ mới"
    )
    assert data["approved"] is False
    assert data["stream"] == "GENERAL"
    assert data["public_consent"] is False
    (log,) = audit("supplier", data["id"], "CREATE")
    assert log.user_id == workshop.pk
    assert after_of(log)["approved"] is False


def test_controlled_needs_a_plot_so_cannot_be_chosen_on_create(
    owner_client: Client, village: Area
) -> None:
    r = post(owner_client, supplier_payload(village, stream="CONTROLLED"))
    assert r.status_code == 409
    err = body(r)
    assert err["code"] == "STREAM_NEEDS_PLOT"
    assert err["details"]["field"] == "stream"
    assert Supplier.objects.count() == 0
    # Số thứ tự không bị đốt khi tạo lỗi.
    assert new_supplier(owner_client, village)["code"] == "NCC-ZC-001"


def test_trader_stream_is_locked_to_general(
    owner_client: Client, commune: Area, village: Area
) -> None:
    r = post(owner_client, supplier_payload(village, kind="TRADER", stream="CONTROLLED"))
    assert r.status_code == 400
    assert body(r)["code"] == "STREAM_LOCKED"
    trader = new_supplier(owner_client, commune, kind="TRADER", name="Thương lái Bình")
    assert trader["stream"] == "GENERAL"
    assert trader["code"] == "NCC-ZC-001"  # thương lái ở cấp xã: mã theo chính xã đó


def test_farmer_and_family_must_be_at_village_level(
    owner_client: Client, province: Area, commune: Area
) -> None:
    for kind in ("FARMER", "FAMILY"):
        r = post(owner_client, supplier_payload(commune, kind=kind))
        assert r.status_code == 400, kind
        err = body(r)
        assert err["code"] == "VALIDATION_ERROR"
        assert err["details"]["field"] == "area"
    assert Supplier.objects.count() == 0


def test_trader_cannot_be_at_province_level(owner_client: Client, province: Area) -> None:
    r = post(owner_client, supplier_payload(province, kind="TRADER"))
    assert r.status_code == 400
    assert body(r)["details"]["field"] == "area"


def test_area_must_exist_and_be_active(owner_client: Client, village: Area) -> None:
    r = post(owner_client, supplier_payload(village, area_id=999999))
    assert r.status_code == 400
    assert body(r)["code"] == "AREA_INVALID"
    Area.objects.filter(pk=village.pk).update(status=ActiveStatus.INACTIVE)
    r = post(owner_client, supplier_payload(village))
    assert r.status_code == 400
    assert body(r)["details"]["field"] == "area_id"


def test_create_validates_body(owner_client: Client, village: Area) -> None:
    for bad in (
        supplier_payload(village, name="  "),
        supplier_payload(village, kind="ALIEN"),
        supplier_payload(village, stream="OTHER"),
        {"name": "Thiếu địa bàn", "kind": "FARMER"},
    ):
        r = post(owner_client, bad)
        assert r.status_code == 400, bad
        assert body(r)["code"] == "VALIDATION_ERROR"


# ---------------------------------------------------------------- cảnh báo trùng


def test_duplicate_name_and_village_warns_but_saves(
    owner_client: Client, village: Area, village2: Area
) -> None:
    first = new_supplier(owner_client, village, name="Nguyễn Văn Hùng")
    dup = new_supplier(owner_client, village, name="  nguyen van HUNG ")  # khác dấu, hoa/thường
    assert [n["code"] for n in dup["notices"]] == ["SUPPLIER_DUPLICATE"]
    assert dup["notices"][0]["supplier_ids"] == [first["id"]]
    assert "Thôn Một" in dup["notices"][0]["message"]
    assert Supplier.objects.count() == 2  # không chặn

    other_place = new_supplier(owner_client, village2, name="Nguyễn Văn Hùng")
    assert other_place["notices"] == []  # khác thôn thì không trùng


def test_rename_or_move_into_duplicate_warns(
    owner_client: Client, village: Area, village2: Area
) -> None:
    new_supplier(owner_client, village, name="Hùng")
    other = new_supplier(owner_client, village2, name="Hùng")
    moved = body(patch(owner_client, f"{URL}/{other['id']}", {"area_id": village.pk}))
    assert [n["code"] for n in moved["notices"]] == ["SUPPLIER_DUPLICATE"]
    renamed = body(patch(owner_client, f"{URL}/{other['id']}", {"phone": "0900000000"}))
    assert renamed["notices"] == []  # sửa SĐT không nhắc lại


# ---------------------------------------------------------------- duyệt


def test_approve_flow(owner_client: Client, workshop_client: Client, village: Area) -> None:
    pending = new_supplier(workshop_client, village)
    assert pending["approved"] is False
    listed = body(owner_client.get(URL, {"approved": "false"}))["items"]
    assert [s["id"] for s in listed] == [pending["id"]]

    r = post(owner_client, {}, f"{URL}/{pending['id']}/approve")
    assert r.status_code == 200
    assert body(r)["approved"] is True
    (log,) = audit("supplier", pending["id"], "UPDATE")
    assert before_of(log)["approved"] is False
    assert after_of(log)["approved"] is True
    assert log.reason == "Duyệt người bán"
    assert body(owner_client.get(URL, {"approved": "false"}))["items"] == []


def test_approve_twice_is_idempotent_without_extra_audit(
    owner_client: Client, workshop_client: Client, village: Area
) -> None:
    pending = new_supplier(workshop_client, village)
    for _ in range(2):
        assert post(owner_client, {}, f"{URL}/{pending['id']}/approve").status_code == 200
    assert len(audit("supplier", pending["id"], "UPDATE")) == 1


def test_approve_unknown_supplier_is_404(owner_client: Client) -> None:
    assert post(owner_client, {}, f"{URL}/999999/approve").status_code == 404


def test_owner_can_change_stream_before_approving(
    owner_client: Client, workshop_client: Client, village: Area
) -> None:
    pending = new_supplier(workshop_client, village)
    new_plot(owner_client, pending["id"], village)
    r = patch(owner_client, f"{URL}/{pending['id']}", {"stream": "CONTROLLED"})
    assert r.status_code == 200
    assert body(post(owner_client, {}, f"{URL}/{pending['id']}/approve"))["stream"] == "CONTROLLED"


# ---------------------------------------------------------------- sửa người bán


def test_patch_updates_only_sent_fields_and_audits(owner_client: Client, village: Area) -> None:
    data = new_supplier(owner_client, village)
    r = patch(owner_client, f"{URL}/{data['id']}", {"phone": None, "public_consent": True})
    assert r.status_code == 200
    out = body(r)
    assert out["phone"] is None
    assert out["public_consent"] is True
    assert out["name"] == "Nguyễn Văn Hùng"
    assert out["code"] == "NCC-ZC-001"
    (log,) = audit("supplier", data["id"], "UPDATE")
    assert before_of(log)["phone"] == "0912345678"
    assert after_of(log)["public_consent"] is True


def test_patch_without_change_writes_no_audit(owner_client: Client, village: Area) -> None:
    data = new_supplier(owner_client, village)
    r = patch(owner_client, f"{URL}/{data['id']}", {"name": data["name"], "kind": data["kind"]})
    assert r.status_code == 200
    assert audit("supplier", data["id"], "UPDATE") == []


def test_patch_null_on_required_field_is_400(owner_client: Client, village: Area) -> None:
    data = new_supplier(owner_client, village)
    for field in ("name", "kind", "area_id", "stream", "public_consent", "status"):
        r = patch(owner_client, f"{URL}/{data['id']}", {field: None})
        assert r.status_code == 400, field
        assert body(r)["code"] == "VALIDATION_ERROR"


def test_controlled_requires_an_active_plot(owner_client: Client, village: Area) -> None:
    data = new_supplier(owner_client, village)
    url = f"{URL}/{data['id']}"
    r = patch(owner_client, url, {"stream": "CONTROLLED"})
    assert r.status_code == 409
    assert body(r)["code"] == "STREAM_NEEDS_PLOT"
    assert Supplier.objects.get(pk=data["id"]).stream == "GENERAL"

    new_plot(owner_client, data["id"], village)
    out = body(patch(owner_client, url, {"stream": "CONTROLLED"}))
    assert out["stream"] == "CONTROLLED"
    assert out["plots_count"] == 1


def test_inactive_plot_does_not_count_for_controlled(owner_client: Client, village: Area) -> None:
    data = new_supplier(owner_client, village)
    plot = new_plot(owner_client, data["id"], village)
    assert (
        patch(owner_client, plots_url(data["id"], plot["id"]), {"status": "INACTIVE"}).status_code
        == 200
    )
    r = patch(owner_client, f"{URL}/{data['id']}", {"stream": "CONTROLLED"})
    assert r.status_code == 409


def test_trader_kind_requires_general_stream(
    owner_client: Client, village: Area, commune: Area
) -> None:
    data = new_supplier(owner_client, village)
    new_plot(owner_client, data["id"], village)
    url = f"{URL}/{data['id']}"
    patch(owner_client, url, {"stream": "CONTROLLED"})
    r = patch(owner_client, url, {"kind": "TRADER"})
    assert r.status_code == 400
    assert body(r)["code"] == "STREAM_LOCKED"
    ok = patch(owner_client, url, {"kind": "TRADER", "stream": "GENERAL"})
    assert ok.status_code == 200
    assert body(ok)["kind"] == "TRADER"


def test_patch_area_follows_level_rule(owner_client: Client, village: Area, commune: Area) -> None:
    data = new_supplier(owner_client, village)
    r = patch(owner_client, f"{URL}/{data['id']}", {"area_id": commune.pk})
    assert r.status_code == 400
    assert body(r)["details"]["field"] == "area"
    assert Supplier.objects.get(pk=data["id"]).area_id == village.pk


def test_deactivate_supplier_and_stock_guard(
    owner_client: Client, village: Area, monkeypatch: pytest.MonkeyPatch
) -> None:
    data = new_supplier(owner_client, village)
    url = f"{URL}/{data['id']}"
    monkeypatch.setattr(service, "_supplier_in_use_checks", [lambda _id: True])
    r = patch(owner_client, url, {"status": "INACTIVE"})
    assert r.status_code == 409
    err = body(r)
    assert err["code"] == "SUPPLIER_IN_USE"
    assert err["details"]["rule"] == "BR-21"
    monkeypatch.setattr(service, "_supplier_in_use_checks", [])
    assert body(patch(owner_client, url, {"status": "INACTIVE"}))["status"] == "INACTIVE"


def test_unknown_supplier_is_404(owner_client: Client) -> None:
    assert owner_client.get(f"{URL}/999999").status_code == 404
    assert patch(owner_client, f"{URL}/999999", {"name": "X"}).status_code == 404
    assert owner_client.get(plots_url(999999)).status_code == 404


# ---------------------------------------------------------------- danh sách và lưới nút


def test_search_ignores_accents_and_matches_code_phone_village(
    workshop_client: Client, owner_client: Client, village: Area, village2: Area
) -> None:
    hung = new_supplier(owner_client, village, name="Nguyễn Văn Hùng", phone="0911111111")
    lan = new_supplier(owner_client, village2, name="Đỗ Thị Lan", phone="0922222222")

    def ids(**params: Any) -> list[int]:
        r = workshop_client.get(URL, params)
        assert r.status_code == 200
        return [s["id"] for s in body(r)["items"]]

    assert ids(q="hung") == [hung["id"]]
    assert ids(q="HÙNG") == [hung["id"]]
    assert ids(q="do thi") == [lan["id"]]  # «Đ» cũng bỏ dấu
    assert ids(q="0922") == [lan["id"]]
    assert ids(q=lan["code"]) == [lan["id"]]
    assert ids(q="thon hai") == [lan["id"]]
    assert ids(q="khong co") == []


def test_recent_returns_latest_active_suppliers(
    workshop_client: Client, owner_client: Client, village: Area
) -> None:
    made = [new_supplier(owner_client, village, name=f"Người bán {i}") for i in range(4)]
    patch(owner_client, f"{URL}/{made[0]['id']}", {"phone": "0900000009"})  # mới sửa → lên đầu
    patch(owner_client, f"{URL}/{made[3]['id']}", {"status": "INACTIVE"})  # ngừng dùng → loại
    r = workshop_client.get(URL, {"recent": 2})
    assert r.status_code == 200
    page = body(r)
    assert [s["id"] for s in page["items"]] == [made[0]["id"], made[2]["id"]]
    assert page["total"] == 2
    assert page["items"][0]["area_name"] == "Thôn Một, Xã Thử"
    assert workshop_client.get(URL, {"recent": 0}).status_code == 400


def test_list_filters_and_orders_by_name(owner_client: Client, village: Area) -> None:
    b = new_supplier(owner_client, village, name="Bình", kind="FAMILY")
    a = new_supplier(owner_client, village, name="An")
    patch(owner_client, f"{URL}/{b['id']}", {"status": "INACTIVE"})
    assert [s["name"] for s in body(owner_client.get(URL))["items"]] == ["An", "Bình"]
    assert [s["id"] for s in body(owner_client.get(URL, {"status": "ACTIVE"}))["items"]] == [
        a["id"]
    ]
    assert [s["id"] for s in body(owner_client.get(URL, {"kind": "FAMILY"}))["items"]] == [b["id"]]
    assert [s["id"] for s in body(owner_client.get(URL, {"area_id": village.pk}))["items"]] == [
        a["id"],
        b["id"],
    ]
    assert body(owner_client.get(URL, {"stream": "CONTROLLED"}))["items"] == []


# ---------------------------------------------------------------- đồi: tạo và mã


def test_first_plot_is_default_and_code_follows_supplier(
    owner_client: Client, owner: Any, village: Area, village2: Area
) -> None:
    sup = new_supplier(owner_client, village)
    first = new_plot(owner_client, sup["id"], village)
    second = new_plot(owner_client, sup["id"], village2)
    assert first["code"] == "D-ZC-001-01"
    assert second["code"] == "D-ZC-001-02"
    assert first["is_default"] is True
    assert second["is_default"] is False
    assert first["area_ha"] == 1.5
    assert first["planted_year"] == 2015
    assert second["area_name"] == "Thôn Hai, Xã Thử"
    (log,) = audit("plot", first["id"], "CREATE")
    assert log.user_id == owner.pk
    # Đếm theo người bán: người bán thứ hai bắt đầu lại ở 01.
    other = new_supplier(owner_client, village, name="Người bán hai")
    assert new_plot(owner_client, other["id"], village)["code"] == "D-ZC-002-01"
    assert body(owner_client.get(f"{URL}/{sup['id']}"))["plots_count"] == 2


def test_new_default_plot_takes_over_and_audits_the_old_one(
    owner_client: Client, village: Area
) -> None:
    sup = new_supplier(owner_client, village)
    first = new_plot(owner_client, sup["id"], village)
    second = new_plot(owner_client, sup["id"], village, is_default=True)
    assert second["is_default"] is True
    plots = body_list(owner_client.get(plots_url(sup["id"])))
    assert [(p["id"], p["is_default"]) for p in plots] == [
        (second["id"], True),
        (first["id"], False),
    ]  # đồi mặc định xếp đầu
    (log,) = audit("plot", first["id"], "UPDATE")
    assert before_of(log)["is_default"] is True
    assert after_of(log)["is_default"] is False


def body_list(response: Any) -> list[dict[str, Any]]:
    assert response.status_code == 200, response.content
    data: list[dict[str, Any]] = json.loads(response.content)
    return data


def test_plot_planted_year_range(owner_client: Client, village: Area) -> None:
    sup = new_supplier(owner_client, village)
    this_year = today_vn().year
    for year in (1950, this_year):
        assert new_plot(owner_client, sup["id"], village, planted_year=year)["planted_year"] == year
    for bad in (1949, this_year + 1):
        r = post(owner_client, {"area_id": village.pk, "planted_year": bad}, plots_url(sup["id"]))
        assert r.status_code == 400, bad
        assert body(r)["code"] == "VALIDATION_ERROR"


def test_plot_year_error_names_the_field(owner_client: Client, village: Area) -> None:
    sup = new_supplier(owner_client, village)
    r = post(
        owner_client,
        {"area_id": village.pk, "planted_year": today_vn().year + 1},
        plots_url(sup["id"]),
    )
    assert r.status_code == 400
    assert body(r)["details"]["field"] == "planted_year"
    assert Plot.objects.count() == 0
    # Lỗi không đốt số: đồi kế tiếp vẫn là 01.
    assert new_plot(owner_client, sup["id"], village)["code"] == "D-ZC-001-01"


def test_patch_plot_year_is_rechecked(owner_client: Client, village: Area) -> None:
    sup = new_supplier(owner_client, village)
    plot = new_plot(owner_client, sup["id"], village)
    url = plots_url(sup["id"], plot["id"])
    assert patch(owner_client, url, {"planted_year": today_vn().year + 1}).status_code == 400
    assert patch(owner_client, url, {"planted_year": 1949}).status_code == 400
    out = body(patch(owner_client, url, {"planted_year": 1990}))
    assert out["planted_year"] == 1990
    assert body(patch(owner_client, url, {"planted_year": None}))["planted_year"] is None


def test_plot_area_must_be_a_village(owner_client: Client, village: Area, commune: Area) -> None:
    sup = new_supplier(owner_client, village)
    r = post(owner_client, {"area_id": commune.pk}, plots_url(sup["id"]))
    assert r.status_code == 400
    assert body(r)["details"]["field"] == "area"
    assert post(owner_client, {"area_id": 999999}, plots_url(sup["id"])).status_code == 400


def test_plot_needs_existing_supplier(owner_client: Client, village: Area) -> None:
    assert post(owner_client, {"area_id": village.pk}, plots_url(999999)).status_code == 404


# ---------------------------------------------------------------- đồi: toạ độ


def test_plot_coordinates_pasted_from_google_maps(owner_client: Client, village: Area) -> None:
    sup = new_supplier(owner_client, village)
    plot = new_plot(owner_client, sup["id"], village, coordinates="21.0285791, 105.8541934")
    assert plot["lat"] == pytest.approx(21.028579)
    assert plot["lng"] == pytest.approx(105.854193)
    stored = Plot.objects.get(pk=plot["id"])
    assert str(stored.lat) == "21.028579"
    assert str(stored.lng) == "105.854193"


def test_plot_coordinates_accept_numbers_and_separators(
    owner_client: Client, village: Area
) -> None:
    sup = new_supplier(owner_client, village)
    numeric = new_plot(owner_client, sup["id"], village, lat=22.1, lng=104.5)
    assert (numeric["lat"], numeric["lng"]) == (22.1, 104.5)
    spaced = new_plot(owner_client, sup["id"], village, coordinates=" -21.5   104.25 ")
    assert (spaced["lat"], spaced["lng"]) == (-21.5, 104.25)


def test_plot_coordinates_rejected_when_wrong(owner_client: Client, village: Area) -> None:
    sup = new_supplier(owner_client, village)
    url = plots_url(sup["id"])
    base = {"area_id": village.pk}
    for bad in (
        {"coordinates": "không phải toạ độ"},
        {"coordinates": "21.0"},
        {"coordinates": "91.0, 105.0"},  # vĩ độ > 90
        {"coordinates": "21.0, 181.0"},  # kinh độ > 180
        {"coordinates": "21.0, 105.0", "lat": 21.0, "lng": 105.0},  # gửi cả hai cách
        {"lat": 95, "lng": 105},
    ):
        r = post(owner_client, {**base, **bad}, url)
        assert r.status_code == 400, bad
        assert body(r)["code"] == "VALIDATION_ERROR"
    for half in ({"lat": 21.0}, {"lng": 105.0}):
        r = post(owner_client, {**base, **half}, url)
        assert r.status_code == 400, half
        assert body(r)["code"] == "COORDINATES_INCOMPLETE"
    assert Plot.objects.count() == 0


def test_patch_plot_coordinates(owner_client: Client, village: Area) -> None:
    sup = new_supplier(owner_client, village)
    plot = new_plot(owner_client, sup["id"], village, coordinates="21.0, 105.0")
    url = plots_url(sup["id"], plot["id"])
    out = body(patch(owner_client, url, {"coordinates": "21.5, 105.5"}))
    assert (out["lat"], out["lng"]) == (21.5, 105.5)
    cleared = body(patch(owner_client, url, {"lat": None, "lng": None}))
    assert (cleared["lat"], cleared["lng"]) == (None, None)
    assert patch(owner_client, url, {"lat": 21.0}).status_code == 400  # thiếu kinh độ
    back = body(patch(owner_client, url, {"coordinates": "21.5, 105.5"}))
    assert body(patch(owner_client, url, {"coordinates": None}))["lat"] is None
    assert back["lat"] == 21.5


# ---------------------------------------------------------------- đồi: ảnh


def test_plot_photo_urls_only_media_or_https(owner_client: Client, village: Area) -> None:
    sup = new_supplier(owner_client, village)
    url = plots_url(sup["id"])
    for bad in (
        "javascript:alert(1)",
        "data:text/html;base64,PHNjcmlwdD4=",
        "http://example.com/a.jpg",
        "//evil.example/a.jpg",
        "/media/../etc/passwd",
        "/media/%2e%2e/secret",
        "/static/a.jpg",
        "https://",
        "https://exa mple.com/a.jpg",
        "ftp://example.com/a.jpg",
    ):
        r = post(owner_client, {"area_id": village.pk, "photo_urls": [bad]}, url)
        assert r.status_code == 400, bad
        assert body(r)["code"] == "VALIDATION_ERROR"
    good = ["/media/img/3f/3fa9abc1-1440.webp", "https://cdn.example.com/doi-que.jpg"]
    plot = new_plot(owner_client, sup["id"], village, photo_urls=good)
    assert plot["photo_urls"] == good
    too_many = ["/media/a.webp"] * 11
    assert (
        post(owner_client, {"area_id": village.pk, "photo_urls": too_many}, url).status_code == 400
    )


def test_patch_plot_photo_urls_are_checked_too(owner_client: Client, village: Area) -> None:
    sup = new_supplier(owner_client, village)
    plot = new_plot(owner_client, sup["id"], village)
    url = plots_url(sup["id"], plot["id"])
    assert patch(owner_client, url, {"photo_urls": ["javascript:alert(1)"]}).status_code == 400
    assert patch(owner_client, url, {"photo_urls": None}).status_code == 400
    out = body(patch(owner_client, url, {"photo_urls": ["/media/x.webp"]}))
    assert out["photo_urls"] == ["/media/x.webp"]
    assert Plot.objects.get(pk=plot["id"]).photo_urls == ["/media/x.webp"]


def test_service_rejects_bad_photo_even_without_schema(owner: Any, village: Area) -> None:
    from catalog.services.suppliers import PlotCreate, SupplierCreate, create_plot, create_supplier
    from core.errors import ApiError

    sup = create_supplier(
        data=SupplierCreate(name="A", kind="FARMER", area_id=village.pk), actor=owner
    ).supplier
    with pytest.raises(ApiError) as exc:
        create_plot(
            supplier_id=sup.pk,
            data=PlotCreate(area_id=village.pk, photo_urls=["data:image/png;base64,AAAA"]),
            actor=owner,
        )
    assert exc.value.code == "PHOTO_URL_INVALID"


# ---------------------------------------------------------------- đồi: mặc định và ngừng dùng


def default_ids(supplier_id: int) -> list[int]:
    return list(
        Plot.objects.filter(supplier_id=supplier_id, is_default=True).values_list("pk", flat=True)
    )


def test_exactly_one_default_among_active_plots(owner_client: Client, village: Area) -> None:
    sup = new_supplier(owner_client, village)
    a = new_plot(owner_client, sup["id"], village)
    b = new_plot(owner_client, sup["id"], village)
    c = new_plot(owner_client, sup["id"], village)
    assert default_ids(sup["id"]) == [a["id"]]
    out = body(patch(owner_client, plots_url(sup["id"], c["id"]), {"is_default": True}))
    assert out["is_default"] is True
    assert default_ids(sup["id"]) == [c["id"]]
    assert b["is_default"] is False


def test_cannot_unset_the_only_default(owner_client: Client, village: Area) -> None:
    sup = new_supplier(owner_client, village)
    only = new_plot(owner_client, sup["id"], village)
    r = patch(owner_client, plots_url(sup["id"], only["id"]), {"is_default": False})
    assert r.status_code == 409
    err = body(r)
    assert err["code"] == "DEFAULT_PLOT_REQUIRED"
    assert err["details"]["field"] == "is_default"
    assert default_ids(sup["id"]) == [only["id"]]


def test_deactivating_default_promotes_another_active_plot(
    owner_client: Client, village: Area
) -> None:
    sup = new_supplier(owner_client, village)
    a = new_plot(owner_client, sup["id"], village)
    b = new_plot(owner_client, sup["id"], village)
    c = new_plot(owner_client, sup["id"], village)
    out = body(patch(owner_client, plots_url(sup["id"], a["id"]), {"status": "INACTIVE"}))
    assert out["status"] == "INACTIVE"
    assert out["is_default"] is False
    assert default_ids(sup["id"]) == [b["id"]]  # đồi đang dùng có id nhỏ nhất
    assert c["is_default"] is False
    promoted = audit("plot", b["id"], "UPDATE")
    assert len(promoted) == 1
    assert after_of(promoted[0])["is_default"] is True


def test_inactive_plot_cannot_be_default(owner_client: Client, village: Area) -> None:
    sup = new_supplier(owner_client, village)
    new_plot(owner_client, sup["id"], village)
    b = new_plot(owner_client, sup["id"], village)
    url = plots_url(sup["id"], b["id"])
    patch(owner_client, url, {"status": "INACTIVE"})
    r = patch(owner_client, url, {"is_default": True})
    assert r.status_code == 400
    assert body(r)["code"] == "PLOT_INACTIVE_DEFAULT"


def test_last_active_plot_of_controlled_supplier_cannot_be_deactivated(
    owner_client: Client, village: Area, village2: Area
) -> None:
    sup = new_supplier(owner_client, village)
    a = new_plot(owner_client, sup["id"], village)
    b = new_plot(owner_client, sup["id"], village2)
    patch(owner_client, f"{URL}/{sup['id']}", {"stream": "CONTROLLED"})
    assert (
        patch(owner_client, plots_url(sup["id"], a["id"]), {"status": "INACTIVE"}).status_code
        == 200
    )
    r = patch(owner_client, plots_url(sup["id"], b["id"]), {"status": "INACTIVE"})
    assert r.status_code == 409
    assert body(r)["code"] == "STREAM_NEEDS_PLOT"
    assert Plot.objects.get(pk=b["id"]).status == "ACTIVE"


def test_general_supplier_can_deactivate_all_and_reactivation_restores_default(
    owner_client: Client, village: Area
) -> None:
    sup = new_supplier(owner_client, village)
    only = new_plot(owner_client, sup["id"], village)
    url = plots_url(sup["id"], only["id"])
    assert patch(owner_client, url, {"status": "INACTIVE"}).status_code == 200
    assert default_ids(sup["id"]) == []
    assert body(owner_client.get(f"{URL}/{sup['id']}"))["plots_count"] == 0
    back = body(patch(owner_client, url, {"status": "ACTIVE"}))
    assert back["is_default"] is True  # đồi duy nhất đang dùng là đồi mặc định
    # Đồi mới sau đó không giành mặc định.
    assert new_plot(owner_client, sup["id"], village)["is_default"] is False


def test_reactivated_plot_does_not_steal_default(owner_client: Client, village: Area) -> None:
    sup = new_supplier(owner_client, village)
    a = new_plot(owner_client, sup["id"], village)
    b = new_plot(owner_client, sup["id"], village)
    patch(owner_client, plots_url(sup["id"], b["id"]), {"status": "INACTIVE"})
    back = body(patch(owner_client, plots_url(sup["id"], b["id"]), {"status": "ACTIVE"}))
    assert back["is_default"] is False
    assert default_ids(sup["id"]) == [a["id"]]


def test_plot_of_another_supplier_is_404(owner_client: Client, village: Area) -> None:
    one = new_supplier(owner_client, village, name="Một")
    two = new_supplier(owner_client, village, name="Hai")
    plot = new_plot(owner_client, one["id"], village)
    r = patch(owner_client, plots_url(two["id"], plot["id"]), {"area_ha": "2"})
    assert r.status_code == 404


def test_patch_plot_fields_and_audit(
    owner_client: Client, owner: Any, village: Area, village2: Area
) -> None:
    sup = new_supplier(owner_client, village)
    plot = new_plot(owner_client, sup["id"], village)
    url = plots_url(sup["id"], plot["id"])
    out = body(patch(owner_client, url, {"area_ha": "2.25", "area_id": village2.pk}))
    assert out["area_ha"] == 2.25
    assert out["area_name"] == "Thôn Hai, Xã Thử"
    assert out["code"] == plot["code"]  # mã không đổi khi đổi thôn
    (log,) = audit("plot", plot["id"], "UPDATE")
    assert log.user_id == owner.pk
    assert before_of(log)["area_id"] == village.pk
    assert after_of(log)["area_id"] == village2.pk
    assert patch(owner_client, url, {"area_ha": "-1"}).status_code == 400
    assert patch(owner_client, url, {"area_ha": "1.234"}).status_code == 400
    # Không đổi gì thì không thêm audit_log.
    patch(owner_client, url, {"area_ha": "2.25"})
    assert len(audit("plot", plot["id"], "UPDATE")) == 1


def test_list_plots_status_filter(
    owner_client: Client, workshop_client: Client, village: Area
) -> None:
    sup = new_supplier(owner_client, village)
    a = new_plot(owner_client, sup["id"], village)
    b = new_plot(owner_client, sup["id"], village)
    patch(owner_client, plots_url(sup["id"], b["id"]), {"status": "INACTIVE"})
    active = body_list(workshop_client.get(plots_url(sup["id"]), {"status": "ACTIVE"}))
    assert [p["id"] for p in active] == [a["id"]]
    assert len(body_list(workshop_client.get(plots_url(sup["id"])))) == 2
