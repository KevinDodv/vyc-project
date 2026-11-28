import { afterEach, describe, expect, it, vi } from "vitest";
import { ApiRequestError } from "../../scripts/admin/api";
import {
  clearErrors,
  formToBody,
  GENERIC_ERROR,
  missingRequired,
  parseApiError,
  REQUIRED_MESSAGE,
  redirectTarget,
  showErrors,
  submitBody,
} from "./form";

afterEach(() => {
  vi.unstubAllGlobals();
});

const validation = (errors: unknown[]) =>
  new ApiRequestError(400, "VALIDATION_ERROR", "Dữ liệu gửi lên không hợp lệ", { errors });

describe("parseApiError", () => {
  it("VALIDATION_ERROR: lỗi theo trường, lấy lỗi đầu của mỗi trường", () => {
    const parsed = parseApiError(
      validation([
        { field: "code", message: "Mã chỉ gồm chữ hoa" },
        { field: "code", message: "Quá dài" },
        { field: "name", message: "Không được để trống" },
      ]),
    );
    expect(parsed).toEqual({
      fields: { code: "Mã chỉ gồm chữ hoa", name: "Không được để trống" },
      general: null,
    });
  });
  it("lỗi validation không nêu trường thì thành lỗi chung", () => {
    const parsed = parseApiError(validation([{ field: "", message: "Thiếu dữ liệu" }]));
    expect(parsed).toEqual({ fields: {}, general: "Thiếu dữ liệu" });
  });
  it("VALIDATION_ERROR không có danh sách thì giữ message của API", () => {
    const parsed = parseApiError(new ApiRequestError(400, "VALIDATION_ERROR", "Sai rồi", {}));
    expect(parsed).toEqual({ fields: {}, general: "Sai rồi" });
  });
  it("lỗi nghiệp vụ có details.field thì gắn vào trường đó", () => {
    const error = new ApiRequestError(
      409,
      "GOODS_TYPE_GROUP_LOCKED",
      "Loại hàng đã có 7 sản phẩm dùng, không đổi nhóm được",
      { rule: "BR-30", field: "group" },
    );
    expect(parseApiError(error)).toEqual({
      fields: { group: "Loại hàng đã có 7 sản phẩm dùng, không đổi nhóm được" },
      general: null,
    });
  });
  it("lỗi nghiệp vụ không nêu trường thì là lỗi chung, giữ nguyên message", () => {
    const error = new ApiRequestError(409, "HAS_STOCK", "Hạng đang có lô trong kho", {});
    expect(parseApiError(error)).toEqual({ fields: {}, general: "Hạng đang có lô trong kho" });
  });
  it("lỗi không phải của API (mạng, TypeError) thì thông báo chung", () => {
    expect(parseApiError(new TypeError("fetch failed"))).toEqual({
      fields: {},
      general: GENERIC_ERROR,
    });
  });
});

describe("formToBody", () => {
  const kinds = {
    code: "text",
    name: "text",
    sort: "int",
    density: "decimal",
    is_food: "boolean",
    password: "password",
  } as const;

  it("ép kiểu theo data-kind, trống thì null", () => {
    const data = new FormData();
    data.set("code", "  TP-TD ");
    data.set("name", "");
    data.set("sort", "12");
    data.set("density", "0,85");
    const body = formToBody(data, kinds);
    expect(body).toEqual({
      code: "TP-TD",
      name: null,
      sort: 12,
      density: "0.85",
      is_food: false,
    });
  });
  it("checkbox có trong form thì true", () => {
    const data = new FormData();
    data.set("is_food", "on");
    expect(formToBody(data, kinds).is_food).toBe(true);
  });
  it("mật khẩu để trống thì bỏ khỏi thân, có thì giữ nguyên (không cắt khoảng trắng)", () => {
    const empty = new FormData();
    empty.set("password", "");
    expect("password" in formToBody(empty, kinds)).toBe(false);
    const filled = new FormData();
    filled.set("password", " abc 12345 ");
    expect(formToBody(filled, kinds).password).toBe(" abc 12345 ");
  });
  it("số nguyên sai thì giữ chuỗi để API báo lỗi theo trường", () => {
    const data = new FormData();
    data.set("sort", "12abc");
    expect(formToBody(data, kinds).sort).toBe("12abc");
  });
});

