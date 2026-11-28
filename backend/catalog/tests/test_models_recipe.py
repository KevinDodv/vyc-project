"""Ràng buộc DB và seed của ingredient, recipe, recipe_item, cột product (TK mục 4, mục 5)
cùng seed area Lào Cai + 9 xã Văn Yên cũ."""

from __future__ import annotations

import importlib
from decimal import Decimal
from typing import Any

import pytest
from django.apps import apps
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from catalog.models import (
    Area,
    AreaLevel,
    Ingredient,
    IngredientKind,
    Product,
    Recipe,
    RecipeItem,
    RecipeOutputKind,
    RecipeStatus,
)
from catalog.tests.conftest import make_product

pytestmark = pytest.mark.django_db


# ---------------------------------------------------------------- dựng dữ liệu
def make_ingredient(code: str = "ZZ", **overrides: Any) -> Ingredient:
    fields: dict[str, Any] = {
        "code": code,
        "name": f"Phụ liệu {code}",
        "kind": IngredientKind.OTHER,
    }
    fields.update(overrides)
    return Ingredient.objects.create(**fields)


def make_recipe(code: str = "ZR", version: int = 1, **overrides: Any) -> Recipe:
    fields: dict[str, Any] = {
        "code": code,
        "version": version,
        "name": f"Công thức {code}",
        "output_kind": RecipeOutputKind.PRODUCT,
        "base_batch_g": Decimal("100"),
    }
    fields.update(overrides)
    return Recipe.objects.create(**fields)


def rejects(**overrides: Any) -> None:
    """Dựng một recipe vi phạm ràng buộc, kỳ vọng DB từ chối."""
    with pytest.raises(IntegrityError), transaction.atomic():
        make_recipe("BAD", **overrides)


def seed_module(name: str) -> Any:
    return importlib.import_module(f"catalog.migrations.{name}")


# ---------------------------------------------------------------- ingredient
def test_ingredient_ma_trung() -> None:
    make_ingredient("ZZ")
    with pytest.raises(IntegrityError), transaction.atomic():
        make_ingredient("ZZ", name="Trùng mã")


@pytest.mark.parametrize("code", ["zz", "Zz", "TOOLONG", ""])
def test_ingredient_ma_phai_chu_hoa_1_6_ky_tu_o_db(code: str) -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        make_ingredient(code)


@pytest.mark.parametrize("code", ["tt1", "A-B", "A B", "TOOLONG", ""])
def test_ingredient_ma_sai_dinh_dang_full_clean(code: str) -> None:
    with pytest.raises(ValidationError) as exc:
        Ingredient(code=code, name="X", kind=IngredientKind.OTHER).full_clean()
    assert "code" in exc.value.message_dict


@pytest.mark.parametrize("code", ["ZQ", "ZT1", "ZNUOC", "ABCDEF", "A"])
def test_ingredient_ma_hop_le(code: str) -> None:
    ing = Ingredient(code=code, name="X", kind=IngredientKind.OTHER)
    ing.full_clean()  # không ném lỗi
    ing.save()


def test_ingredient_kind_va_status_ngoai_tap() -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        make_ingredient("K1", kind="LIQUID")
    with pytest.raises(IntegrityError), transaction.atomic():
        make_ingredient("K2", status="DELETED")


def test_ingredient_ty_trong_phai_duong() -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        make_ingredient("D0", density_g_ml=Decimal("0"))
    make_ingredient("D1", density_g_ml=Decimal("0.845"))
    make_ingredient("D2")  # NULL được


def test_ingredient_mac_dinh() -> None:
    ing = make_ingredient("DF")
    assert ing.track_stock is True
    assert ing.requires_coa is False
    assert ing.status == "ACTIVE"


# ---------------------------------------------------------------- recipe
def test_recipe_code_version_duy_nhat() -> None:
    make_recipe("ZR", 1, status=RecipeStatus.RETIRED)
    with pytest.raises(IntegrityError), transaction.atomic():
        make_recipe("ZR", 1, status=RecipeStatus.RETIRED)
    make_recipe("ZR", 2, status=RecipeStatus.RETIRED)  # version khác thì được


def test_recipe_moi_code_chi_mot_ban_active() -> None:
    make_recipe("ZR", 1, status=RecipeStatus.ACTIVE)
    with pytest.raises(IntegrityError), transaction.atomic():
        make_recipe("ZR", 2, status=RecipeStatus.ACTIVE)
    # DRAFT và RETIRED không bị giới hạn
    make_recipe("ZR", 2, status=RecipeStatus.DRAFT)
    make_recipe("ZR", 3, status=RecipeStatus.RETIRED)
    make_recipe("ZR", 4, status=RecipeStatus.RETIRED)
    # code khác có bản ACTIVE riêng
    make_recipe("ZS", 1, status=RecipeStatus.ACTIVE)


