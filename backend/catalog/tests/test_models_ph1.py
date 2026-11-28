"""Ràng buộc DB và seed của các bảng PH1: area, material, grade, price, supplier, plot,
farm_log, customer, certificate (TK mục 4, mục 5)."""

from __future__ import annotations

import datetime
from decimal import Decimal
from typing import Any

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from accounts.models import User
from catalog.models import (
    Area,
    AreaLevel,
    Certificate,
    Customer,
    CustomerKind,
    FarmLog,
    Grade,
    Material,
    Plot,
    Price,
    Supplier,
    SupplierKind,
    SupplierStream,
)
from catalog.tests.conftest import make_product
from core.models import CodeCounter
from core.timeutil import today_vn

pytestmark = pytest.mark.django_db


# ---------------------------------------------------------------- dựng dữ liệu
def make_area(code: str, level: str, name: str, parent: Area | None = None) -> Area:
    return Area.objects.create(code=code, level=level, name=name, parent=parent)


@pytest.fixture
def province(db: None) -> Area:
    return Area.objects.get(code="LC")  # đã seed ở migration 0007


@pytest.fixture
def commune(province: Area) -> Area:
    return Area.objects.get(code="CQ")  # đã seed ở migration 0007


@pytest.fixture
def village(commune: Area) -> Area:
    return make_area("CQ-T3", AreaLevel.VILLAGE, "Thôn 3", commune)


def make_supplier(area: Area, code: str = "NCC-CQ-001", **overrides: Any) -> Supplier:
    fields: dict[str, Any] = {
        "code": code,
        "name": "Nguyễn Văn A",
        "kind": SupplierKind.FARMER,
        "area": area,
        "stream": SupplierStream.CONTROLLED,
    }
    fields.update(overrides)
    return Supplier.objects.create(**fields)


def make_plot(supplier: Supplier, area: Area, code: str = "D-CQ-1-01", **overrides: Any) -> Plot:
    return Plot.objects.create(code=code, supplier=supplier, area=area, **overrides)


# ----------------------------------------------------------------------- seed
def test_seed_vat_lieu_va_hang() -> None:
    materials = {m.code: m for m in Material.objects.select_related("goods_type")}
    assert set(materials) == {"VQ", "QV"}
    assert materials["VQ"].name == "Vỏ quế"
    assert materials["QV"].name == "Quế vụn"
    assert {m.goods_type.code for m in materials.values()} == {"QUE_NL"}
    for material in materials.values():
        grades = list(material.grades.order_by("rank"))
        assert [(g.rank, g.name) for g in grades] == [(1, "Loại 1"), (2, "Loại 2"), (3, "Loại 3")]
    assert Grade.objects.count() == 6


def test_seed_khach_hang_va_bo_dem_ma() -> None:
    by_name = {c.name: c for c in Customer.objects.all()}
    assert set(by_name) == {"Khách lẻ", "Shopee", "TikTok Shop", "Lazada"}
    assert by_name["Khách lẻ"].kind == CustomerKind.RETAIL
    marketplaces = [c for c in by_name.values() if c.kind == CustomerKind.MARKETPLACE]
    assert len(marketplaces) == 3
    codes = sorted(c.code for c in by_name.values())
    assert codes == ["KH-0001", "KH-0002", "KH-0003", "KH-0004"]
    # Khách tạo sau (core.codes.customer_code) phải bắt đầu từ KH-0005.
    assert CodeCounter.objects.get(prefix="KH", period="-").last_no == 4


# ----------------------------------------------------------------------- area
def test_area_cay_tinh_xa_thon(village: Area) -> None:
    assert village.parent is not None and village.parent.parent is not None
    assert village.parent.parent.level == AreaLevel.PROVINCE
    village.full_clean()
    assert village.valid_from == datetime.date(2025, 7, 1)


def test_area_tinh_khong_duoc_co_cha(province: Area) -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        make_area("X", AreaLevel.PROVINCE, "Tỉnh X", parent=province)


@pytest.mark.parametrize("level", [AreaLevel.COMMUNE, AreaLevel.VILLAGE])
def test_area_xa_thon_bat_buoc_co_cha(level: AreaLevel) -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        make_area("X", level, "Không cha")


def test_area_cap_khong_hop_le(province: Area) -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        make_area("X", "DISTRICT", "Huyện", parent=province)


