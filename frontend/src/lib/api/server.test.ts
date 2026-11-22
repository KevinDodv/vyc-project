import { describe, expect, it } from "vitest";
import { callApi, forwardHeaders } from "./server";

const req = (headers: Record<string, string>) => new Request("http://x/", { headers });

describe("forwardHeaders", () => {
  it("chuyển nguyên X-Forwarded-For, không thêm Cookie khi anon", () => {
    const h = forwardHeaders(
      req({ "x-forwarded-for": "1.2.3.4", cookie: "sessionid=abc" }),
      "anon",
    );
    expect(h["X-Forwarded-For"]).toBe("1.2.3.4");
    expect(h.Cookie).toBeUndefined();
    expect(h.Accept).toBe("application/json");
  });
  it("session thì thêm Cookie", () => {
    const h = forwardHeaders(req({ cookie: "sessionid=abc" }), "session");
    expect(h.Cookie).toBe("sessionid=abc");
  });
  it("không có XFF thì không gửi header này", () => {
    expect(forwardHeaders(req({}), "anon")["X-Forwarded-For"]).toBeUndefined();
  });
});

const resp = (status: number, headers: Record<string, string> = {}) =>
  new Response(null, { status, headers });

describe("callApi", () => {
  it("200 có data thì ok", async () => {
    const out = await callApi(async () => ({ data: [1], response: resp(200) }));
    expect(out).toEqual({ kind: "ok", data: [1] });
  });
  it("404 thì not_found", async () => {
    expect(await callApi(async () => ({ response: resp(404) }))).toEqual({ kind: "not_found" });
  });
  it("429 thì unavailable, giữ Retry-After", async () => {
    const out = await callApi(async () => ({ response: resp(429, { "retry-after": "12" }) }));
    expect(out).toEqual({ kind: "unavailable", retryAfter: "12" });
  });
  it("5xx, lỗi mạng, body trống thì unavailable", async () => {
    expect((await callApi(async () => ({ response: resp(502) }))).kind).toBe("unavailable");
    const boom = await callApi(async () => {
      throw new Error("timeout");
    });
    expect(boom.kind).toBe("unavailable");
    expect((await callApi(async () => ({ response: resp(200) }))).kind).toBe("unavailable");
  });
});
