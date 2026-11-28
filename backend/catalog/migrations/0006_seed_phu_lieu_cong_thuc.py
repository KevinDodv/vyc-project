"""Seed 19 phụ liệu và 15 công thức (TK mục 4, «Seed phụ liệu và công thức»; nguồn: sổ tay sản xuất
bản 2, 17/11/2026). Hàm ngược là noop. Chạy lại không trùng (get_or_create).

- ingredient: 16 phụ liệu mua ngoài hoặc tự làm + 3 bán thành phẩm TT1, TT2, DDT. Q, QM, VQH cũng
  là bán thành phẩm (đầu ra của U-Q, chưng cất, SC-VQH) nên có bản ghi ingredient riêng.
- recipe: 6 công thức tinh dầu QC1–TQ2 (lưu mẫu 12 tháng) và TT1, TT2, DDT, SAP, VTC, TUI, U-Q,
  Q100, SC-VQH. Tất cả ACTIVE, version 1.
- CHUNG-QM (chưng cất dầu quế mới) không seed: sổ tay không mô tả (TK mục 4).
- SC-VQH không có dòng phụ liệu (đầu vào là lô quế vụn). base_batch_g cột NOT NULL > 0 nên đặt
  100 g làm mẻ danh nghĩa; không có dòng nào để cộng.
"""

from decimal import Decimal

from django.db import migrations

D = Decimal

# (code, name, kind, density g/ml, track_stock, requires_coa, shelf_life_months)
INGREDIENTS = [
    ("Q", "Dầu quế đã ủ", "ESSENTIAL_OIL", D("1.05"), True, True, 24),
    ("QM", "Dầu quế mới chưng", "ESSENTIAL_OIL", D("1.05"), True, False, 24),
    ("CAM", "Tinh dầu cam ngọt", "ESSENTIAL_OIL", D("0.845"), True, True, None),
    ("TTV", "Tinh dầu tuyết tùng Virginia", "ESSENTIAL_OIL", D("0.95"), True, True, None),
    ("HH", "Tinh dầu hoắc hương", "ESSENTIAL_OIL", D("0.96"), True, True, None),
    ("HOI", "Tinh dầu hồi", "ESSENTIAL_OIL", D("0.98"), True, True, None),
    ("DPG", "DPG loại mỹ phẩm", "SOLVENT", D("1.02"), True, False, None),
    ("SD", "Sáp đậu nành loại cột", "WAX", None, True, False, None),
    ("SO", "Sáp ong vàng đã lọc", "WAX", None, True, False, None),
    ("TC", "Bột thạch cao", "MINERAL", None, True, False, None),
    ("BM", "Bột màu khoáng nâu quế", "MINERAL", None, True, False, None),
    ("DG", "Dăm gỗ thông bào mỏng", "BOTANICAL", None, True, False, None),
    ("HT", "Hạt thạch cao 3–5 mm", "MINERAL", None, True, False, None),
    ("VQH", "Vỏ quế cắt hạt lựu 0,5–1 cm", "BOTANICAL", None, True, False, None),
    ("DEC", "Đồ trang trí sáp", "BOTANICAL", None, True, False, None),
    ("NUOC", "Nước sạch", "OTHER", None, False, False, None),
    ("TT1", "Hương nền TT1 (dầu nhẹ)", "BLEND", None, True, False, None),
    ("TT2", "Hương nền TT2 (đậm đà)", "BLEND", None, True, False, None),
    ("DDT", "Dung dịch tẩm DDT", "BLEND", None, True, False, None),
]

QC_NOTE = "Pha 100 ml, đóng chai hổ phách, ủ đủ ngày rồi mới đóng gói."

