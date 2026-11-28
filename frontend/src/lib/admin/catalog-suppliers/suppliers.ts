/** Logic màn người bán (task #94): nhãn, quy tắc luồng theo kiểu, lọc địa bàn, cảnh báo trùng, dòng danh sách.
 *  Kiểu theo lib/api/v1.d.ts; quy tắc theo thiet-ke-chi-tiet.md mục 5 và backend `services/suppliers.py`. */

import type { components } from "../../api/v1";
import type { AdminRole, FieldOption } from "../catalog";
import { fold } from "./text";

export type SupplierOut = components["schemas"]["SupplierOut"];
export type SupplierSavedOut = components["schemas"]["SupplierSavedOut"];
export type PlotOut = components["schemas"]["PlotOut"];
export type AreaNode = components["schemas"]["AreaNode"];

export type SupplierKind = "FAMILY" | "FARMER" | "TRADER";
export type SupplierStream = "CONTROLLED" | "GENERAL";

export const KIND_LABEL: Record<SupplierKind, string> = {
  FAMILY: "Gia đình",
  FARMER: "Hộ dân",
  TRADER: "Thương lái",
};

export const STREAM_LABEL: Record<SupplierStream, string> = {
  CONTROLLED: "Luồng kiểm soát",
  GENERAL: "Luồng thường",
};

export const KIND_OPTIONS: FieldOption[] = (Object.keys(KIND_LABEL) as SupplierKind[]).map((k) => ({
  value: k,
  label: KIND_LABEL[k],
}));

export function isSupplierKind(value: unknown): value is SupplierKind {
  return value === "FAMILY" || value === "FARMER" || value === "TRADER";
}

export function isSupplierStream(value: unknown): value is SupplierStream {
  return value === "CONTROLLED" || value === "GENERAL";
}

export function kindLabel(kind: string): string {
  return isSupplierKind(kind) ? KIND_LABEL[kind] : kind;
}

export function streamLabel(stream: string): string {
  return isSupplierStream(stream) ? STREAM_LABEL[stream] : stream;
}

// ----------------------------------------------------------------------------- quyền

/** Chỉ OWNER sửa, ngừng dùng, thêm đồi và duyệt (backend: PATCH, POST plots, approve là OWNER_ONLY). */
export function canManageSuppliers(role: AdminRole | undefined): boolean {
  return role === "OWNER";
}

/** WORKSHOP và OWNER đều thêm nhanh được (POST /suppliers là ANY_STAFF). Không rõ vai thì không. */
export function canQuickAddSupplier(role: AdminRole | undefined): boolean {
  return role === "OWNER" || role === "WORKSHOP";
}

/** Nút «Duyệt» chỉ hiện cho OWNER và chỉ khi người bán còn chờ duyệt. */
export function canApprove(role: AdminRole | undefined, supplier: { approved: boolean }): boolean {
  return canManageSuppliers(role) && !supplier.approved;
}

// ----------------------------------------------------------------------------- luồng theo kiểu

export type StreamRule = {
  /** Khoá luồng: chỉ còn một lựa chọn, không đổi được. */
  locked: boolean;
  options: Array<{ value: SupplierStream; label: string; disabled: boolean }>;
  /** Lý do hiện dưới ô luồng; rỗng khi chọn tự do. */
  hint: string;
};

export const TRADER_STREAM_HINT = "Thương lái luôn là luồng thường, không đổi được.";
export const NEEDS_PLOT_HINT =
  "Luồng kiểm soát chỉ chọn được khi người bán có ít nhất 1 đồi quế đang dùng.";

/** Thương lái: khoá GENERAL. Hộ dân, gia đình: CONTROLLED chỉ chọn được khi có ≥ 1 đồi đang dùng
 *  (người bán mới tạo chưa có đồi nên luôn là GENERAL). */
export function streamRule(kind: string, activePlots: number): StreamRule {
  const general = { value: "GENERAL" as const, label: STREAM_LABEL.GENERAL, disabled: false };
  if (kind === "TRADER") {
    return { locked: true, options: [general], hint: TRADER_STREAM_HINT };
  }
  const needsPlot = activePlots <= 0;
  return {
    locked: false,
    options: [
      { value: "CONTROLLED", label: STREAM_LABEL.CONTROLLED, disabled: needsPlot },
      general,
    ],
    hint: needsPlot ? NEEDS_PLOT_HINT : "",
  };
}

