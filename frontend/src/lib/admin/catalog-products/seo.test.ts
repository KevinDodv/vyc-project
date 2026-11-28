import { describe, expect, it } from "vitest";
import { SEO_DESCRIPTION_LIMIT, SEO_TITLE_LIMIT, seoCount, seoLength } from "./seo";

describe("seoLength", () => {
  it("bỏ khoảng trắng hai đầu, đếm theo ký tự Unicode", () => {
    expect(seoLength("  Quế Văn Yên  ")).toBe(11);
    expect(seoLength("")).toBe(0);
    // Emoji ngoài BMP là hai đơn vị UTF-16 nhưng một ký tự (Python len() cũng đếm một).
    expect(seoLength("🌿")).toBe(1);
  });
});

describe("seoCount tiêu đề (≤ 60, cứng 70)", () => {
  const at = (n: number) => seoCount("a".repeat(n), SEO_TITLE_LIMIT);
  it("đúng 60 vẫn ổn", () => {
    expect(at(60).level).toBe("ok");
    expect(at(60).message).toBe("");
    expect(at(60).label).toBe("60/60 (tối đa 70)");
  });
  it("61 đến 70: cảnh báo nhưng vẫn lưu được", () => {
    expect(at(61).level).toBe("warn");
    expect(at(70).level).toBe("warn");
    expect(at(61).message).toContain("60");
  });
  it("71 trở lên: vượt giới hạn cứng, nói rõ phải bớt bao nhiêu", () => {
    const r = at(75);
    expect(r.level).toBe("over");
    expect(r.message).toContain("bớt 5");
  });
  it("trống là ổn (dùng tiêu đề mặc định)", () => {
    expect(at(0).level).toBe("ok");
  });
});

describe("seoCount mô tả (≤ 160, cứng 170)", () => {
  const at = (n: number) => seoCount("b".repeat(n), SEO_DESCRIPTION_LIMIT);
  it("ngưỡng 160 và 170", () => {
    expect(at(160).level).toBe("ok");
    expect(at(161).level).toBe("warn");
    expect(at(170).level).toBe("warn");
    expect(at(171).level).toBe("over");
  });
  it("chữ có dấu đếm một ký tự mỗi chữ", () => {
    expect(seoCount("ế".repeat(160), SEO_DESCRIPTION_LIMIT).level).toBe("ok");
  });
});
