"""Ảnh công khai tải lên: kiểm, xoay theo EXIF, bỏ metadata, sinh AVIF, WebP và JPEG OG (6.5).

Chỉ dành cho ảnh được phép nằm dưới `/media/`. Ảnh nội bộ (chứng từ, COA) không đi qua đây.
"""

from __future__ import annotations

import hashlib
import io
import os
import struct
import tempfile
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import IO, Any

from django.conf import settings
from PIL import ExifTags, Image, ImageOps

from core.errors import ApiError

MAX_BYTES = 10 * 1024 * 1024
MAX_PIXELS = 40_000_000
MAX_HEIGHT = 10_000  # khớp giới hạn `h` của schema ảnh sản phẩm; WebP cũng không quá 16383
WIDTHS = (480, 960, 1440)
OUTPUTS: tuple[tuple[str, str, int], ...] = (("avif", "AVIF", 60), ("webp", "WEBP", 80))
OG_SIZE = (1200, 630)  # ảnh chia sẻ mạng xã hội (backend.md 8.2)
# Giá trị thẻ EXIF Orientation -> phép biến đổi để ảnh đứng đúng chiều.
ORIENTATIONS = {
    2: Image.Transpose.FLIP_LEFT_RIGHT,
    3: Image.Transpose.ROTATE_180,
    4: Image.Transpose.FLIP_TOP_BOTTOM,
    5: Image.Transpose.TRANSPOSE,
    6: Image.Transpose.ROTATE_270,
    7: Image.Transpose.TRANSVERSE,
    8: Image.Transpose.ROTATE_90,
}

Image.MAX_IMAGE_PIXELS = MAX_PIXELS


@dataclass(frozen=True)
class ImageRef:
    """Phần tử của `product.images`, `plot.photo_urls`, trừ `alt` (người dùng nhập ở form).

    `url`, `w`, `h` là của bản WebP lớn nhất.
    """

    url: str
    key: str
    w: int
    h: int
    widths: list[int]


def _too_large(message: str) -> ApiError:
    return ApiError("IMAGE_TOO_LARGE", message, field="file")


def _input_formats() -> list[str]:
    """Chỉ mở đúng các bộ giải mã này. HEIC chỉ có khi Pillow được cài thêm bộ đọc HEIF."""
    Image.init()
    return ["JPEG", "PNG", "WEBP"] + [name for name in ("HEIF",) if name in Image.OPEN]


def _normalize(source: Image.Image) -> tuple[Image.Image, bytes | None]:
    """Ảnh đã xoay đúng chiều, RGB hoặc RGBA, không còn metadata; kèm ICC profile giữ màu."""
    # Không dùng ImageOps.exif_transpose: nó ghi lại khối EXIF (đằng nào cũng bỏ) nên ảnh chụp
    # có EXIF lỗi sẽ làm nó văng TypeError, struct.error.
    source.load()  # PNG có thể để EXIF sau dữ liệu ảnh
    method = ORIENTATIONS.get(source.getexif().get(ExifTags.Base.Orientation, 1))
    img = source if method is None else source.transpose(method)
    if img.mode.startswith("I"):  # PNG xám 16 bit: convert thẳng thì cắt thành trắng
        img = img.point(lambda value: value / 256).convert("L")
    # ICC chỉ còn đúng khi không đổi hệ màu (CMYK, xám đổi sang RGB thì bỏ).
    icc = img.info.get("icc_profile") if img.mode in ("RGB", "RGBA") else None
    out = img.convert("RGBA" if img.has_transparency_data else "RGB")
    out.info.clear()  # EXIF (GPS), XMP: bộ ghi AVIF/WebP không được thấy
    return out, icc


def _decode(data: bytes) -> tuple[Image.Image, bytes | None]:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(data), formats=_input_formats()) as source:
                width, height = source.size  # kiểm trước khi giải nén
                if width * height > MAX_PIXELS:
                    raise _too_large("Ảnh quá 40 triệu điểm ảnh, hãy thu nhỏ rồi tải lại")
                return _normalize(source)
    except (Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        raise _too_large("Ảnh quá 40 triệu điểm ảnh, hãy thu nhỏ rồi tải lại") from exc
    except (OSError, ValueError, SyntaxError, TypeError, struct.error) as exc:  # sai loại, hỏng
        raise ApiError(
            "IMAGE_INVALID",
            "File không phải ảnh JPEG, PNG, WebP hoặc đã hỏng",
            field="file",
        ) from exc


def _save(img: Image.Image, path: Path, **options: Any) -> None:
    """Ghi qua file tạm rồi đổi tên: Caddy không bao giờ đọc phải file ghi dở."""
    if path.exists():  # tên theo băm nội dung nên file đã có là đúng nội dung
        return
    handle, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(handle, "wb") as out:
            img.save(out, **options)
        os.chmod(tmp, 0o644)  # mkstemp tạo 0600; Caddy cần đọc được
        os.replace(tmp, path)
    finally:
        Path(tmp).unlink(missing_ok=True)


def _og_card(img: Image.Image) -> Image.Image:
    """Cắt giữa đúng 1200x630 (ảnh nhỏ thì phóng lên). JPEG không có alpha nên lót nền trắng."""
    card = ImageOps.fit(img, OG_SIZE, Image.Resampling.LANCZOS)
    if card.mode != "RGBA":
        return card
    background = Image.new("RGB", card.size, "white")
    background.paste(card, mask=card.getchannel("A"))
    return background


def store_image(file: IO[bytes]) -> ImageRef:
    """Lưu `MEDIA_ROOT/img/<2 ký tự>/<sha256>-<w>.<avif|webp>` và `<sha256>-og.jpg`.

    Ảnh hẹp hơn 480 px chỉ có một bản, giữ nguyên bề rộng gốc. Bản OG sinh cho mọi ảnh vì DTO công
    khai trỏ tới nó theo ảnh đầu, mà thứ tự ảnh đổi được sau khi tải lên.
    """
    data = file.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise _too_large("Ảnh quá 10 MB, hãy giảm dung lượng rồi tải lại")
    img, icc = _decode(data)

    widths = [w for w in WIDTHS if w <= img.width] or [img.width]
    sizes = [(w, max(1, round(img.height * w / img.width))) for w in widths]
    largest_w, largest_h = sizes[-1]
    if largest_h > MAX_HEIGHT:
        raise _too_large("Ảnh quá dài so với bề ngang, hãy cắt bớt rồi tải lại")

    digest = hashlib.sha256(data).hexdigest()
    key = f"{digest[:2]}/{digest}"
    base = Path(settings.MEDIA_ROOT) / "img"
    (base / digest[:2]).mkdir(parents=True, exist_ok=True)
    for size in sizes:
        resized = img if size == img.size else img.resize(size, Image.Resampling.LANCZOS)
        for ext, fmt, quality in OUTPUTS:
            path = base / f"{key}-{size[0]}.{ext}"
            _save(resized, path, format=fmt, quality=quality, icc_profile=icc)
    og_path = base / f"{key}-og.jpg"
    _save(_og_card(img), og_path, format="JPEG", quality=85, icc_profile=icc)

    return ImageRef(
        url=f"{settings.MEDIA_URL}img/{key}-{largest_w}.webp",
        key=key,
        w=largest_w,
        h=largest_h,
        widths=widths,
    )
