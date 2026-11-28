import { describe, expect, it } from "vitest";
import {
  type AreaNode,
  allowedAreaLevels,
  areaOptionsFor,
  canApprove,
  canManageSuppliers,
  canQuickAddSupplier,
  duplicateMessage,
  findTwins,
  flattenAreas,
  kindLabel,
  NEEDS_PLOT_HINT,
  normalizeStream,
  type SupplierOut,
  streamLabel,
  streamRule,
  TRADER_STREAM_HINT,
  toSupplierRow,
  villageOptions,
} from "./suppliers";
import { fold } from "./text";

const supplier = (over: Partial<SupplierOut> = {}): SupplierOut => ({
  id: 1,
  code: "NCC-CQ-001",
  name: "Nguyễn Văn Hùng",
  kind: "FARMER",
  phone: null,
  area_id: 7,
  area_name: "Thôn 3, Châu Quế",
  stream: "GENERAL",
  public_consent: false,
  approved: true,
  status: "ACTIVE",
  plots_count: 0,
  created_at: "2026-11-01T00:00:00Z",
  updated_at: "2026-11-01T00:00:00Z",
  ...over,
});

const node = (
  id: number,
  level: string,
  name: string,
  children: AreaNode[] = [],
  status = "ACTIVE",
): AreaNode => ({
  id,
  code: `A${id}`,
  level,
  name,
  parent_id: null,
  former_name: null,
  valid_from: "2025-01-01",
  valid_to: null,
  status,
  children,
});

describe("fold", () => {
  it("bỏ dấu, đ → d, gộp khoảng trắng như backend", () => {
    expect(fold("  Đặng   Văn  LONG ")).toBe("dang van long");
    expect(fold("Nguyễn Văn Hùng")).toBe(fold("nguyen van hung"));
  });
});

describe("quyền", () => {
  it("chỉ OWNER quản lý; cả hai vai thêm nhanh được", () => {
    expect(canManageSuppliers("OWNER")).toBe(true);
    expect(canManageSuppliers("WORKSHOP")).toBe(false);
    expect(canManageSuppliers(undefined)).toBe(false);
    expect(canQuickAddSupplier("WORKSHOP")).toBe(true);
    expect(canQuickAddSupplier("OWNER")).toBe(true);
    expect(canQuickAddSupplier(undefined)).toBe(false);
  });
  it("nút Duyệt: OWNER và còn chờ duyệt", () => {
    expect(canApprove("OWNER", { approved: false })).toBe(true);
    expect(canApprove("OWNER", { approved: true })).toBe(false);
    expect(canApprove("WORKSHOP", { approved: false })).toBe(false);
  });
});

describe("streamRule: khoá luồng theo kiểu", () => {
  it("thương lái: chỉ còn luồng thường, khoá", () => {
    for (const plots of [0, 3]) {
      const rule = streamRule("TRADER", plots);
      expect(rule.locked).toBe(true);
      expect(rule.options).toEqual([{ value: "GENERAL", label: "Luồng thường", disabled: false }]);
      expect(rule.hint).toBe(TRADER_STREAM_HINT);
    }
  });
  it("hộ dân, gia đình chưa có đồi: tắt luồng kiểm soát", () => {
    for (const kind of ["FARMER", "FAMILY"]) {
      const rule = streamRule(kind, 0);
      expect(rule.locked).toBe(false);
      expect(rule.options.find((o) => o.value === "CONTROLLED")?.disabled).toBe(true);
      expect(rule.options.find((o) => o.value === "GENERAL")?.disabled).toBe(false);
      expect(rule.hint).toBe(NEEDS_PLOT_HINT);
    }
  });
  it("có ít nhất 1 đồi đang dùng: chọn tự do, không cần lời nhắc", () => {
    const rule = streamRule("FARMER", 1);
    expect(rule.options.every((o) => !o.disabled)).toBe(true);
    expect(rule.hint).toBe("");
  });
  it("normalizeStream đưa về giá trị hợp lệ", () => {
    expect(normalizeStream("TRADER", 2, "CONTROLLED")).toBe("GENERAL");
    expect(normalizeStream("FARMER", 0, "CONTROLLED")).toBe("GENERAL");
    expect(normalizeStream("FARMER", 1, "CONTROLLED")).toBe("CONTROLLED");
    expect(normalizeStream("FARMER", 1, "GENERAL")).toBe("GENERAL");
    expect(normalizeStream("FARMER", 1, "rác")).toBe("GENERAL");
  });
});

