import { API_INTERNAL_URL } from "astro:env/server";
import type { APIContext, MiddlewareHandler } from "astro";
import { forwardHeaders } from "./lib/api/server";
import { CACHE_PRIVATE } from "./lib/cache";
import { LOGIN_PATH, sanitizeNext } from "./scripts/admin/next";

/** Người dùng đang đăng nhập, theo `GET /api/v1/auth/me` (backend.md 4.1). */
export type AuthUser = {
  id: number;
  username: string;
  full_name: string;
  role: "OWNER" | "WORKSHOP";
};

declare global {
  // Mở rộng kiểu `Astro.locals` (frontend-seo.md 5.5). Nên dời sang src/env.d.ts khi có người giữ file đó.
  namespace App {
    interface Locals {
      user?: AuthUser;
    }
  }
}

/** Màn chỉ OWNER vào được (TK mục 2 và 7.1). Chỉ là lớp báo sớm: quyền thật kiểm ở API.
 *  Không có /quan-ly/thu-luu-huong, /mau-luu, /cong-thuc, /phu-lieu: màn hai vai dùng chung (frontend-seo.md 5.5). */
export const OWNER_ONLY_PREFIXES = [
  "/quan-ly/danh-muc",
  "/quan-ly/bang-gia",
  "/quan-ly/cuon-tem",
  "/quan-ly/tra-cuu",
  "/quan-ly/khach-hang",
  "/quan-ly/bao-cao",
  "/quan-ly/vung-nguyen-lieu",
  // Màn tối thiểu của khung code (luồng mẫu tạo sản phẩm, publish): ghi sản phẩm chỉ OWNER (backend.md 4.3).
  "/quan-ly/san-pham",
] as const;

const FORBIDDEN_PATH = "/quan-ly/khong-co-quyen";
const UNAVAILABLE_PATH = "/500";
const AUTH_TIMEOUT_MS = 3000;

type PathInfo = { kind: "other" } | { kind: "invalid" } | { kind: "admin"; segments: string[] };

/** Chuẩn hoá đường dẫn như bộ định tuyến sẽ hiểu: giải mã %xx, coi "\" như "/", bỏ "//", "." và "..", chữ thường.
 *  Không so khớp trên chuỗi thô, nếu không `/quan-ly/danh-%6duc` sẽ lọt qua kiểm vai. */
export function parseAdminPath(pathname: string): PathInfo {
  let decoded: string;
  try {
    decoded = decodeURIComponent(pathname);
  } catch {
    const first = pathname.split("/").find(Boolean)?.toLowerCase() ?? "";
    return first === "quan-ly" || first.includes("%") ? { kind: "invalid" } : { kind: "other" };
  }
  const segments: string[] = [];
  for (const raw of decoded.replaceAll("\\", "/").split("/")) {
    const seg = raw.toLowerCase();
    if (seg === "" || seg === ".") continue;
    if (seg === "..") segments.pop();
    else segments.push(seg);
  }
  return segments[0] === "quan-ly" ? { kind: "admin", segments } : { kind: "other" };
}

function startsWithSegments(segments: string[], prefix: string): boolean {
  const want = prefix.split("/").filter(Boolean);
  return want.every((seg, i) => segments[i] === seg);
}

export function isOwnerOnly(segments: string[]): boolean {
  return OWNER_ONLY_PREFIXES.some((prefix) => startsWithSegments(segments, prefix));
}

function isAuthUser(value: unknown): value is AuthUser {
  if (typeof value !== "object" || value === null) return false;
  const v = value as Record<string, unknown>;
  return (
    typeof v.id === "number" &&
    typeof v.username === "string" &&
    typeof v.full_name === "string" &&
    (v.role === "OWNER" || v.role === "WORKSHOP")
  );
}

type MeResult = { kind: "ok"; user: AuthUser } | { kind: "anonymous" } | { kind: "failed" };

/** 200 và đúng kiểu: ok. 401: chưa đăng nhập. Mọi thứ khác (403, 5xx, quá giờ, lỗi mạng, body sai kiểu): failed. */
async function fetchMe(request: Request): Promise<MeResult> {
  try {
    const response = await fetch(new URL("/api/v1/auth/me", API_INTERNAL_URL), {
      method: "GET",
      headers: forwardHeaders(request, "session"),
      redirect: "manual",
      signal: AbortSignal.timeout(AUTH_TIMEOUT_MS),
    });
    if (response.status === 401) return { kind: "anonymous" };
    if (response.status !== 200) return { kind: "failed" };
    const body: unknown = await response.json();
    return isAuthUser(body) ? { kind: "ok", user: body } : { kind: "failed" };
  } catch {
    return { kind: "failed" };
  }
}

/** Header cho mọi trả lời dưới /quan-ly (frontend-seo.md mục 2): không cache, không lập chỉ mục. */
function withAdminHeaders(response: Response): Response {
  try {
    response.headers.set("Cache-Control", CACHE_PRIVATE);
    response.headers.set("X-Robots-Tag", "noindex, nofollow");
    return response;
  } catch {
    // Header của Response bất biến (ví dụ trả lời chuyển tiếp): dựng bản sao.
    const copy = new Response(response.body, response);
    copy.headers.set("Cache-Control", CACHE_PRIVATE);
    copy.headers.set("X-Robots-Tag", "noindex, nofollow");
    return copy;
  }
}

/** Ép mã trạng thái, phòng trang được rewrite không tự đặt đúng mã. */
function withStatus(response: Response, status: number): Response {
  if (response.status === status) return response;
  return new Response(response.body, { status, headers: response.headers });
}

/** Fail-closed: không xác minh được người dùng thì render 500.astro với mã 503, không render trang được yêu cầu. */
async function unavailable(context: APIContext): Promise<Response> {
  const response = withStatus(await context.rewrite(UNAVAILABLE_PATH), 503);
  if (!response.headers.has("Retry-After")) response.headers.set("Retry-After", "30");
  return response;
}

export const onRequest: MiddlewareHandler = async (context, next) => {
  const info = parseAdminPath(context.url.pathname);
  if (info.kind === "other") return next();

  if (info.kind === "invalid") {
    return withAdminHeaders(new Response("Không tìm thấy", { status: 404 }));
  }

  const { segments } = info;
  const isLoginPage = segments.length === 2 && segments[1] === "dang-nhap";
  if (isLoginPage) return withAdminHeaders(await next());

  let user = context.locals.user;
  if (!user) {
    const me = await fetchMe(context.request);
    if (me.kind === "failed") return withAdminHeaders(await unavailable(context));
    if (me.kind === "anonymous") {
      const next_ = sanitizeNext(context.url.pathname + context.url.search);
      const target = next_ ? `${LOGIN_PATH}?next=${encodeURIComponent(next_)}` : LOGIN_PATH;
      return withAdminHeaders(context.redirect(target, 302));
    }
    user = me.user;
    context.locals.user = user;
  }

  if (isOwnerOnly(segments) && user.role !== "OWNER") {
    return withAdminHeaders(withStatus(await context.rewrite(FORBIDDEN_PATH), 403));
  }

  return withAdminHeaders(await next());
};
