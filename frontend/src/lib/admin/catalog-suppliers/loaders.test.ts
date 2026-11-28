import { afterEach, describe, expect, it, vi } from "vitest";
import { parseListQuery } from "../catalog";
import { type CustomerOut, customerFields, toCustomerRow } from "./customers";
import { loadCustomer, loadCustomerList, loadSupplierDetail, loadSupplierList } from "./loaders";
import { buildApiUrl, getJson, parseId } from "./server";

afterEach(() => {
  vi.unstubAllGlobals();
});

const json = (body: unknown, status = 200): Response =>
  new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });

const request = new Request("http://localhost:4321/quan-ly/nguoi-ban", {
  headers: { cookie: "sessionid=abc" },
});

const supplier = (over: Record<string, unknown> = {}) => ({
  id: 1,
  code: "NCC-CQ-001",
  name: "Nguyễn Văn Hùng",
  kind: "FARMER",
  phone: null,
  area_id: 7,
  area_name: "Thôn 3, Châu Quế",
  stream: "GENERAL",
  public_consent: false,
  approved: true,
  status: "ACTIVE",
  plots_count: 0,
  created_at: "",
  updated_at: "",
  ...over,
});

/** Giả fetch theo đường dẫn: `routes["/api/v1/suppliers/1"]` là Response hoặc hàm trả Response. */
function stubApi(routes: Record<string, Response | (() => Response)>): ReturnType<typeof vi.fn> {
  const fetcher = vi.fn(async (input: URL | Request | string) => {
    const url = new URL(input instanceof Request ? input.url : String(input));
    const key = url.pathname;
    const route = routes[key];
    if (!route) return json({ code: "NOT_FOUND", message: "Không tìm thấy" }, 404);
    return typeof route === "function" ? route() : route.clone();
  });
  vi.stubGlobal("fetch", fetcher);
  return fetcher;
}

describe("server helper", () => {
  it("parseId chỉ nhận số nguyên dương", () => {
    expect(parseId("12")).toBe(12);
    for (const bad of [undefined, "", "0", "-1", "1.5", "abc", "01", "12345678901"]) {
      expect(parseId(bad)).toBeNull();
    }
  });
  it("buildApiUrl bỏ tham số rỗng", () => {
    const url = buildApiUrl("/suppliers", {
      q: "",
      page: 2,
      approved: undefined,
      status: "ACTIVE",
    });
    expect(url.pathname).toBe("/api/v1/suppliers");
    expect(url.search).toBe("?page=2&status=ACTIVE");
  });
  it("getJson gom kết quả: ok, 404, 401, 5xx, lỗi mạng", async () => {
    const cases: Array<[Response | Error, string]> = [
      [json({ a: 1 }), "ok"],
      [json({}, 404), "not_found"],
      [json({}, 401), "unauthorized"],
      [json({}, 403), "unavailable"],
      [json({}, 500), "unavailable"],
      [new TypeError("mạng"), "unavailable"],
    ];
    for (const [result, kind] of cases) {
      const fetcher = vi.fn(async () => {
        if (result instanceof Error) throw result;
        return result;
      });
      const outcome = await getJson(request, "/suppliers", {}, fetcher as unknown as typeof fetch);
      expect(outcome.kind).toBe(kind);
    }
  });
  it("getJson chuyển Cookie phiên", async () => {
    const fetcher = vi.fn(async (_url: URL | string, init?: RequestInit) => {
      expect((init?.headers as Record<string, string> | undefined)?.Cookie).toBe("sessionid=abc");
      return json({});
    });
    await getJson(request, "/suppliers", {}, fetcher as unknown as typeof fetch);
    expect(fetcher).toHaveBeenCalledOnce();
  });
});

describe("loadSupplierList", () => {
  it("lọc chờ duyệt gọi approved=false và lấy thêm số người chờ", async () => {
    const fetcher = stubApi({
      "/api/v1/suppliers": () =>
        json({ items: [supplier({ approved: false })], total: 1, page: 1, page_size: 50 }),
    });
    const result = await loadSupplierList(
      request,
      parseListQuery(new URLSearchParams("q=hung")),
      true,
    );
    expect(result.kind).toBe("ok");
    if (result.kind === "ok") expect(result.waiting).toBe(1);
    const urls = fetcher.mock.calls.map((c) => String(c[0]));
    expect(urls.some((u) => u.includes("approved=false") && u.includes("q=hung"))).toBe(true);
    expect(urls.some((u) => u.includes("page_size=1"))).toBe(true);
  });
  it("không lọc: không gửi approved", async () => {
    const fetcher = stubApi({
      "/api/v1/suppliers": () => json({ items: [], total: 0, page: 1, page_size: 50 }),
    });
    await loadSupplierList(request, parseListQuery(new URLSearchParams("")), false);
    const first = String(fetcher.mock.calls[0]?.[0]);
    expect(first).not.toContain("approved");
  });
  it("API lỗi thì unavailable, 401 thì unauthorized (không vẽ danh sách rỗng)", async () => {
    stubApi({ "/api/v1/suppliers": () => json({}, 500) });
    expect(
      (await loadSupplierList(request, parseListQuery(new URLSearchParams("")), false)).kind,
    ).toBe("unavailable");
    stubApi({ "/api/v1/suppliers": () => json({}, 401) });
    expect(
      (await loadSupplierList(request, parseListQuery(new URLSearchParams("")), false)).kind,
    ).toBe("unauthorized");
  });
});

