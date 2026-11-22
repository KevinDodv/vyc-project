import { describe, expect, it } from "vitest";
import { safeJson } from "./safe-json";

describe("safeJson", () => {
  it("không còn ký tự < nào và thay bằng \\u003c", () => {
    const out = safeJson("</script><img src=x onerror=alert(1)>");
    expect(out).not.toContain("<");
    expect(out).toContain("\\u003c/script>");
  });

  it("thay U+2028 và U+2029 bằng 6 ký tự ASCII", () => {
    const out = safeJson("a\u2028b\u2029c");
    expect(out).not.toContain("\u2028");
    expect(out).not.toContain("\u2029");
    expect(out).toContain("\\u2028");
    expect(out).toContain("\\u2029");
  });

  it("vẫn là JSON hợp lệ, JSON.parse trả đúng giá trị gốc", () => {
    const value = {
      name: "Quế </script> & \u2028 \u2029 <!-- x",
      nested: [{ a: "<b>" }],
      n: 12,
      ok: true,
      nil: null,
    };
    expect(JSON.parse(safeJson(value))).toEqual(value);
  });

  it("khoá của object cũng được escape", () => {
    const out = safeJson({ "</script>": 1 });
    expect(out).not.toContain("<");
    expect(JSON.parse(out)).toEqual({ "</script>": 1 });
  });

  it("undefined thành null thay vì trả undefined", () => {
    expect(safeJson(undefined)).toBe("null");
  });
});