describe("missingRequired", () => {
  it("trả các trường bắt buộc còn trống hoặc chỉ có khoảng trắng", () => {
    const data = new FormData();
    data.set("code", "A");
    data.set("name", "   ");
    expect(missingRequired(data, ["code", "name", "group"])).toEqual(["name", "group"]);
  });
});

/** Phần tử giả đủ cho showErrors/clearErrors: không có jsdom trong dự án. */
function fakeEl(attrs: Record<string, string> = {}) {
  const attributes = new Map(Object.entries(attrs));
  return {
    textContent: "",
    hidden: true,
    focused: false,
    getAttribute: (name: string) => attributes.get(name) ?? null,
    setAttribute: (name: string, value: string) => void attributes.set(name, value),
    removeAttribute: (name: string) => void attributes.delete(name),
    has: (name: string) => attributes.has(name),
  };
}
type FakeEl = ReturnType<typeof fakeEl>;

function fakeForm(elements: { slots?: FakeEl[]; controls?: FakeEl[]; box?: FakeEl }) {
  const { slots = [], controls = [], box } = elements;
  return {
    querySelectorAll(selector: string) {
      if (selector === "[data-error-for]") return slots;
      if (selector === "[name]") return controls;
      if (selector === "[aria-invalid]") return controls.filter((c) => c.has("aria-invalid"));
      if (selector === "[data-form-error]") return box ? [box] : [];
      return [];
    },
  } as unknown as Parameters<typeof showErrors>[0];
}

describe("showErrors / clearErrors", () => {
  it("hiện lỗi ngay dưới trường và đánh dấu aria-invalid", () => {
    const slot = fakeEl({ "data-error-for": "code" });
    const control = fakeEl({ name: "code" });
    const other = fakeEl({ name: "name" });
    const form = fakeForm({ slots: [slot], controls: [control, other] });
    const first = showErrors(form, { fields: { code: "Mã đã tồn tại" }, general: null });
    expect(slot.textContent).toBe("Mã đã tồn tại");
    expect(slot.hidden).toBe(false);
    expect(control.getAttribute("aria-invalid")).toBe("true");
    expect(other.getAttribute("aria-invalid")).toBeNull();
    expect(first).toBe(control);
  });
  it("tên lồng nhau thử khớp đoạn đầu (grades.0.name → grades)", () => {
    const slot = fakeEl({ "data-error-for": "grades" });
    const form = fakeForm({ slots: [slot] });
    showErrors(form, { fields: { "grades.0.name": "Tên hạng bắt buộc" }, general: null });
    expect(slot.textContent).toBe("Tên hạng bắt buộc");
    expect(slot.hidden).toBe(false);
  });
  it("trường không có chỗ hiện thì xuống lỗi chung kèm nhãn trường", () => {
    const box = fakeEl();
    const form = fakeForm({ box });
    const first = showErrors(
      form,
      { fields: { unit: "Phải là gram" }, general: null },
      { unit: "Đơn vị" },
    );
    expect(box.textContent).toBe("Đơn vị: Phải là gram");
    expect(box.hidden).toBe(false);
    expect(first).toBe(box);
  });
  it("lỗi chung hiện nguyên message của API", () => {
    const box = fakeEl();
    showErrors(fakeForm({ box }), {
      fields: {},
      general: "Phiên làm việc đã cũ, tải lại trang rồi thử lại",
    });
    expect(box.textContent).toBe("Phiên làm việc đã cũ, tải lại trang rồi thử lại");
  });
  it("clearErrors xoá hết", () => {
    const slot = fakeEl({ "data-error-for": "code" });
    const control = fakeEl({ name: "code" });
    const box = fakeEl();
    const form = fakeForm({ slots: [slot], controls: [control], box });
    showErrors(form, { fields: { code: "Sai" }, general: "Lỗi chung" });
    clearErrors(form);
    expect(slot.textContent).toBe("");
    expect(slot.hidden).toBe(true);
    expect(control.getAttribute("aria-invalid")).toBeNull();
    expect(box.hidden).toBe(true);
  });
  it("REQUIRED_MESSAGE có chữ tiếng Việt cho người dùng", () => {
    expect(REQUIRED_MESSAGE).toBe("Trường này bắt buộc");
  });
});

