"""Seed giá trị mặc định của setting (TK mục 13); không ghi đè giá trị đã chỉnh."""

from django.db import migrations

# Giữ trùng với catalog/services/settings.py (DEFAULTS): migration không import code ứng dụng.
DEFAULTS = {
    "scan_warning_threshold": 20,
    "price_deviation_pct": 20,
    "label_size": {"width_mm": 40, "height_mm": 30},
    "print_format": "A5",
    "retain_default_months": 12,
}


def seed(apps, schema_editor):
    Setting = apps.get_model("core", "Setting")
    for key, value in DEFAULTS.items():
        Setting.objects.get_or_create(key=key, defaults={"value": value})


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed, migrations.RunPython.noop),
    ]
