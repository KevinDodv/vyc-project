/** Logic thuần của màn /quan-ly/cai-dat (TK mục 13, `GET/PATCH /api/v1/settings`).
 *  Giới hạn khớp `SettingsPatch` ở backend; khoá lạ bị API từ chối nên chỉ gửi đúng các khoá này. */

import type { components } from "../../api/v1";
import type { FieldErrors } from "../form";

export type Settings = components["schemas"]["SettingsOut"];
export type PrintFormat = Settings["print_format"];

export const PRINT_FORMAT_OPTIONS: ReadonlyArray<{ value: PrintFormat; label: string }> = [
  { value: "A5", label: "Giấy A5" },
  { value: "THERMAL_80", label: "Giấy nhiệt 80 mm" },
];

export type NumericKey =
  | "scan_warning_threshold"
  | "price_deviation_pct"
  | "retain_default_months"
  | "label_width_mm"
  | "label_height_mm";

export const SETTINGS_LIMITS: Record<NumericKey, { label: string; min: number; max: number }> = {
  scan_warning_threshold: { label: "Ngưỡng cảnh báo quét", min: 1, max: 10000 },
  price_deviation_pct: { label: "Ngưỡng lệch giá (%)", min: 1, max: 100 },
  retain_default_months: { label: "Số tháng giữ mẫu mặc định", min: 1, max: 120 },
  label_width_mm: { label: "Chiều rộng tem (mm)", min: 10, max: 200 },
  label_height_mm: { label: "Chiều cao tem (mm)", min: 10, max: 200 },
};

export type SettingsInput = Record<NumericKey, string> & { print_format: string };

export type SettingsBody = {
  scan_warning_threshold: number;
  price_deviation_pct: number;
  retain_default_months: number;
  label_size: { width_mm: number; height_mm: number };
  print_format: PrintFormat;
};

export type SettingsResult = { ok: true; body: SettingsBody } | { ok: false; errors: FieldErrors };

export function settingsToInput(settings: Settings): SettingsInput {
  return {
    scan_warning_threshold: String(settings.scan_warning_threshold),
    price_deviation_pct: String(settings.price_deviation_pct),
    retain_default_months: String(settings.retain_default_months),
    label_width_mm: String(settings.label_size.width_mm),
    label_height_mm: String(settings.label_size.height_mm),
    print_format: settings.print_format,
  };
}

/** Kiểm từng ô số nguyên trong khoảng cho phép rồi gom `label_size` thành đối tượng lồng nhau như API đòi. */
export function buildSettingsBody(input: SettingsInput): SettingsResult {
  const errors: FieldErrors = {};
  const num = {} as Record<NumericKey, number>;
  for (const key of Object.keys(SETTINGS_LIMITS) as NumericKey[]) {
    const { label, min, max } = SETTINGS_LIMITS[key];
    const raw = input[key].trim();
    if (!raw) {
      errors[key] = `${label} là bắt buộc`;
      continue;
    }
    const n = /^\d+$/.test(raw) ? Number(raw) : Number.NaN;
    if (!Number.isSafeInteger(n) || n < min || n > max) {
      errors[key] = `${label} là số nguyên từ ${min} đến ${max}`;
      continue;
    }
    num[key] = n;
  }
  const format = PRINT_FORMAT_OPTIONS.find((o) => o.value === input.print_format);
  if (!format) errors.print_format = "Chọn khổ giấy in";
  if (Object.keys(errors).length > 0 || !format) return { ok: false, errors };
  return {
    ok: true,
    body: {
      scan_warning_threshold: num.scan_warning_threshold,
      price_deviation_pct: num.price_deviation_pct,
      retain_default_months: num.retain_default_months,
      label_size: { width_mm: num.label_width_mm, height_mm: num.label_height_mm },
      print_format: format.value,
    },
  };
}

/** Lỗi API về `label_size.width_mm` hiện ở ô chiều rộng, `label_size.height_mm` ở ô chiều cao. */
export function mapSettingsErrorField(field: string): string {
  if (field === "label_size.width_mm") return "label_width_mm";
  if (field === "label_size.height_mm") return "label_height_mm";
  return field;
}
