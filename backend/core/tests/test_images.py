"""`core.images.store_image` và `POST /api/v1/images` (backend.md 6.5)."""

from __future__ import annotations

import hashlib
import io
import struct
from pathlib import Path
from typing import Any

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from PIL import Image

from core.errors import ApiError
from core.images import MAX_BYTES, ImageRef, store_image

URL = "/api/v1/images"
EXIF_ORIENTATION = 0x0112
EXIF_MAKE = 0x010F
EXIF_GPS = 0x8825


@pytest.fixture(autouse=True)
def media_root(settings: Any, tmp_path: Path) -> Path:
    settings.MEDIA_ROOT = tmp_path
    return tmp_path


def encode(
    size: tuple[int, int], fmt: str = "JPEG", mode: str = "RGB", color: Any = 0, **options: Any
) -> bytes:
    buf = io.BytesIO()
    Image.new(mode, size, color).save(buf, format=fmt, **options)
    return buf.getvalue()


def store(data: bytes) -> ImageRef:
    return store_image(io.BytesIO(data))


def stored_files(root: Path) -> list[str]:
    return sorted(p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file())


def expected_files(ref: ImageRef) -> list[str]:
    variants = [f"img/{ref.key}-{w}.{ext}" for w in ref.widths for ext in ("avif", "webp")]
    return sorted([*variants, f"img/{ref.key}-og.jpg"])


def open_variant(root: Path, ref: ImageRef, width: int | str, ext: str) -> Image.Image:
    img = Image.open(root / "img" / f"{ref.key}-{width}.{ext}")
    img.load()
    return img


def error_code(data: bytes) -> str:
    with pytest.raises(ApiError) as info:
        store(data)
    assert info.value.status == 400
    return info.value.code


@pytest.mark.parametrize("fmt", ["JPEG", "PNG", "WEBP"])
def test_valid_image_makes_all_variants(media_root: Path, fmt: str) -> None:
    data = encode((2000, 1500), fmt)
    ref = store(data)

    digest = hashlib.sha256(data).hexdigest()
    assert ref.key == f"{digest[:2]}/{digest}"
    assert ref.url == f"/media/img/{ref.key}-1440.webp"
    assert (ref.w, ref.h, ref.widths) == (1440, 1080, [480, 960, 1440])
    assert stored_files(media_root) == expected_files(ref)
    for width, height in ((480, 360), (960, 720), (1440, 1080)):
        for ext in ("avif", "webp"):
            variant = open_variant(media_root, ref, width, ext)
            assert variant.format == ext.upper()
            assert variant.size == (width, height)


def test_widths_larger_than_original_are_skipped(media_root: Path) -> None:
    ref = store(encode((1000, 500)))
    assert (ref.w, ref.h, ref.widths) == (960, 480, [480, 960])
    assert stored_files(media_root) == expected_files(ref)


def test_image_narrower_than_smallest_width_keeps_own_width(media_root: Path) -> None:
    ref = store(encode((300, 200)))
    assert (ref.w, ref.h, ref.widths) == (300, 200, [300])
    for ext in ("avif", "webp"):
        assert open_variant(media_root, ref, 300, ext).size == (300, 200)
    assert stored_files(media_root) == expected_files(ref)


@pytest.mark.parametrize(
    "size", [(2000, 1500), (3000, 500), (600, 2000), (300, 200)], ids=["to", "dai", "cao", "nho"]
)
def test_og_card_is_always_1200_by_630_jpeg(media_root: Path, size: tuple[int, int]) -> None:
    og = open_variant(media_root, store(encode(size)), "og", "jpg")
    assert (og.format, og.mode, og.size) == ("JPEG", "RGB", (1200, 630))


def test_og_card_is_cropped_from_the_centre(media_root: Path) -> None:
    source = Image.new("RGB", (2400, 630), "red")
    source.paste((0, 0, 255), (600, 0, 1800, 630))  # giữa xanh, hai mép đỏ
    buf = io.BytesIO()
    source.save(buf, format="PNG")
    og = open_variant(media_root, store(buf.getvalue()), "og", "jpg")
    for x in (10, 600, 1190):
        pixel = og.getpixel((x, 315))
        assert isinstance(pixel, tuple)
        assert pixel[0] < 20 and pixel[2] > 235