describe("địa bàn", () => {
  const tree = [
    node(1, "PROVINCE", "Yên Bái", [
      node(2, "COMMUNE", "Châu Quế", [
        node(7, "VILLAGE", "Thôn 3"),
        node(8, "VILLAGE", "Khe Hùm", [], "INACTIVE"),
      ]),
      node(3, "COMMUNE", "Đông Cuông", [node(9, "VILLAGE", "Đồng Vối")]),
    ]),
  ];
  it("flattenAreas: bỏ tỉnh và địa bàn ngừng dùng, nhãn «Xã › Thôn»", () => {
    expect(flattenAreas(tree)).toEqual([
      { id: 2, level: "COMMUNE", label: "Châu Quế" },
      { id: 7, level: "VILLAGE", label: "Châu Quế › Thôn 3" },
      { id: 3, level: "COMMUNE", label: "Đông Cuông" },
      { id: 9, level: "VILLAGE", label: "Đông Cuông › Đồng Vối" },
    ]);
  });
  it("hộ dân, gia đình chỉ chọn thôn; thương lái chọn từ xã", () => {
    const areas = flattenAreas(tree);
    expect(allowedAreaLevels("FARMER")).toEqual(["VILLAGE"]);
    expect(areaOptionsFor("FAMILY", areas).map((o) => o.value)).toEqual([7, 9]);
    expect(areaOptionsFor("TRADER", areas).map((o) => o.value)).toEqual([2, 7, 3, 9]);
    expect(villageOptions(areas).map((o) => o.value)).toEqual([7, 9]);
  });
});

describe("findTwins: cảnh báo trùng tên + thôn", () => {
  const self = { id: 1, name: "Nguyễn Văn Hùng", area_id: 7 };
  it("trùng tên không phân biệt dấu và hoa thường ở cùng thôn", () => {
    const twin = supplier({ id: 2, name: "nguyen van  HUNG" });
    expect(findTwins(self, [supplier(), twin]).map((s) => s.id)).toEqual([2]);
  });
  it("khác thôn hoặc khác tên thì không phải bản sao", () => {
    expect(findTwins(self, [supplier({ id: 3, area_id: 8 })])).toEqual([]);
    expect(findTwins(self, [supplier({ id: 4, name: "Nguyễn Văn Hải" })])).toEqual([]);
  });
  it("không tự tính chính mình", () => {
    expect(findTwins(self, [supplier()])).toEqual([]);
  });
  it("duplicateMessage nêu mã và tên", () => {
    const msg = duplicateMessage("Thôn 3, Châu Quế", [supplier({ id: 2, code: "NCC-CQ-002" })]);
    expect(msg).toContain("NCC-CQ-002 Nguyễn Văn Hùng");
    expect(msg).toContain("Thôn 3, Châu Quế");
  });
});

describe("dòng danh sách", () => {
  it("nhãn kiểu, luồng và huy hiệu chờ duyệt", () => {
    const row = toSupplierRow(supplier({ approved: false, kind: "TRADER", stream: "GENERAL" }));
    expect(row).toMatchObject({
      kind: "Thương lái",
      stream: "Luồng thường",
      approval: "Chờ duyệt",
      approved: false,
      status: "ACTIVE",
    });
    expect(toSupplierRow(supplier()).approval).toBe("");
  });
  it("giá trị lạ giữ nguyên chữ", () => {
    expect(kindLabel("X")).toBe("X");
    expect(streamLabel("Y")).toBe("Y");
    expect(toSupplierRow(supplier({ status: "INACTIVE" })).status).toBe("INACTIVE");
  });
});
