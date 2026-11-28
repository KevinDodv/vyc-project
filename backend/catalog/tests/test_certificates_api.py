"""API chứng nhận: quyền 2 vai, một đích, hết hạn ≥ ngày cấp, URL file, audit_log, service web."""

from __future__ import annotations

import datetime
import json
from typing import Any

import pytest
from django.test import Client

from catalog.models import (
    Area,
    AreaLevel,
    Certificate,
    GoodsType,
    Plot,
    Product,
    Supplier,
    SupplierKind,
    SupplierStream,
)
from catalog.services.certificates import active_public_for_product
from catalog.tests.conftest import make_product
from core.models import AuditLog
from core.timeutil import today_vn

pytestmark = pytest.mark.django_db

URL = "/api/v1/certificates"
TODAY = today_vn()


def post(client: Client, payload: dict[str, Any]) -> Any:
    return client.post(URL, payload, content_type="application/json")


def patch(client: Client, certificate_id: int, payload: dict[str, Any]) -> Any:
    return client.patch(f"{URL}/{certificate_id}", payload, content_type="application/json")


def body(response: Any) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(response.content)
    return data


@pytest.fixture
def product(goods_type: GoodsType) -> Product:
    return make_product(goods_type)


@pytest.fixture
def plot(db: None) -> Plot:
    province = Area.objects.create(code="ZZ", level=AreaLevel.PROVINCE, name="Tỉnh thử")
    commune = Area.objects.create(
        code="ZZ-C", level=AreaLevel.COMMUNE, name="Xã thử", parent=province
    )
    village = Area.objects.create(
        code="ZZ-V", level=AreaLevel.VILLAGE, name="Thôn thử", parent=commune
    )
    supplier = Supplier.objects.create(
        code="NCC-ZZ-001",
        name="Hộ thử",
        kind=SupplierKind.FARMER,
        area=village,
        stream=SupplierStream.CONTROLLED,
    )
    return Plot.objects.create(code="D-ZZ-1-01", supplier=supplier, area=village)


def payload(product: Product, **overrides: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        "kind": "OCOP",
        "number": "OCOP-2026-01",
        "issuer": "UBND tỉnh Lào Cai",
        "issued_on": "2026-01-10",
        "expires_on": "2029-01-10",
        "stars": 4,
        "product_id": product.pk,
    }
    data.update(overrides)
    return data


def make_cert(**fields: Any) -> Certificate:
    fields.setdefault("kind", "FOOD_SAFETY")
    fields.setdefault("number", "ATTP-1")
    return Certificate.objects.create(**fields)


# ------------------------------------------------------------------ phân quyền


def test_anonymous_gets_401(client: Client, product: Product) -> None:
    assert client.get(URL).status_code == 401
    assert post(client, payload(product)).status_code == 401


def test_workshop_reads_but_cannot_write(workshop_client: Client, product: Product) -> None:
    cert = make_cert(product=product)
    assert workshop_client.get(URL).status_code == 200
    assert workshop_client.get(f"{URL}/{cert.pk}").status_code == 200

    r = post(workshop_client, payload(product))
    assert r.status_code == 403
    assert body(r)["code"] == "FORBIDDEN"
    r = patch(workshop_client, cert.pk, {"is_public": False})
    assert r.status_code == 403
    cert.refresh_from_db()
    assert cert.is_public is True
    assert Certificate.objects.count() == 1
    assert AuditLog.objects.count() == 0


# ------------------------------------------------------------------ tạo


def test_owner_creates_for_product_with_audit(owner_client: Client, product: Product) -> None:
    r = post(owner_client, payload(product))
    assert r.status_code == 201, r.content
    out = body(r)
    assert out["kind"] == "OCOP"
    assert out["product_id"] == product.pk
    assert out["plot_id"] is None
    assert out["is_public"] is True
    assert out["is_expired"] is False

    log = AuditLog.objects.get(entity="certificate", entity_id=out["id"])
    assert log.action == "CREATE"
    assert log.before is None
    assert log.after is not None
    assert log.after["number"] == "OCOP-2026-01"


def test_owner_creates_for_plot(owner_client: Client, plot: Plot) -> None:
    r = owner_client.post(
        URL,
        {"kind": "ORGANIC", "number": "HC-9", "plot_id": plot.pk, "is_public": False},
        content_type="application/json",
    )
    assert r.status_code == 201, r.content
    assert body(r)["plot_id"] == plot.pk
    assert body(r)["is_public"] is False


@pytest.mark.parametrize(
    "overrides",
    [
        {"product_id": None, "plot_id": None},  # không có đích
        {"plot_id": "BOTH"},  # cả hai đích (điền plot thật ở test)
    ],
)
def test_requires_exactly_one_target(
    owner_client: Client, product: Product, plot: Plot, overrides: dict[str, Any]
) -> None:
    overrides = {k: (plot.pk if v == "BOTH" else v) for k, v in overrides.items()}
    r = post(owner_client, payload(product, **overrides))
    assert r.status_code == 400
    assert body(r)["code"] == "CERTIFICATE_TARGET_INVALID"
    assert body(r)["details"]["field"] == "product_id"
    assert Certificate.objects.count() == 0


