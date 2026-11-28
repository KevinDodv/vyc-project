import { describe, expect, it } from "vitest";
import {
  computeScale,
  computeView,
  type HeaderValues,
  headerToCreateBody,
  headerToPatchBody,
  type ItemState,
  isBlankItem,
  itemsToBody,
  missingHeaderFields,
  nonBlankItems,
  normalizeHeader,
  type SavedDraft,
  sameItems,
  sendDraftChanges,
  validateItems,
} from "./recipe-form";

const item = (
  ingredientId: number | null,
  qtyText: string,
  over: Partial<ItemState> = {},
): ItemState => ({
  ingredientId,
  qtyText,
  altGroup: null,
  isOptional: false,
  note: "",
  ...over,
});

const header = (over: Partial<HeaderValues> = {}): HeaderValues => ({
  code: "TD10",
  name: "Tinh dầu 10 ml",
  output_kind: "PRODUCT",
  output_ingredient_id: "",
  base_label: "",
  cure_min_days: "0",
  cure_max_days: "",
  retain_months: "",
  note: "",
  ...over,
});

describe("computeView: % khối lượng và mẻ chuẩn tự cộng", () => {
  it("% từng dòng trên mẻ chuẩn", () => {
    const view = computeView([item(1, "60"), item(2, "30"), item(3, "10")]);
    expect(view.baseCenti).toBe(10_000);
    expect(view.pcts).toEqual(["60,00 %", "30,00 %", "10,00 %"]);
  });
  it("nhóm TT1: mẻ chuẩn lấy phương án nặng nhất, mỗi dòng vẫn chia cho mẻ chuẩn", () => {
    const view = computeView([
      item(1, "50"),
      item(2, "20", { altGroup: 1 }),
      item(3, "30", { altGroup: 1 }),
    ]);
    expect(view.baseCenti).toBe(8_000);
    expect(view.pcts).toEqual(["62,50 %", "25,00 %", "37,50 %"]);
  });
  it("dòng chưa nhập hoặc nhập sai gram hiện «–» và không vào mẻ", () => {
    const view = computeView([item(1, "40"), item(2, ""), item(3, "abc")]);
    expect(view.baseCenti).toBe(4_000);
    expect(view.pcts).toEqual(["100,00 %", "–", "–"]);
  });
  it("chưa có dòng nào", () => {
    expect(computeView([])).toEqual({ baseCenti: 0, pcts: [] });
    expect(computeView([item(1, "")]).pcts).toEqual(["–"]);
  });
});

describe("computeScale: thử scale theo batch_g", () => {
  const labels = (id: number) => `P${id}`;
  const items = [item(1, "60"), item(2, "40", { isOptional: true })];
  it("ô trống thì không hiện gì", () => {
    expect(computeScale(items, "  ", labels)).toEqual({ kind: "empty" });
  });
  it("tính lượng cân gợi ý", () => {
    const view = computeScale(items, "250,5", labels);
    expect(view).toEqual({
      kind: "ok",
      batchText: "250,5",
      rows: [
        { label: "P1", group: "", baseText: "60", suggestedText: "150,3" },
        { label: "P2", group: "Tuỳ chọn", baseText: "40", suggestedText: "100,2" },
      ],
    });
  });
  it("mẻ sai hoặc công thức chưa có gram thì báo lỗi", () => {
    expect(computeScale(items, "0", labels).kind).toBe("error");
    expect(computeScale(items, "abc", labels).kind).toBe("error");
    expect(computeScale([item(1, "")], "100", labels).kind).toBe("error");
  });
  it("nhóm lựa chọn có nhãn TT; mẻ chuẩn lấy phương án nặng nhất", () => {
    const view = computeScale(
      [item(1, "10", { altGroup: 1 }), item(2, "20", { altGroup: 1 })],
      "30",
      labels,
    );
    expect(view.kind === "ok" && view.rows.map((r) => r.group)).toEqual(["Nhóm 1", "Nhóm 1"]);
    // mẻ chuẩn = 20 g; làm 30 g thì dòng 10 g thành 15 g, dòng 20 g thành 30 g
    expect(view.kind === "ok" && view.rows.map((r) => r.suggestedText)).toEqual(["15", "30"]);
  });
});