def test_og_card_puts_transparent_pixels_on_white(media_root: Path) -> None:
    ref = store(encode((500, 400), "PNG", "RGBA", (0, 0, 0, 0)))
    og = open_variant(media_root, ref, "og", "jpg")
    assert og.getpixel((600, 315)) == (255, 255, 255)


def test_same_content_uploaded_twice_is_idempotent(media_root: Path) -> None:
    data = encode((500, 400))
    first = store(data)
    files = stored_files(media_root)
    assert store(data) == first
    assert stored_files(media_root) == files  # không đẻ thêm file, không sót file tạm


def test_exif_rotation_applied_and_metadata_removed(media_root: Path) -> None:
    exif = Image.Exif()
    exif[EXIF_ORIENTATION] = 6  # xoay 90 độ
    exif[EXIF_MAKE] = "SECRETCAM"
    exif.get_ifd(EXIF_GPS).update({1: "N", 2: (21.0, 52.0, 30.0), 3: "E", 4: (104.0, 40.0, 0.0)})
    xmp = b"<x:xmpmeta xmlns:x='adobe:ns:meta/'>SECRETXMP</x:xmpmeta>"
    data = encode((1000, 600), exif=exif, xmp=xmp, comment=b"SECRETNOTE")
    with Image.open(io.BytesIO(data)) as source:
        assert source.getexif().get_ifd(EXIF_GPS)  # ảnh thử thật sự có GPS
    assert b"SECRETXMP" in data

    ref = store(data)

    assert (ref.w, ref.h, ref.widths) == (480, 800, [480])  # sau xoay rộng 600
    outputs: list[tuple[int | str, str, tuple[int, int]]] = [
        (480, "avif", (480, 800)),
        (480, "webp", (480, 800)),
        ("og", "jpg", (1200, 630)),
    ]
    for width, ext, size in outputs:
        variant = open_variant(media_root, ref, width, ext)
        assert variant.size == size
        assert not variant.getexif()
        assert "exif" not in variant.info
        assert "xmp" not in variant.info
        assert "comment" not in variant.info
        raw = (media_root / "img" / f"{ref.key}-{width}.{ext}").read_bytes()
        for secret in (b"SECRETCAM", b"SECRETXMP", b"SECRETNOTE"):
            assert secret not in raw


@pytest.mark.parametrize(
    ("orientation", "red_corner"),
    [
        (1, (0, 0)),
        (2, (1, 0)),
        (3, (1, 1)),
        (4, (0, 1)),
        (5, (0, 0)),
        (6, (1, 0)),
        (7, (1, 1)),
        (8, (0, 1)),
    ],
)
def test_every_exif_orientation_is_applied(
    media_root: Path, orientation: int, red_corner: tuple[int, int]
) -> None:
    source = Image.new("RGB", (400, 300), "blue")
    source.paste((255, 0, 0), (0, 0, 100, 100))  # góc trên trái đỏ
    exif = Image.Exif()
    exif[EXIF_ORIENTATION] = orientation
    buf = io.BytesIO()
    source.save(buf, format="PNG", exif=exif)

    ref = store(buf.getvalue())

    assert (ref.w, ref.h) == ((300, 400) if orientation >= 5 else (400, 300))
    variant = open_variant(media_root, ref, ref.w, "webp")
    right, bottom = red_corner
    pixel = variant.getpixel((ref.w - 20 if right else 20, ref.h - 20 if bottom else 20))
    assert isinstance(pixel, tuple)
    assert pixel[0] > 200 and pixel[2] < 60


def test_broken_exif_does_not_break_upload(media_root: Path) -> None:
    # IFD khai 3 thẻ nhưng cụt: chỉ có thẻ Orientation = 6 đọc được.
    exif = bytes.fromhex("4578696600004d4d002a0000000800030112000300000001000600008769")
    with pytest.warns(UserWarning, match="EXIF"):
        ref = store(encode((600, 400), exif=exif))
    assert (ref.w, ref.h) == (400, 600)


@pytest.mark.parametrize("error", [TypeError, struct.error])
def test_decoder_crash_becomes_image_invalid(
    media_root: Path, monkeypatch: pytest.MonkeyPatch, error: type[Exception]
) -> None:
    def boom(self: Image.Image) -> None:
        raise error("EXIF lạ")

    data = encode((20, 20))
    monkeypatch.setattr(Image.Image, "getexif", boom)
    assert error_code(data) == "IMAGE_INVALID"
    assert stored_files(media_root) == []