def test_area_cha_dung_cap_trong_clean(province: Area, commune: Area, village: Area) -> None:
    # Xã phải thuộc tỉnh, không thuộc xã khác.
    with pytest.raises(ValidationError) as exc:
        Area(code="X1", level=AreaLevel.COMMUNE, name="Xã lạ", parent=commune).full_clean()
    assert "parent" in exc.value.message_dict
    # Thôn phải thuộc xã, không thuộc tỉnh.
    with pytest.raises(ValidationError) as exc:
        Area(code="X2", level=AreaLevel.VILLAGE, name="Thôn lạ", parent=province).full_clean()
    assert "parent" in exc.value.message_dict
    # Tỉnh không có cha.
    with pytest.raises(ValidationError):
        Area(code="X3", level=AreaLevel.PROVINCE, name="Tỉnh lạ", parent=province).full_clean()
    # Đúng cấp thì qua.
    Area(code="X4", level=AreaLevel.VILLAGE, name="Thôn 4", parent=commune).full_clean()


def test_area_ma_trung(province: Area) -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        make_area("LC", AreaLevel.PROVINCE, "Tỉnh khác")


def test_area_khong_trung_ten_trong_cung_cha(commune: Area, village: Area) -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        make_area("CQ-T3B", AreaLevel.VILLAGE, "Thôn 3", commune)
    # Cùng tên nhưng khác cha thì được.
    other = make_area("XX", AreaLevel.COMMUNE, "Xã khác", commune.parent)
    make_area("XX-T3", AreaLevel.VILLAGE, "Thôn 3", other)


def test_area_tinh_khong_trung_ten(province: Area) -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        make_area("LC2", AreaLevel.PROVINCE, "Lào Cai")


def test_area_hieu_luc_den_khong_truoc_hieu_luc_tu(province: Area) -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        make_area("Y", AreaLevel.PROVINCE, "Tỉnh Y")
        Area.objects.filter(code="Y").update(
            valid_from=datetime.date(2025, 7, 1), valid_to=datetime.date(2025, 6, 30)
        )


def test_area_khong_xoa_cha_khi_con_con(commune: Area) -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        assert commune.parent is not None
        commune.parent.delete()


# --------------------------------------------------------- material, grade
def test_grade_bac_tu_1_den_9() -> None:
    material = Material.objects.get(code="VQ")
    for rank in (0, 10):
        with pytest.raises(IntegrityError), transaction.atomic():
            Grade.objects.create(material=material, rank=rank, name=f"Loại {rank}")
    Grade.objects.create(material=material, rank=9, name="Loại 9")


def test_grade_trung_bac_trong_cung_nguyen_lieu() -> None:
    material = Material.objects.get(code="VQ")
    with pytest.raises(IntegrityError), transaction.atomic():
        Grade.objects.create(material=material, rank=1, name="Loại 1 bis")
    # Nguyên liệu khác thì cùng bậc được (seed đã có Loại 1 của QV).
    assert Grade.objects.filter(rank=1).count() == 2


def test_material_ma_trung_va_trang_thai_sai() -> None:
    goods_type = Material.objects.get(code="VQ").goods_type
    with pytest.raises(IntegrityError), transaction.atomic():
        Material.objects.create(code="VQ", name="Trùng", goods_type=goods_type)
    with pytest.raises(IntegrityError), transaction.atomic():
        Material.objects.create(code="XX", name="X", goods_type=goods_type, status="DELETED")


def test_material_khong_xoa_khi_con_hang() -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        Material.objects.get(code="VQ").delete()


# ---------------------------------------------------------------------- price
@pytest.fixture
def grade() -> Grade:
    return Grade.objects.get(material__code="VQ", rank=1)


def test_price_tao_duoc_va_bat_buoc_nguoi_cap_nhat(grade: Grade, owner: User) -> None:
    price = Price.objects.create(
        grade=grade,
        price_date=datetime.date(2026, 11, 22),
        buy_price=100_000,
        sell_price=120_000,
        updated_by=owner,
    )
    assert price.buy_price == 100_000
    with pytest.raises(IntegrityError), transaction.atomic():
        Price.objects.create(
            grade=grade, price_date=datetime.date(2026, 11, 23), buy_price=1, sell_price=1
        )


@pytest.mark.parametrize(("buy", "sell"), [(-1, 10), (10, -1)])
def test_price_khong_am(grade: Grade, owner: User, buy: int, sell: int) -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        Price.objects.create(
            grade=grade,
            price_date=datetime.date(2026, 11, 22),
            buy_price=buy,
            sell_price=sell,
            updated_by=owner,
        )


def test_price_mot_gia_moi_hang_moi_ngay(grade: Grade, owner: User) -> None:
    kwargs: dict[str, Any] = {"price_date": datetime.date(2026, 11, 22), "updated_by": owner}
    Price.objects.create(grade=grade, buy_price=1, sell_price=2, **kwargs)
    with pytest.raises(IntegrityError), transaction.atomic():
        Price.objects.create(grade=grade, buy_price=3, sell_price=4, **kwargs)
    # Hạng khác cùng ngày thì được.
    other = Grade.objects.get(material__code="VQ", rank=2)
    Price.objects.create(grade=other, buy_price=3, sell_price=4, **kwargs)


