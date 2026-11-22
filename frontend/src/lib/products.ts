import type { PublicProductOut } from "./seo";

export const HOME_LIMIT = 6;

/** Trang chủ (frontend-seo.md 5.3): giữ nguyên thứ tự API trả cho nhóm nổi bật (không tự sắp),
 *  rồi nối các sản phẩm mới cập nhật chưa có trong nhóm đó (so theo slug), cắt còn `limit`. */
export function mergeFeatured(
  featured: PublicProductOut[],
  recent: PublicProductOut[],
  limit = HOME_LIMIT,
): PublicProductOut[] {
  const seen = new Set<string>();
  const out: PublicProductOut[] = [];
  for (const p of [...featured, ...recent]) {
    if (seen.has(p.slug)) continue;
    seen.add(p.slug);
    out.push(p);
    if (out.length === limit) break;
  }
  return out;
}
