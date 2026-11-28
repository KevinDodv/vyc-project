import { describe, expect, it } from "vitest";
import {
  draftsFromMaterial,
  filterMaterials,
  type GoodsTypeLite,
  type GradeDraft,
  type GradeOut,
  goodsTypeOptions,
  gradesSummary,
  gradesToBody,
  type MaterialOut,
  materialBody,
  nextRank,
  parseRank,
  validateGrades,
} from "./materials";

const grade = (id: number, rank: number, name: string, status = "ACTIVE"): GradeOut => ({
  id,
  material_id: 1,
  rank,
  name,
  status,
});

const materials: MaterialOut[] = [
  {
    id: 1,
    code: "VQ",
    name: "Vỏ quế",
    goods_type_id: 10,
    image_url: null,
    sort_order: 1,
    status: "ACTIVE",
    grades: [grade(3, 3, "Loại 3"), grade(1, 1, "Loại 1"), grade(2, 2, "Loại 2", "INACTIVE")],
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  },
  {
    id: 2,
    code: "QV",
    name: "Quế vụn",
    goods_type_id: 10,
    image_url: null,
    sort_order: 2,
    status: "INACTIVE",
    grades: [],
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  },
];
const goodsTypes: GoodsTypeLite[] = [
  { id: 10, name: "Nguyên liệu quế", grp: "MATERIAL", status: "ACTIVE" },
  { id: 11, name: "Tinh dầu", grp: "PRODUCT", status: "ACTIVE" },
  { id: 12, name: "Củ cũ", grp: "MATERIAL", status: "INACTIVE" },
];

describe("danh sách", () => {
  it("hạng xếp theo bậc, hạng ngừng dùng có ghi chú", () => {
    expect(gradesSummary(materials[0]?.grades ?? [])).toBe("Loại 1 · Loại 2 (ngừng) · Loại 3");
  });
  it("tra tên loại hàng, lọc từ khoá và tình trạng", () => {
    const rows = filterMaterials(materials, goodsTypes, {});
    expect(rows.map((r) => [r.code, r.goods_type])).toEqual([
      ["VQ", "Nguyên liệu quế"],
      ["QV", "Nguyên liệu quế"],
    ]);
    expect(filterMaterials(materials, goodsTypes, { q: "que vun" }).map((r) => r.code)).toEqual([
      "QV",
    ]);
    expect(filterMaterials(materials, goodsTypes, { status: "ACTIVE" }).map((r) => r.code)).toEqual(
      ["VQ"],
    );
  });
  it("loại hàng không tra được thì hiện #id", () => {
    expect(filterMaterials(materials, [], {})[0]?.goods_type).toBe("#10");
  });
});

describe("goodsTypeOptions", () => {
  it("chỉ nhóm nguyên liệu đang dùng, kèm loại hiện tại dù đã ngừng", () => {
    expect(goodsTypeOptions(goodsTypes).map((o) => o.value)).toEqual([10]);
    expect(goodsTypeOptions(goodsTypes, 12).map((o) => o.value)).toEqual([10, 12]);
  });
});

describe("bảng hạng", () => {
  const drafts = draftsFromMaterial(materials[0]?.grades ?? []);
  it("draftsFromMaterial xếp theo bậc và giữ trạng thái", () => {
    expect(drafts.map((d) => [d.id, d.rank, d.status])).toEqual([
      [1, "1", "ACTIVE"],
      [2, "2", "INACTIVE"],
      [3, "3", "ACTIVE"],
    ]);
  });
  it("nextRank lấy bậc trống nhỏ nhất", () => {
    expect(nextRank(drafts)).toBe(4);
    expect(nextRank([{ id: null, rank: "2", name: "x", status: "ACTIVE" }])).toBe(1);
    expect(nextRank([])).toBe(1);
  });
  it("parseRank chỉ nhận số nguyên 1–9", () => {
    expect(parseRank(" 3 ")).toBe(3);
    for (const bad of ["", "0", "10", "1.5", "-1", "a"]) expect(parseRank(bad)).toBeNull();
  });
  it("validateGrades: tên trống, bậc sai, trùng bậc, quá 9 hạng", () => {
    const ok: GradeDraft = { id: null, rank: "1", name: "Loại 1", status: "ACTIVE" };
    expect(validateGrades([ok])).toBeNull();
    expect(validateGrades([{ ...ok, name: "  " }])).toBe("Tên hạng không được để trống");
    expect(validateGrades([{ ...ok, rank: "12" }])).toContain("từ 1 đến 9");
    expect(validateGrades([ok, { ...ok, name: "Loại 1b" }])).toBe(
      "Hai hạng không được cùng một bậc",
    );
    const ten = Array.from({ length: 10 }, (_, i) => ({ ...ok, rank: String((i % 9) + 1) }));
    expect(validateGrades(ten)).toBe("Tối đa 9 hạng");
  });
  it("gradesToBody: hạng mới không có id/status, hạng đã lưu gửi cả hai", () => {
    expect(
      gradesToBody([
        { id: null, rank: "4", name: " Loại 4 ", status: "ACTIVE" },
        { id: 2, rank: "2", name: "Loại 2", status: "INACTIVE" },
      ]),
    ).toEqual([
      { rank: 4, name: "Loại 4" },
      { id: 2, rank: 2, name: "Loại 2", status: "INACTIVE" },
    ]);
  });
  it("materialBody ghép phần thường với hạng", () => {
    const body = materialBody({ name: "Vỏ quế" }, [
      { id: null, rank: "1", name: "Loại 1", status: "ACTIVE" },
    ]);
    expect(body).toEqual({ name: "Vỏ quế", grades: [{ rank: 1, name: "Loại 1" }] });
  });
});
