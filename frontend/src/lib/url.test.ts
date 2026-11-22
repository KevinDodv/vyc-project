import { describe, expect, it } from "vitest";
import { absoluteUrl, canonicalPath, redirectLocation } from "./url";

const ORIGIN = "https://quevanyen.example"; // khớp tests/stubs/astro-env-server.ts

describe("canonicalPath", () => {
  it("không đổi thì trả null", () => {
    expect(canonicalPath("/")).toBeNull();
    expect(canonicalPath("/san-pham/que-10ml")).toBeNull();
  });
  it("bỏ / cuối, đổi chữ hoa", () => {
    expect(canonicalPath("/San-Pham/")).toBe("/san-pham");
    expect(canonicalPath("/san-pham/")).toBe("/san-pham");
  });
  it("/q/ giữ chữ hoa của serial", () => {
    expect(canonicalPath("/q/ABC123/")).toBe("/q/ABC123");
    expect(canonicalPath("/q/ABC123")).toBeNull();
  });
  it("gộp nhiều / ở đầu", () => {
    expect(canonicalPath("//evil.com/")).toBe("/evil.com");
    expect(canonicalPath("///evil.com/")).toBe("/evil.com");
  });
  it("path có \\ hoặc %5C thì ném lỗi (middleware trả 404)", () => {
    expect(() => canonicalPath("/\\evil.com")).toThrow();
    expect(() => canonicalPath("/%5Cevil.com")).toThrow();
    expect(() => canonicalPath("/%5cevil.com")).toThrow();
  });
});

describe("redirectLocation: 301 an toàn", () => {
  const cases = ["//evil.com/", "///evil.com/", "//evil.com", "/San-Pham/", "////a//b", "/", ""];
  it.each(cases)("%j luôn cùng origin với SITE_URL", (input) => {
    expect(new URL(redirectLocation(input, "")).origin).toBe(ORIGIN);
  });
  it("sau canonicalPath, //evil.com/ vẫn cùng origin", () => {
    const next = canonicalPath("//evil.com/");
    expect(next).not.toBeNull();
    expect(new URL(redirectLocation(next as string, "")).origin).toBe(ORIGIN);
  });
  it("ném lỗi với \\ và %5C", () => {
    expect(() => redirectLocation("/\\evil.com", "")).toThrow();
    expect(() => redirectLocation("/%5Cevil.com", "")).toThrow();
    expect(() => redirectLocation("\\\\evil.com", "")).toThrow();
  });
  it("giữ query string (UTM không mất)", () => {
    expect(redirectLocation("/san-pham/moi", "?utm_source=ads&x=1")).toBe(
      `${ORIGIN}/san-pham/moi?utm_source=ads&x=1`,
    );
  });
  it("ký tự ? # trong path bị mã hoá, không tách thành query hay fragment", () => {
    const u = new URL(redirectLocation("/a?b#c", ""));
    expect(u.search).toBe("");
    expect(u.hash).toBe("");
    expect(u.origin).toBe(ORIGIN);
  });
  it("slug mới có dấu được mã hoá", () => {
    expect(redirectLocation(`/san-pham/${encodeURIComponent("tinh-dầu")}`, "")).toBe(
      `${ORIGIN}/san-pham/tinh-d%E1%BA%A7u`,
    );
  });
});

describe("absoluteUrl", () => {
  it("ghép với SITE_URL", () => {
    expect(absoluteUrl("/san-pham/a")).toBe(`${ORIGIN}/san-pham/a`);
  });
  it("//host không thoát ra khỏi origin", () => {
    expect(new URL(absoluteUrl("//evil.com/x.webp")).origin).toBe(ORIGIN);
  });
});