def test_rejects_expiry_before_issue(owner_client: Client, product: Product) -> None:
    r = post(owner_client, payload(product, issued_on="2026-05-01", expires_on="2026-04-30"))
    assert r.status_code == 400
    assert body(r)["code"] == "CERTIFICATE_DATES_INVALID"
    assert body(r)["details"]["field"] == "expires_on"
    # cùng ngày thì được (hết hạn ≥ ngày cấp)
    r = post(owner_client, payload(product, issued_on="2026-05-01", expires_on="2026-05-01"))
    assert r.status_code == 201


def test_dates_optional(owner_client: Client, product: Product) -> None:
    r = post(owner_client, payload(product, issued_on=None, expires_on=None, stars=None))
    assert r.status_code == 201
    assert body(r)["is_expired"] is False


@pytest.mark.parametrize("stars", [2, 6, 0])
def test_stars_range(owner_client: Client, product: Product, stars: int) -> None:
    r = post(owner_client, payload(product, stars=stars))
    assert r.status_code == 400
    assert body(r)["code"] == "VALIDATION_ERROR"


def test_stars_only_for_ocop(owner_client: Client, product: Product) -> None:
    r = post(owner_client, payload(product, kind="FOOD_SAFETY", stars=4))
    assert r.status_code == 400
    assert body(r)["code"] == "CERTIFICATE_STARS_INVALID"


def test_rejects_unknown_kind_and_blank_number(owner_client: Client, product: Product) -> None:
    assert post(owner_client, payload(product, kind="ISO")).status_code == 400
    assert post(owner_client, payload(product, number="   ")).status_code == 400


def test_rejects_missing_product_or_plot(owner_client: Client, product: Product) -> None:
    r = post(owner_client, payload(product, product_id=999_999))
    assert (r.status_code, body(r)["code"]) == (400, "PRODUCT_INVALID")
    r = post(owner_client, payload(product, product_id=None, plot_id=999_999))
    assert (r.status_code, body(r)["code"]) == (400, "PLOT_INVALID")


@pytest.mark.parametrize(
    "file_url",
    [
        "javascript:alert(1)",
        "data:text/html;base64,PHNjcmlwdD4=",
        "http://example.com/a.pdf",
        "//evil.com/a.pdf",
        "/media/../etc/passwd",
        "/other/a.pdf",
        "https://",
    ],
)
def test_rejects_unsafe_file_url(owner_client: Client, product: Product, file_url: str) -> None:
    r = post(owner_client, payload(product, file_url=file_url))
    assert r.status_code == 400, file_url
    assert body(r)["code"] == "VALIDATION_ERROR"


@pytest.mark.parametrize("file_url", ["/media/files/cert.pdf", "https://example.com/cert.pdf"])
def test_accepts_media_or_https_file_url(
    owner_client: Client, product: Product, file_url: str
) -> None:
    r = post(owner_client, payload(product, file_url=file_url))
    assert r.status_code == 201, r.content
    assert body(r)["file_url"] == file_url


# ------------------------------------------------------------------ sửa


def test_patch_updates_and_audits(owner_client: Client, product: Product) -> None:
    cert = make_cert(product=product, is_public=True)
    r = patch(owner_client, cert.pk, {"is_public": False, "issuer": "Sở Y tế"})
    assert r.status_code == 200, r.content
    assert body(r)["is_public"] is False

    log = AuditLog.objects.get(entity="certificate", entity_id=cert.pk, action="UPDATE")
    assert log.before is not None and log.after is not None
    assert log.before["is_public"] is True
    assert log.after["is_public"] is False
    assert log.after["issuer"] == "Sở Y tế"


def test_patch_without_change_writes_no_audit(owner_client: Client, product: Product) -> None:
    cert = make_cert(product=product, is_public=True)
    assert patch(owner_client, cert.pk, {"is_public": True}).status_code == 200
    assert patch(owner_client, cert.pk, {}).status_code == 200
    assert AuditLog.objects.count() == 0


def test_patch_checks_dates_against_stored_values(owner_client: Client, product: Product) -> None:
    cert = make_cert(
        product=product,
        issued_on=datetime.date(2026, 3, 1),
        expires_on=datetime.date(2027, 3, 1),
    )
    r = patch(owner_client, cert.pk, {"expires_on": "2026-02-28"})
    assert (r.status_code, body(r)["code"]) == (400, "CERTIFICATE_DATES_INVALID")
    r = patch(owner_client, cert.pk, {"issued_on": "2027-03-02"})
    assert (r.status_code, body(r)["code"]) == (400, "CERTIFICATE_DATES_INVALID")
    cert.refresh_from_db()
    assert cert.expires_on == datetime.date(2027, 3, 1)


