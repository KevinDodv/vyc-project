import { describe, expect, it } from "vitest";
import { addDays, fold, formatIsoDate, matchesQuery, parseIsoDate, todayVn } from "./text";

describe("fold / matchesQuery", () => {
  it("bỏ dấu và đ", () => {
    expect(fold("Đắk Lắk")).toBe("dak lak");
    expect(fold("  Lào Cai ")).toBe("lao cai");
  });
  it("khớp không dấu, không phân biệt hoa thường, nhiều trường", () => {
    expect(matchesQuery("lao", "Lào Cai")).toBe(true);
    expect(matchesQuery("VQ", "Vỏ quế", "VQ")).toBe(true);
    expect(matchesQuery("xyz", "Lào Cai", null)).toBe(false);
    expect(matchesQuery("", "bất kỳ")).toBe(true);
  });
});

describe("ngày", () => {
  it("formatIsoDate", () => {
    expect(formatIsoDate("2025-07-01")).toBe("01/07/2025");
    expect(formatIsoDate(null)).toBe("");
    expect(formatIsoDate("lạ")).toBe("lạ");
  });
  it("parseIsoDate chỉ nhận ngày thật", () => {
    expect(parseIsoDate("2025-07-01")).toBe("2025-07-01");
    expect(parseIsoDate("2025-02-30")).toBeNull();
    expect(parseIsoDate("01/07/2025")).toBeNull();
    expect(parseIsoDate("")).toBeNull();
    expect(parseIsoDate(null)).toBeNull();
  });
  it("todayVn theo giờ Việt Nam (UTC+7)", () => {
    expect(todayVn(new Date("2026-11-22T18:00:00Z"))).toBe("2026-11-23");
    expect(todayVn(new Date("2026-11-22T16:59:00Z"))).toBe("2026-11-22");
  });
  it("addDays qua ranh giới tháng", () => {
    expect(addDays("2026-03-01", -1)).toBe("2026-02-28");
    expect(addDays("2026-12-31", 1)).toBe("2027-01-01");
  });
});