# (code, name, output_kind, output_ingredient, base_batch_g, base_label, cure_min, cure_max,
#  retain_months, note, items)
# item: (ingredient, qty_g, alt_group, is_optional, note)
RECIPES = [
    (
        "QC1",
        "Quế Cam, dầu nhẹ",
        "PRODUCT",
        None,
        D("89.72"),
        "mẻ 100 ml ≈ 89,72 g",
        21,
        None,
        12,
        QC_NOTE,
        [("TTV", D("31.40")), ("Q", D("8.97")), ("CAM", D("49.35"))],
    ),
    (
        "QC2",
        "Quế Cam, đậm đà",
        "PRODUCT",
        None,
        D("92.17"),
        "mẻ 100 ml ≈ 92,17 g",
        28,
        None,
        12,
        QC_NOTE,
        [("TTV", D("36.87")), ("Q", D("18.43")), ("CAM", D("36.87"))],
    ),
    (
        "RQ1",
        "Rừng Quế, dầu nhẹ",
        "PRODUCT",
        None,
        D("92.13"),
        "mẻ 100 ml ≈ 92,13 g",
        21,
        None,
        12,
        QC_NOTE,
        [("HH", D("9.21")), ("TTV", D("46.07")), ("Q", D("7.37")), ("CAM", D("29.48"))],
    ),
    (
        "RQ2",
        "Rừng Quế, đậm đà",
        "PRODUCT",
        None,
        D("94.25"),
        "mẻ 100 ml ≈ 94,25 g",
        28,
        None,
        12,
        QC_NOTE,
        [("HH", D("14.14")), ("TTV", D("46.18")), ("Q", D("15.08")), ("CAM", D("18.85"))],
    ),
    (
        "TQ1",
        "Tết Quế, dầu nhẹ",
        "PRODUCT",
        None,
        D("89.60"),
        "mẻ 100 ml ≈ 89,60 g",
        21,
        None,
        12,
        QC_NOTE,
        [("TTV", D("26.88")), ("HOI", D("2.69")), ("Q", D("8.96")), ("CAM", D("51.07"))],
    ),
    (
        "TQ2",
        "Tết Quế, đậm đà",
        "PRODUCT",
        None,
        D("91.93"),
        "mẻ 100 ml ≈ 91,93 g",
        28,
        None,
        12,
        QC_NOTE,
        [("TTV", D("32.17")), ("HOI", D("4.60")), ("Q", D("16.55")), ("CAM", D("38.61"))],
    ),
    (
        "TT1",
        "Hương nền TT1, dầu nhẹ",
        "INTERMEDIATE",
        "TT1",
        D("94.44"),
        None,
        14,
        None,
        None,
        "Hương nền dầu nhẹ (sổ tay tr.9).",
        [("HH", D("28.33")), ("TTV", D("42.50")), ("Q", D("9.44")), ("CAM", D("14.17"))],
    ),
    (
        "TT2",
        "Hương nền TT2, đậm đà",
        "INTERMEDIATE",
        "TT2",
        D("95.77"),
        None,
        14,
        None,
        None,
        "Hương nền đậm đà (sổ tay tr.9).",
        [("HH", D("28.73")), ("TTV", D("40.22")), ("Q", D("17.24")), ("CAM", D("9.58"))],
    ),
    (
        "DDT",
        "Dung dịch tẩm",
        "INTERMEDIATE",
        "DDT",
        D("100.00"),
        None,
        2,
        None,
        None,
        "Ủ 48 giờ (sổ tay tr.9–10). Chọn TT1 hoặc TT2.",
        [("DPG", D("65.00")), ("TT1", D("35.00"), 1), ("TT2", D("35.00"), 1)],
    ),
    (
        "SAP",
        "Sáp thơm",
        "PRODUCT",
        None,
        D("109.00"),
        "mẻ nhỏ 2 tấm sáp, ≈ 55 g/tấm",
        14,
        None,
        None,
        "Trang trí 3–5 g/tấm nhập dòng ngoài công thức (sổ tay tr.10–11). Chọn TT1 hoặc TT2.",
        [
            ("SD", D("70.00")),
            ("SO", D("30.00")),
            ("TT1", D("9.00"), 1),
            ("TT2", D("9.00"), 1),
        ],
    ),
    (
        "VTC",
        "Viên thạch cao",
        "PRODUCT",
        None,
        D("173.50"),
        "mẻ nhỏ ≈ 6 viên 20 g",
        7,
        None,
        None,
        "DDT 3 g/viên. Phơi khô 5–7 ngày trước khi tẩm, không theo dõi bằng lệnh "
        "(sổ tay tr.11–12).",
        [
            ("TC", D("100.00")),
            ("NUOC", D("55.00")),
            ("BM", D("0.50"), None, True),
            ("DDT", D("18.00")),
        ],
    ),
    (
        "TUI",
        "Túi vỏ quế",
        "PRODUCT",
        None,
        D("1100.00"),
        "40 túi 25 g",
        5,
        7,
        None,
        "DDT chỉ tẩm dăm gỗ và hạt thạch cao (sổ tay tr.12–13).",
        [
            ("VQH", D("480.00")),
            ("DG", D("320.00")),
            ("HT", D("200.00")),
            ("DDT", D("100.00")),
        ],
    ),
    (
        "U-Q",
        "Ủ dầu quế",
        "INTERMEDIATE",
        "Q",
        D("100.00"),
        None,
        28,
        42,
        None,
        "Ủ dầu quế 4–6 tuần (sổ tay tr.8). Lắng 3–5 ngày và thoát khí 7 ngày đầu làm trước, "
        "không theo dõi bằng lệnh.",
        [("QM", D("100.00"))],
    ),
    (
        "Q100",
        "Tinh dầu quế 100%",
        "PRODUCT",
        None,
        D("100.00"),
        None,
        0,
        None,
        None,
        "Đóng chai 10 ml hổ phách; hạn 24 tháng (sổ tay tr.8).",
        [("Q", D("100.00"))],
    ),
    (
        "SC-VQH",
        "Sơ chế vỏ quế cắt hạt lựu",
        "INTERMEDIATE",
        "VQH",
        D("100.00"),
        "không có dòng phụ liệu; đưa lô quế vụn vào",
        0,
        None,
        None,
        "Sơ chế: sấy rồi cắt hạt lựu. Đầu vào là lô quế (Quế vụn), không có dòng phụ liệu.",
        [],
    ),
]


