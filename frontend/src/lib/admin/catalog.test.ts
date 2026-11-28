import { describe, expect, it } from "vitest";
import {
  canEditCatalog,
  fieldKind,
  isCatalogStatus,
  listApiQuery,
  listPageUrl,
  pageInfo,
  pageNumbers,
  parseListQuery,
} from "./catalog";

describe("canEditCatalog", () => {
  it("chỉ OWNER sửa được", () => {
    expect(canEditCatalog("OWNER")).toBe(true);
    expect(canEditCatalog("WORKSHOP")).toBe(false);
    expect(canEditCatalog(undefined)).toBe(false);
  });
});

describe("isCatalogStatus", () => {
  it("nhận ACTIVE, INACTIVE", () => {
    expect(isCatalogStatus("ACTIVE")).toBe(true);
    expect(isCatalogStatus("INACTIVE")).toBe(true);
    expect(isCatalogStatus("DRAFT")).toBe(false);
    expect(isCatalogStatus(undefined)).toBe(false);
  });
});

describe("parseListQuery", () => {
  it("mặc định", () => {
    expect(parseListQuery(new URLSearchParams(""))).toEqual({
      q: "",
      status: "",
      page: 1,
      pageSize: 50,
    });
  });
  it("đọc q, status, page, page_size", () => {
    const params = new URLSearchParams("q=%20que%20&status=ACTIVE&page=3&page_size=20");
    expect(parseListQuery(params)).toEqual({ q: "que", status: "ACTIVE", page: 3, pageSize: 20 });
  });
  it("giá trị sai thì về mặc định", () => {
    const params = new URLSearchParams("status=XOA&page=-2&page_size=abc");
    expect(parseListQuery(params)).toEqual({ q: "", status: "", page: 1, pageSize: 50 });
  });
  it("page_size kẹp ở 200 như backend", () => {
    expect(parseListQuery(new URLSearchParams("page_size=999")).pageSize).toBe(200);
  });
  it("page=0 hoặc số thập phân không hợp lệ thì về 1", () => {
    expect(parseListQuery(new URLSearchParams("page=0")).page).toBe(1);
    expect(parseListQuery(new URLSearchParams("page=1.5")).page).toBe(1);
  });
});

describe("listPageUrl", () => {
  it("bỏ tham số mặc định", () => {
    expect(listPageUrl("/quan-ly/loai-hang", { q: "", status: "", page: 1, pageSize: 50 })).toBe(
      "/quan-ly/loai-hang",
    );
  });
  it("giữ q, status, page; mã hoá tiếng Việt", () => {
    expect(
      listPageUrl("/quan-ly/dia-ban", { q: "Văn Yên", status: "ACTIVE", page: 2, pageSize: 50 }),
    ).toBe("/quan-ly/dia-ban?q=V%C4%83n+Y%C3%AAn&status=ACTIVE&page=2");
  });
  it("giữ page_size khác mặc định", () => {
    expect(listPageUrl("/x", { pageSize: 20 })).toBe("/x?page_size=20");
  });
});

describe("listApiQuery", () => {
  it("luôn có page và page_size, chỉ thêm q và status khi có", () => {
    expect(listApiQuery({ q: "", status: "", page: 2, pageSize: 50 })).toEqual({
      page: 2,
      page_size: 50,
    });
    expect(listApiQuery({ q: "que", status: "INACTIVE", page: 1, pageSize: 20 })).toEqual({
      page: 1,
      page_size: 20,
      q: "que",
      status: "INACTIVE",
    });
  });
});

describe("pageInfo", () => {
  it("rỗng", () => {
    expect(pageInfo(1, 50, 0)).toEqual({
      page: 1,
      totalPages: 1,
      from: 0,
      to: 0,
      hasPrev: false,
      hasNext: false,
    });
  });
  it("trang giữa và trang cuối", () => {
    expect(pageInfo(2, 50, 120)).toMatchObject({
      from: 51,
      to: 100,
      totalPages: 3,
      hasPrev: true,
      hasNext: true,
    });
    expect(pageInfo(3, 50, 120)).toMatchObject({ from: 101, to: 120, hasNext: false });
  });
  it("trang vượt quá thì kẹp về trang cuối", () => {
    expect(pageInfo(9, 50, 120).page).toBe(3);
  });
});

describe("pageNumbers", () => {
  it("ít trang thì liệt kê hết", () => {
    expect(pageNumbers(1, 3)).toEqual([1, 2, 3]);
  });
  it("nhiều trang thì có chỗ cách quãng", () => {
    expect(pageNumbers(10, 20)).toEqual([1, "gap", 8, 9, 10, 11, 12, "gap", 20]);
    expect(pageNumbers(1, 20)).toEqual([1, 2, 3, "gap", 20]);
  });
});

describe("fieldKind", () => {
  it("ánh xạ loại ô sang kiểu gửi API", () => {
    expect(fieldKind(undefined)).toBe("text");
    expect(fieldKind("select")).toBe("text");
    expect(fieldKind("textarea")).toBe("text");
    expect(fieldKind("checkbox")).toBe("boolean");
    expect(fieldKind("int")).toBe("int");
    expect(fieldKind("decimal")).toBe("decimal");
    expect(fieldKind("password")).toBe("password");
  });
});
