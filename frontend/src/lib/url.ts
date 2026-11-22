import { SITE_URL } from "astro:env/server";

/** Có dấu "\" (hoặc dạng mã hoá %5C) trong đường dẫn: trình duyệt hiểu nó như "/", nên không chuyển hướng. */
const BACKSLASH = /\\|%5c/i;

/** Trả path đã chuẩn hoá (một "/" đầu, chữ thường trừ /q/, không "/" cuối), hoặc null nếu path không cần đổi.
 *  Ném lỗi khi path có "\" (cả dạng %5C) để middleware trả 404. */
export function canonicalPath(pathname: string): string | null {
  if (BACKSLASH.test(pathname)) throw new Error("Đường dẫn chứa dấu gạch ngược");
  let p = pathname.replace(/^\/{2,}/, "/");
  const isTrace = p === "/q" || p.startsWith("/q/");
  if (!isTrace) p = p.toLowerCase();
  if (p.length > 1) p = p.replace(/\/+$/, "") || "/";
  return p === pathname ? null : p;
}

/** URL tuyệt đối cùng origin với SITE_URL, dựng bằng new URL (không ghép chuỗi vào Location).
 *  Nhiều "/" ở đầu được gộp thành một; path có "\" thì ném lỗi. `search` gồm cả "?" hoặc rỗng. */
export function redirectLocation(path: string, search: string): string {
  if (BACKSLASH.test(path)) throw new Error("Đường dẫn chứa dấu gạch ngược");
  const base = new URL(SITE_URL);
  const url = new URL(base.origin);
  url.pathname = `/${path.replace(/^\/+/, "")}`;
  url.search = search;
  if (url.origin !== base.origin) throw new Error("Location khác origin của SITE_URL");
  return url.toString();
}

/** URL tuyệt đối cho canonical, og:url, JSON-LD, luôn cùng origin với SITE_URL (kể cả khi `path` là "//host").
 *  `path` chỉ là đường dẫn, không có query. */
export function absoluteUrl(path: string): string {
  return redirectLocation(path, "");
}
