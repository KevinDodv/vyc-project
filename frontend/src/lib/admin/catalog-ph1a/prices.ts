/** Màn bảng giá (task #93): lưới nguyên liệu × hạng, mỗi ô giá mua và giá bán (đồng/kg, số nguyên).
 *  Kiểu theo lib/api/v1.d.ts. Backend: GET /prices?date=, GET /prices/history?to=, PUT /prices/{date}. */

import type { components } from "../../api/v1";
import { formatIsoDate } from "./text";

export type PriceCell = components["schemas"]["PriceCellOut"];
export type PriceHistoryDay = components["schemas"]["PriceHistoryDayOut"];

/** Khớp `MAX_PRICE` của backend/catalog/services/prices.py. */
export const MAX_PRICE = 1_000_000_000;

/** `mixed`: cùng bậc nhưng các nguyên liệu đặt tên hạng khác nhau, tên phải ghi trong từng ô. */
export type GridColumn = { rank: number; label: string; mixed: boolean };
export type GridRow = {
  material_id: number;
  material_code: string;
  material_name: string;
  /** Cùng thứ tự với `columns`; null: nguyên liệu không có hạng ở bậc đó. */
  cells: Array<PriceCell | null>;
};
export type PriceGrid = { columns: GridColumn[]; rows: GridRow[] };

/** Gom ô giá thành lưới: hàng theo nguyên liệu (giữ thứ tự API), cột theo bậc hạng. */
export function buildGrid(items: readonly PriceCell[]): PriceGrid {
  const ranks = new Map<number, Set<string>>();
  for (const item of items) {
    const names = ranks.get(item.grade_rank) ?? new Set<string>();
    ranks.set(item.grade_rank, names.add(item.grade_name));
  }
  const columns = [...ranks.entries()]
    .sort(([a], [b]) => a - b)
    .map(([rank, names]) => {
      const mixed = names.size > 1;
      return { rank, label: mixed ? `Bậc ${rank}` : [...names].join(), mixed };
    });

  const rows: GridRow[] = [];
  const byMaterial = new Map<number, GridRow>();
  for (const item of items) {
    let row = byMaterial.get(item.material_id);
    if (!row) {
      row = {
        material_id: item.material_id,
        material_code: item.material_code,
        material_name: item.material_name,
        cells: columns.map(() => null),
      };
      byMaterial.set(item.material_id, row);
      rows.push(row);
    }
    const index = columns.findIndex((c) => c.rank === item.grade_rank);
    if (index >= 0) row.cells[index] = item;
  }
  return { columns, rows };
}

const vnd = new Intl.NumberFormat("vi-VN");

/** 250000 → "250.000". null → "". */
export function formatPrice(value: number | null | undefined): string {
  return value === null || value === undefined ? "" : vnd.format(value);
}

export type ParsedPrice = { ok: true; value: number | null } | { ok: false; message: string };

/** Số nguyên viết liền, hoặc ngăn nghìn đúng nhóm 3 chữ số bằng cùng một dấu (chấm, phẩy, khoảng trắng). */
const WHOLE_PRICE = /^(?:\d+|\d{1,3}([.\s])\d{3}(?:\1\d{3})*)$/;

/** Đọc ô giá người dùng gõ: "250.000" → 250000. Rỗng là hợp lệ (value null).
 *  Số âm, số lẻ ("250,5"), dấu ngăn đặt sai chỗ hay chữ thì lỗi, không đoán. */
export function parsePrice(raw: string): ParsedPrice {
  const text = raw.trim();
  if (text === "") return { ok: true, value: null };
  if (text.startsWith("-")) return { ok: false, message: "Giá không được âm" };
  if (!WHOLE_PRICE.test(text)) {
    return { ok: false, message: "Giá phải là số nguyên (đồng/kg), ví dụ 250.000" };
  }
  const value = Number(text.replace(/\D/g, ""));
  if (!Number.isSafeInteger(value) || value > MAX_PRICE) {
    return { ok: false, message: `Giá quá lớn (tối đa ${formatPrice(MAX_PRICE)} đ/kg)` };
  }
  return { ok: true, value };
}

/** Giá trị một ô trên màn hình: chữ người dùng gõ cho giá mua và giá bán. */
export type CellInput = { grade_id: number; buy: string; sell: string };

export type PriceItemBody = { grade_id: number; buy_price: number; sell_price: number };
export type CellError = { grade_id: number; field: "buy" | "sell"; message: string };

export type PreparedPrices =
  | { ok: true; items: PriceItemBody[] }
  | { ok: false; errors: CellError[]; empty: boolean };

