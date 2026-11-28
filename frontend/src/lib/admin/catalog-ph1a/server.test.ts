import { describe, expect, it } from "vitest";
import { buildApiUrl, getJson, loginUrl } from "./server";

const request = new Request("http://localhost/quan-ly/dia-ban", {
  headers: { cookie: "sessionid=abc", "x-forwarded-for": "1.2.3.4" },
});

function fake(status: number, body: unknown = {}): typeof fetch {
  return (async () =>
    new Response(JSON.stringify(body), {
      status,
      headers: { "content-type": "application/json" },
    })) as typeof fetch;
}

describe("buildApiUrl", () => {
  it("ghép /api/v1 và query, bỏ giá trị rỗng", () => {
    const url = buildApiUrl("/prices", { date: "2026-11-23", to: "", x: undefined });
    expect(url.pathname).toBe("/api/v1/prices");
    expect(url.search).toBe("?date=2026-11-23");
  });
});

describe("getJson", () => {
  it("200 → ok kèm dữ liệu", async () => {
    expect(await getJson(request, "/areas", {}, fake(200, [{ id: 1 }]))).toEqual({
      kind: "ok",
      data: [{ id: 1 }],
    });
  });
  it("chuyển Cookie của người xem", async () => {
    let seen: Record<string, string> = {};
    const spy = (async (_url: unknown, init?: RequestInit) => {
      seen = init?.headers as Record<string, string>;
      return new Response("[]", { status: 200 });
    }) as typeof fetch;
    await getJson(request, "/areas", {}, spy);
    expect(seen.Cookie).toBe("sessionid=abc");
    expect(seen["X-Forwarded-For"]).toBe("1.2.3.4");
  });
  it("404 → not_found, 401 → unauthorized", async () => {
    expect(await getJson(request, "/areas/9", {}, fake(404))).toEqual({ kind: "not_found" });
    expect(await getJson(request, "/areas", {}, fake(401))).toEqual({ kind: "unauthorized" });
  });
  it("403, 429, 500 → unavailable (không hiện danh sách rỗng)", async () => {
    for (const status of [403, 429, 500, 502]) {
      expect(await getJson(request, "/areas", {}, fake(status))).toEqual({ kind: "unavailable" });
    }
  });
  it("lỗi mạng hoặc body không phải JSON → unavailable", async () => {
    const boom = (async () => {
      throw new Error("ECONNREFUSED");
    }) as typeof fetch;
    expect(await getJson(request, "/areas", {}, boom)).toEqual({ kind: "unavailable" });
    const html = (async () => new Response("<html>", { status: 200 })) as typeof fetch;
    expect(await getJson(request, "/areas", {}, html)).toEqual({ kind: "unavailable" });
  });
});

describe("loginUrl", () => {
  it("kèm next là trang đang xem", () => {
    expect(loginUrl(new URL("http://x/quan-ly/bang-gia?date=2026-11-23"))).toBe(
      "/quan-ly/dang-nhap?next=%2Fquan-ly%2Fbang-gia%3Fdate%3D2026-11-23",
    );
  });
});
