import { describe, expect, it, vi } from "vitest";
import { ApiRequestError } from "../../../scripts/admin/api";
import { remapErrors } from "./errors";
import {
  buildSupplierBody,
  createdId,
  type SupplierBody,
  type SupplierFormValues,
  saveThenApprove,
  sendJson,
  supplierPath,
} from "./supplier-form";

const values = (over: Partial<SupplierFormValues> = {}): SupplierFormValues => ({
  name: "  Nguyễn Văn Bình ",
  kind: "FARMER",
  area_id: "7",
  phone: " 0912345678 ",
  stream: "GENERAL",
  public_consent: false,
  ...over,
});

describe("buildSupplierBody", () => {
  it("OWNER gửi đủ trường, tên và SĐT được cắt khoảng trắng", () => {
    expect(buildSupplierBody(values(), { owner: true, activePlots: 0 })).toEqual({
      ok: true,
      body: {
        name: "Nguyễn Văn Bình",
        kind: "FARMER",
        area_id: 7,
        phone: "0912345678",
        stream: "GENERAL",
        public_consent: false,
      },
    });
  });
  it("WORKSHOP (thêm nhanh) không gửi luồng và đồng ý công khai", () => {
    const result = buildSupplierBody(values({ stream: "CONTROLLED", public_consent: true }), {
      owner: false,
      activePlots: 0,
    });
    expect(result.ok).toBe(true);
    if (result.ok) {
      expect("stream" in result.body).toBe(false);
      expect("public_consent" in result.body).toBe(false);
    }
  });
  it("SĐT trống gửi null (xoá số)", () => {
    const result = buildSupplierBody(values({ phone: "  " }), { owner: true, activePlots: 0 });
    expect(result.ok && result.body.phone).toBeNull();
  });
  it("khoá luồng theo kiểu: thương lái luôn GENERAL, chưa có đồi thì không CONTROLLED", () => {
    const trader = buildSupplierBody(values({ kind: "TRADER", stream: "CONTROLLED" }), {
      owner: true,
      activePlots: 2,
    });
    expect(trader.ok && trader.body.stream).toBe("GENERAL");
    const noPlot = buildSupplierBody(values({ stream: "CONTROLLED" }), {
      owner: true,
      activePlots: 0,
    });
    expect(noPlot.ok && noPlot.body.stream).toBe("GENERAL");
    const withPlot = buildSupplierBody(values({ stream: "CONTROLLED" }), {
      owner: true,
      activePlots: 1,
    });
    expect(withPlot.ok && withPlot.body.stream).toBe("CONTROLLED");
  });
  it("thiếu tên, kiểu, địa bàn: báo lỗi từng trường", () => {
    const result = buildSupplierBody(values({ name: " ", kind: "", area_id: "" }), {
      owner: true,
      activePlots: 0,
    });
    expect(result.ok).toBe(false);
    if (!result.ok) expect(Object.keys(result.errors).sort()).toEqual(["area_id", "kind", "name"]);
  });
});

describe("sendJson", () => {
  it("thành công: trả dữ liệu", async () => {
    const send = vi.fn().mockResolvedValue({ id: 9 });
    const result = await sendJson("POST", "/suppliers", { a: 1 }, {}, send);
    expect(result).toEqual({ ok: true, data: { id: 9 } });
    expect(send).toHaveBeenCalledWith("POST", "/suppliers", { a: 1 });
  });
  it("lỗi model `area` đổi thành ô area_id; toạ độ lat/lng thành coordinates", async () => {
    const error = new ApiRequestError(400, "VALIDATION_ERROR", "Dữ liệu không hợp lệ", {
      errors: [
        { field: "area", message: "Hộ dân, gia đình phải chọn địa bàn cấp thôn" },
        { field: "lat", message: "Toạ độ phải có đủ vĩ độ và kinh độ" },
      ],
    });
    const send = vi.fn().mockRejectedValue(error);
    const supplier = await sendJson("POST", "/suppliers", {}, { area: "area_id" }, send);
    expect(supplier).toEqual({
      ok: false,
      error: {
        fields: {
          area_id: "Hộ dân, gia đình phải chọn địa bàn cấp thôn",
          lat: "Toạ độ phải có đủ vĩ độ và kinh độ",
        },
        general: null,
      },
    });
    const plot = await sendJson(
      "PATCH",
      "/x",
      {},
      { lat: "coordinates", lng: "coordinates" },
      send,
    );
    expect(plot.ok === false && plot.error.fields).toHaveProperty("coordinates");
  });
  it("lỗi nghiệp vụ 409 có details.field gắn vào đúng ô", async () => {
    const error = new ApiRequestError(409, "STREAM_NEEDS_PLOT", "Luồng kiểm soát cần đồi", {
      field: "stream",
    });
    const result = await sendJson(
      "PATCH",
      "/suppliers/1",
      {},
      {},
      vi.fn().mockRejectedValue(error),
    );
    expect(result).toEqual({
      ok: false,
      error: { fields: { stream: "Luồng kiểm soát cần đồi" }, general: null },
    });
  });
  it("lỗi mạng: thông báo chung", async () => {
    const result = await sendJson(
      "POST",
      "/x",
      {},
      {},
      vi.fn().mockRejectedValue(new TypeError("x")),
    );
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.error.general).toContain("Không kết nối");
  });
});

describe("saveThenApprove", () => {
  const body: SupplierBody = {
    name: "Nguyễn Văn Bình",
    kind: "FARMER",
    area_id: 7,
    phone: null,
    stream: "CONTROLLED",
    public_consent: false,
  };
  it("lưu form trước rồi mới duyệt", async () => {
    const send = vi.fn().mockResolvedValue({ id: 3 });
    const result = await saveThenApprove(3, body, send);
    expect(result.ok).toBe(true);
    expect(send.mock.calls).toEqual([
      ["PATCH", "/suppliers/3", body],
      ["POST", "/suppliers/3/approve", undefined],
    ]);
  });
  it("lưu lỗi thì không gọi duyệt", async () => {
    const send = vi.fn().mockRejectedValue(new TypeError("offline"));
    const result = await saveThenApprove(3, body, send);
    expect(result.ok).toBe(false);
    expect(send).toHaveBeenCalledTimes(1);
  });
});

describe("tiện ích", () => {
  it("remapErrors giữ lỗi đầu tiên của ô đích", () => {
    expect(
      remapErrors(
        { fields: { lat: "A", lng: "B", name: "C" }, general: "G" },
        { lat: "coordinates", lng: "coordinates" },
      ),
    ).toEqual({ fields: { coordinates: "A", name: "C" }, general: "G" });
  });
  it("createdId và supplierPath", () => {
    expect(createdId({ id: 12, code: "NCC-1" })).toBe(12);
    expect(createdId({ id: "12" })).toBeNull();
    expect(createdId(null)).toBeNull();
    expect(supplierPath(5)).toBe("/quan-ly/nguoi-ban/5");
  });
});