def test_recipe_kich_hoat_ban_moi_sau_khi_retire_ban_cu() -> None:
    old = make_recipe("ZR", 1, status=RecipeStatus.ACTIVE)
    new = make_recipe("ZR", 2, status=RecipeStatus.DRAFT)
    old.status = RecipeStatus.RETIRED
    old.save()
    new.status = RecipeStatus.ACTIVE
    new.save()
    assert Recipe.objects.filter(code="ZR", status="ACTIVE").count() == 1


def test_recipe_ban_thanh_pham_bat_buoc_co_phu_lieu_dau_ra() -> None:
    rejects(output_kind=RecipeOutputKind.INTERMEDIATE)  # thiếu output_ingredient


def test_recipe_thanh_pham_khong_duoc_co_phu_lieu_dau_ra() -> None:
    rejects(output_kind=RecipeOutputKind.PRODUCT, output_ingredient=make_ingredient("OUT"))


def test_recipe_ban_thanh_pham_hop_le() -> None:
    out = make_ingredient("OUT")
    r = make_recipe("ZR", output_kind=RecipeOutputKind.INTERMEDIATE, output_ingredient=out)
    assert out.recipes.get() == r


def test_recipe_khong_xoa_phu_lieu_dau_ra() -> None:
    out = make_ingredient("OUT")
    make_recipe("ZR", output_kind=RecipeOutputKind.INTERMEDIATE, output_ingredient=out)
    with pytest.raises(IntegrityError), transaction.atomic():
        out.delete()


@pytest.mark.parametrize("grams", [Decimal("0"), Decimal("-1")])
def test_recipe_me_chuan_phai_duong(grams: Decimal) -> None:
    rejects(base_batch_g=grams)


def test_recipe_output_kind_va_status_ngoai_tap() -> None:
    rejects(output_kind="OTHER")
    rejects(status="DELETED")


def test_recipe_version_phai_tu_1() -> None:
    rejects(version=0)


def test_recipe_ngay_u() -> None:
    rejects(cure_min_days=-1)
    rejects(cure_min_days=21, cure_max_days=14)
    make_recipe("ZR", cure_min_days=21, cure_max_days=21)
    make_recipe("ZS", cure_min_days=0)  # không ủ, cure_max NULL


def test_recipe_mac_dinh() -> None:
    r = make_recipe("ZR")
    assert r.version == 1
    assert r.cure_min_days == 0
    assert r.status == "DRAFT"
    assert r.retain_months is None


# ---------------------------------------------------------------- recipe_item
def test_recipe_item_line_no_duy_nhat_trong_recipe() -> None:
    r, ing = make_recipe("ZR"), make_ingredient("A1")
    RecipeItem.objects.create(recipe=r, line_no=1, ingredient=ing, qty_g=Decimal("10"))
    with pytest.raises(IntegrityError), transaction.atomic():
        RecipeItem.objects.create(recipe=r, line_no=1, ingredient=ing, qty_g=Decimal("5"))
    RecipeItem.objects.create(recipe=r, line_no=2, ingredient=ing, qty_g=Decimal("5"))
    # recipe khác dùng lại line_no 1
    RecipeItem.objects.create(
        recipe=make_recipe("ZS"), line_no=1, ingredient=ing, qty_g=Decimal("5")
    )


@pytest.mark.parametrize("grams", [Decimal("0"), Decimal("-0.01")])
def test_recipe_item_gram_phai_duong(grams: Decimal) -> None:
    r, ing = make_recipe("ZR"), make_ingredient("A1")
    with pytest.raises(IntegrityError), transaction.atomic():
        RecipeItem.objects.create(recipe=r, line_no=1, ingredient=ing, qty_g=grams)


def test_recipe_item_mac_dinh_va_nhom_lua_chon() -> None:
    r, ing = make_recipe("ZR"), make_ingredient("A1")
    item = RecipeItem.objects.create(recipe=r, line_no=1, ingredient=ing, qty_g=Decimal("1.5"))
    assert item.alt_group is None
    assert item.is_optional is False
    alt = RecipeItem.objects.create(
        recipe=r, line_no=2, ingredient=ing, qty_g=Decimal("2"), alt_group=1, is_optional=True
    )
    assert (alt.alt_group, alt.is_optional) == (1, True)


def test_recipe_item_khong_xoa_recipe_hay_phu_lieu_dang_dung() -> None:
    r, ing = make_recipe("ZR"), make_ingredient("A1")
    RecipeItem.objects.create(recipe=r, line_no=1, ingredient=ing, qty_g=Decimal("1"))
    with pytest.raises(IntegrityError), transaction.atomic():
        r.delete()
    with pytest.raises(IntegrityError), transaction.atomic():
        ing.delete()


