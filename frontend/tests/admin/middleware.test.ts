import type { APIContext } from "astro";
import { afterEach, describe, expect, it, vi } from "vitest";
import {
  type AuthUser,
  isOwnerOnly,
  OWNER_ONLY_PREFIXES,
  onRequest,
  parseAdminPath,
} from "../../src/middleware";

const OWNER: AuthUser = { id: 1, username: "chu", full_name: "Chủ", role: "OWNER" };
const WORKSHOP: AuthUser = { id: 2, username: "xuong", full_name: "Xưởng", role: "WORKSHOP" };

function json(status: number, body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

/** Dựng context giả: rewrite trả Response ghi lại đích, redirect trả 302 kèm Location. */
function makeContext(path: string, cookie = "sessionid=abc") {
  const url = new URL(`http://site.test${path}`);
  const rewrites: string[] = [];
  const context = {
    url,
    request: new Request(url, { headers: cookie ? { cookie } : {} }),
    locals: {} as App.Locals,
    redirect: (to: string, status = 302) =>
      new Response(null, { status, headers: { Location: to } }),
    rewrite: async (to: string) => {
      rewrites.push(to);
      return new Response(`rewrite:${to}`, { status: 200 });
    },
  };
  return { context: context as unknown as APIContext, rewrites };
}

async function run(path: string, cookie?: string) {
  const { context, rewrites } = makeContext(path, cookie);
  const next = vi.fn(async () => new Response("trang", { status: 200 }));
  const response = await onRequest(context, next);
  return { response: response as Response, next, rewrites, locals: context.locals };
}

function mockMe(impl: () => Promise<Response>) {
  const fetchMock = vi.fn(impl);
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("middleware /quan-ly: đăng nhập", () => {
  it("chưa đăng nhập (401) thì 302 sang trang đăng nhập kèm next", async () => {
    mockMe(async () => json(401, { code: "UNAUTHORIZED", message: "x", details: {} }));
    const { response, next } = await run("/quan-ly/san-pham?x=1");
    expect(response.status).toBe(302);
    expect(response.headers.get("Location")).toBe(
      `/quan-ly/dang-nhap?next=${encodeURIComponent("/quan-ly/san-pham?x=1")}`,
    );
    expect(next).not.toHaveBeenCalled();
  });

  it("gửi Cookie của request tới /api/v1/auth/me", async () => {
    const fetchMock = mockMe(async () => json(200, OWNER));
    await run("/quan-ly", "sessionid=zzz");
    const [url, init] = fetchMock.mock.calls[0] as unknown as [URL, RequestInit];
    expect(String(url)).toBe("http://backend:8000/api/v1/auth/me");
    expect((init.headers as Record<string, string>).Cookie).toBe("sessionid=zzz");
  });

  it("đăng nhập rồi thì gán locals.user và cho qua", async () => {
    mockMe(async () => json(200, OWNER));
    const { response, next, locals } = await run("/quan-ly");
    expect(response.status).toBe(200);
    expect(next).toHaveBeenCalledOnce();
    expect(locals.user).toEqual(OWNER);
  });

  it("trang đăng nhập không cần phiên và không gọi auth/me", async () => {
    const fetchMock = mockMe(async () => json(500, {}));
    const { response, next } = await run("/quan-ly/dang-nhap");
    expect(response.status).toBe(200);
    expect(next).toHaveBeenCalledOnce();
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("next không hợp lệ thì bỏ, không chuyển hướng ra ngoài", async () => {
    mockMe(async () => json(401, {}));
    const { response } = await run("/quan-ly//evil.com");
    expect(response.headers.get("Location")).toBe("/quan-ly/dang-nhap");
  });
});

describe("middleware /quan-ly: fail-closed khi auth/me lỗi", () => {
  const cases: [string, () => Promise<Response>][] = [
    ["5xx", async () => json(500, {})],
    ["503", async () => json(503, {})],
    ["403", async () => json(403, {})],
    ["429", async () => json(429, {})],
    ["3xx", async () => new Response(null, { status: 302, headers: { Location: "/x" } })],
    ["body sai kiểu", async () => json(200, { id: "1", role: "ADMIN" })],
    ["body không phải JSON", async () => new Response("<html>", { status: 200 })],
    ["role lạ", async () => json(200, { ...OWNER, role: "SUPERUSER" })],
    [
      "lỗi mạng",
      async () => {
        throw new TypeError("fetch failed");
      },
    ],
    [
      "quá giờ",
      async () => {
        throw new DOMException("timeout", "TimeoutError");
      },
    ],
  ];

  it.each(cases)("%s thì 503, không render trang, không gán user", async (_name, impl) => {
    mockMe(impl);
    const { response, next, rewrites, locals } = await run("/quan-ly/san-pham");
    expect(response.status).toBe(503);
    expect(rewrites).toEqual(["/500"]);
    expect(next).not.toHaveBeenCalled();
    expect(locals.user).toBeUndefined();
    expect(response.headers.get("Cache-Control")).toBe("private, no-store");
  });
});

describe("middleware /quan-ly: vai", () => {
  it("WORKSHOP vào trang OWNER-only thì 403 và không render trang", async () => {
    mockMe(async () => json(200, WORKSHOP));
    const { response, next, rewrites } = await run("/quan-ly/danh-muc/khu-vuc");
    expect(response.status).toBe(403);
    expect(rewrites).toEqual(["/quan-ly/khong-co-quyen"]);
    expect(next).not.toHaveBeenCalled();
  });

  it.each(OWNER_ONLY_PREFIXES)("WORKSHOP bị chặn ở %s", async (prefix) => {
    mockMe(async () => json(200, WORKSHOP));
    const { response } = await run(prefix);
    expect(response.status).toBe(403);
  });

  it("OWNER vào được trang OWNER-only", async () => {
    mockMe(async () => json(200, OWNER));
    const { response, next } = await run("/quan-ly/vung-nguyen-lieu");
    expect(response.status).toBe(200);
    expect(next).toHaveBeenCalledOnce();
  });

  it("WORKSHOP vào được màn hai vai dùng chung (thu-luu-huong, mau-luu)", async () => {
    mockMe(async () => json(200, WORKSHOP));
    for (const path of ["/quan-ly/thu-luu-huong", "/quan-ly/mau-luu", "/quan-ly/cong-thuc"]) {
      const { response, next } = await run(path);
      expect(response.status, path).toBe(200);
      expect(next, path).toHaveBeenCalledOnce();
    }
  });

  const MENU_OWNER_ONLY = ["/quan-ly/tai-khoan", "/quan-ly/cai-dat", "/quan-ly/chung-nhan"];

  it.each(MENU_OWNER_ONLY)("WORKSHOP gõ thẳng %s (kể cả trang con) thì 403", async (path) => {
    mockMe(async () => json(200, WORKSHOP));
    for (const p of [path, `${path}/3`]) {
      const { response, next, rewrites } = await run(p);
      expect(response.status, p).toBe(403);
      expect(rewrites, p).toEqual(["/quan-ly/khong-co-quyen"]);
      expect(next, p).not.toHaveBeenCalled();
    }
  });

  it.each(MENU_OWNER_ONLY)("OWNER vào được %s", async (path) => {
    mockMe(async () => json(200, OWNER));
    const { response, next } = await run(path);
    expect(response.status).toBe(200);
    expect(next).toHaveBeenCalledOnce();
  });

  it.each(MENU_OWNER_ONLY)("%s-xyz không bị khớp nhầm", (path) => {
    const info = parseAdminPath(`${path}-xyz`);
    expect(info.kind === "admin" && isOwnerOnly(info.segments)).toBe(false);
  });

  it("màn chỉ xem với WORKSHOP (nguoi-ban, nguyen-lieu, dia-ban) không bị chặn", async () => {
    mockMe(async () => json(200, WORKSHOP));
    for (const path of ["/quan-ly/nguoi-ban", "/quan-ly/nguyen-lieu", "/quan-ly/dia-ban"]) {
      const { response, next } = await run(path);
      expect(response.status, path).toBe(200);
      expect(next, path).toHaveBeenCalledOnce();
    }
  });

  it("danh sách OWNER-only có vung-nguyen-lieu, không có thu-luu-huong", () => {
    expect(OWNER_ONLY_PREFIXES).toContain("/quan-ly/vung-nguyen-lieu");
    expect(OWNER_ONLY_PREFIXES).not.toContain("/quan-ly/thu-luu-huong");
  });

  // Cách lách: bộ định tuyến giải mã %xx, bỏ "//" và coi "\" như "/", nên kiểm vai phải làm tương tự.
  it.each([
    "/quan-ly/danh-%6Duc",
    "/quan-ly/%64anh-muc/x",
    "/quan-ly//danh-muc",
    "/quan-ly/danh-muc/",
    "/quan-ly/DANH-MUC",
    "/Quan-Ly/danh-muc",
    "/quan-ly/./danh-muc",
    "/quan-ly/x/../danh-muc",
    "/quan-ly/x/%2e%2e/danh-muc",
    "/quan-ly\\danh-muc",
    "/quan-ly%5Cdanh-muc",
    "//quan-ly/danh-muc",
  ])("WORKSHOP không lách được bằng %s", async (path) => {
    mockMe(async () => json(200, WORKSHOP));
    const { response, next } = await run(path);
    expect(response.status).toBe(403);
    expect(next).not.toHaveBeenCalled();
  });

  it("tiền tố chỉ khớp theo đoạn: danh-muc-khac không bị coi là danh-muc", () => {
    const info = parseAdminPath("/quan-ly/danh-muc-khac");
    expect(info.kind === "admin" && isOwnerOnly(info.segments)).toBe(false);
  });
});

describe("middleware: phạm vi và header", () => {
  it("đường dẫn ngoài /quan-ly đi thẳng, không gọi auth/me", async () => {
    const fetchMock = mockMe(async () => json(500, {}));
    for (const path of ["/", "/san-pham/abc", "/quan-ly-gia", "/q/ABC"]) {
      const { next } = await run(path);
      expect(next, path).toHaveBeenCalledOnce();
    }
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("trả lời dưới /quan-ly có no-store và noindex", async () => {
    mockMe(async () => json(200, OWNER));
    const { response } = await run("/quan-ly");
    expect(response.headers.get("Cache-Control")).toBe("private, no-store");
    expect(response.headers.get("X-Robots-Tag")).toBe("noindex, nofollow");
  });

  it("chuyển hướng về đăng nhập cũng có no-store và noindex", async () => {
    mockMe(async () => json(401, {}));
    const { response } = await run("/quan-ly");
    expect(response.headers.get("Cache-Control")).toBe("private, no-store");
    expect(response.headers.get("X-Robots-Tag")).toBe("noindex, nofollow");
  });

  it("%-mã hoá hỏng dưới /quan-ly thì 404, không qua trang", async () => {
    const fetchMock = mockMe(async () => json(200, OWNER));
    const { response, next } = await run("/quan-ly/%E0%A4%A");
    expect(response.status).toBe(404);
    expect(next).not.toHaveBeenCalled();
    expect(fetchMock).not.toHaveBeenCalled();
  });
});
