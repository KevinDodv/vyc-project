import { describe, expect, it } from "vitest";
import { isValidSlug, SLUG_MAX, slugify } from "./slug";

describe("slugify", () => {
  it("bỏ dấu tiếng Việt, đ thành d, chữ thường, nối bằng gạch", () => {
    expect(slugify("Tinh dầu quế Văn Yên 10 ml")).toBe("tinh-dau-que-van-yen-10-ml");
    expect(slugify("Đồi quế Đại Sơn")).toBe("doi-que-dai-son");
  });
  it("gom ký tự lạ và khoảng trắng thành một gạch, bỏ gạch ở hai đầu", () => {
    expect(slugify("  Trà quế (túi lọc) – 20g!! ")).toBe("tra-que-tui-loc-20g");
    expect(slugify("---a___b---")).toBe("a-b");
  });
  it("nhận cả chữ gõ dạng tổ hợp (NFD)", () => {
    expect(slugify("Quế Văn Yên")).toBe("que-van-yen");
  });
  it("tên rỗng hoặc toàn ký tự lạ cho chuỗi rỗng", () => {
    expect(slugify("")).toBe("");
    expect(slugify("!!!")).toBe("");
  });
  it("cắt ở giới hạn 120 và không để gạch ở cuối", () => {
    const long = `${"a".repeat(119)} b`;
    const slug = slugify(long);
    expect(slug.length).toBeLessThanOrEqual(SLUG_MAX);
    expect(slug.endsWith("-")).toBe(false);
    expect(isValidSlug(slug)).toBe(true);
  });
  it("kết quả luôn hợp lệ khi không rỗng", () => {
    for (const name of ["Sáp thơm quế", "Q100 – Tinh dầu 100%", "Ống quế 30cm"]) {
      expect(isValidSlug(slugify(name))).toBe(true);
    }
  });
});

describe("isValidSlug", () => {
  it("khớp luật của backend", () => {
    expect(isValidSlug("tinh-dau-que")).toBe(true);
    expect(isValidSlug("q100")).toBe(true);
    expect(isValidSlug("")).toBe(false);
    expect(isValidSlug("Tinh-Dau")).toBe(false);
    expect(isValidSlug("tinh--dau")).toBe(false);
    expect(isValidSlug("-tinh")).toBe(false);
    expect(isValidSlug("tinh-")).toBe(false);
    expect(isValidSlug("tinh dầu")).toBe(false);
    expect(isValidSlug("a".repeat(121))).toBe(false);
  });
});
