"""Seed loại hàng hóa (TK mục 4, ghi chú cột goods_type.name). Hàm ngược là noop."""

from django.db import migrations

# (code, name, grp, is_food). Chỉ Trà đánh dấu is_food theo AC-17; chủ DN chốt thêm sau.
GOODS_TYPES = [
    ("QUE_NL", "Nguyên liệu quế", "MATERIAL", False),
    ("TINH_DAU", "Tinh dầu", "PRODUCT", False),
    ("TUI_THOM", "Túi thơm", "PRODUCT", False),
    ("TRA", "Trà", "PRODUCT", True),
    ("BOT", "Bột", "PRODUCT", False),
    ("ONG_QUE", "Ống quế", "PRODUCT", False),
    ("QUE_KHO_XK", "Quế khô XK", "PRODUCT", False),
]


def seed(apps, schema_editor):
    GoodsType = apps.get_model("catalog", "GoodsType")
    for code, name, grp, is_food in GOODS_TYPES:
        GoodsType.objects.get_or_create(
            code=code, defaults={"name": name, "grp": grp, "is_food": is_food}
        )


class Migration(migrations.Migration):
    dependencies = [("catalog", "0001_initial")]

    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
