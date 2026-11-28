"""API bảng giá: lưới giá theo ngày (gần nhất kèm effective_date), PUT, lịch sử 30 ngày, audit."""

from __future__ import annotations

import datetime
import json
from typing import Any

import pytest
from django.test import Client

from catalog.models import Grade, Material, Price
from core.models import AuditLog
from core.timeutil import today_vn

pytestmark = pytest.mark.django_db

URL = "/api/v1/prices"
D1 = datetime.date(2026, 11, 10)
D2 = datetime.date(2026, 11, 20)


def put(client: Client, date: datetime.date | str, payload: dict[str, Any]) -> Any:
    return client.put(f"{URL}/{date}", payload, content_type="application/json")


def body(response: Any) -> Any:
    return json.loads(response.content)


def grade(code: str, rank: int) -> Grade:
    return Grade.objects.get(material__code=code, rank=rank)


def cell(code: str, rank: int, buy: int, sell: int) -> dict[str, int]:
    return {"grade_id": grade(code, rank).pk, "buy_price": buy, "sell_price": sell}


def find(sheet: dict[str, Any], code: str, rank: int) -> dict[str, Any]:
    for item in sheet["items"]:
        if item["material_code"] == code and item["grade_rank"] == rank:
            found: dict[str, Any] = item
            return found
    raise AssertionError(f"không có ô {code} loại {rank}")


# ------------------------------------------------------------------ phân quyền


def test_anonymous_gets_401(client: Client, db: None) -> None:
    assert client.get(URL).status_code == 401
    assert client.get(f"{URL}/history").status_code == 401
    assert put(client, D1, {"items": [cell("VQ", 1, 1, 1)]}).status_code == 401


def test_workshop_reads_but_cannot_put(workshop_client: Client, owner_client: Client) -> None:
    put(owner_client, D1, {"items": [cell("VQ", 1, 100, 120)]})
    r = workshop_client.get(f"{URL}?date={D1}")
    assert r.status_code == 200
    assert find(body(r), "VQ", 1)["buy_price"] == 100
    assert workshop_client.get(f"{URL}/history?to={D1}").status_code == 200

    r = put(workshop_client, D2, {"items": [cell("VQ", 1, 999, 999)]})
    assert r.status_code == 403
    assert body(r)["code"] == "FORBIDDEN"
    assert Price.objects.count() == 1
    assert AuditLog.objects.filter(entity="price").count() == 1  # chỉ lần của OWNER


# ------------------------------------------------------------------ GET lưới giá


def test_get_without_prices_returns_empty_cells(owner_client: Client, db: None) -> None:
    r = owner_client.get(f"{URL}?date={D1}")
    assert r.status_code == 200
    sheet = body(r)
    assert sheet["date"] == str(D1)
    assert [(i["material_code"], i["grade_rank"]) for i in sheet["items"]] == [
        ("VQ", 1),
        ("VQ", 2),
        ("VQ", 3),
        ("QV", 1),
        ("QV", 2),
        ("QV", 3),
    ]
    assert all(i["buy_price"] is None and i["effective_date"] is None for i in sheet["items"])
    assert sheet["items"][0]["material_name"] == "Vỏ quế"
    assert sheet["items"][0]["grade_name"] == "Loại 1"


def test_get_defaults_to_today_vn(owner_client: Client) -> None:
    put(owner_client, today_vn(), {"items": [cell("QV", 2, 50, 70)]})
    sheet = body(owner_client.get(URL))
    assert sheet["date"] == str(today_vn())
    qv2 = find(sheet, "QV", 2)
    assert (qv2["buy_price"], qv2["sell_price"], qv2["effective_date"]) == (
        50,
        70,
        str(today_vn()),
    )


def test_get_returns_nearest_earlier_price_with_effective_date(owner_client: Client) -> None:
    put(owner_client, D1, {"items": [cell("VQ", 1, 100, 120), cell("VQ", 2, 80, 90)]})
    put(owner_client, D2, {"items": [cell("VQ", 1, 110, 130)]})

    exact = body(owner_client.get(f"{URL}?date={D2}"))
    vq1 = find(exact, "VQ", 1)
    assert (vq1["buy_price"], vq1["effective_date"]) == (110, str(D2))
    # VQ loại 2 không có giá ngày D2: lấy giá gần nhất trước đó (D1).
    vq2 = find(exact, "VQ", 2)
    assert (vq2["buy_price"], vq2["sell_price"], vq2["effective_date"]) == (80, 90, str(D1))

    later = body(owner_client.get(f"{URL}?date=2026-12-31"))
    assert find(later, "VQ", 1)["effective_date"] == str(D2)
    assert find(later, "VQ", 2)["effective_date"] == str(D1)

    between = body(owner_client.get(f"{URL}?date=2026-11-15"))
    assert find(between, "VQ", 1)["buy_price"] == 100
    assert find(between, "VQ", 1)["effective_date"] == str(D1)

    before_all = body(owner_client.get(f"{URL}?date=2026-11-09"))
    assert find(before_all, "VQ", 1)["buy_price"] is None
    assert find(before_all, "VQ", 1)["effective_date"] is None
    assert find(exact, "QV", 1)["buy_price"] is None  # hạng chưa từng có giá