describe("dòng thành phần", () => {
  it("dòng trống hoàn toàn bị bỏ", () => {
    const rows = [item(null, ""), item(1, "5"), item(null, "  ", { note: " " })];
    expect(isBlankItem(item(null, ""))).toBe(true);
    expect(nonBlankItems(rows)).toEqual([rows[1]]);
  });
  it("validateItems báo dòng đầu tiên sai", () => {
    expect(validateItems([item(1, "5")])).toBeNull();
    expect(validateItems([item(1, "5"), item(null, "3")])).toBe("Dòng 2: chọn phụ liệu");
    expect(validateItems([item(1, "0")])).toBe(
      "Dòng 1: gram phải là số lớn hơn 0 và nhỏ hơn 100 000 000, tối đa 2 số lẻ",
    );
    expect(validateItems([item(1, "100000000")])).toContain("nhỏ hơn 100 000 000");
    expect(validateItems([item(1, "1.234")])).toContain("Dòng 1");
  });
  it("itemsToBody: gram dạng chuỗi hai số lẻ (frontend-seo.md 10), ghi chú trống thành null", () => {
    expect(
      itemsToBody([
        item(7, "12,5", { altGroup: 2, isOptional: true, note: " thơm " }),
        item(8, "3"),
      ]),
    ).toEqual([
      { ingredient_id: 7, qty_g: "12.50", alt_group: 2, is_optional: true, note: "thơm" },
      { ingredient_id: 8, qty_g: "3.00", alt_group: null, is_optional: false, note: null },
    ]);
  });
  it("sameItems so gram theo giá trị và bỏ dòng trống", () => {
    expect(sameItems([item(1, "12.5")], [item(1, "12,50"), item(null, "")])).toBe(true);
    expect(sameItems([item(1, "12.5")], [item(1, "12.6")])).toBe(false);
    expect(sameItems([item(1, "5")], [item(1, "5", { altGroup: 1 })])).toBe(false);
    expect(sameItems([item(1, "5"), item(2, "6")], [item(2, "6"), item(1, "5")])).toBe(false);
  });
});

describe("phần đầu form", () => {
  it("thành phẩm không gửi phụ liệu làm ra", () => {
    const v = header({ output_ingredient_id: "5" });
    expect(normalizeHeader(v).output_ingredient_id).toBe("");
    expect(headerToCreateBody(v).output_ingredient_id).toBeNull();
    const semi = header({ output_kind: "INTERMEDIATE", output_ingredient_id: "5" });
    expect(headerToCreateBody(semi).output_ingredient_id).toBe(5);
  });
  it("body tạo: ô trống thành null, số nguyên thành số", () => {
    expect(headerToCreateBody(header({ cure_max_days: "14", note: " ghi chú " }))).toEqual({
      code: "TD10",
      name: "Tinh dầu 10 ml",
      output_kind: "PRODUCT",
      output_ingredient_id: null,
      base_label: null,
      cure_min_days: 0,
      cure_max_days: 14,
      retain_months: null,
      note: "ghi chú",
    });
  });
  it("số nguyên sai giữ nguyên chuỗi để API báo lỗi theo trường", () => {
    expect(headerToCreateBody(header({ retain_months: "ab" })).retain_months).toBe("ab");
  });
  it("body sửa chỉ có trường đã đổi và không bao giờ có mã", () => {
    const a = header();
    expect(headerToPatchBody(a, a)).toEqual({});
    expect(headerToPatchBody(a, header({ code: "KHAC" }))).toEqual({});
    expect(headerToPatchBody(a, header({ name: "Tên mới", cure_max_days: "10" }))).toEqual({
      name: "Tên mới",
      cure_max_days: 10,
    });
    // xoá giá trị thì gửi null (API cho phép xoá ngày ủ tối đa)
    expect(headerToPatchBody(header({ cure_max_days: "10" }), header())).toEqual({
      cure_max_days: null,
    });
  });
  it("đổi sang thành phẩm thì xoá phụ liệu làm ra", () => {
    const from = header({ output_kind: "INTERMEDIATE", output_ingredient_id: "5" });
    const to = header({ output_kind: "PRODUCT", output_ingredient_id: "5" });
    expect(headerToPatchBody(from, to)).toEqual({
      output_kind: "PRODUCT",
      output_ingredient_id: null,
    });
  });
  it("trường bắt buộc: mã chỉ khi tạo mới", () => {
    const blank = header({ code: "", name: "", cure_min_days: "" });
    expect(missingHeaderFields(blank, true)).toEqual(["code", "name", "cure_min_days"]);
    expect(missingHeaderFields(header({ code: "", name: "" }), false)).toEqual(["name"]);
    expect(missingHeaderFields(header(), true)).toEqual([]);
  });
});

