import { afterEach, describe, expect, it, vi } from "vitest";
import { ApiRequestError, api, readCookie } from "../../src/scripts/admin/api";

function stubBrowser(cookie: { value: string }) {
  vi.stubGlobal("document", {
    get cookie() {
      return cookie.value;
    },
  });
}

const res = (status: number, body?: unknown) =>
  new Response(body === undefined ? null : JSON.stringify(body), { status });

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("readCookie", () => {
  it("đọc đúng cookie theo tên", () => {
    expect(readCookie("csrftoken", "a=1; csrftoken=tok%20en; b=2")).toBe("tok en");
  });
  it("không nhầm tên có chung đuôi", () => {
    expect(readCookie("csrftoken", "xcsrftoken=bad")).toBeNull();
  });
  it("không có thì null", () => {
    expect(readCookie("csrftoken", "")).toBeNull();
  });
});

describe("api client", () => {
  it("POST gửi X-CSRFToken và JSON, cùng origin", async () => {
    stubBrowser({ value: "csrftoken=abc123" });
    const fetchMock = vi.fn(async () => res(201, { id: 7 }));
    vi.stubGlobal("fetch", fetchMock);
    const out = await api.post<{ id: number }>("/products", { name: "x" });
    expect(out).toEqual({ id: 7 });
    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toBe("/api/v1/products");
    expect(init.method).toBe("POST");
    expect(init.credentials).toBe("same-origin");
    const headers = init.headers as Record<string, string>;
    expect(headers["X-CSRFToken"]).toBe("abc123");
    expect(headers["Content-Type"]).toBe("application/json");
    expect(init.body).toBe(JSON.stringify({ name: "x" }));
  });

  it("PATCH cũng gửi X-CSRFToken", async () => {
    stubBrowser({ value: "csrftoken=abc123" });
    const fetchMock = vi.fn(async () => res(200, { id: 7 }));
    vi.stubGlobal("fetch", fetchMock);
    await api.patch("/products/7", { status: "PUBLISHED" });
    const [, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect((init.headers as Record<string, string>)["X-CSRFToken"]).toBe("abc123");
  });

  it("GET không gửi X-CSRFToken", async () => {
    stubBrowser({ value: "csrftoken=abc123" });
    const fetchMock = vi.fn(async () => res(200, { ok: true }));
    vi.stubGlobal("fetch", fetchMock);
    await api.get("/auth/me");
    const [, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect((init.headers as Record<string, string>)["X-CSRFToken"]).toBeUndefined();
  });

  it("chưa có cookie csrftoken thì gọi /auth/csrf trước khi ghi", async () => {
    const cookie = { value: "" };
    stubBrowser(cookie);
    const fetchMock = vi.fn(async (url: string) => {
      if (url === "/api/v1/auth/csrf") {
        cookie.value = "csrftoken=fresh";
        return res(204);
      }
      return res(200, { ok: true });
    });
    vi.stubGlobal("fetch", fetchMock);
    await api.post("/auth/login", { username: "a", password: "b" });
    expect(fetchMock.mock.calls.map((c) => c[0])).toEqual([
      "/api/v1/auth/csrf",
      "/api/v1/auth/login",
    ]);
    const init = (
      fetchMock.mock.calls as unknown as [string, RequestInit][]
    )[1]?.[1] as RequestInit;
    expect((init.headers as Record<string, string>)["X-CSRFToken"]).toBe("fresh");
  });

  it("CSRF_FAILED thì lấy token mới và thử lại đúng một lần", async () => {
    const cookie = { value: "csrftoken=old" };
    stubBrowser(cookie);
    let writes = 0;
    const fetchMock = vi.fn(async (url: string) => {
      if (url === "/api/v1/auth/csrf") {
        cookie.value = "csrftoken=new";
        return res(204);
      }
      writes += 1;
      return writes === 1
        ? res(403, { code: "CSRF_FAILED", message: "Phiên làm việc đã cũ", details: {} })
        : res(200, { id: 1 });
    });
    vi.stubGlobal("fetch", fetchMock);
    await expect(api.post("/products", {})).resolves.toEqual({ id: 1 });
    expect(writes).toBe(2);
  });

  it("lỗi API thành ApiRequestError, giữ nguyên message", async () => {
    stubBrowser({ value: "csrftoken=t" });
    vi.stubGlobal(
      "fetch",
      vi.fn(async () =>
        res(409, { code: "SLUG_TAKEN", message: "Slug đã dùng", details: { slug: "a" } }),
      ),
    );
    const error = (await api.post("/products", {}).catch((e) => e)) as ApiRequestError;
    expect(error).toBeInstanceOf(ApiRequestError);
    expect(error.status).toBe(409);
    expect(error.code).toBe("SLUG_TAKEN");
    expect(error.message).toBe("Slug đã dùng");
    expect(error.details).toEqual({ slug: "a" });
  });

  it("lỗi không phải JSON (502 từ proxy) vẫn có thông báo chung", async () => {
    stubBrowser({ value: "csrftoken=t" });
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => new Response("<html>", { status: 502 })),
    );
    const error = (await api.get("/x").catch((e) => e)) as ApiRequestError;
    expect(error).toBeInstanceOf(ApiRequestError);
    expect(error.status).toBe(502);
    expect(error.code).toBe("HTTP_502");
  });

  it("từ chối đường dẫn thoát khỏi /api/v1", async () => {
    stubBrowser({ value: "" });
    vi.stubGlobal("fetch", vi.fn());
    await expect(api.get("//evil.com/x")).rejects.toThrow(TypeError);
    await expect(api.get("products")).rejects.toThrow(TypeError);
  });
});
