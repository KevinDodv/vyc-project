import { describe, expect, it } from "vitest";
import {
  CATALOG_MENU,
  isActivePath,
  isCatalogPath,
  ROLE_LABEL,
  userLabel,
  visibleMenu,
} from "./menu";

const ROUTES = [
  "dia-ban",
  "loai-hang",
  "nguyen-lieu",
  "bang-gia",
  "nguoi-ban",
  "khach-hang",
  "phu-lieu",
  "cong-thuc",
  "san-pham",
  "chung-nhan",
  "tai-khoan",
  "cai-dat",
].map((slug) => `/quan-ly/${slug}`);

describe("CATALOG_MENU", () => {
  it("có đủ 12 mục của brief, dưới /quan-ly, không trùng", () => {
    const hrefs = CATALOG_MENU.map((item) => item.href);
    expect([...hrefs].sort()).toEqual([...ROUTES].sort());
    expect(new Set(hrefs).size).toBe(hrefs.length);
  });
});

describe("visibleMenu", () => {
  it("OWNER thấy cả 12 mục", () => {
    expect(visibleMenu("OWNER")).toHaveLength(12);
  });
  it("WORKSHOP không thấy mục OWNER-only (bảng giá, tài khoản, cài đặt...)", () => {
    const hrefs = visibleMenu("WORKSHOP").map((item) => item.href);
    for (const hidden of [
      "bang-gia",
      "tai-khoan",
      "cai-dat",
      "khach-hang",
      "san-pham",
      "chung-nhan",
    ]) {
      expect(hrefs).not.toContain(`/quan-ly/${hidden}`);
    }
  });
  it("WORKSHOP vẫn xem được công thức, phụ liệu và các danh mục tra cứu", () => {
    const hrefs = visibleMenu("WORKSHOP").map((item) => item.href);
    for (const shown of [
      "cong-thuc",
      "phu-lieu",
      "dia-ban",
      "loai-hang",
      "nguyen-lieu",
      "nguoi-ban",
    ]) {
      expect(hrefs).toContain(`/quan-ly/${shown}`);
    }
  });
  it("chưa đăng nhập thì không có mục nào", () => {
    expect(visibleMenu(undefined)).toEqual([]);
  });
});

describe("isActivePath", () => {
  it("khớp đúng đường dẫn và trang con", () => {
    expect(isActivePath("/quan-ly/loai-hang", "/quan-ly/loai-hang")).toBe(true);
    expect(isActivePath("/quan-ly/loai-hang", "/quan-ly/loai-hang/")).toBe(true);
    expect(isActivePath("/quan-ly/loai-hang", "/quan-ly/loai-hang/3")).toBe(true);
  });
  it("không nhầm tiền tố chung chữ", () => {
    expect(isActivePath("/quan-ly/san-pham", "/quan-ly/san-pham-moi")).toBe(false);
    expect(isActivePath("/quan-ly/cong-thuc", "/quan-ly")).toBe(false);
  });
  it("isCatalogPath", () => {
    expect(isCatalogPath("/quan-ly/phu-lieu/2")).toBe(true);
    expect(isCatalogPath("/quan-ly")).toBe(false);
  });
});

describe("userLabel (#915)", () => {
  it("họ tên trùng nhãn vai thì chỉ hiện một lần", () => {
    expect(userLabel({ full_name: "Chủ doanh nghiệp", role: "OWNER" })).toEqual({
      name: "Chủ doanh nghiệp",
      roleBadge: null,
    });
  });
  it("trùng không phân biệt hoa thường và khoảng trắng", () => {
    expect(userLabel({ full_name: "  chủ DOANH nghiệp ", role: "OWNER" }).roleBadge).toBeNull();
  });
  it("họ tên khác thì kèm huy hiệu vai", () => {
    expect(userLabel({ full_name: "Nguyễn Văn A", role: "WORKSHOP" })).toEqual({
      name: "Nguyễn Văn A",
      roleBadge: ROLE_LABEL.WORKSHOP,
    });
  });
  it("họ tên trống thì hiện nhãn vai, không để trống", () => {
    expect(userLabel({ full_name: " ", role: "OWNER" })).toEqual({
      name: ROLE_LABEL.OWNER,
      roleBadge: null,
    });
  });
});
