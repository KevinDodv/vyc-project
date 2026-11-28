import { describe, expect, it, vi } from "vitest";
import { type Plot, plotLabel, plotOptions } from "./certificate";
import { plotChoices } from "./certificate-form";
import { collectPages, findPlots } from "./lookup";

const plot = (id: number, status = "ACTIVE", supplier_id = 1): Plot => ({
  id,
  code: `D-CQ-0001-${id}`,
  supplier_id,
  area_id: 1,
  area_name: "Thôn 3",
  area_ha: null,
  planted_year: null,
  lat: null,
  lng: null,
  photo_urls: [],
  is_default: false,
  status,
  created_at: "2026-11-01T00:00:00Z",
  updated_at: "2026-11-01T00:00:00Z",
});

describe("ô chọn đồi", () => {
  it("nhãn theo mã, thôn, diện tích; ghi rõ đồi ngừng dùng", () => {
    expect(plotLabel({ ...plot(1), area_ha: 1.5 })).toBe("D-CQ-0001-1 – Thôn 3 · 1,5 ha");
    expect(plotLabel(plot(2, "INACTIVE"))).toBe("D-CQ-0001-2 – Thôn 3 (ngừng dùng)");
  });
  it("chỉ đồi đang dùng, cộng đồi đang gắn", () => {
    const plots = [plot(1), plot(2, "INACTIVE"), plot(3, "INACTIVE")];
    expect(plotOptions(plots, null).map((o) => o.value)).toEqual(["1"]);
    expect(plotOptions(plots, 3).map((o) => o.value)).toEqual(["1", "3"]);
  });
  it("mục đầu luôn rỗng: chưa chọn người bán, không có đồi, lỗi tải", async () => {
    const load = vi.fn(async () => [plot(1)]);
    expect(await plotChoices("", null, load)).toHaveLength(1);
    expect(load).not.toHaveBeenCalled();
    expect((await plotChoices("1", null, load)).map((o) => o.value)).toEqual(["", "1"]);
    expect((await plotChoices("1", null, async () => []))[0]?.label).toContain("chưa có đồi");
    const failed = await plotChoices("1", null, async () => Promise.reject(new Error("502")));
    expect(failed).toEqual([{ value: "", label: expect.stringContaining("Chưa tải được") }]);
  });
});

describe("collectPages", () => {
  it("gom đủ mọi trang", async () => {
    const pages = [[1, 2], [3]];
    const got = await collectPages(async (p) => ({ items: pages[p - 1] ?? [], total: 3 }));
    expect(got).toEqual([1, 2, 3]);
  });
  it("một trang lỗi thì trả null", async () => {
    expect(await collectPages(async (p) => (p === 1 ? { items: [1], total: 2 } : null))).toBeNull();
  });
});

describe("findPlots", () => {
  const sellers = Array.from({ length: 20 }, (_, i) => ({ id: i + 1, plots_count: i ? 1 : 0 }));
  it("hỏi người bán có đồi trước và dừng khi đủ", async () => {
    const fetchPlots = vi.fn(async (id: number) => [plot(id * 10, "ACTIVE", id)]);
    const out = await findPlots(sellers, [30, null], fetchPlots);
    expect(out.found.get(30)?.supplier_id).toBe(3);
    expect(out.bySupplier.has(3)).toBe(true);
    expect(fetchPlots).toHaveBeenCalledTimes(8);
    expect(fetchPlots).not.toHaveBeenCalledWith(1);
  });
  it("vẫn tới được người bán chỉ còn đồi ngừng dùng", async () => {
    const out = await findPlots(sellers, [10], async (id) => [plot(id * 10, "INACTIVE", id)]);
    expect(out.found.has(10)).toBe(true);
  });
  it("không cần tra thì không gọi; cả lượt lỗi thì thôi", async () => {
    const fetchPlots = vi.fn(async () => null);
    await findPlots(sellers, [null], fetchPlots);
    expect(fetchPlots).not.toHaveBeenCalled();
    expect((await findPlots(sellers, [10], fetchPlots)).found.size).toBe(0);
    expect(fetchPlots).toHaveBeenCalledTimes(8);
  });
});