def test_price_khong_xoa_hang_da_co_gia(grade: Grade, owner: User) -> None:
    Price.objects.create(
        grade=grade, price_date=datetime.date(2026, 11, 22), buy_price=1, sell_price=2,
        updated_by=owner,
    )  # fmt: skip
    with pytest.raises(IntegrityError), transaction.atomic():
        grade.delete()


# ------------------------------------------------------------------- supplier
def test_supplier_thuong_lai_chi_luong_general(commune: Area) -> None:
    make_supplier(commune, "NCC-CQ-010", kind=SupplierKind.TRADER, stream=SupplierStream.GENERAL)
    with pytest.raises(IntegrityError), transaction.atomic():
        make_supplier(
            commune, "NCC-CQ-011", kind=SupplierKind.TRADER, stream=SupplierStream.CONTROLLED
        )


@pytest.mark.parametrize(
    "overrides", [{"kind": "OTHER"}, {"stream": "OTHER"}, {"status": "DELETED"}]
)
def test_supplier_enum_sai(village: Area, overrides: dict[str, str]) -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        make_supplier(village, **overrides)


def test_supplier_ma_trung_va_mac_dinh(village: Area) -> None:
    supplier = make_supplier(village)
    assert supplier.approved is True
    assert supplier.public_consent is False
    assert supplier.status == "ACTIVE"
    with pytest.raises(IntegrityError), transaction.atomic():
        make_supplier(village)


def test_supplier_dia_ban_dung_cap_trong_clean(
    province: Area, commune: Area, village: Area
) -> None:
    make_supplier(village).full_clean()  # hộ dân ở thôn: đúng
    for area in (province, commune):
        with pytest.raises(ValidationError) as exc:
            make_supplier(area, f"NCC-{area.code}", kind=SupplierKind.FAMILY).full_clean()
        assert "area" in exc.value.message_dict
    trader = {"kind": SupplierKind.TRADER, "stream": SupplierStream.GENERAL}
    make_supplier(commune, "NCC-T1", **trader).full_clean()
    make_supplier(village, "NCC-T2", **trader).full_clean()
    with pytest.raises(ValidationError):
        make_supplier(province, "NCC-T3", **trader).full_clean()


def test_supplier_dia_ban_la_bat_buoc() -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        Supplier.objects.create(
            code="NCC-X", name="X", kind=SupplierKind.FARMER, stream=SupplierStream.GENERAL
        )


# ----------------------------------------------------------------------- plot
def test_plot_tao_duoc(village: Area) -> None:
    supplier = make_supplier(village)
    plot = make_plot(
        supplier,
        village,
        area_ha=Decimal("1.25"),
        planted_year=2015,
        lat=Decimal("21.711111"),
        lng=Decimal("104.555555"),
    )
    plot.refresh_from_db()
    assert plot.area_ha == Decimal("1.25")
    assert plot.photo_urls == []
    assert plot.is_default is False
    plot.full_clean()


@pytest.mark.parametrize("year", [1949, 2101])
def test_plot_nam_trong_ngoai_khoang_db(village: Area, year: int) -> None:
    supplier = make_supplier(village)
    with pytest.raises(IntegrityError), transaction.atomic():
        make_plot(supplier, village, planted_year=year)


def test_plot_nam_trong_bien_1950(village: Area) -> None:
    supplier = make_supplier(village)
    make_plot(supplier, village, planted_year=1950)


def test_plot_nam_trong_khong_qua_nam_nay_trong_clean(village: Area) -> None:
    supplier = make_supplier(village)
    this_year = today_vn().year
    make_plot(supplier, village, "D-1", planted_year=this_year).full_clean()
    with pytest.raises(ValidationError) as exc:
        make_plot(supplier, village, "D-2", planted_year=this_year + 1).full_clean()
    assert "planted_year" in exc.value.message_dict


def test_plot_phai_thuoc_thon_trong_clean(village: Area, commune: Area) -> None:
    supplier = make_supplier(village)
    with pytest.raises(ValidationError) as exc:
        make_plot(supplier, commune).full_clean()
    assert "area" in exc.value.message_dict


@pytest.mark.parametrize(
    "overrides",
    [
        {"lat": Decimal("90.000001")},
        {"lat": Decimal("-90.000001")},
        {"lng": Decimal("180.000001")},
        {"lng": Decimal("-180.000001")},
        {"area_ha": Decimal("-0.01")},
    ],
)
def test_plot_toa_do_va_dien_tich(village: Area, overrides: dict[str, Any]) -> None:
    supplier = make_supplier(village)
    with pytest.raises(IntegrityError), transaction.atomic():
        make_plot(supplier, village, **overrides)


