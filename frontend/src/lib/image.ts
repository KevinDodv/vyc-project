import type { components } from "./api/public";

export type ImageRef = components["schemas"]["ImageRef"];

/** Đường dẫn file của một bề rộng: /media/img/{key}-{w}.{ext}. Backend không trả từng URL (frontend-seo.md 4.3). */
function variantPath(img: ImageRef, w: number, ext: "avif" | "webp"): string {
  return `/media/img/${img.key}-${w}.${ext}`;
}

/** → "/media/img/3f/3fa9…-480.avif 480w, /media/img/3f/3fa9…-960.avif 960w, …" */
export function srcset(img: ImageRef, ext: "avif" | "webp"): string {
  return img.widths.map((w) => `${variantPath(img, w, ext)} ${w}w`).join(", ");
}

/** Chiều cao giữ tỉ lệ w/h của ảnh gốc, làm tròn. */
export function heightFor(img: ImageRef, w: number): number {
  return Math.round((w * img.h) / img.w);
}
