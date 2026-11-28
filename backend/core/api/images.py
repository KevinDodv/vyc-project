"""Router `/api/v1/images` (backend.md 6.5): chỉ OWNER, theo `OWNER_ONLY` mặc định của `api_v1`."""

from __future__ import annotations

from django.http import HttpRequest
from ninja import File, Router, Schema, Status, UploadedFile

from core.images import store_image
from core.schemas import SafeMediaPath

router = Router(tags=["Ảnh"])


class ImageOut(Schema):
    """Phần tử `product.images` còn thiếu `alt`: thêm `alt` rồi PATCH vào entity."""

    url: SafeMediaPath
    key: str
    w: int
    h: int
    widths: list[int]


@router.post("", response={201: ImageOut}, summary="Tải ảnh công khai lên")
def upload_image(request: HttpRequest, file: File[UploadedFile]) -> Status:
    return Status(201, ImageOut.model_validate(store_image(file)))