def test_patch_can_move_target_in_one_request(
    owner_client: Client, product: Product, plot: Plot
) -> None:
    cert = make_cert(product=product)
    # chỉ gửi plot_id thì còn hai đích
    r = patch(owner_client, cert.pk, {"plot_id": plot.pk})
    assert (r.status_code, body(r)["code"]) == (400, "CERTIFICATE_TARGET_INVALID")
    r = patch(owner_client, cert.pk, {"plot_id": plot.pk, "product_id": None})
    assert r.status_code == 200, r.content
    cert.refresh_from_db()
    assert (cert.product_id, cert.plot_id) == (None, plot.pk)
    # bỏ cả hai đích thì sai
    r = patch(owner_client, cert.pk, {"plot_id": None})
    assert (r.status_code, body(r)["code"]) == (400, "CERTIFICATE_TARGET_INVALID")


def test_patch_rejects_null_for_required_fields(owner_client: Client, product: Product) -> None:
    cert = make_cert(product=product)
    for name in ("kind", "number", "is_public"):
        r = patch(owner_client, cert.pk, {name: None})
        assert r.status_code == 400, name
        assert body(r)["code"] == "VALIDATION_ERROR"


def test_patch_clears_optional_fields(owner_client: Client, product: Product) -> None:
    cert = make_cert(kind="OCOP", product=product, stars=4, issuer="X", file_url="/media/a.pdf")
    r = patch(owner_client, cert.pk, {"stars": None, "issuer": None, "file_url": None})
    assert r.status_code == 200, r.content
    cert.refresh_from_db()
    assert (cert.stars, cert.issuer, cert.file_url) == (None, None, None)


def test_patch_stars_on_non_ocop_rejected(owner_client: Client, product: Product) -> None:
    cert = make_cert(kind="FOOD_SAFETY", product=product)
    r = patch(owner_client, cert.pk, {"stars": 4})
    assert (r.status_code, body(r)["code"]) == (400, "CERTIFICATE_STARS_INVALID")
    # đổi sang OCOP cùng lúc thì được
    r = patch(owner_client, cert.pk, {"stars": 4, "kind": "OCOP"})
    assert r.status_code == 200


def test_unknown_id_is_404(owner_client: Client) -> None:
    assert owner_client.get(f"{URL}/999999").status_code == 404
    assert patch(owner_client, 999_999, {"is_public": False}).status_code == 404


# ------------------------------------------------------------------ danh sách


def test_list_filters(owner_client: Client, product: Product, plot: Plot) -> None:
    yesterday = TODAY - datetime.timedelta(days=1)
    expired = make_cert(number="OLD", product=product, expires_on=yesterday)
    valid = make_cert(number="NEW", product=product, expires_on=TODAY)
    forever = make_cert(number="FOREVER", kind="ORGANIC", plot=plot, is_public=False)

    def ids(query: str) -> set[int]:
        r = owner_client.get(f"{URL}?{query}")
        assert r.status_code == 200
        return {item["id"] for item in body(r)["items"]}

    assert ids("") == {expired.pk, valid.pk, forever.pk}
    assert ids("active=true") == {valid.pk, forever.pk}  # hết hạn hôm nay vẫn còn hiệu lực
    assert ids("active=false") == {expired.pk}
    assert ids("kind=ORGANIC") == {forever.pk}
    assert ids(f"product_id={product.pk}") == {expired.pk, valid.pk}
    assert ids(f"plot_id={plot.pk}") == {forever.pk}
    assert ids("is_public=false") == {forever.pk}
    assert ids("q=forev") == {forever.pk}

    items = body(owner_client.get(f"{URL}?product_id={product.pk}&active=false"))["items"]
    assert items[0]["is_expired"] is True


def test_pagination(owner_client: Client, product: Product) -> None:
    for i in range(3):
        make_cert(number=f"N{i}", product=product)
    data = body(owner_client.get(f"{URL}?page=2&page_size=2"))
    assert data["total"] == 3
    assert len(data["items"]) == 1


# ------------------------------------------------------------------ service cho website


def test_active_public_for_product(product: Product, goods_type: GoodsType) -> None:
    other = make_product(goods_type, sku="TD20", slug="tinh-dau-20")
    ok_forever = make_cert(number="A", product=product)
    ok_today = make_cert(number="B", kind="OCOP", product=product, expires_on=TODAY)
    make_cert(number="HIDDEN", product=product, is_public=False)
    make_cert(number="EXPIRED", product=product, expires_on=TODAY - datetime.timedelta(days=1))
    make_cert(number="OTHER", product=other)

    result = list(active_public_for_product(product.pk))
    assert [c.pk for c in result] == [
        ok_forever.pk,
        ok_today.pk,
    ]  # sắp theo loại: FOOD_SAFETY, OCOP
    # theo ngày chỉ định: hôm sau thì chứng nhận hết hạn hôm nay không còn
    tomorrow = TODAY + datetime.timedelta(days=1)
    assert {c.number for c in active_public_for_product(product.pk, on=tomorrow)} == {"A"}
