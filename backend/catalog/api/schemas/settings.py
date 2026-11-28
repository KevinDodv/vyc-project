"""Schema `/api/v1/settings` (TK mục 13). Khoá và mặc định: `catalog.services.settings.DEFAULTS`."""

from __future__ import annotations

from typing import Any, Literal

from ninja import Schema
from pydantic import ConfigDict, Field, model_validator


class LabelSize(Schema):
    width_mm: int = Field(ge=10, le=200)
    height_mm: int = Field(ge=10, le=200)


class SettingsOut(Schema):
    scan_warning_threshold: int
    price_deviation_pct: int
    label_size: LabelSize
    print_format: Literal["A5", "THERMAL_80"]
    retain_default_months: int


class SettingsPatch(Schema):
    """Chỉ đổi khoá có trong body. Khoá lạ thì 400; `null` không hợp lệ cho khoá nào."""

    model_config = ConfigDict(extra="forbid")

    scan_warning_threshold: int | None = Field(None, ge=1, le=10000)
    price_deviation_pct: int | None = Field(None, ge=1, le=100)
    label_size: LabelSize | None = None
    print_format: Literal["A5", "THERMAL_80"] | None = None
    retain_default_months: int | None = Field(None, ge=1, le=120)

    @model_validator(mode="after")
    def _reject_null(self) -> SettingsPatch:
        for name in self.model_fields_set:
            if getattr(self, name) is None:
                raise ValueError(f"{name} không được để trống")
        return self

    def changes(self) -> dict[str, Any]:
        return self.model_dump(exclude_unset=True)