def test_get_skips_inactive_grade_and_material(owner_client: Client) -> None:
    Grade.objects.filter(material__code="VQ", rank=3).update(status="INACTIVE")
    sheet = body(owner_client.get(f"{URL}?date={D1}"))
    assert ("VQ", 3) not in {(i["material_code"], i["grade_rank"]) for i in sheet["items"]}
    assert len(sheet["items"]) == 5

    Material.objects.filter(code="QV").update(status="INACTIVE")
    sheet = body(owner_client.get(f"{URL}?date={D1}"))
    assert {i["material_code"] for i in sheet["items"]} == {"VQ"}


def test_get_invalid_date_is_400(owner_client: Client, db: None) -> None:
    r = owner_client.get(f"{URL}?date=hom-nay")
    assert r.status_code == 400
    assert body(r)["code"] == "VALIDATION_ERROR"


# ------------------------------------------------------------------ PUT


def test_put_creates_prices_returns_sheet_and_audits(owner_client: Client, owner: Any) -> None:
    r = put(
        owner_client,
        D1,
        {"items": [cell("VQ", 1, 100000, 130000), cell("QV", 3, 20000, 25000)]},
    )
    assert r.status_code == 200
    sheet = body(r)
    assert sheet["date"] == str(D1)
    assert find(sheet, "VQ", 1)["sell_price"] == 130000
    assert find(sheet, "QV", 3)["effective_date"] == str(D1)
    assert find(sheet, "VQ", 2)["buy_price"] is None  # ô không gửi thì không có giá

    prices = Price.objects.order_by("grade__material_id", "grade__rank")
    assert [(p.price_date, p.buy_price, p.sell_price) for p in prices] == [
        (D1, 100000, 130000),
        (D1, 20000, 25000),
    ]
    assert all(p.updated_by_id == owner.pk for p in prices)
    logs = AuditLog.objects.filter(entity="price")
    assert logs.count() == 2
    log = logs.get(entity_id=prices[0].pk)
    assert log.action == "CREATE"
    assert log.before is None
    assert log.after is not None and log.after["buy_price"] == 100000
    assert log.user_id == owner.pk


def test_put_again_updates_same_row_and_audits_before_after(owner_client: Client) -> None:
    put(owner_client, D1, {"items": [cell("VQ", 1, 100, 120)]})
    r = put(owner_client, D1, {"items": [cell("VQ", 1, 105, 125)]})
    assert r.status_code == 200
    assert find(body(r), "VQ", 1)["buy_price"] == 105
    assert Price.objects.count() == 1

    price = Price.objects.get()
    log = AuditLog.objects.get(entity="price", entity_id=price.pk, action="UPDATE")
    assert log.before is not None and log.before["buy_price"] == 100
    assert log.after is not None and log.after["buy_price"] == 105
    assert log.after["sell_price"] == 125


def test_put_same_values_writes_no_audit(owner_client: Client) -> None:
    put(owner_client, D1, {"items": [cell("VQ", 1, 100, 120)]})
    assert AuditLog.objects.filter(entity="price").count() == 1
    r = put(owner_client, D1, {"items": [cell("VQ", 1, 100, 120)]})
    assert r.status_code == 200
    assert AuditLog.objects.filter(entity="price").count() == 1


def test_put_accepts_zero_price(owner_client: Client) -> None:
    r = put(owner_client, D1, {"items": [cell("VQ", 1, 0, 0)]})
    assert r.status_code == 200
    assert find(body(r), "VQ", 1)["buy_price"] == 0


def test_put_negative_price_is_400_and_saves_nothing(owner_client: Client) -> None:
    r = put(owner_client, D1, {"items": [cell("VQ", 1, 100, 120), cell("VQ", 2, -1, 50)]})
    assert r.status_code == 400
    assert body(r)["code"] == "PRICE_NEGATIVE"
    assert body(r)["message"] == "Giá mua không được âm"
    assert body(r)["details"]["field"] == "items"

    r = put(owner_client, D1, {"items": [cell("VQ", 1, 100, -5)]})
    assert body(r)["message"] == "Giá bán không được âm"
    assert Price.objects.count() == 0  # cả bộ không lưu ô nào
    assert not AuditLog.objects.filter(entity="price").exists()


