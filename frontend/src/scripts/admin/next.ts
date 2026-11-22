/** Đích chuyển hướng sau khi đăng nhập. Chỉ nhận đường dẫn trong /quan-ly (chống open redirect,
 *  frontend-seo.md 5.5): bắt đầu bằng "/quan-ly", không "//", không "\" (cả dạng %5C) trong phần path. */
export const LOGIN_PATH = "/quan-ly/dang-nhap";
export const ADMIN_HOME = "/quan-ly";

export function sanitizeNext(value: string | null | undefined): string | null {
  if (!value) return null;
  const [path = "", ...rest] = value.split("?");
  if (path !== "/quan-ly" && !path.startsWith("/quan-ly/")) return null;
  if (path.includes("\\") || /%5c/i.test(path) || path.includes("//")) return null;
  for (const char of value) {
    const code = char.charCodeAt(0);
    if (code < 0x20 || code === 0x7f) return null;
  }
  if (path === LOGIN_PATH) return null;
  return rest.length ? `${path}?${rest.join("?")}` : path;
}
