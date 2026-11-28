/** Slug sản phẩm: chữ thường không dấu, số, gạch nối (khớp `Slug` của backend: ^[a-z0-9]+(?:-[a-z0-9]+)*$, ≤ 120). */

export const SLUG_MAX = 120;
export const SLUG_PATTERN = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

export function isValidSlug(slug: string): boolean {
  return slug.length > 0 && slug.length <= SLUG_MAX && SLUG_PATTERN.test(slug);
}

/** Sinh slug từ tên: bỏ dấu tiếng Việt (đ → d), chữ thường, mọi đoạn ký tự lạ thành một dấu «-».
 *  Quá dài thì cắt rồi bỏ «-» thừa ở cuối. Tên rỗng hoặc toàn ký tự lạ cho chuỗi rỗng. */
export function slugify(name: string): string {
  const base = name
    .normalize("NFD")
    .replace(/\p{M}+/gu, "")
    .replace(/đ/g, "d")
    .replace(/Đ/g, "D")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
  return base.slice(0, SLUG_MAX).replace(/-+$/g, "");
}
