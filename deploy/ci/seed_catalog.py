"""Dữ liệu seed cho job CI `lighthouse` (frontend-seo.md 8.2). Chạy trong container backend:

    manage.py shell < deploy/ci/seed_catalog.py

Tạo 1 sản phẩm PUBLISHED slug `tinh-dau-que-van-yen-10ml` có 3 ảnh (file thật trong MEDIA_ROOT,
đúng đường dẫn mà frontend dựng: /media/img/<key>-<w>.<avif|webp>). Chạy lại được: đã có thì bỏ qua.
Chỉ dùng cho CI/dev, không bao giờ cho prod. Ảnh sinh bằng Pillow nên repo không phải chứa nhị phân.
"""

from pathlib import Path

from django.conf import settings
from PIL import Image

from accounts.models import User
from catalog.models import GoodsType, Product
from catalog.services.products import (
    ProductCreate,
    ProductUpdate,
    create_product,
    update_product,
)
from core.roles import Role

SLUG = "tinh-dau-que-van-yen-10ml"
WIDTHS = [480, 960]
SOURCE_W, SOURCE_H = 1200, 900
KEYS = ["a1/a1b2c3d4e5f60718", "b2/b2c3d4e5f6071829", "c3/c3d4e5f607182930"]
COLORS = [(176, 108, 62), (140, 82, 44), (205, 150, 96)]


def make_image(key: str, color: tuple[int, int, int]) -> dict:
    base = Image.linear_gradient("L").resize((SOURCE_W, SOURCE_H))
    tint = Image.new("RGB", (SOURCE_W, SOURCE_H), color)
    shade = Image.new("RGB", (SOURCE_W, SOURCE_H), (255, 255, 255))
    picture = Image.composite(tint, shade, base.point(lambda v: 255 - v // 2))
    root = Path(settings.MEDIA_ROOT) / "img"
    for width in WIDTHS:
        height = round(width * SOURCE_H / SOURCE_W)
        resized = picture.resize((width, height))
        (root / key).parent.mkdir(parents=True, exist_ok=True)
        resized.save(root / f"{key}-{width}.webp", "WEBP", quality=60)
        resized.save(root / f"{key}-{width}.avif", "AVIF", quality=45)
    return {
        "url": f"/media/img/{key}-{WIDTHS[-1]}.webp",
        "alt": "Chai tinh dầu quế Văn Yên 10 ml",
        "key": key,
        "w": SOURCE_W,
        "h": SOURCE_H,
        "widths": WIDTHS,
    }


if Product.objects.filter(slug=SLUG).exists():
    print(f"seed: đã có sản phẩm {SLUG}, bỏ qua")
else:
    owner = User.objects.filter(role=Role.OWNER).order_by("id").first()
    if owner is None:
        raise SystemExit("seed: chưa có tài khoản OWNER (chạy create_owner trước)")
    images = [make_image(key, color) for key, color in zip(KEYS, COLORS, strict=True)]
    product = create_product(
        data=ProductCreate(
            sku="CI-TD-10",
            name="Tinh dầu quế Văn Yên 10 ml",
            slug=SLUG,
            goods_type_id=GoodsType.objects.get(code="TINH_DAU").pk,
            size_label="10 ml",
            unit="chai",
            retail_price=250000,
            featured_rank=1,
            short_desc="Tinh dầu quế chưng cất từ vỏ quế Văn Yên.",
            story_md="Quế Văn Yên được thu hái và chưng cất tại chỗ.",
            usage_md="Pha loãng trước khi dùng.",
            images=images,
        ),
        actor=owner,
    )
    update_product(product_id=product.pk, data=ProductUpdate(status="PUBLISHED"), actor=owner)
    print(f"seed: đã tạo và đăng {SLUG}")
