import { describe, expect, it } from "vitest";
import {
  certificateApiQuery,
  certificateState,
  certificateTarget,
  formatDate,
  todayInVietnam,
} from "./certificate";
import { targetKindOf } from "./certificate-form";
import { buildSettingsBody, mapSettingsErrorField, settingsToInput } from "./settings";
import { canToggleStatus, formatLastLogin, isSelf, roleLabel } from "./user";

describe("chứng nhận", () => {
  const cert = (expires_on: string | null, is_expired = false) => ({ expires_on, is_expired });
  it("còn hiệu lực, sắp hết hạn (< 30 ngày), hết hạn", () => {
    expect(certificateState(cert(null), "2026-11-23")).toBe("valid");
    expect(certificateState(cert("2027-01-01"), "2026-11-23")).toBe("valid");
    expect(certificateState(cert("2026-12-22"), "2026-11-23")).toBe("soon");
    expect(certificateState(cert("2026-12-23"), "2026-11-23")).toBe("valid");
    expect(certificateState(cert("2026-11-23"), "2026-11-23")).toBe("soon");
    expect(certificateState(cert("2026-11-22"), "2026-11-23")).toBe("expired");
    expect(certificateState(cert("2027-01-01", true), "2026-11-23")).toBe("expired");
  });
  it("hôm nay theo giờ Việt Nam", () => {
    expect(todayInVietnam(new Date("2026-11-22T18:00:00Z"))).toBe("2026-11-23");
    expect(todayInVietnam(new Date("2026-11-22T16:00:00Z"))).toBe("2026-11-22");
  });
  it("định dạng ngày", () => {
    expect(formatDate("2026-11-23")).toBe("23/11/2026");
    expect(formatDate(null)).toBe("");
  });
  it("bộ lọc Đang dùng/Ngừng dùng thành active true/false", () => {
    const q = { q: "OCOP", status: "ACTIVE" as const, page: 2, pageSize: 50 };
    expect(certificateApiQuery(q)).toEqual({ page: 2, page_size: 50, q: "OCOP", active: true });
    expect(certificateApiQuery({ ...q, status: "INACTIVE" })).toMatchObject({ active: false });
    expect(certificateApiQuery({ ...q, status: "" })).not.toHaveProperty("active");
    expect(certificateApiQuery({ ...q, status: "" })).not.toHaveProperty("status");
  });
  it("cột Áp dụng cho", () => {
    const skus = new Map([[3, "Q100"]]);
    expect(certificateTarget({ product_id: 3, plot_id: null }, skus)).toBe("Sản phẩm Q100");
    expect(certificateTarget({ product_id: 9, plot_id: null }, skus)).toBe("Sản phẩm #9");
    expect(certificateTarget({ product_id: null, plot_id: 7 }, skus)).toBe("Đồi #7");
    const codes = new Map([[7, "D-CQ-0001-1"]]);
    expect(certificateTarget({ product_id: null, plot_id: 7 }, skus, codes)).toBe(
      "Đồi D-CQ-0001-1",
    );
  });
  it("ô chọn nơi áp dụng", () => {
    expect(
      targetKindOf([
        { value: "product", checked: false },
        { value: "plot", checked: true },
      ]),
    ).toBe("plot");
    expect(
      targetKindOf([
        { value: "product", checked: true },
        { value: "plot", checked: false },
      ]),
    ).toBe("product");
    expect(targetKindOf([])).toBe("product");
  });
});

describe("tài khoản", () => {
  it("không tự ngừng dùng chính mình", () => {
    expect(isSelf(5, 5)).toBe(true);
    expect(isSelf(5, 6)).toBe(false);
    expect(isSelf(undefined, 5)).toBe(false);
    expect(canToggleStatus(5, { id: 5, status: "ACTIVE" })).toBe(false);
    expect(canToggleStatus(5, { id: 6, status: "ACTIVE" })).toBe(true);
    expect(canToggleStatus(5, { id: 6, status: "INACTIVE" })).toBe(true);
  });
  it("nhãn vai và lần đăng nhập gần nhất", () => {
    expect(roleLabel("OWNER")).toBe("Chủ doanh nghiệp");
    expect(roleLabel("WORKSHOP")).toBe("Xưởng");
    expect(formatLastLogin(null)).toBe("Chưa đăng nhập");
    expect(formatLastLogin("2026-11-22T02:30:00Z")).toBe("22/11/2026 09:30");
    expect(formatLastLogin("không phải ngày")).toBe("không phải ngày");
  });
});

describe("cài đặt", () => {
  const settings = {
    scan_warning_threshold: 20,
    price_deviation_pct: 20,
    label_size: { width_mm: 40, height_mm: 30 },
    print_format: "A5" as const,
    retain_default_months: 12,
  };
  it("đi vòng: settings → form → thân PATCH có label_size lồng nhau", () => {
    const r = buildSettingsBody(settingsToInput(settings));
    expect(r).toEqual({ ok: true, body: settings });
  });
  it("giá trị ngoài khoảng bị chặn theo từng ô", () => {
    const r = buildSettingsBody({
      ...settingsToInput(settings),
      scan_warning_threshold: "0",
      price_deviation_pct: "101",
      label_width_mm: "9",
      label_height_mm: "201",
      retain_default_months: "abc",
      print_format: "B4",
    });
    expect(r.ok).toBe(false);
    if (r.ok) return;
    expect(Object.keys(r.errors).sort()).toEqual([
      "label_height_mm",
      "label_width_mm",
      "price_deviation_pct",
      "print_format",
      "retain_default_months",
      "scan_warning_threshold",
    ]);
  });
  it("ô trống là lỗi bắt buộc", () => {
    const r = buildSettingsBody({ ...settingsToInput(settings), scan_warning_threshold: " " });
    expect(r.ok).toBe(false);
    if (r.ok) return;
    expect(r.errors.scan_warning_threshold).toContain("bắt buộc");
  });
  it("lỗi API của label_size về đúng ô", () => {
    expect(mapSettingsErrorField("label_size.width_mm")).toBe("label_width_mm");
    expect(mapSettingsErrorField("label_size.height_mm")).toBe("label_height_mm");
    expect(mapSettingsErrorField("print_format")).toBe("print_format");
  });
});
