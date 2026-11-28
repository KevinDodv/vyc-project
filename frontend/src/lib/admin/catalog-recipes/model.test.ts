import { describe, expect, it } from "vitest";
import {
  altGroupOptions,
  filterIngredients,
  filterRecipes,
  fold,
  type IngredientOut,
  ingredientKindLabel,
  matchesQuery,
  outputKindLabel,
  paginate,
  type RecipeOut,
  recipeAbilities,
  recipeStatusLabel,
} from "./model";

const ing = (id: number, code: string, name: string, status = "ACTIVE"): IngredientOut => ({
  id,
  code,
  name,
  kind: "OTHER",
  density_g_ml: null,
  track_stock: true,
  requires_coa: false,
  shelf_life_months: null,
  status,
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
});

const rec = (
  id: number,
  code: string,
  version: number,
  status = "DRAFT",
  name = code,
): RecipeOut => ({
  id,
  code,
  version,
  name,
  output_kind: "PRODUCT",
  output_ingredient_id: null,
  output_ingredient_code: null,
  base_batch_g: "100.00",
  base_label: null,
  cure_min_days: 0,
  cure_max_days: null,
  retain_months: null,
  status,
  note: null,
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
});

describe("tìm không phân biệt dấu", () => {
  it("fold", () => {
    expect(fold("Tinh dầu QUẾ Đặc")).toBe("tinh dau que dac");
  });
  it("matchesQuery khớp mã hoặc tên; từ khoá trống thì khớp hết", () => {
    expect(matchesQuery("que", "TD", "Tinh dầu quế")).toBe(true);
    expect(matchesQuery("td", "TD", "Tinh dầu quế")).toBe(true);
    expect(matchesQuery("xyz", "TD", "Tinh dầu quế")).toBe(false);
    expect(matchesQuery("  ", "TD", null)).toBe(true);
  });
});

describe("filterIngredients", () => {
  const list = [ing(1, "TD", "Tinh dầu quế"), ing(2, "DM", "Dung môi", "INACTIVE")];
  it("lọc từ khoá và tình trạng", () => {
    expect(filterIngredients(list, { q: "que" }).map((i) => i.id)).toEqual([1]);
    expect(filterIngredients(list, { status: "INACTIVE" }).map((i) => i.id)).toEqual([2]);
    expect(filterIngredients(list, {}).length).toBe(2);
  });
});

describe("filterRecipes", () => {
  const list = [
    rec(1, "TD10", 1, "RETIRED"),
    rec(3, "TD10", 2, "ACTIVE"),
    rec(2, "AA", 1, "DRAFT", "Túi thơm"),
  ];
  it("xếp theo mã rồi phiên bản mới trước", () => {
    expect(filterRecipes(list, {}).map((r) => r.id)).toEqual([2, 3, 1]);
  });
  it("lọc trạng thái và từ khoá", () => {
    expect(filterRecipes(list, { status: "ACTIVE" }).map((r) => r.id)).toEqual([3]);
    expect(filterRecipes(list, { q: "tui" }).map((r) => r.id)).toEqual([2]);
  });
  it("không đổi mảng gốc", () => {
    const copy = [...list];
    filterRecipes(list, {});
    expect(list).toEqual(copy);
  });
});

describe("paginate", () => {
  it("cắt trang", () => {
    const items = [1, 2, 3, 4, 5];
    expect(paginate(items, 1, 2)).toEqual([1, 2]);
    expect(paginate(items, 3, 2)).toEqual([5]);
    expect(paginate(items, 9, 2)).toEqual([]);
  });
});

describe("recipeAbilities (BR-26: bản đã khoá thì chỉ đọc)", () => {
  it("OWNER sửa bản nháp chưa dùng, kích hoạt được, chưa có «Tạo phiên bản mới»", () => {
    expect(recipeAbilities("OWNER", { status: "DRAFT", editable: true })).toEqual({
      edit: true,
      activate: true,
      retire: false,
      newVersion: false,
    });
  });
  it("bản ACTIVE: chỉ đọc, được ngừng và tạo phiên bản mới", () => {
    expect(recipeAbilities("OWNER", { status: "ACTIVE", editable: false })).toEqual({
      edit: false,
      activate: false,
      retire: true,
      newVersion: true,
    });
  });
  it("bản RETIRED: chỉ tạo phiên bản mới", () => {
    expect(recipeAbilities("OWNER", { status: "RETIRED", editable: false })).toEqual({
      edit: false,
      activate: false,
      retire: false,
      newVersion: true,
    });
  });
  it("bản nháp đã có lệnh dùng: không sửa, vẫn kích hoạt, không mời tạo bản mới", () => {
    expect(recipeAbilities("OWNER", { status: "DRAFT", editable: false })).toEqual({
      edit: false,
      activate: true,
      retire: false,
      newVersion: false,
    });
  });
  it("WORKSHOP và khách chưa rõ vai không ghi được gì", () => {
    const none = { edit: false, activate: false, retire: false, newVersion: false };
    expect(recipeAbilities("WORKSHOP", { status: "DRAFT", editable: true })).toEqual(none);
    expect(recipeAbilities("WORKSHOP", { status: "ACTIVE", editable: false })).toEqual(none);
    expect(recipeAbilities(undefined, null)).toEqual(none);
  });
  it("công thức mới: OWNER tạo được", () => {
    expect(recipeAbilities("OWNER", null).edit).toBe(true);
    expect(recipeAbilities("WORKSHOP", null).edit).toBe(false);
  });
});

describe("nhãn", () => {
  it("altGroupOptions giữ nhóm cao đã lưu", () => {
    expect(altGroupOptions(null).map((o) => o.label)).toEqual([
      "Nhóm 1",
      "Nhóm 2",
      "Nhóm 3",
      "Nhóm 4",
    ]);
    expect(altGroupOptions(7).at(-1)).toEqual({ value: 7, label: "Nhóm 7" });
  });
  it("loại phụ liệu BLEND khớp nhãn của backend", () => {
    expect(ingredientKindLabel("BLEND")).toBe("Hương nền, dung dịch tẩm");
  });
  it("trạng thái và loại đầu ra", () => {
    expect(recipeStatusLabel("DRAFT")).toBe("Nháp");
    expect(recipeStatusLabel("X")).toBe("X");
    expect(outputKindLabel("INTERMEDIATE")).toBe("Bán thành phẩm");
  });
});
