/** Màn nguyên liệu và hạng (task #93). Kiểu theo lib/api/v1.d.ts; API trả mảng thường (2 nguyên liệu). */

import type { components } from "../../api/v1";
import type { FieldOption, StatusFilter } from "../catalog";
import { matchesQuery } from "./text";

export type MaterialOut = components["schemas"]["MaterialOut"];
export type GradeOut = components["schemas"]["GradeOut"];
export type GoodsTypeLite = { id: number; name: string; grp: string; status: string };

export type MaterialRow = {
  id: number;
  sort_order: number;
  code: string;
  name: string;
  goods_type: string;
  grades: string;
  status: "ACTIVE" | "INACTIVE";
};

function byRank(a: GradeOut, b: GradeOut): number {
  return a.rank - b.rank;
}

/** «Loại 1 · Loại 2 · Loại 3 (ngừng)»: hạng đã ngừng dùng vẫn hiện để biết còn tồn tại. */
export function gradesSummary(grades: readonly GradeOut[]): string {
  return [...grades]
    .sort(byRank)
    .map((g) => (g.status === "INACTIVE" ? `${g.name} (ngừng)` : g.name))
    .join(" · ");
}

export function filterMaterials(
  items: readonly MaterialOut[],
  goodsTypes: readonly GoodsTypeLite[],
  filter: { q?: string; status?: StatusFilter },
): MaterialRow[] {
  const typeName = new Map(goodsTypes.map((t) => [t.id, t.name]));
  return items
    .filter((m) => matchesQuery(filter.q ?? "", m.code, m.name))
    .filter((m) => !filter.status || m.status === filter.status)
    .map((m) => ({
      id: m.id,
      sort_order: m.sort_order,
      code: m.code,
      name: m.name,
      goods_type: typeName.get(m.goods_type_id) ?? `#${m.goods_type_id}`,
      grades: gradesSummary(m.grades),
      status: m.status === "INACTIVE" ? "INACTIVE" : "ACTIVE",
    }));
}

/** Loại hàng chọn được cho nguyên liệu: nhóm nguyên liệu, đang dùng (kèm loại hiện tại dù đã ngừng). */
export function goodsTypeOptions(
  goodsTypes: readonly GoodsTypeLite[],
  currentId?: number | null,
): FieldOption[] {
  return goodsTypes
    .filter((t) => t.id === currentId || (t.grp === "MATERIAL" && t.status === "ACTIVE"))
    .map((t) => ({ value: t.id, label: t.name }));
}

/* ---- Bảng con hạng ---- */

export type GradeDraft = {
  /** Có id: hạng đã lưu (bậc khoá). Không có: hạng mới. */
  id: number | null;
  rank: string;
  name: string;
  status: "ACTIVE" | "INACTIVE";
};

export const MAX_GRADES = 9;

export function draftsFromMaterial(grades: readonly GradeOut[]): GradeDraft[] {
  return [...grades].sort(byRank).map((g) => ({
    id: g.id,
    rank: String(g.rank),
    name: g.name,
    status: g.status === "INACTIVE" ? "INACTIVE" : "ACTIVE",
  }));
}

/** Bậc gợi ý cho hạng thêm mới: số nhỏ nhất từ 1 chưa dùng. */
export function nextRank(drafts: readonly GradeDraft[]): number {
  const used = new Set(drafts.map((d) => Number(d.rank)));
  for (let r = 1; r <= MAX_GRADES; r++) if (!used.has(r)) return r;
  return MAX_GRADES;
}

export function parseRank(raw: string): number | null {
  const text = raw.trim();
  if (!/^\d+$/.test(text)) return null;
  const n = Number(text);
  return n >= 1 && n <= MAX_GRADES ? n : null;
}

/** Kiểm trước khi gửi (API vẫn kiểm lại): tên không trống, bậc 1–9, không trùng bậc. Trả lỗi đầu tiên hoặc null. */
export function validateGrades(drafts: readonly GradeDraft[]): string | null {
  if (drafts.length > MAX_GRADES) return `Tối đa ${MAX_GRADES} hạng`;
  const seen = new Set<number>();
  for (const d of drafts) {
    if (d.name.trim() === "") return "Tên hạng không được để trống";
    const rank = parseRank(d.rank);
    if (rank === null) return `Bậc của hạng «${d.name.trim()}» phải là số từ 1 đến ${MAX_GRADES}`;
    if (seen.has(rank)) return "Hai hạng không được cùng một bậc";
    seen.add(rank);
  }
  return null;
}

export type GradeBody = { id?: number; rank: number; name: string; status?: "ACTIVE" | "INACTIVE" };

/** Thân `grades` của POST/PATCH. Hạng mới: không `id`, không `status`. Hạng đã lưu: gửi cả `id` và `status`. */
export function gradesToBody(drafts: readonly GradeDraft[]): GradeBody[] {
  return drafts.map((d) => {
    const rank = parseRank(d.rank) ?? 0;
    const name = d.name.trim();
    return d.id === null ? { rank, name } : { id: d.id, rank, name, status: d.status };
  });
}

export type MaterialBody = Record<string, unknown>;

/** Ghép thân request từ phần thường của form (đã qua `formToBody`) và bảng hạng. */
export function materialBody(
  base: Record<string, unknown>,
  drafts: readonly GradeDraft[],
): MaterialBody {
  const body: MaterialBody = { ...base, grades: gradesToBody(drafts) };
  // «Thứ tự» để trống: không gửi (tạo mới lấy 0, sửa giữ số cũ); API từ chối null.
  if (body.sort_order === null) delete body.sort_order;
  return body;
}
