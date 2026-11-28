/** Gọi GET /api/v1 từ máy chủ Astro cho các màn danh mục PH1a (task #93).
 *  Chuyển Cookie phiên của người xem để Django biết vai; chỉ đọc, mọi lệnh ghi do trình duyệt gửi
 *  (frontend-seo.md 5.2). */

import { API_INTERNAL_URL } from "astro:env/server";
import { LOGIN_PATH, sanitizeNext } from "../../../scripts/admin/next";
import { forwardHeaders } from "../../api/server";

export type FetchOutcome<T> =
  | { kind: "ok"; data: T }
  | { kind: "not_found" }
  | { kind: "unauthorized" }
  /** 5xx, 403, 429, quá giờ, lỗi mạng hoặc body không phải JSON: trang báo «chưa tải được», không hiện danh sách rỗng. */
  | { kind: "unavailable" };

const TIMEOUT_MS = 3000;

export function buildApiUrl(path: string, query: Record<string, string | undefined> = {}): URL {
  const url = new URL(`/api/v1${path}`, API_INTERNAL_URL);
  for (const [key, value] of Object.entries(query)) {
    if (value !== undefined && value !== "") url.searchParams.set(key, value);
  }
  return url;
}

export async function getJson<T>(
  request: Request,
  path: string,
  query: Record<string, string | undefined> = {},
  fetcher: typeof fetch = fetch,
): Promise<FetchOutcome<T>> {
  try {
    const response = await fetcher(buildApiUrl(path, query), {
      method: "GET",
      headers: forwardHeaders(request, "session"),
      redirect: "manual",
      signal: AbortSignal.timeout(TIMEOUT_MS),
    });
    if (response.status === 404) return { kind: "not_found" };
    if (response.status === 401) return { kind: "unauthorized" };
    if (!response.ok) return { kind: "unavailable" };
    return { kind: "ok", data: (await response.json()) as T };
  } catch {
    return { kind: "unavailable" };
  }
}

/** Đường dẫn trang đăng nhập kèm `next` là trang đang xem (phiên hết hạn giữa chừng). */
export function loginUrl(url: URL): string {
  const next = sanitizeNext(url.pathname + url.search);
  return next ? `${LOGIN_PATH}?next=${encodeURIComponent(next)}` : LOGIN_PATH;
}