describe("loadSupplierDetail", () => {
  const tree = [
    {
      id: 1,
      level: "PROVINCE",
      name: "Yên Bái",
      status: "ACTIVE",
      children: [
        {
          id: 2,
          level: "COMMUNE",
          name: "Châu Quế",
          status: "ACTIVE",
          children: [{ id: 7, level: "VILLAGE", name: "Thôn 3", status: "ACTIVE", children: [] }],
        },
      ],
    },
  ];
  it("gom người bán, đồi, địa bàn và người trùng tên + thôn", async () => {
    stubApi({
      "/api/v1/suppliers/1": () => json(supplier()),
      "/api/v1/suppliers/1/plots": () => json([]),
      "/api/v1/areas": () => json(tree),
      "/api/v1/suppliers": () =>
        json({
          items: [supplier(), supplier({ id: 2, code: "NCC-CQ-002", name: "nguyen van hung" })],
          total: 2,
          page: 1,
          page_size: 200,
        }),
    });
    const result = await loadSupplierDetail(request, 1);
    expect(result.kind).toBe("ok");
    if (result.kind === "ok") {
      expect(result.twins?.map((t) => t.code)).toEqual(["NCC-CQ-002"]);
      expect(result.areas.map((a) => a.id)).toEqual([2, 7]);
    }
  });
  it("người bán không có thì not_found", async () => {
    stubApi({});
    expect((await loadSupplierDetail(request, 99)).kind).toBe("not_found");
  });
  it("lỗi một nguồn thì unavailable; kiểm trùng lỗi thì vẫn vẽ, twins = null", async () => {
    stubApi({
      "/api/v1/suppliers/1": () => json(supplier()),
      "/api/v1/suppliers/1/plots": () => json({}, 500),
      "/api/v1/areas": () => json(tree),
    });
    expect((await loadSupplierDetail(request, 1)).kind).toBe("unavailable");
    stubApi({
      "/api/v1/suppliers/1": () => json(supplier()),
      "/api/v1/suppliers/1/plots": () => json([]),
      "/api/v1/areas": () => json(tree),
      "/api/v1/suppliers": () => json({}, 500),
    });
    const result = await loadSupplierDetail(request, 1);
    expect(result.kind === "ok" && result.twins).toBeNull();
  });
});

describe("khách hàng", () => {
  const customer: CustomerOut = {
    id: 3,
    code: "KH-0003",
    name: "Đại lý An Phát",
    kind: "AGENT",
    phone: null,
    address: "Yên Bái",
    status: "ACTIVE",
    created_at: "",
    updated_at: "",
  };
  it("toCustomerRow đổi nhãn kiểu, null thành rỗng", () => {
    expect(toCustomerRow(customer)).toMatchObject({
      kind: "Đại lý",
      phone: "",
      address: "Yên Bái",
    });
    expect(toCustomerRow({ ...customer, kind: "LẠ" }).kind).toBe("LẠ");
  });
  it("customerFields: tạo trống, sửa có giá trị; tên và kiểu bắt buộc", () => {
    const create = customerFields();
    expect(create.map((f) => f.name)).toEqual(["name", "kind", "phone", "address"]);
    expect(create.filter((f) => f.required).map((f) => f.name)).toEqual(["name", "kind"]);
    expect(customerFields(customer).find((f) => f.name === "kind")?.value).toBe("AGENT");
  });
  it("loadCustomerList và loadCustomer", async () => {
    stubApi({
      "/api/v1/customers": () => json({ items: [customer], total: 1, page: 1, page_size: 50 }),
      "/api/v1/customers/3": () => json(customer),
    });
    const list = await loadCustomerList(request, parseListQuery(new URLSearchParams("")));
    expect(list.kind === "ok" && list.page.total).toBe(1);
    expect((await loadCustomer(request, 3)).kind).toBe("ok");
    expect((await loadCustomer(request, 4)).kind).toBe("not_found");
  });
});