def test_plot_toi_da_mot_doi_mac_dinh_moi_nguoi_ban(village: Area) -> None:
    a, b = make_supplier(village, "NCC-A"), make_supplier(village, "NCC-B")
    make_plot(a, village, "D-A1", is_default=True)
    make_plot(a, village, "D-A2")  # không mặc định: nhiều đồi được
    make_plot(a, village, "D-A3")
    with pytest.raises(IntegrityError), transaction.atomic():
        make_plot(a, village, "D-A4", is_default=True)
    make_plot(b, village, "D-B1", is_default=True)  # người bán khác có mặc định riêng


def test_plot_ma_trung(village: Area) -> None:
    supplier = make_supplier(village)
    make_plot(supplier, village)
    with pytest.raises(IntegrityError), transaction.atomic():
        make_plot(supplier, village)


def test_plot_khong_xoa_nguoi_ban_con_doi(village: Area) -> None:
    supplier = make_supplier(village)
    make_plot(supplier, village)
    with pytest.raises(IntegrityError), transaction.atomic():
        supplier.delete()


# -------------------------------------------------------------------- farm_log
def test_farm_log(village: Area) -> None:
    plot = make_plot(make_supplier(village), village)
    log = FarmLog.objects.create(
        plot=plot, log_date=datetime.date(2026, 11, 1), activity="Tỉa cành"
    )
    log.refresh_from_db()
    assert log.photo_urls == []
    assert log.note is None
    with pytest.raises(IntegrityError), transaction.atomic():
        FarmLog.objects.create(plot=plot, activity="Thiếu ngày")


# -------------------------------------------------------------------- customer
def test_customer_kind_hop_le() -> None:
    for i, kind in enumerate(CustomerKind.values):
        Customer.objects.create(code=f"KH-T{i}", name=f"Khách {kind}", kind=kind)
    with pytest.raises(IntegrityError), transaction.atomic():
        Customer.objects.create(code="KH-BAD", name="X", kind="VIP")
    with pytest.raises(IntegrityError), transaction.atomic():
        Customer.objects.create(code="KH-BAD2", name="X", kind="RETAIL", status="DELETED")


def test_customer_ma_trung() -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        Customer.objects.create(code="KH-0001", name="Trùng mã", kind="RETAIL")


# ----------------------------------------------------------------- certificate
def test_certificate_can_san_pham_hoac_doi(village: Area) -> None:
    goods_type = Material.objects.get(code="VQ").goods_type  # loại bất kỳ để dựng sản phẩm
    product = make_product(goods_type)
    plot = make_plot(make_supplier(village), village)
    Certificate.objects.create(kind="OCOP", number="OCOP-1", product=product, stars=4)
    Certificate.objects.create(kind="ORGANIC", number="HC-1", plot=plot)
    Certificate.objects.create(kind="FOOD_SAFETY", number="AT-1", product=product, plot=plot)
    with pytest.raises(IntegrityError), transaction.atomic():
        Certificate.objects.create(kind="OCOP", number="OCOP-2")


def test_certificate_kind_sai(village: Area) -> None:
    product = make_product(Material.objects.get(code="VQ").goods_type)
    with pytest.raises(IntegrityError), transaction.atomic():
        Certificate.objects.create(kind="ISO", number="X", product=product)


def test_certificate_het_han_khong_truoc_ngay_cap() -> None:
    product = make_product(Material.objects.get(code="VQ").goods_type)
    day = datetime.date(2026, 1, 10)
    Certificate.objects.create(
        kind="OCOP", number="A", product=product, issued_on=day, expires_on=day
    )
    Certificate.objects.create(kind="OCOP", number="B", product=product, expires_on=day)
    Certificate.objects.create(kind="OCOP", number="C", product=product, issued_on=day)
    with pytest.raises(IntegrityError), transaction.atomic():
        Certificate.objects.create(
            kind="OCOP",
            number="D",
            product=product,
            issued_on=day,
            expires_on=day - datetime.timedelta(days=1),
        )


@pytest.mark.parametrize("stars", [2, 6])
def test_certificate_so_sao_3_den_5(stars: int) -> None:
    product = make_product(Material.objects.get(code="VQ").goods_type)
    with pytest.raises(IntegrityError), transaction.atomic():
        Certificate.objects.create(kind="OCOP", number="S", product=product, stars=stars)


def test_certificate_mac_dinh_cong_khai() -> None:
    product = make_product(Material.objects.get(code="VQ").goods_type)
    cert = Certificate.objects.create(kind="OCOP", number="P", product=product)
    assert cert.is_public is True