def test_icc_profile_is_kept(media_root: Path) -> None:
    from PIL import ImageCms

    icc = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
    ref = store(encode((500, 400), icc_profile=icc))
    for width, ext in ((480, "avif"), (480, "webp"), ("og", "jpg")):
        assert open_variant(media_root, ref, width, ext).info["icc_profile"] == icc


@pytest.mark.parametrize(
    ("mode", "color"), [("RGBA", (200, 100, 50, 0)), ("LA", (100, 0)), ("P", 0)]
)
def test_transparency_is_kept(media_root: Path, mode: str, color: Any) -> None:
    options = {"transparency": 0} if mode == "P" else {}
    ref = store(encode((500, 400), "PNG", mode, color, **options))
    for ext in ("avif", "webp"):
        variant = open_variant(media_root, ref, 480, ext).convert("RGBA")
        assert variant.getchannel("A").getextrema() == (0, 0)


@pytest.mark.parametrize(
    ("fmt", "mode", "color", "expected"),
    [
        ("PNG", "I;16", 32768, 128),  # xám 16 bit không được thành trắng
        ("PNG", "L", 128, 128),
        ("JPEG", "CMYK", (0, 0, 0, 127), 128),
    ],
)
def test_other_colour_modes_become_rgb(
    media_root: Path, fmt: str, mode: str, color: Any, expected: int
) -> None:
    ref = store(encode((500, 400), fmt, mode, color))
    variant = open_variant(media_root, ref, 480, "webp")
    assert variant.mode == "RGB"
    pixel = variant.getpixel((10, 10))
    assert isinstance(pixel, tuple)
    assert all(abs(channel - expected) <= 3 for channel in pixel)


def test_multi_picture_jpeg_from_phones_is_accepted() -> None:
    buf = io.BytesIO()
    frame = Image.new("RGB", (500, 400))
    frame.save(buf, format="MPO", save_all=True, append_images=[frame.copy()])
    assert store(buf.getvalue()).widths == [480]


@pytest.mark.parametrize(
    "data",
    [
        b"",
        b"khong phai anh",
        b"<svg xmlns='http://www.w3.org/2000/svg'/>",
        encode((20, 20), "GIF"),
        encode((20, 20), "BMP"),
        encode((20, 20), "TIFF"),
        encode((600, 400))[:200],  # JPEG cụt
        encode((600, 400), "PNG")[:60],  # PNG cụt
    ],
    ids=["rong", "chu", "svg", "gif", "bmp", "tiff", "jpeg-cut", "png-cut"],
)
def test_wrong_or_broken_file_is_rejected(media_root: Path, data: bytes) -> None:
    assert error_code(data) == "IMAGE_INVALID"
    assert stored_files(media_root) == []


def test_over_10_mb_is_rejected(media_root: Path) -> None:
    data = encode((20, 20))
    assert error_code(data + b"\0" * (MAX_BYTES - len(data) + 1)) == "IMAGE_TOO_LARGE"
    assert stored_files(media_root) == []


def test_exactly_10_mb_is_accepted() -> None:
    data = encode((20, 20))
    assert store(data + b"\0" * (MAX_BYTES - len(data))).widths == [20]


@pytest.mark.parametrize(
    "size",
    [(8000, 5001), (10000, 8001)],  # trên 40 triệu (warning) và trên 80 triệu (error)
    ids=["warning", "error"],
)
def test_too_many_pixels_is_rejected(media_root: Path, size: tuple[int, int]) -> None:
    previous, Image.MAX_IMAGE_PIXELS = Image.MAX_IMAGE_PIXELS, None
    try:
        data = encode(size, "PNG", "1")
    finally:
        Image.MAX_IMAGE_PIXELS = previous
    assert error_code(data) == "IMAGE_TOO_LARGE"
    assert stored_files(media_root) == []


def test_pixel_limit_is_set_on_pillow() -> None:
    assert Image.MAX_IMAGE_PIXELS == 40_000_000


def test_too_tall_output_is_rejected(media_root: Path) -> None:
    assert error_code(encode((100, 10001), "PNG", "1")) == "IMAGE_TOO_LARGE"
    assert stored_files(media_root) == []


# ------------------------------------------------------------------ API


