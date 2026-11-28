"""Router `/api/v1/settings` (TK mục 9: GET cả hai vai, PATCH chỉ OWNER).

Một tài nguyên duy nhất (không có id): GET trả mọi khoá, PATCH đổi một phần.
"""

from __future__ import annotations

from typing import cast

from django.http import HttpRequest
from ninja import Router

from accounts.models import User
from catalog.api.schemas.settings import SettingsOut, SettingsPatch
from catalog.services import settings as service
from core.permissions import ANY_STAFF

router = Router(tags=["Cấu hình"])


@router.get("", auth=ANY_STAFF, response=SettingsOut, summary="Cấu hình hệ thống")
def get_settings(request: HttpRequest) -> SettingsOut:
    return SettingsOut.model_validate(service.get_all())


@router.patch("", response=SettingsOut, summary="Sửa cấu hình (một phần)")
def update_settings(request: HttpRequest, payload: SettingsPatch) -> SettingsOut:
    values = service.update_settings(changes=payload.changes(), actor=cast(User, request.user))
    return SettingsOut.model_validate(values)