def seed(apps, schema_editor):
    Ingredient = apps.get_model("catalog", "Ingredient")
    Recipe = apps.get_model("catalog", "Recipe")
    RecipeItem = apps.get_model("catalog", "RecipeItem")

    by_code = {}
    for code, name, kind, density, track_stock, requires_coa, shelf in INGREDIENTS:
        by_code[code], _ = Ingredient.objects.get_or_create(
            code=code,
            defaults={
                "name": name,
                "kind": kind,
                "density_g_ml": density,
                "track_stock": track_stock,
                "requires_coa": requires_coa,
                "shelf_life_months": shelf,
            },
        )

    for row in RECIPES:
        code, name, kind, out_code, base_g, label, cure_min, cure_max, retain, note, items = row
        recipe, created = Recipe.objects.get_or_create(
            code=code,
            version=1,
            defaults={
                "name": name,
                "output_kind": kind,
                "output_ingredient": by_code[out_code] if out_code else None,
                "base_batch_g": base_g,
                "base_label": label,
                "cure_min_days": cure_min,
                "cure_max_days": cure_max,
                "retain_months": retain,
                "status": "ACTIVE",
                "note": note,
            },
        )
        if not created:
            continue
        for line_no, item in enumerate(items, start=1):
            ing_code, qty = item[0], item[1]
            alt_group = item[2] if len(item) > 2 else None
            optional = item[3] if len(item) > 3 else False
            RecipeItem.objects.create(
                recipe=recipe,
                line_no=line_no,
                ingredient=by_code[ing_code],
                qty_g=qty,
                alt_group=alt_group,
                is_optional=optional,
            )


class Migration(migrations.Migration):
    dependencies = [("catalog", "0005_ph1_phu_lieu_cong_thuc")]

    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
