import { describe, expect, it } from "vitest";
import { sanitizeNext } from "../../src/scripts/admin/next";
import { readProductForm } from "../../src/scripts/admin/product-form";

describe("sanitizeNext", () => {
  it.each([
    ["/quan-ly", "/quan-ly"],
    ["/quan-ly/san-pham", "/quan-ly/san-pham"],
    ["/quan-ly/san-pham?a=1&b=http://x", "/quan-ly/san-pham?a=1&b=http://x"],
  ])("nhận %s", (input, expected) => {
    expect(sanitizeNext(input)).toBe(expected);
  });

  it.each([
    null,
    undefined,
    "",
    "/",
    "//evil.com",
    "/\\evil.com",
    "https://evil.com",
    "/quan-ly//evil.com",
    "/quan-ly/\\evil.com",
    "/quan-ly/%5Cevil.com",
    "/quan-lyx",
    "/san-pham",
    "/quan-ly/dang-nhap",
    "/quan-ly/a\nb",
    "javascript:alert(1)",
  ])("bỏ %j", (input) => {
    expect(sanitizeNext(input)).toBeNull();
  });
});

function formOf(values: Record<string, string>): FormData {
  const data = new FormData();
  for (const [key, value] of Object.entries(values)) data.set(key, value);
  return data;
}

const VALID = {
  sku: "TD10",
  name: "Tinh dầu quế",
  slug: "tinh-dau-que",
  goods_type_id: "2",
  size_label: "10 ml",
  unit: "chai",
  retail_price: "",
  short_desc: "",
};

describe("readProductForm", () => {
  it("form hợp lệ thì trả thân request, bỏ trường trống", () => {
    expect(readProductForm(formOf(VALID))).toEqual({
      sku: "TD10",
      name: "Tinh dầu quế",
      slug: "tinh-dau-que",
      goods_type_id: 2,
      size_label: "10 ml",
      unit: "chai",
    });
  });
  it("giá là số nguyên", () => {
    expect(readProductForm(formOf({ ...VALID, retail_price: "150000" }))).toMatchObject({
      retail_price: 150000,
    });
    expect(typeof readProductForm(formOf({ ...VALID, retail_price: "1.5" }))).toBe("string");
  });
  it("slug sai thì báo lỗi", () => {
    expect(typeof readProductForm(formOf({ ...VALID, slug: "Tinh Dầu" }))).toBe("string");
  });
  it("thiếu trường thì báo lỗi", () => {
    expect(typeof readProductForm(formOf({ ...VALID, sku: " " }))).toBe("string");
    expect(typeof readProductForm(formOf({ ...VALID, goods_type_id: "" }))).toBe("string");
  });
});