def test_put_absurd_price_is_400(owner_client: Client) -> None:
    r = put(owner_client, D1, {"items": [cell("VQ", 1, 10**12, 10)]})
    assert r.status_code == 400
    assert body(r)["code"] == "PRICE_TOO_LARGE"
    assert Price.objects.count() == 0


def test_put_empty_duplicate_and_unknown_grade_are_400(owner_client: Client) -> None:
    r = put(owner_client, D1, {"items": []})
    assert r.status_code == 400
    assert body(r)["code"] == "PRICE_EMPTY"
    assert body(r)["message"] == "Chưa có giá nào để lưu"

    r = put(owner_client, D1, {"items": [cell("VQ", 1, 1, 1), cell("VQ", 1, 2, 2)]})
    assert r.status_code == 400
    assert body(r)["code"] == "PRICE_GRADE_DUPLICATE"

    r = put(owner_client, D1, {"items": [{"grade_id": 999999, "buy_price": 1, "sell_price": 1}]})
    assert r.status_code == 400
    assert body(r)["code"] == "PRICE_GRADE_INVALID"
    assert body(r)["message"] == "Hạng không có hoặc đã ngừng dùng"
    assert Price.objects.count() == 0


def test_put_inactive_grade_or_material_is_400(owner_client: Client) -> None:
    Grade.objects.filter(material__code="VQ", rank=3).update(status="INACTIVE")
    r = put(owner_client, D1, {"items": [cell("VQ", 3, 1, 1)]})
    assert r.status_code == 400
    assert body(r)["code"] == "PRICE_GRADE_INVALID"

    Material.objects.filter(code="QV").update(status="INACTIVE")
    r = put(owner_client, D1, {"items": [cell("QV", 1, 1, 1)]})
    assert r.status_code == 400
    assert Price.objects.count() == 0


def test_put_invalid_date_or_body_is_400(owner_client: Client) -> None:
    r = put(owner_client, "2026-13-45", {"items": [cell("VQ", 1, 1, 1)]})
    assert r.status_code == 400
    assert body(r)["code"] == "VALIDATION_ERROR"
    r = put(owner_client, D1, {"items": [{"grade_id": grade("VQ", 1).pk, "buy_price": "abc"}]})
    assert r.status_code == 400
    assert body(r)["code"] == "VALIDATION_ERROR"


def test_put_invalid_input_never_leaves_partial_rows_when_later_cell_fails(
    owner_client: Client,
) -> None:
    Grade.objects.filter(material__code="QV", rank=2).update(status="INACTIVE")
    r = put(owner_client, D1, {"items": [cell("VQ", 1, 1, 1), cell("QV", 2, 1, 1)]})
    assert r.status_code == 400
    assert Price.objects.count() == 0


# ------------------------------------------------------------------ lịch sử 30 ngày


def test_history_covers_30_days_newest_first(owner_client: Client, workshop_client: Client) -> None:
    end = datetime.date(2026, 11, 30)
    first_day = end - datetime.timedelta(days=29)  # 01/11
    too_old = end - datetime.timedelta(days=30)  # 31/10
    put(owner_client, too_old, {"items": [cell("VQ", 1, 1, 1)]})
    put(owner_client, first_day, {"items": [cell("VQ", 1, 2, 2), cell("QV", 1, 3, 3)]})
    put(owner_client, end, {"items": [cell("VQ", 1, 4, 4)]})
    put(owner_client, end + datetime.timedelta(days=1), {"items": [cell("VQ", 1, 9, 9)]})

    for client in (owner_client, workshop_client):
        r = client.get(f"{URL}/history?to={end}")
        assert r.status_code == 200
        days = body(r)
        assert [d["price_date"] for d in days] == [str(end), str(first_day)]
        assert [(i["buy_price"], i["sell_price"]) for i in days[0]["items"]] == [(4, 4)]
        assert [i["grade_id"] for i in days[1]["items"]] == [
            grade("VQ", 1).pk,
            grade("QV", 1).pk,
        ]
        assert days[0]["items"][0]["updated_by_id"]


def test_history_defaults_to_today_and_can_be_empty(owner_client: Client, db: None) -> None:
    assert body(owner_client.get(f"{URL}/history")) == []
    put(owner_client, today_vn(), {"items": [cell("VQ", 1, 7, 8)]})
    days = body(owner_client.get(f"{URL}/history"))
    assert [d["price_date"] for d in days] == [str(today_vn())]
