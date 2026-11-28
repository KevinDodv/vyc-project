"""Seed danh mục PH1 (TK mục 4, mục 5): nguyên liệu × hạng và khách mặc định. Hàm ngược là noop.

- material: VQ Vỏ quế, QV Quế vụn (loại hàng QUE_NL, seed ở 0002); mỗi nguyên liệu 3 hạng Loại 1–3.
- customer: «Khách lẻ» và mỗi sàn một khách (Shopee, TikTok Shop, Lazada: các kênh sàn ở
  issue.channel). Mã KH-NNNN cấp theo `core.codes.customer_code`, nên bộ đếm ('KH', '-')
  phải đẩy lên cho khớp, không thì khách tạo sau sẽ trùng mã.
"""

from django.db import migrations

MATERIALS = [
    # (code, name, sort_order)
    ("VQ", "Vỏ quế", 1),
    ("QV", "Quế vụn", 2),
]
GRADE_RANKS = (1, 2, 3)

CUSTOMERS = [
    # (name, kind)
    ("Khách lẻ", "RETAIL"),
    ("Shopee", "MARKETPLACE"),
    ("TikTok Shop", "MARKETPLACE"),
    ("Lazada", "MARKETPLACE"),
]
KH_PREFIX = "KH"
KH_PERIOD = "-"  # core.codes.NO_PERIOD


def seed(apps, schema_editor):
    GoodsType = apps.get_model("catalog", "GoodsType")
    Material = apps.get_model("catalog", "Material")
    Grade = apps.get_model("catalog", "Grade")
    Customer = apps.get_model("catalog", "Customer")
    CodeCounter = apps.get_model("core", "CodeCounter")

    goods_type = GoodsType.objects.get(code="QUE_NL")
    for code, name, sort_order in MATERIALS:
        material, _ = Material.objects.get_or_create(
            code=code,
            defaults={"name": name, "goods_type": goods_type, "sort_order": sort_order},
        )
        for rank in GRADE_RANKS:
            Grade.objects.get_or_create(
                material=material, rank=rank, defaults={"name": f"Loại {rank}"}
            )

    last_no = 0
    for no, (name, kind) in enumerate(CUSTOMERS, start=1):
        code = f"KH-{no:04d}"
        Customer.objects.get_or_create(code=code, defaults={"name": name, "kind": kind})
        last_no = no
    counter, created = CodeCounter.objects.get_or_create(
        prefix=KH_PREFIX, period=KH_PERIOD, defaults={"last_no": last_no}
    )
    if not created and counter.last_no < last_no:
        counter.last_no = last_no
        counter.save(update_fields=["last_no", "updated_at"])


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0003_ph1_danh_muc"),
        ("core", "0001_initial"),
    ]

    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
