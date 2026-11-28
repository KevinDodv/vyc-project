/** Logic thuần của màn /quan-ly/chung-nhan (TK mục 5, dòng Chứng nhận). */

import type { components } from "../../api/v1";
import { type ListQuery, listApiQuery } from "../catalog";

export type Certificate = components["schemas"]["CertificateOut"];
export type CertificateKind = components["schemas"]["CertificateIn"]["kind"];
export type Plot = components["schemas"]["PlotOut"];
export type SelectOption = { value: string; label: string };

export const CERTIFICATE_KIND_OPTIONS: ReadonlyArray<{ value: CertificateKind; label: string }> = [
  { value: "OCOP", label: "OCOP" },
  { value: "ORGANIC", label: "Hữu cơ" },
  { value: "FOOD_SAFETY", label: "An toàn thực phẩm" },
  { value: "DECLARATION", label: "Công bố sản phẩm" },
];

export const CERTIFICATE_KIND_LABEL: Record<string, string> = Object.fromEntries(
  CERTIFICATE_KIND_OPTIONS.map((o) => [o.value, o.label]),
);

export const OCOP_STAR_OPTIONS = [3, 4, 5] as const;

/** Chứng nhận còn dưới ngần này ngày là «Sắp hết hạn» (mockup màn Chứng nhận). */
export const EXPIRING_SOON_DAYS = 30;

export type CertificateState = "valid" | "soon" | "expired";

export const CERTIFICATE_STATE_LABEL: Record<CertificateState, string> = {
  valid: "Còn hiệu lực",
  soon: "Sắp hết hạn",
  expired: "Hết hạn",
};

const DAY_MS = 86_400_000;

function dayNumber(iso: string): number | null {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso);
  if (!match) return null;
  return Math.floor(Date.UTC(Number(match[1]), Number(match[2]) - 1, Number(match[3])) / DAY_MS);
}

/** Ngày hôm nay theo giờ Việt Nam, dạng YYYY-MM-DD (backend so «còn hiệu lực» theo ngày, không theo giờ). */
export function todayInVietnam(now: Date = new Date()): string {
  return new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Ho_Chi_Minh" }).format(now);
}

/** Không có ngày hết hạn là còn hiệu lực mãi. `is_expired` của API là nguồn quyết định «hết hạn»;
 *  hàm này chỉ thêm mức «sắp hết hạn» (còn dưới 30 ngày). */
export function certificateState(
  cert: Pick<Certificate, "expires_on" | "is_expired">,
  today: string,
): CertificateState {
  if (cert.is_expired) return "expired";
  if (!cert.expires_on) return "valid";
  const end = dayNumber(cert.expires_on);
  const now = dayNumber(today);
  if (end === null || now === null) return "valid";
  if (end < now) return "expired";
  return end - now < EXPIRING_SOON_DAYS ? "soon" : "valid";
}

/** 2026-11-23 → 23/11/2026; chuỗi lạ giữ nguyên. */
export function formatDate(iso: string | null | undefined): string {
  if (!iso) return "";
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso);
  return match ? `${match[3]}/${match[2]}/${match[1]}` : iso;
}

/** Màn dùng bộ lọc «Đang dùng/Ngừng dùng» của CatalogList; với chứng nhận nó là còn/hết hiệu lực (`active`). */
export function certificateApiQuery(query: ListQuery): Record<string, string | number | boolean> {
  const { status, ...rest } = listApiQuery(query);
  const out: Record<string, string | number | boolean> = { ...rest };
  if (status === "ACTIVE") out.active = true;
  else if (status === "INACTIVE") out.active = false;
  return out;
}

/** «Sản phẩm Q100» hoặc «Đồi D-CQ-0001-1»; `skuById` là id → SKU, `plotCodeById` là id → mã đồi.
 *  Không tra được (API lỗi) thì hiện id để các dòng vẫn phân biệt được. */
export function certificateTarget(
  cert: Pick<Certificate, "product_id" | "plot_id">,
  skuById: ReadonlyMap<number, string>,
  plotCodeById: ReadonlyMap<number, string> = new Map(),
): string {
  if (cert.product_id !== null) {
    const sku = skuById.get(cert.product_id);
    return sku ? `Sản phẩm ${sku}` : `Sản phẩm #${cert.product_id}`;
  }
  if (cert.plot_id !== null) {
    const code = plotCodeById.get(cert.plot_id);
    return code ? `Đồi ${code}` : `Đồi #${cert.plot_id}`;
  }
  return "";
}

/** «D-CQ-0001-1 – Thôn 3 · 1,5 ha»; đồi ngừng dùng ghi rõ. */
export function plotLabel(plot: Plot): string {
  const area = plot.area_ha === null ? "" : ` · ${String(plot.area_ha).replace(".", ",")} ha`;
  const inactive = plot.status === "INACTIVE" ? " (ngừng dùng)" : "";
  return `${plot.code} – ${plot.area_name}${area}${inactive}`;
}

/** Đồi đang dùng của một người bán, cộng đồi đang gắn với chứng nhận (dù đã ngừng dùng). */
export function plotOptions(plots: readonly Plot[], currentId: number | null): SelectOption[] {
  return plots
    .filter((p) => p.status === "ACTIVE" || p.id === currentId)
    .map((p) => ({ value: String(p.id), label: plotLabel(p) }));
}