/** Dựng thân PUT từ các ô: chỉ gửi ô có đổi so với lúc mở (`initial`), nên ô không sửa vẫn lấy giá gần nhất.
 *  Ô sửa phải đủ giá mua và giá bán. Không ô nào đổi: `empty` (báo «chưa sửa ô nào»). */
export function preparePrices(
  cells: readonly CellInput[],
  initial: ReadonlyArray<Pick<PriceCell, "grade_id" | "buy_price" | "sell_price">>,
): PreparedPrices {
  const start = new Map(initial.map((c) => [c.grade_id, c]));
  const items: PriceItemBody[] = [];
  const errors: CellError[] = [];
  for (const cell of cells) {
    const before = start.get(cell.grade_id);
    const buy = parsePrice(cell.buy);
    const sell = parsePrice(cell.sell);
    if (!buy.ok) errors.push({ grade_id: cell.grade_id, field: "buy", message: buy.message });
    if (!sell.ok) errors.push({ grade_id: cell.grade_id, field: "sell", message: sell.message });
    if (!buy.ok || !sell.ok) continue;
    const unchanged =
      (buy.value ?? null) === (before?.buy_price ?? null) &&
      (sell.value ?? null) === (before?.sell_price ?? null);
    if (unchanged) continue;
    if (buy.value === null) {
      errors.push({ grade_id: cell.grade_id, field: "buy", message: "Nhập giá mua" });
    }
    if (sell.value === null) {
      errors.push({ grade_id: cell.grade_id, field: "sell", message: "Nhập giá bán" });
    }
    if (buy.value !== null && sell.value !== null) {
      items.push({ grade_id: cell.grade_id, buy_price: buy.value, sell_price: sell.value });
    }
  }
  if (errors.length > 0) return { ok: false, errors, empty: false };
  if (items.length === 0) return { ok: false, errors: [], empty: true };
  return { ok: true, items };
}

/** Ghi chú dưới ô: giá lấy từ ngày nào. Ô chưa từng có giá thì nhắc nhập. */
export function cellNote(cell: PriceCell, date: string): string {
  if (cell.effective_date === null) return "Chưa có giá";
  if (cell.effective_date === date) return "";
  return `Giá ngày ${formatIsoDate(cell.effective_date)}`;
}

export type HistoryRow = {
  date: string;
  /** Cùng thứ tự với cột hạng (grid.columns × rows); chuỗi "mua / bán" hoặc "" khi ngày đó không đổi hạng này. */
  values: Array<{ grade_id: number; text: string }>;
};

/** Lịch sử theo ngày, cột theo hạng (thứ tự `grades`). Ngày không đổi giá một hạng thì để trống. */
export function buildHistory(
  days: readonly PriceHistoryDay[],
  grades: ReadonlyArray<{ grade_id: number }>,
): HistoryRow[] {
  return days.map((day) => {
    const byGrade = new Map(day.items.map((i) => [i.grade_id, i]));
    return {
      date: day.price_date,
      values: grades.map(({ grade_id }) => {
        const item = byGrade.get(grade_id);
        return {
          grade_id,
          text: item ? `${formatPrice(item.buy_price)} / ${formatPrice(item.sell_price)}` : "",
        };
      }),
    };
  });
}

/** Danh sách hạng theo thứ tự lưới (nguyên liệu rồi bậc), làm cột cho bảng lịch sử. */
export function gradeColumns(
  items: readonly PriceCell[],
): Array<{ grade_id: number; label: string }> {
  return items.map((i) => ({
    grade_id: i.grade_id,
    label: `${i.material_name} · ${i.grade_name}`,
  }));
}

type MaterialNames = {
  name: string;
  grades: ReadonlyArray<{ id: number; name: string }>;
};

/** Cột lịch sử: các hạng đang dùng (như lưới), thêm hạng đã ngừng dùng mà còn giá trong 30 ngày đó.
 *  Tên hạng ngừng lấy từ /materials; không tải được thì ghi theo số hạng. */
export function historyColumns(
  items: readonly PriceCell[],
  days: readonly PriceHistoryDay[],
  materials: readonly MaterialNames[],
): Array<{ grade_id: number; label: string }> {
  const columns = gradeColumns(items);
  const shown = new Set(columns.map((c) => c.grade_id));
  const missing = new Set(
    days.flatMap((d) => d.items.map((i) => i.grade_id)).filter((id) => !shown.has(id)),
  );
  for (const material of materials) {
    for (const grade of material.grades) {
      if (!missing.delete(grade.id)) continue;
      columns.push({ grade_id: grade.id, label: `${material.name} · ${grade.name} (ngừng)` });
    }
  }
  for (const grade_id of missing) {
    columns.push({ grade_id, label: `Hạng #${grade_id} (ngừng)` });
  }
  return columns;
}