# ---------------------------------------------------------------- cột product (mục 4, mục 5)
def test_product_co_du_cot_cong_thuc_va_quy_cach() -> None:
    names = {f.name for f in Product._meta.get_fields()}
    assert {
        "recipe_code",
        "shelf_life_months",
        "requires_retention_sample",
        "size_label",
        "unit",
    } <= names


def test_product_cot_moi_mac_dinh(goods_type: Any) -> None:
    p = make_product(goods_type)
    assert p.recipe_code is None
    assert p.shelf_life_months is None
    assert p.requires_retention_sample is False


# ---------------------------------------------------------------- seed phụ liệu
SEED_INGREDIENT_CODES = {
    "Q", "QM", "CAM", "TTV", "HH", "HOI", "DPG", "SD", "SO", "TC",
    "BM", "DG", "HT", "VQH", "DEC", "NUOC", "TT1", "TT2", "DDT",
}  # fmt: skip


def test_seed_du_19_phu_lieu() -> None:
    assert Ingredient.objects.count() == 19
    assert set(Ingredient.objects.values_list("code", flat=True)) == SEED_INGREDIENT_CODES


def test_seed_phu_lieu_theo_muc_4() -> None:
    by = {i.code: i for i in Ingredient.objects.all()}
    # 5 tinh dầu cần COA
    assert {c for c, i in by.items() if i.requires_coa} == {"Q", "CAM", "TTV", "HH", "HOI"}
    # chỉ nước sạch không theo dõi tồn
    assert {c for c, i in by.items() if not i.track_stock} == {"NUOC"}
    # tỷ trọng g/ml
    assert by["CAM"].density_g_ml == Decimal("0.845")
    assert by["Q"].density_g_ml == Decimal("1.05")
    assert by["DPG"].density_g_ml == Decimal("1.02")
    # dầu quế hạn 24 tháng
    assert by["Q"].shelf_life_months == 24
    assert by["QM"].shelf_life_months == 24
    assert by["TT1"].kind == IngredientKind.BLEND
    assert by["DDT"].kind == IngredientKind.BLEND
    assert by["SD"].kind == IngredientKind.WAX
    assert all(i.status == "ACTIVE" for i in by.values())
    # mã seed hợp lệ với validator
    for ing in by.values():
        ing.full_clean()


# ---------------------------------------------------------------- seed công thức
SEED_RECIPE_CODES = {
    "QC1", "QC2", "RQ1", "RQ2", "TQ1", "TQ2", "TT1", "TT2", "DDT",
    "SAP", "VTC", "TUI", "U-Q", "Q100", "SC-VQH",
}  # fmt: skip


def batch_total(recipe: Recipe) -> Decimal:
    """Σ qty_g, mỗi nhóm lựa chọn tính một phương án (TK mục 4)."""
    total = Decimal("0")
    seen_groups: set[int] = set()
    for item in recipe.items.all():
        if item.alt_group is not None:
            if item.alt_group in seen_groups:
                continue
            seen_groups.add(item.alt_group)
        total += item.qty_g
    return total


def test_seed_du_15_cong_thuc_active_version_1() -> None:
    assert Recipe.objects.count() == 15
    assert set(Recipe.objects.values_list("code", flat=True)) == SEED_RECIPE_CODES
    assert not Recipe.objects.exclude(status="ACTIVE", version=1).exists()


def test_seed_me_chuan_bang_tong_gram_cac_dong() -> None:
    for recipe in Recipe.objects.exclude(code="SC-VQH"):
        assert batch_total(recipe) == recipe.base_batch_g, recipe.code
    assert not RecipeItem.objects.filter(recipe__code="SC-VQH").exists()


def test_seed_6_cong_thuc_tinh_dau_khuech_tan() -> None:
    expected = {
        "QC1": (21, {"TTV": "31.40", "Q": "8.97", "CAM": "49.35"}),
        "QC2": (28, {"TTV": "36.87", "Q": "18.43", "CAM": "36.87"}),
        "RQ1": (21, {"HH": "9.21", "TTV": "46.07", "Q": "7.37", "CAM": "29.48"}),
        "RQ2": (28, {"HH": "14.14", "TTV": "46.18", "Q": "15.08", "CAM": "18.85"}),
        "TQ1": (21, {"TTV": "26.88", "HOI": "2.69", "Q": "8.96", "CAM": "51.07"}),
        "TQ2": (28, {"TTV": "32.17", "HOI": "4.60", "Q": "16.55", "CAM": "38.61"}),
    }
    for code, (cure, lines) in expected.items():
        r = Recipe.objects.get(code=code)
        assert r.output_kind == RecipeOutputKind.PRODUCT
        assert r.output_ingredient is None
        assert r.retain_months == 12
        assert r.cure_min_days == cure
        got = {i.ingredient.code: i.qty_g for i in r.items.select_related("ingredient")}
        assert got == {k: Decimal(v) for k, v in lines.items()}


