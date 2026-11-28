"""Seed địa bàn (TK mục 4, «Dữ liệu khởi tạo»): tỉnh Lào Cai và 9 xã thuộc huyện Văn Yên cũ.
Hàm ngược là noop. Chạy lại không trùng (get_or_create theo code).

Mã xã theo quy ước mục 1042 (2–3 chữ viết tắt, bỏ dấu; CQ = Châu Quế, DC = Đông Cuông); dùng làm
đầu mã NCC-<mã xã>-NNN và D-<mã xã>-<số NCC>-NN. Thôn do chủ doanh nghiệp nhập.

Cha đúng cấp của area chỉ kiểm ở Area.clean(), không ở DB, nên seed này gán parent tường minh.
"""

from django.db import migrations

PROVINCE = ("LC", "Lào Cai")
FORMER_NAME = "huyện Văn Yên, tỉnh Yên Bái"
COMMUNES = [
    # (code, name)
    ("PDH", "Phong Dụ Hạ"),
    ("PDT", "Phong Dụ Thượng"),
    ("CQ", "Châu Quế"),
    ("LG", "Lâm Giang"),
    ("DC", "Đông Cuông"),
    ("TH", "Tân Hợp"),
    ("MA", "Mậu A"),
    ("XA", "Xuân Ái"),
    ("MV", "Mỏ Vàng"),
]


def seed(apps, schema_editor):
    Area = apps.get_model("catalog", "Area")
    province, _ = Area.objects.get_or_create(
        code=PROVINCE[0], defaults={"level": "PROVINCE", "name": PROVINCE[1]}
    )
    for code, name in COMMUNES:
        Area.objects.get_or_create(
            code=code,
            defaults={
                "level": "COMMUNE",
                "name": name,
                "parent": province,
                "former_name": FORMER_NAME,
            },
        )


class Migration(migrations.Migration):
    dependencies = [("catalog", "0006_seed_phu_lieu_cong_thuc")]

    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
