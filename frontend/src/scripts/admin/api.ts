/** Client gọi /api/v1 từ trình duyệt (frontend-seo.md 5.2). TypeScript thuần, không phụ thuộc framework.
 *  Mọi request không phải GET tự gửi X-CSRFToken lấy từ cookie `csrftoken`; chưa có cookie thì gọi
 *  GET /api/v1/auth/csrf trước. Astro SSR không bao giờ ghi thay trình duyệt. */

const BASE = "/api/v1";
const CSRF_COOKIE = "csrftoken";
const CSRF_HEADER = "X-CSRFToken";
const SAFE_METHODS = new Set(["GET", "HEAD", "OPTIONS"]);

export type ApiMethod = "GET" | "POST" | "PATCH" | "PUT" | "DELETE";

/** Lỗi API theo backend.md 3.2: `{code, message, details}`. `message` hiện nguyên cho người dùng. */
export class ApiRequestError extends Error {
  readonly status: number;
  readonly code: string;
  readonly details: Record<string, unknown>;

  constructor(
    status: number,
    code: string,
    message: string,
    details: Record<string, unknown> = {},
  ) {
    super(message);
    this.name = "ApiRequestError";
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

/** Đọc một cookie từ chuỗi `document.cookie`. Trả null khi không có. */
export function readCookie(name: string, cookieString: string = document.cookie): string | null {
  for (const part of cookieString.split(";")) {
    const idx = part.indexOf("=");
    if (idx === -1) continue;
    if (part.slice(0, idx).trim() !== name) continue;
    const raw = part.slice(idx + 1).trim();
    try {
      return decodeURIComponent(raw);
    } catch {
      return raw;
    }
  }
  return null;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

async function toError(response: Response): Promise<ApiRequestError> {
  let body: unknown = null;
  try {
    body = await response.json();
  } catch {
    // Body không phải JSON (ví dụ 502 từ Caddy): dùng thông báo chung bên dưới.
  }
  if (isRecord(body) && typeof body.code === "string" && typeof body.message === "string") {
    const details = isRecord(body.details) ? body.details : {};
    return new ApiRequestError(response.status, body.code, body.message, details);
  }
  return new ApiRequestError(
    response.status,
    `HTTP_${response.status}`,
    "Hệ thống đang bận hoặc trả lỗi không đọc được, bạn thử lại sau ít phút",
  );
}

/** Gọi GET /api/v1/auth/csrf để Django đặt cookie `csrftoken` (trả 204). */
export async function refreshCsrf(): Promise<void> {
  const response = await fetch(`${BASE}/auth/csrf`, {
    method: "GET",
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) throw await toError(response);
}

async function send(method: ApiMethod, path: string, body: unknown): Promise<Response> {
  const headers: Record<string, string> = { Accept: "application/json" };
  if (!SAFE_METHODS.has(method)) {
    if (!readCookie(CSRF_COOKIE)) await refreshCsrf();
    const token = readCookie(CSRF_COOKIE);
    if (token) headers[CSRF_HEADER] = token;
  }
  const init: RequestInit = { method, headers, credentials: "same-origin" };
  if (body !== undefined) {
    headers["Content-Type"] = "application/json";
    init.body = JSON.stringify(body);
  }
  return fetch(`${BASE}${path}`, init);
}

/** `path` bắt đầu bằng "/" và tính từ /api/v1, ví dụ `request("POST", "/products", {...})`. */
export async function request<T = unknown>(
  method: ApiMethod,
  path: string,
  body?: unknown,
): Promise<T> {
  if (!path.startsWith("/") || path.startsWith("//") || path.includes("\\")) {
    throw new TypeError(`Đường dẫn API không hợp lệ: ${path}`);
  }
  let response = await send(method, path, body);
  if (response.status === 403 && !SAFE_METHODS.has(method)) {
    // Cookie csrftoken cũ hoặc đã bị xoá: lấy token mới rồi thử lại đúng một lần.
    const error = await toError(response.clone());
    if (error.code === "CSRF_FAILED") {
      await refreshCsrf();
      response = await send(method, path, body);
    }
  }
  if (!response.ok) throw await toError(response);
  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

export const api = {
  get: <T = unknown>(path: string) => request<T>("GET", path),
  post: <T = unknown>(path: string, body?: unknown) => request<T>("POST", path, body),
  patch: <T = unknown>(path: string, body?: unknown) => request<T>("PATCH", path, body),
  put: <T = unknown>(path: string, body?: unknown) => request<T>("PUT", path, body),
  delete: <T = unknown>(path: string) => request<T>("DELETE", path),
};
