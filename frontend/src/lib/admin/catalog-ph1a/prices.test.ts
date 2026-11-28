import { describe, expect, it } from "vitest";
import {
  buildGrid,
  buildHistory,
  cellNote,
  formatPrice,
  gradeColumns,
  historyColumns,
  MAX_PRICE,
  type PriceCell,
  parsePrice,
  preparePrices,
} from "./prices";

const cell = (
  grade_id: number,
  material_id: number,
  material_name: string,
  grade_rank: number,
  buy: number | null,
  sell: number | null,
  effective: string | null = "2026-11-20",
): PriceCell => ({
  grade_id,
  grade_rank,
  grade_name: `Loại ${grade_rank}`,
  material_id,
  material_code: material_id === 1 ? "VQ" : "QV",
  material_name,
  buy_price: buy,
  sell_price: sell,
  effective_date: effective,
});

const items: PriceCell[] = [
  cell(1, 1, "Vỏ quế", 1, 100000, 130000),
  cell(2, 1, "Vỏ quế", 2, 80000, 100000),
  cell(3, 1, "Vỏ quế", 3, 60000, 80000),
  cell(4, 2, "Quế vụn", 1, null, null, null),
  cell(5, 2, "Quế vụn", 2, 30000, 40000),
  cell(6, 2, "Quế vụn", 3, 20000, 30000),
];

describe("buildGrid", () => {
  it("2 nguyên liệu × 3 loại, giữ thứ tự hàng của API", () => {
    const grid = buildGrid(items);
    expect(grid.columns.map((c) => c.label)).toEqual(["Loại 1", "Loại 2", "Loại 3"]);
    expect(grid.rows.map((r) => r.material_name)).toEqual(["Vỏ quế", "Quế vụn"]);
    expect(grid.rows[1]?.cells.map((c) => c?.grade_id)).toEqual([4, 5, 6]);
  });
  it("nguyên liệu thiếu một bậc thì ô đó là null", () => {
    const grid = buildGrid(items.filter((i) => i.grade_id !== 5));
    expect(grid.rows[1]?.cells.map((c) => c?.grade_id ?? null)).toEqual([4, null, 6]);
  });
  it("cùng bậc khác tên hạng: tiêu đề ghi bậc và đánh dấu để ô ghi tên", () => {
    const renamed = items.map((i) => (i.grade_id === 4 ? { ...i, grade_name: "Vụn to" } : i));
    expect(buildGrid(renamed).columns.map((c) => [c.label, c.mixed])).toEqual([
      ["Bậc 1", true],
      ["Loại 2", false],
      ["Loại 3", false],
    ]);
  });
  it("không có hạng nào thì lưới rỗng", () => {
    expect(buildGrid([])).toEqual({ columns: [], rows: [] });
  });
});

describe("parsePrice", () => {
  it("bỏ dấu ngăn nghìn", () => {
    expect(parsePrice("250000")).toEqual({ ok: true, value: 250000 });
    expect(parsePrice("250.000")).toEqual({ ok: true, value: 250000 });
    expect(parsePrice(" 1.250.000 ")).toEqual({ ok: true, value: 1250000 });
    expect(parsePrice("1 250 000")).toEqual({ ok: true, value: 1250000 });
    const nbsp = String.fromCharCode(160);
    expect(parsePrice(["1", "250", "000"].join(nbsp))).toEqual({ ok: true, value: 1250000 });
    expect(parsePrice("0")).toEqual({ ok: true, value: 0 });
  });
  it("số lẻ hay dấu ngăn sai nhóm thì lỗi, không nuốt dấu", () => {
    const bad = ["12,5", "250.5", "12.5.3", "250,5", "250.50", "1.5", "250.0000", "2500.000"];
    for (const raw of [...bad, "1,250,000", "1.250,000", "1.250 000", "250..000"]) {
      expect(parsePrice(raw), raw).toMatchObject({ ok: false });
    }
  });
  it("rỗng là hợp lệ (chưa nhập)", () => {
    expect(parsePrice("  ")).toEqual({ ok: true, value: null });
  });
  it("âm, chữ, số lẻ kiểu e, quá lớn thì lỗi", () => {
    expect(parsePrice("-5")).toEqual({ ok: false, message: "Giá không được âm" });
    expect(parsePrice("12a")).toMatchObject({ ok: false });
    expect(parsePrice("1e5")).toMatchObject({ ok: false });
    expect(parsePrice(String(MAX_PRICE + 1))).toMatchObject({ ok: false });
    expect(parsePrice(String(MAX_PRICE))).toEqual({ ok: true, value: MAX_PRICE });
  });
});

describe("formatPrice", () => {
  it("dùng dấu chấm ngăn nghìn", () => {
    expect(formatPrice(250000)).toMatch(/^250[.  ]000$/);
    expect(formatPrice(null)).toBe("");
  });
});