describe("mẻ chuẩn khi không còn dòng nào (SC-VQH)", () => {
  it("giữ mẻ đang lưu, kể cả khi chỉ có dòng trống", () => {
    expect(computeView([], 10_000).baseCenti).toBe(10_000);
    expect(computeView([item(null, "")], 10_000).baseCenti).toBe(10_000);
  });
  it("có dòng thì cộng theo dòng; form mới chưa có gì thì 0", () => {
    expect(computeView([item(1, "5")], 10_000).baseCenti).toBe(500);
    expect(computeView([item(1, "")], 10_000).baseCenti).toBe(0);
    expect(computeView([]).baseCenti).toBe(0);
  });
});

describe("sendDraftChanges", () => {
  const recorder = () => {
    const calls: string[] = [];
    const send = async (method: string, path: string) => {
      calls.push(`${method} ${path}`);
      return null;
    };
    return { calls, send };
  };
  const draft = (): SavedDraft => ({ header: header(), items: [item(1, "5")], baseCenti: 500 });

  it("không đổi gì thì không gửi", async () => {
    const { calls, send } = recorder();
    await sendDraftChanges(7, draft(), header(), [item(1, "5,00")], send);
    expect(calls).toEqual([]);
  });
  it("xoá hết dòng đã lưu rồi thêm lại đúng như cũ thì vẫn PUT lại", async () => {
    const { calls, send } = recorder();
    const saved = draft();
    await sendDraftChanges(7, saved, header(), [], send);
    expect(saved.baseCenti).toBe(500); // máy chủ giữ mẻ hiện có khi không còn dòng
    await sendDraftChanges(7, saved, header(), [item(1, "5")], send);
    expect(calls).toEqual(["PUT /recipes/7/items", "PUT /recipes/7/items"]);
  });
  it("đổi phần đầu rồi đổi lại thì PATCH cả hai lần", async () => {
    const { calls, send } = recorder();
    const saved = draft();
    await sendDraftChanges(7, saved, header({ name: "Mới" }), saved.items, send);
    await sendDraftChanges(7, saved, header(), saved.items, send);
    expect(calls).toEqual(["PATCH /recipes/7", "PATCH /recipes/7"]);
  });
  it("lệnh lỗi thì không ghi nhận; lệnh đã thành công trước đó vẫn được ghi", async () => {
    const saved = draft();
    const failPut = async (method: string) => {
      if (method === "PUT") throw new Error("PUT lỗi");
      return null;
    };
    const next = [item(1, "9")];
    await expect(
      sendDraftChanges(7, saved, header({ name: "Mới" }), next, failPut),
    ).rejects.toThrow("PUT lỗi");
    expect(saved.header.name).toBe("Mới");
    expect(saved.items).toEqual([item(1, "5")]);
    expect(saved.baseCenti).toBe(500);
    const { calls, send } = recorder();
    await sendDraftChanges(7, saved, header({ name: "Mới" }), next, send);
    expect(calls).toEqual(["PUT /recipes/7/items"]);
    expect(saved.baseCenti).toBe(900);
  });
});
