import { describe, expect, it } from "vitest";
import { product } from "./fixtures";
import { heightFor, srcset } from "./image";

const img = product().images[0];
if (!img) throw new Error("fixture thiếu ảnh");

describe("image", () => {
  it("srcset theo các bề rộng có thật", () => {
    expect(srcset(img, "avif")).toBe(
      "/media/img/3f/3fa9abc-480.avif 480w, /media/img/3f/3fa9abc-960.avif 960w, /media/img/3f/3fa9abc-1440.avif 1440w",
    );
    expect(srcset({ ...img, widths: [480] }, "webp")).toBe("/media/img/3f/3fa9abc-480.webp 480w");
  });
  it("heightFor giữ tỉ lệ", () => {
    expect(heightFor(img, 480)).toBe(360);
  });
});