describe("preparePrices", () => {
  const same = items.map((i) => ({
    grade_id: i.grade_id,
    buy: formatPrice(i.buy_price),
    sell: formatPrice(i.sell_price),
  }));
  it("không sửa ô nào thì báo empty, không gửi gì", () => {
    expect(preparePrices(same, items)).toEqual({ ok: false, errors: [], empty: true });
  });
  it("chỉ gửi ô đổi, kèm cả giá mua lẫn giá bán", () => {
    const cells = same.map((c) => (c.grade_id === 2 ? { ...c, buy: "85.000" } : c));
    expect(preparePrices(cells, items)).toEqual({
      ok: true,
      items: [{ grade_id: 2, buy_price: 85000, sell_price: 100000 }],
    });
  });
  it("ô chưa từng có giá: nhập đủ hai giá thì gửi", () => {
    const cells = same.map((c) => (c.grade_id === 4 ? { ...c, buy: "50000", sell: "70000" } : c));
    expect(preparePrices(cells, items)).toEqual({
      ok: true,
      items: [{ grade_id: 4, buy_price: 50000, sell_price: 70000 }],
    });
  });
  it("ô chưa từng có giá: chỉ nhập một giá thì lỗi đúng ô", () => {
    const cells = same.map((c) => (c.grade_id === 4 ? { ...c, buy: "50000" } : c));
    expect(preparePrices(cells, items)).toEqual({
      ok: false,
      empty: false,
      errors: [{ grade_id: 4, field: "sell", message: "Nhập giá bán" }],
    });
  });
  it("xoá trắng ô đã có giá thì lỗi (API không nhận giá trống)", () => {
    const cells = same.map((c) => (c.grade_id === 1 ? { ...c, sell: "" } : c));
    expect(preparePrices(cells, items)).toMatchObject({
      ok: false,
      errors: [{ grade_id: 1, field: "sell" }],
    });
  });
  it("giá âm hoặc không phải số: lỗi theo ô và theo cột", () => {
    const cells = same.map((c) => (c.grade_id === 3 ? { ...c, buy: "-1", sell: "abc" } : c));
    const result = preparePrices(cells, items);
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.errors.map((e) => `${e.grade_id}-${e.field}`)).toEqual(["3-buy", "3-sell"]);
    }
  });
  it("giá 0 là hợp lệ", () => {
    const cells = same.map((c) => (c.grade_id === 6 ? { ...c, buy: "0" } : c));
    expect(preparePrices(cells, items)).toEqual({
      ok: true,
      items: [{ grade_id: 6, buy_price: 0, sell_price: 30000 }],
    });
  });
});

describe("cellNote", () => {
  it("ghi chú nguồn giá", () => {
    expect(cellNote(cell(1, 1, "Vỏ quế", 1, 1, 1, "2026-11-23"), "2026-11-23")).toBe("");
    expect(cellNote(cell(1, 1, "Vỏ quế", 1, 1, 1, "2026-11-20"), "2026-11-23")).toBe(
      "Giá ngày 20/11/2026",
    );
    expect(cellNote(cell(1, 1, "Vỏ quế", 1, null, null, null), "2026-11-23")).toBe("Chưa có giá");
  });
});

describe("lịch sử", () => {
  const cols = gradeColumns(items);
  it("gradeColumns ghi nguyên liệu và hạng", () => {
    expect(cols[0]).toEqual({ grade_id: 1, label: "Vỏ quế · Loại 1" });
  });
  it("mỗi ngày một dòng, ô trống khi ngày đó không đổi hạng", () => {
    const rows = buildHistory(
      [
        {
          price_date: "2026-11-20",
          items: [{ grade_id: 1, buy_price: 100000, sell_price: 130000, updated_by_id: 1 }],
        },
        { price_date: "2026-11-10", items: [] },
      ],
      cols.slice(0, 2),
    );
    expect(rows).toHaveLength(2);
    expect(rows[0]?.values.map((v) => v.text.replace(/ /g, " "))).toEqual([
      "100.000 / 130.000",
      "",
    ]);
    expect(rows[1]?.values.map((v) => v.text)).toEqual(["", ""]);
  });
  it("không có ngày nào thì rỗng", () => {
    expect(buildHistory([], cols)).toEqual([]);
  });
});

describe("historyColumns", () => {
  const day = (...ids: number[]) => ({
    price_date: "2026-11-20",
    items: ids.map((grade_id) => ({ grade_id, buy_price: 1, sell_price: 2, updated_by_id: 1 })),
  });
  const materials = [{ name: "Vỏ quế", grades: [{ id: 3, name: "Loại 3" }] }];
  const active = items.filter((i) => i.grade_id !== 3);
  it("giữ cột của hạng đã ngừng dùng còn giá trong lịch sử", () => {
    const columns = historyColumns(active, [day(1, 3), day(3)], materials);
    expect(columns.map((c) => c.grade_id)).toEqual([1, 2, 4, 5, 6, 3]);
    expect(columns.at(-1)?.label).toBe("Vỏ quế · Loại 3 (ngừng)");
  });
  it("hạng ngừng không có giá trong lịch sử thì không thêm cột", () => {
    expect(historyColumns(active, [day(1)], materials)).toEqual(gradeColumns(active));
  });
  it("không tải được tên thì vẫn giữ cột", () => {
    expect(historyColumns(active, [day(3)], []).at(-1)).toEqual({
      grade_id: 3,
      label: "Hạng #3 (ngừng)",
    });
  });
});
