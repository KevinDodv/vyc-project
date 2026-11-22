import { API_INTERNAL_URL } from "astro:env/server";
import createClient, { type Client } from "openapi-fetch";
import type { paths as PublicPaths } from "./public";

/** "anon": không chuyển Cookie (HTML giống nhau cho mọi khách, cache `public` được).
 *  "session": thêm Cookie (chỉ /q/ và /quan-ly, để Django biết người đang xem là nhân viên). */
export type ForwardMode = "anon" | "session";

const TIMEOUT_MS = 3000;

/** Header chung: chuyển NGUYÊN X-Forwarded-For nhận từ Caddy, không nối thêm, không sửa
 *  (frontend-seo.md 5.2). Không có header này (dev không qua Caddy) thì không gửi; Django dùng REMOTE_ADDR. */
export function forwardHeaders(request: Request, mode: ForwardMode): Record<string, string> {
  const headers: Record<string, string> = { Accept: "application/json" };
  const xff = request.headers.get("x-forwarded-for");
  if (xff) headers["X-Forwarded-For"] = xff;
  if (mode === "session") {
    const cookie = request.headers.get("cookie");
    if (cookie) headers.Cookie = cookie;
  }
  return headers;
}

/** Query theo kiểu Django Ninja: boolean thành 1/0 (?featured=1), bỏ giá trị undefined. */
function serializeQuery(query: Record<string, unknown>): string {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(query)) {
    if (value === undefined || value === null) continue;
    params.set(key, typeof value === "boolean" ? (value ? "1" : "0") : String(value));
  }
  return params.toString();
}

/** Timeout riêng cho từng lần gọi (mỗi lần 3 giây), không dùng chung một tín hiệu cho cả client. */
function fetchWithTimeout(input: Request): Promise<Response> {
  return fetch(new Request(input, { signal: AbortSignal.timeout(TIMEOUT_MS) }));
}

/** /api/public. mode "anon" cho trang nội dung, "session" cho /q/ (BR-18). */
export function publicApi(request: Request, mode: ForwardMode): Client<PublicPaths> {
  return createClient<PublicPaths>({
    baseUrl: API_INTERNAL_URL,
    headers: forwardHeaders(request, mode),
    fetch: fetchWithTimeout,
    querySerializer: serializeQuery,
  });
}

export type ApiOutcome<T> =
  | { kind: "ok"; data: T }
  | { kind: "not_found" }
  /** 5xx, 429, quá giờ, lỗi mạng hoặc body sai kiểu: trang trả 503 + no-store (mục 5.2). */
  | { kind: "unavailable"; retryAfter: string };

const DEFAULT_RETRY_AFTER = "30";

/** Gom mọi kết quả của một lần gọi về ba trường hợp mà trang công khai xử lý.
 *  Không có nhánh «lỗi thì render trang rỗng». */
export async function callApi<T>(
  call: () => Promise<{ data?: T; response: Response }>,
): Promise<ApiOutcome<T>> {
  try {
    const { data, response } = await call();
    if (response.status === 404) return { kind: "not_found" };
    if (response.status === 429) {
      return { kind: "unavailable", retryAfter: response.headers.get("retry-after") || "60" };
    }
    if (!response.ok || data === undefined) {
      return { kind: "unavailable", retryAfter: DEFAULT_RETRY_AFTER };
    }
    return { kind: "ok", data };
  } catch {
    return { kind: "unavailable", retryAfter: DEFAULT_RETRY_AFTER };
  }
}
