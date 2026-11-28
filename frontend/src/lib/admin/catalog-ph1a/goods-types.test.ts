import { describe, expect, it } from "vitest";
import {
  createFields,
  editFields,
  filterGoodsTypes,
  type GoodsTypeOut,
  groupLabel,
  yesNo,
} from "./goods-types";

const items: GoodsTypeOut[] = [
  {
    id: 1,
    code: "NL_QUE",
    name: "Nguyên liệu quế",
    grp: "MATERIAL",
    is_food: false,
    status: "ACTIVE",
  },
  { id: 2, code: "TINH_DAU", name: "Tinh dầu", grp: "PRODUCT", is_food: false, status: "ACTIVE" },
  { id: 3, code: "TRA", name: "Trà quế", grp: "PRODUCT", is_food: true, status: "INACTIVE" },
];

describe("filterGoodsTypes", () => {
  it("không lọc thì giữ thứ tự API", () => {
    expect(filterGoodsTypes(items, {}).map((r) => r.id)).toEqual([1, 2, 3]);
  });
  it("lọc từ khoá không dấu theo mã hoặc tên", () => {
    expect(filterGoodsTypes(items, { q: "nguyen lieu" }).map((r) => r.id)).toEqual([1]);
    expect(filterGoodsTypes(items, { q: "tinh_dau" }).map((r) => r.id)).toEqual([2]);
  });
  it("lọc tình trạng", () => {
    expect(filterGoodsTypes(items, { status: "INACTIVE" }).map((r) => r.id)).toEqual([3]);
  });
});

describe("nhãn", () => {
  it("nhóm và có/không", () => {
    expect(groupLabel("MATERIAL")).toBe("Nguyên liệu");
    expect(groupLabel("PRODUCT")).toBe("Thành phẩm");
    expect(groupLabel("X")).toBe("X");
    expect(yesNo(true)).toBe("✔ Có");
    expect(yesNo(false)).toBe("");
  });
});

describe("trường form", () => {
  it("tạo: mã, tên, nhóm bắt buộc; là thực phẩm mặc định không tích", () => {
    const fields = createFields();
    expect(fields.filter((f) => f.required).map((f) => f.name)).toEqual(["code", "name", "grp"]);
    expect(fields.find((f) => f.name === "is_food")?.value).toBe(false);
  });
  it("sửa: mã chỉ đọc, giá trị lấy từ bản ghi", () => {
    const first = items[0];
    if (!first) throw new Error("thiếu dữ liệu mẫu");
    const fields = editFields(first);
    expect(fields.find((f) => f.name === "code")?.readonly).toBe(true);
    expect(fields.find((f) => f.name === "grp")?.value).toBe("MATERIAL");
  });
});