describe("submitBody", () => {
  const res = (status: number, body?: unknown) =>
    new Response(body === undefined ? null : JSON.stringify(body), { status });

  it("POST kèm X-CSRFToken lấy từ cookie csrftoken (qua client api.ts)", async () => {
    vi.stubGlobal("document", { cookie: "csrftoken=tok123" });
    const fetchMock = vi.fn(async () => res(201, { id: 5 }));
    vi.stubGlobal("fetch", fetchMock);
    const result = await submitBody("POST", "/goods-types", { code: "TP-TD", name: "Tinh dầu" });
    expect(result).toEqual({ ok: true, data: { id: 5 } });
    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toBe("/api/v1/goods-types");
    expect(init.method).toBe("POST");
    expect((init.headers as Record<string, string>)["X-CSRFToken"]).toBe("tok123");
    expect(JSON.parse(String(init.body))).toEqual({ code: "TP-TD", name: "Tinh dầu" });
  });
  it("PATCH {status} cho Ngừng dùng", async () => {
    vi.stubGlobal("document", { cookie: "csrftoken=t" });
    const fetchMock = vi.fn(async () => res(200, { id: 5, status: "INACTIVE" }));
    vi.stubGlobal("fetch", fetchMock);
    const result = await submitBody("PATCH", "/goods-types/5", { status: "INACTIVE" });
    expect(result.ok).toBe(true);
    const [, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(init.method).toBe("PATCH");
    expect(JSON.parse(String(init.body))).toEqual({ status: "INACTIVE" });
  });
  it("400 của API thành lỗi theo trường", async () => {
    vi.stubGlobal("document", { cookie: "csrftoken=t" });
    vi.stubGlobal(
      "fetch",
      vi.fn(async () =>
        res(400, {
          code: "VALIDATION_ERROR",
          message: "Dữ liệu gửi lên không hợp lệ",
          details: { errors: [{ field: "code", message: "Mã đã tồn tại" }] },
        }),
      ),
    );
    const result = await submitBody("POST", "/goods-types", { code: "X" });
    expect(result).toEqual({
      ok: false,
      error: { fields: { code: "Mã đã tồn tại" }, general: null },
    });
  });
  it("lỗi mạng thì không ném, trả thông báo chung", async () => {
    vi.stubGlobal("document", { cookie: "csrftoken=t" });
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => {
        throw new TypeError("fetch failed");
      }),
    );
    const result = await submitBody("POST", "/goods-types", {});
    expect(result).toEqual({ ok: false, error: { fields: {}, general: GENERIC_ERROR } });
  });
  it("dùng được deps tự đưa vào", async () => {
    const send = vi.fn(async () => ({ id: 1 }));
    const result = await submitBody("POST", "/x", { a: 1 }, { send });
    expect(send).toHaveBeenCalledWith("POST", "/x", { a: 1 });
    expect(result.ok).toBe(true);
  });
});

describe("redirectTarget", () => {
  it("chỉ nhận đường dẫn dưới /quan-ly", () => {
    expect(redirectTarget("/quan-ly/loai-hang")).toBe("/quan-ly/loai-hang");
    expect(redirectTarget("https://evil.example")).toBeNull();
    expect(redirectTarget("//evil.example")).toBeNull();
    expect(redirectTarget(undefined)).toBeNull();
  });
});