/** Luồng hợp lệ gần nhất với `current`: không được chọn thì về GENERAL. */
export function normalizeStream(
  kind: string,
  activePlots: number,
  current: string,
): SupplierStream {
  const allowed = streamRule(kind, activePlots).options.find((o) => o.value === current);
  return allowed && !allowed.disabled ? allowed.value : "GENERAL";
}

// ----------------------------------------------------------------------------- địa bàn

export type AreaChoice = { id: number; level: "COMMUNE" | "VILLAGE"; label: string };

/** Cấp địa bàn mà kiểu người bán được chọn: hộ dân, gia đình phải là thôn; thương lái từ xã trở xuống. */
export function allowedAreaLevels(kind: string): ReadonlyArray<"COMMUNE" | "VILLAGE"> {
  return kind === "TRADER" ? ["COMMUNE", "VILLAGE"] : ["VILLAGE"];
}

/** Cây Tỉnh › Xã › Thôn thành danh sách phẳng xã và thôn đang dùng, nhãn «Châu Quế › Thôn 3». */
export function flattenAreas(tree: readonly AreaNode[]): AreaChoice[] {
  const out: AreaChoice[] = [];
  const walk = (nodes: readonly AreaNode[], parents: string[]): void => {
    for (const node of nodes) {
      if (node.status !== "ACTIVE") continue;
      // Nhãn bỏ tên tỉnh: xã đứng đầu, thôn đứng sau xã.
      const path = node.level === "PROVINCE" ? [] : [...parents, node.name];
      if (node.level === "COMMUNE" || node.level === "VILLAGE") {
        out.push({ id: node.id, level: node.level, label: path.join(" › ") });
      }
      walk(node.children ?? [], path);
    }
  };
  walk(tree, []);
  return out;
}

export function areaOptionsFor(kind: string, areas: readonly AreaChoice[]): FieldOption[] {
  const levels = allowedAreaLevels(kind);
  return areas
    .filter((a) => levels.includes(a.level))
    .map((a) => ({ value: a.id, label: a.label }));
}

/** Địa bàn của đồi: chỉ cấp thôn. */
export function villageOptions(areas: readonly AreaChoice[]): FieldOption[] {
  return areas.filter((a) => a.level === "VILLAGE").map((a) => ({ value: a.id, label: a.label }));
}

// ----------------------------------------------------------------------------- trùng tên

/** Người bán trùng tên (không phân biệt dấu, hoa thường, khoảng trắng) ở cùng địa bàn: chỉ cảnh báo. */
export function findTwins(
  self: { id: number; name: string; area_id: number },
  candidates: readonly SupplierOut[],
): SupplierOut[] {
  const needle = fold(self.name);
  return candidates.filter(
    (s) => s.id !== self.id && s.area_id === self.area_id && fold(s.name) === needle,
  );
}

export function duplicateMessage(areaName: string, twins: readonly SupplierOut[]): string {
  const listing = twins.map((s) => `${s.code} ${s.name}`).join(", ");
  return `Trùng tên và địa bàn với người bán khác ở ${areaName}: ${listing}.`;
}

// ----------------------------------------------------------------------------- danh sách

export type SupplierRow = {
  id: number;
  status: "ACTIVE" | "INACTIVE";
  code: string;
  name: string;
  kind: string;
  area_name: string;
  stream: string;
  plots_count: number;
  public_consent: boolean;
  approved: boolean;
  approval: string;
};

export const PENDING_LABEL = "Chờ duyệt";

export function toSupplierRow(s: SupplierOut): SupplierRow {
  return {
    id: s.id,
    status: s.status === "INACTIVE" ? "INACTIVE" : "ACTIVE",
    code: s.code,
    name: s.name,
    kind: kindLabel(s.kind),
    area_name: s.area_name,
    stream: streamLabel(s.stream),
    plots_count: s.plots_count,
    public_consent: s.public_consent,
    approved: s.approved,
    approval: s.approved ? "" : PENDING_LABEL,
  };
}

export const SUPPLIER_COLUMNS = [
  { key: "code", label: "Mã", mono: true },
  { key: "name", label: "Tên" },
  { key: "kind", label: "Kiểu" },
  { key: "area_name", label: "Địa bàn" },
  { key: "stream", label: "Luồng" },
  { key: "plots_count", label: "Đồi", numeric: true },
  {
    key: "public_consent",
    label: "Cho khách thấy tên",
    format: (v: unknown) => (v === true ? "✔ Có" : ""),
  },
  { key: "approval", label: "Duyệt" },
  { key: "status", label: "Tình trạng" },
];

export const SUPPLIERS_PATH = "/quan-ly/nguoi-ban";
export const PENDING_PATH = `${SUPPLIERS_PATH}/cho-duyet`;