def test_seed_ban_thanh_pham_tro_ve_phu_lieu_dau_ra() -> None:
    expected = {"TT1": "TT1", "TT2": "TT2", "DDT": "DDT", "U-Q": "Q", "SC-VQH": "VQH"}
    for code, out in expected.items():
        r = Recipe.objects.get(code=code)
        assert r.output_kind == RecipeOutputKind.INTERMEDIATE
        assert r.output_ingredient is not None
        assert r.output_ingredient.code == out
    products = Recipe.objects.filter(output_kind=RecipeOutputKind.PRODUCT)
    assert {r.code for r in products} == {
        "QC1", "QC2", "RQ1", "RQ2", "TQ1", "TQ2", "SAP", "VTC", "TUI", "Q100",
    }  # fmt: skip


def test_seed_nhom_lua_chon_tt1_hoac_tt2() -> None:
    for code in ("DDT", "SAP"):
        alt = RecipeItem.objects.filter(recipe__code=code, alt_group__isnull=False)
        assert {i.ingredient.code for i in alt} == {"TT1", "TT2"}
        assert {i.alt_group for i in alt} == {1}
    assert RecipeItem.objects.filter(alt_group__isnull=False).count() == 4


def test_seed_dong_tuy_chon_chi_bot_mau_trong_vtc() -> None:
    opt = RecipeItem.objects.filter(is_optional=True)
    assert [(i.recipe.code, i.ingredient.code) for i in opt] == [("VTC", "BM")]


def test_seed_ngay_u() -> None:
    cure = {r.code: (r.cure_min_days, r.cure_max_days) for r in Recipe.objects.all()}
    assert cure["TT1"] == (14, None)
    assert cure["TT2"] == (14, None)
    assert cure["DDT"] == (2, None)
    assert cure["SAP"] == (14, None)
    assert cure["VTC"] == (7, None)
    assert cure["TUI"] == (5, 7)
    assert cure["U-Q"] == (28, 42)
    assert cure["Q100"] == (0, None)
    assert cure["SC-VQH"] == (0, None)


def test_seed_chay_lai_khong_trung() -> None:
    for name in ("0006_seed_phu_lieu_cong_thuc", "0007_seed_area_van_yen"):
        seed_module(name).seed(apps, None)
    assert Ingredient.objects.count() == 19
    assert Recipe.objects.count() == 15
    assert RecipeItem.objects.count() == 47
    assert Area.objects.count() == 10


# ---------------------------------------------------------------- seed area
COMMUNES = {
    # code: tên (mã theo quy ước TK mục 1042: 2-3 chữ viết tắt, bỏ dấu)
    "PDH": "Phong Dụ Hạ",
    "PDT": "Phong Dụ Thượng",
    "CQ": "Châu Quế",
    "LG": "Lâm Giang",
    "DC": "Đông Cuông",
    "TH": "Tân Hợp",
    "MA": "Mậu A",
    "XA": "Xuân Ái",
    "MV": "Mỏ Vàng",
}


def test_seed_area_du_10_ban_ghi() -> None:
    assert Area.objects.count() == 10
    assert Area.objects.filter(level=AreaLevel.PROVINCE).count() == 1
    assert Area.objects.filter(level=AreaLevel.COMMUNE).count() == 9


def test_seed_area_tinh_lao_cai() -> None:
    lc = Area.objects.get(code="LC")
    assert (lc.name, lc.level, lc.parent_id, lc.status) == (
        "Lào Cai",
        AreaLevel.PROVINCE,
        None,
        "ACTIVE",
    )
    assert lc.former_name is None


def test_seed_area_moi_xa_dung_cap_va_cha() -> None:
    lc = Area.objects.get(code="LC")
    got = {a.code: a.name for a in Area.objects.filter(level=AreaLevel.COMMUNE)}
    assert got == COMMUNES
    for commune in Area.objects.filter(level=AreaLevel.COMMUNE):
        assert commune.level == AreaLevel.COMMUNE, commune.code
        assert commune.parent == lc, commune.code
        assert commune.former_name == "huyện Văn Yên, tỉnh Yên Bái", commune.code
        assert commune.status == "ACTIVE"
        commune.full_clean()  # cha đúng cấp (clean) và mã hợp lệ
    assert lc.children.count() == 9


def test_seed_area_ma_xa_theo_quy_uoc() -> None:
    for code in COMMUNES:
        assert 2 <= len(code) <= 3
        assert code.isascii()
        assert code == code.upper()
