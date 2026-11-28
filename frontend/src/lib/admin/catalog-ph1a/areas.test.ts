import { describe, expect, it } from "vitest";
import {
  type AreaNode,
  allAreas,
  areaPathLabel,
  createFields,
  editFields,
  findArea,
  flattenAreaTree,
  parentLevelMap,
  parentOptions,
  treeLabel,
} from "./areas";

const node = (
  id: number,
  level: string,
  name: string,
  parent_id: number | null,
  children: AreaNode[] = [],
  status = "ACTIVE",
): AreaNode => ({
  id,
  code: `A${id}`,
  level,
  name,
  parent_id,
  former_name: null,
  valid_from: "2025-07-01",
  valid_to: null,
  status,
  children,
});

const tree: AreaNode[] = [
  node(1, "PROVINCE", "Hà Nội", null),
  node(2, "PROVINCE", "Lào Cai", null, [
    node(3, "COMMUNE", "Phong Dụ Hạ", 2, [node(4, "VILLAGE", "Thôn 1", 3)]),
    node(5, "COMMUNE", "Châu Quế", 2, [], "INACTIVE"),
  ]),
];

function need<T>(value: T | null | undefined): T {
  if (value === null || value === undefined) throw new Error("thiếu dữ liệu mẫu");
  return value;
}

describe("flattenAreaTree", () => {
  it("duyệt sâu theo thứ tự cây, có độ sâu và nhãn cấp", () => {
    const rows = flattenAreaTree(tree);
    expect(rows.map((r) => [r.name, r.depth, r.levelLabel])).toEqual([
      ["Hà Nội", 0, "Tỉnh"],
      ["Lào Cai", 0, "Tỉnh"],
      ["Phong Dụ Hạ", 1, "Xã"],
      ["Thôn 1", 2, "Thôn"],
      ["Châu Quế", 1, "Xã"],
    ]);
  });
  it("từ khoá giữ dòng khớp và các cấp trên của nó", () => {
    const rows = flattenAreaTree(tree, { q: "thon 1" });
    expect(rows.map((r) => r.name)).toEqual(["Lào Cai", "Phong Dụ Hạ", "Thôn 1"]);
  });
  it("lọc tình trạng", () => {
    const rows = flattenAreaTree(tree, { status: "INACTIVE" });
    expect(rows.map((r) => r.name)).toEqual(["Lào Cai", "Châu Quế"]);
  });
  it("không khớp thì rỗng", () => {
    expect(flattenAreaTree(tree, { q: "không có" })).toEqual([]);
  });
});

describe("treeLabel", () => {
  it("tỉnh để nguyên, cấp dưới thụt vào theo độ sâu", () => {
    expect(treeLabel({ name: "Lào Cai", depth: 0 })).toBe("Lào Cai");
    expect(treeLabel({ name: "Xã", depth: 1 })).toBe("└ Xã");
    expect(treeLabel({ name: "Thôn", depth: 2 })).toBe("    └ Thôn");
  });
});

describe("tra cứu", () => {
  it("allAreas, findArea, areaPathLabel", () => {
    expect(allAreas(tree)).toHaveLength(5);
    expect(findArea(tree, 4)?.name).toBe("Thôn 1");
    expect(findArea(tree, 99)).toBeNull();
    expect(areaPathLabel(tree, need(findArea(tree, 4)))).toBe("Lào Cai › Phong Dụ Hạ › Thôn 1");
  });
});

describe("chọn cha", () => {
  it("trang tạo: tỉnh và xã đang dùng, bỏ nút đã ngừng", () => {
    expect(parentOptions(tree, null).map((o) => o.label)).toEqual([
      "Tỉnh: Hà Nội",
      "Tỉnh: Lào Cai",
      "Xã: Lào Cai › Phong Dụ Hạ",
    ]);
  });
  it("xã chỉ chọn tỉnh; thôn chỉ chọn xã; tỉnh không có cha", () => {
    expect(parentOptions(tree, "COMMUNE").map((o) => o.value)).toEqual([1, 2]);
    expect(parentOptions(tree, "VILLAGE").map((o) => o.value)).toEqual([3]);
    expect(parentOptions(tree, "PROVINCE")).toEqual([]);
  });
  it("giữ cha hiện tại dù đã ngừng dùng", () => {
    expect(parentOptions(tree, "VILLAGE", 5).map((o) => o.value)).toEqual([3, 5]);
  });
  it("parentLevelMap bỏ thôn (thôn không làm cha)", () => {
    expect(parentLevelMap(tree)).toEqual({
      "1": "PROVINCE",
      "2": "PROVINCE",
      "3": "COMMUNE",
      "5": "COMMUNE",
    });
  });
});

describe("trường form", () => {
  it("tạo: cấp, mã, tên bắt buộc", () => {
    const fields = createFields(tree);
    expect(fields.filter((f) => f.required).map((f) => f.name)).toEqual(["level", "code", "name"]);
  });
  it("sửa: mã và cấp chỉ đọc; tỉnh không có ô «Thuộc»", () => {
    const fields = editFields(tree, need(findArea(tree, 2)));
    expect(fields.find((f) => f.name === "code")?.readonly).toBe(true);
    expect(fields.find((f) => f.name === "level_label")?.readonly).toBe(true);
    expect(fields.some((f) => f.name === "parent_id")).toBe(false);
  });
  it("sửa xã: ô «Thuộc» có giá trị hiện tại và chỉ liệt kê tỉnh", () => {
    const parent = editFields(tree, need(findArea(tree, 3))).find((f) => f.name === "parent_id");
    expect(parent?.value).toBe(2);
    expect(parent?.options?.map((o) => o.value)).toEqual([1, 2]);
  });
});