def upload(client: Client, data: bytes, name: str = "anh.jpg") -> Any:
    return client.post(URL, {"file": SimpleUploadedFile(name, data, "image/jpeg")})


@pytest.mark.parametrize("fmt", ["JPEG", "PNG", "WEBP"])
def test_api_owner_uploads(owner_client: Client, media_root: Path, fmt: str) -> None:
    response = upload(owner_client, encode((1600, 1200), fmt), name="../../x.php")

    assert response.status_code == 201, response.content
    body = response.json()
    assert set(body) == {"url", "key", "w", "h", "widths"}
    assert body["url"] == f"/media/img/{body['key']}-1440.webp"
    assert (body["w"], body["h"], body["widths"]) == (1440, 1080, [480, 960, 1440])
    assert (media_root / body["url"].removeprefix("/media/")).is_file()
    assert all(name.startswith("img/") for name in stored_files(media_root))


def test_api_result_plus_alt_patches_product_and_shows_publicly(
    owner_client: Client, media_root: Path
) -> None:
    """Đi hết qua HTTP vì `core` không được import `catalog`, `website`."""

    def send(method: str, url: str, payload: dict[str, Any]) -> Any:
        call = getattr(owner_client, method)
        response = call(url, payload, content_type="application/json")
        assert response.status_code in (200, 201), response.content
        return response.json()

    goods_types = owner_client.get("/api/v1/goods-types").json()
    goods_type_id = next(g["id"] for g in goods_types if g["code"] == "TINH_DAU")
    product = send(
        "post",
        "/api/v1/products",
        {
            "sku": "TD10",
            "name": "Tinh dầu quế 10 ml",
            "slug": "tinh-dau-que-10ml",
            "goods_type_id": goods_type_id,
            "size_label": "10 ml",
            "unit": "chai",
            "retail_price": 250000,
        },
    )
    # Ảnh nhỏ hơn 480 px cũng phải PATCH được (widths không rỗng).
    uploaded = upload(owner_client, encode((300, 200))).json()
    image = {**uploaded, "alt": "Chai tinh dầu quế"}

    send("patch", f"/api/v1/products/{product['id']}", {"images": [image], "status": "PUBLISHED"})
    public = owner_client.get("/api/public/products/tinh-dau-que-10ml").json()

    assert public["images"] == [image]
    assert public["og_image"] == f"/media/img/{uploaded['key']}-og.jpg"
    for url in (public["images"][0]["url"], public["og_image"]):
        assert (media_root / url.removeprefix("/media/")).is_file()


def test_api_write_without_csrf_is_blocked(owner: Any, media_root: Path) -> None:
    client = Client(enforce_csrf_checks=True)
    client.force_login(owner)

    response = upload(client, encode((500, 400)))
    assert response.status_code == 403
    assert response.json()["code"] == "CSRF_FAILED"
    assert stored_files(media_root) == []

    token = "a" * 32
    client.cookies["csrftoken"] = token
    response = client.post(
        URL,
        {"file": SimpleUploadedFile("anh.jpg", encode((500, 400)), "image/jpeg")},
        headers={"X-CSRFToken": token},
    )
    assert response.status_code == 201, response.content


@pytest.mark.parametrize(
    ("data", "code"),
    [(b"khong phai anh", "IMAGE_INVALID"), (b"\0" * (MAX_BYTES + 1), "IMAGE_TOO_LARGE")],
    ids=["sai-loai", "qua-10mb"],
)
def test_api_bad_file_returns_400(owner_client: Client, data: bytes, code: str) -> None:
    response = upload(owner_client, data)
    assert response.status_code == 400
    assert response.json()["code"] == code
    assert response.json()["details"]["field"] == "file"


def test_api_missing_file_returns_400(owner_client: Client) -> None:
    response = owner_client.post(URL, {})
    assert response.status_code == 400
    assert response.json()["code"] == "VALIDATION_ERROR"


def test_api_workshop_is_forbidden(workshop_client: Client, media_root: Path) -> None:
    response = upload(workshop_client, encode((500, 400)))
    assert response.status_code == 403
    assert response.json()["code"] == "FORBIDDEN"
    assert stored_files(media_root) == []


@pytest.mark.django_db
def test_api_anonymous_is_unauthenticated(client: Client, media_root: Path) -> None:
    assert upload(client, encode((500, 400))).status_code == 401
    assert stored_files(media_root) == []
