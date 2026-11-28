/** Đổi tên trường lỗi của API về tên ô trên form (task #94).
 *  Model Django báo lỗi theo `area` (không phải `area_id`), toạ độ báo theo `lat`/`lng` còn form chỉ có một ô «Toạ độ». */

import type { ParsedError } from "../form";

export const SUPPLIER_ERROR_ALIASES: Record<string, string> = { area: "area_id" };
export const PLOT_ERROR_ALIASES: Record<string, string> = {
  area: "area_id",
  lat: "coordinates",
  lng: "coordinates",
};

export function remapErrors(parsed: ParsedError, aliases: Record<string, string>): ParsedError {
  const fields: Record<string, string> = {};
  for (const [name, message] of Object.entries(parsed.fields)) {
    const target = aliases[name] ?? name;
    if (!(target in fields)) fields[target] = message;
  }
  return { fields, general: parsed.general };
}
