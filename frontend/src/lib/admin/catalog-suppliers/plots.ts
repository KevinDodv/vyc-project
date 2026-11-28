/** Logic bảng con đồi quế (task #94): dán toạ độ Google Maps, năm trồng, ảnh, dựng thân request.
 *  Quy tắc khớp schema PlotIn/PlotPatch và model Plot của backend (catalog/api/schemas/suppliers.py). */

import type { FieldErrors } from "../form";
import type { PlotOut } from "./suppliers";

export const PLANTED_YEAR_MIN = 1950;
export const MAX_PHOTOS = 10;

export const REQUIRED_AREA = "Chọn thôn của đồi";
export const COORDINATES_HINT =
  "Dán từ Google Maps: bấm giữ vào điểm trên bản đồ, chạm dòng toạ độ để chép, rồi dán vào đây. Ví dụ 21.028579, 105.854193.";

// Giống `_COORDINATES` của backend: hai số cách nhau dấu phẩy, chấm phẩy hoặc khoảng trắng.
const COORDINATES = /^\s*(-?\d{1,3}(?:\.\d+)?)\s*[,;\s]\s*(-?\d{1,3}(?:\.\d+)?)\s*$/;

export type CoordinatesResult =
  | { ok: true; lat: string; lng: string }
  | { ok: false; message: string };

/** «21.0285791, 105.8541934» → vĩ độ, kinh độ (6 chữ số thập phân, như backend). */
export function parseCoordinates(text: string): CoordinatesResult {
  const match = COORDINATES.exec(text);
  if (!match) {
    return {
      ok: false,
      message: "Toạ độ phải có dạng «vĩ độ, kinh độ», ví dụ 21.028579, 105.854193",
    };
  }
  const lat = Number(match[1]);
  const lng = Number(match[2]);
  if (lat < -90 || lat > 90) return { ok: false, message: "Vĩ độ phải từ -90 đến 90" };
  if (lng < -180 || lng > 180) return { ok: false, message: "Kinh độ phải từ -180 đến 180" };
  return { ok: true, lat: lat.toFixed(6), lng: lng.toFixed(6) };
}

/** Toạ độ của đồi để hiện trong ô nhập; chưa có thì rỗng. */
export function formatCoordinates(lat: number | null, lng: number | null): string {
  if (lat === null || lng === null) return "";
  return `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
}

/** Năm trồng: rỗng là hợp lệ (không bắt buộc); có thì số nguyên 1950 ≤ năm ≤ năm nay. */
export function validatePlantedYear(raw: string, nowYear: number): string | null {
  const text = raw.trim();
  if (!text) return null;
  const message = `Năm trồng phải từ ${PLANTED_YEAR_MIN} đến năm nay (${nowYear})`;
  if (!/^\d{1,5}$/.test(text)) return message;
  const year = Number(text);
  return year >= PLANTED_YEAR_MIN && year <= nowYear ? null : message;
}

/** Diện tích (ha): số không âm, tối đa 4 chữ số trước và 2 sau dấu phẩy (max_digits 6, decimal_places 2). */
export function validateAreaHa(raw: string): string | null {
  const text = raw.trim();
  if (!text) return null;
  return /^\d{1,4}(?:[.,]\d{1,2})?$/.test(text)
    ? null
    : "Diện tích là số không âm, tối đa 2 chữ số thập phân (ví dụ 1,5)";
}

/** Mỗi dòng một đường dẫn ảnh; bỏ dòng trống. */
export function parsePhotoUrls(text: string): string[] {
  return text
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);
}

/** Ảnh: `/media/...` hoặc `https://...` (chặn `javascript:`, `data:`, `http:`), tối đa 10. */
export function validatePhotoUrls(urls: readonly string[]): string | null {
  if (urls.length > MAX_PHOTOS) return `Tối đa ${MAX_PHOTOS} ảnh mỗi đồi`;
  for (const url of urls) {
    const ok = url.startsWith("/media/") || /^https:\/\/[^\s/]+/.test(url);
    if (!ok || /\s/.test(url) || url.length > 500) {
      return "Ảnh phải là đường dẫn /media/... hoặc địa chỉ https://";
    }
  }
  return null;
}

/** Giá trị thô của form đồi (chuỗi như người dùng gõ). `is_default` là null khi ô bị khoá (không gửi). */
export type PlotFormValues = {
  area_id: string;
  area_ha: string;
  planted_year: string;
  coordinates: string;
  photo_urls: string;
  is_default: boolean | null;
};

export type PlotBody = {
  area_id: number;
  area_ha: string | null;
  planted_year: number | null;
  coordinates: string | null;
  photo_urls: string[];
  is_default?: boolean;
};

export type PlotBodyResult = { ok: true; body: PlotBody } | { ok: false; errors: FieldErrors };

/** Kiểm đầu vào ở trình duyệt rồi dựng thân POST/PATCH. Sai thì trả lỗi theo trường, không gọi API. */
export function buildPlotBody(values: PlotFormValues, nowYear: number): PlotBodyResult {
  const errors: FieldErrors = {};
  const areaId = values.area_id.trim();
  if (!/^\d+$/.test(areaId)) errors.area_id = REQUIRED_AREA;

  const areaHaError = validateAreaHa(values.area_ha);
  if (areaHaError) errors.area_ha = areaHaError;

  const yearError = validatePlantedYear(values.planted_year, nowYear);
  if (yearError) errors.planted_year = yearError;

  const coordinatesText = values.coordinates.trim();
  if (coordinatesText) {
    const parsed = parseCoordinates(coordinatesText);
    if (!parsed.ok) errors.coordinates = parsed.message;
  }

  const photos = parsePhotoUrls(values.photo_urls);
  const photoError = validatePhotoUrls(photos);
  if (photoError) errors.photo_urls = photoError;

  if (Object.keys(errors).length > 0) return { ok: false, errors };

  const body: PlotBody = {
    area_id: Number(areaId),
    area_ha: values.area_ha.trim() ? values.area_ha.trim().replace(",", ".") : null,
    planted_year: values.planted_year.trim() ? Number(values.planted_year.trim()) : null,
    coordinates: coordinatesText || null,
    photo_urls: photos,
  };
  if (values.is_default !== null) body.is_default = values.is_default;
  return { ok: true, body };
}

/** Số đồi đang dùng: quyết định có chọn được luồng kiểm soát hay không. */
export function countActivePlots(plots: readonly Pick<PlotOut, "status">[]): number {
  return plots.filter((p) => p.status === "ACTIVE").length;
}

/** Chữ ở cột «Tình trạng» của bảng đồi. */
export function plotStatusLabel(plot: Pick<PlotOut, "status" | "is_default">): string {
  if (plot.status === "INACTIVE") return "Ngừng dùng";
  return plot.is_default ? "Mặc định" : "Đang dùng";
}

/** Năm hiện tại theo giờ Việt Nam (cùng quy ước `today_vn` của backend). */
export function currentYearVn(now: Date = new Date()): number {
  const year = new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Ho_Chi_Minh", year: "numeric" })
    .format(now)
    .slice(0, 4);
  return Number(year);
}
