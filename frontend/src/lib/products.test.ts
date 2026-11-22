import { describe, expect, it } from "vitest";
import { product } from "./fixtures";
import { mergeFeatured } from "./products";

const p = (slug: string) => product({ slug });

describe("mergeFeatured", () => {
  it("giữ nguyên thứ tự nổi bật rồi bù theo slug, không trùng, cắt còn 6", () => {
    const out = mergeFeatured([p("b"), p("a")], [p("a"), p("c"), p("d"), p("e"), p("f"), p("g")]);
    expect(out.map((x) => x.slug)).toEqual(["b", "a", "c", "d", "e", "f"]);
  });
  it("nổi bật rỗng thì lấy sản phẩm mới cập nhật", () => {
    expect(mergeFeatured([], [p("a"), p("b")]).map((x) => x.slug)).toEqual(["a", "b"]);
  });
  it("đã đủ 6 nổi bật thì không lấy thêm", () => {
    const six = ["1", "2", "3", "4", "5", "6"].map(p);
    expect(mergeFeatured(six, [p("x")]).map((x) => x.slug)).toEqual(["1", "2", "3", "4", "5", "6"]);
  });
});
