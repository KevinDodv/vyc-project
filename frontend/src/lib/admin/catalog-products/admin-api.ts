/** Gọi /api/v1 từ phía máy chủ Astro cho các trang quản lý (kèm Cookie phiên của người đang xem).
 *  Dùng chung `callApi` của trang công khai nên kết quả chỉ có ok / not_found / unavailable. */

import { API_INTERNAL_URL } from "astro:env/server";
import createClient, { type Client } from "openapi-fetch";
import { forwardHeaders } from "../../api/server";
import type { paths } from "../../api/v1";

export { type ApiOutcome, callApi } from "../../api/server";

const TIMEOUT_MS = 5000;

function serializeQuery(query: Record<string, unknown>): string {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(query)) {
    if (value === undefined || value === null || value === "") continue;
    params.set(key, typeof value === "boolean" ? (value ? "1" : "0") : String(value));
  }
  return params.toString();
}

export function adminApi(request: Request): Client<paths> {
  return createClient<paths>({
    baseUrl: API_INTERNAL_URL,
    headers: forwardHeaders(request, "session"),
    fetch: (input: Request) =>
      fetch(new Request(input, { signal: AbortSignal.timeout(TIMEOUT_MS) })),
    querySerializer: serializeQuery,
  });
}
