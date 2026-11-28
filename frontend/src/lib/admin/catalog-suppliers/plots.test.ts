import { describe, expect, it } from "vitest";
import {
  buildPlotBody,
  countActivePlots,
  currentYearVn,
  formatCoordinates,
  type PlotFormValues,
  parseCoordinates,
  parsePhotoUrls,
  plotStatusLabel,
  validateAreaHa,
  validatePhotoUrls,
  validatePlantedYear,
} from "./plots";

const NOW = 2026;
const values = (over: Partial<PlotFormValues> = {}): PlotFormValues => ({
  area_id: "7",
  area_ha: "",
  planted_year: "",
  coordinates: "",
  photo_urls: "",
  is_default: false,
  ...over,
});

describe("parseCoordinates: dán từ Google Maps", () => {
  it("dấu phẩy, chấm phẩy hoặc khoảng trắng; làm tròn 6 chữ số", () => {
    const expected = { ok: true, lat: "21.028579", lng: "105.854193" };
    expect(parseCoordinates("21.0285791, 105.8541934")).toEqual(expected);
    expect(parseCoordinates("21.028579;105.854193")).toEqual(expected);
    expect(parseCoordinates(" 21.028579 105.854193 ")).toEqual(expected);
  });
  it("số âm hợp lệ", () => {
    expect(parseCoordinates("-12.5, -70")).toEqual({
      ok: true,
      lat: "-12.500000",
      lng: "-70.000000",
    });
  });
  it("sai dạng hoặc ngoài miền thì báo lỗi tiếng Việt", () => {
    for (const bad of ["abc", "21.0", "21.0, 105.8, 3", "21,0285 105,85", "21.0 ,"]) {
      expect(parseCoordinates(bad).ok).toBe(false);
    }
    expect(parseCoordinates("91, 100")).toEqual({ ok: false, message: "Vĩ độ phải từ -90 đến 90" });
    expect(parseCoordinates("10, 181")).toEqual({
      ok: false,
      message: "Kinh độ phải từ -180 đến 180",
    });
  });
  it("formatCoordinates", () => {
    expect(formatCoordinates(21.028579, 105.854193)).toBe("21.028579, 105.854193");
    expect(formatCoordinates(null, null)).toBe("");
    expect(formatCoordinates(1, null)).toBe("");
  });
});

describe("validatePlantedYear: 1950 ≤ năm ≤ năm nay", () => {
  it("rỗng là hợp lệ", () => {
    expect(validatePlantedYear("", NOW)).toBeNull();
    expect(validatePlantedYear("  ", NOW)).toBeNull();
  });
  it("biên", () => {
    expect(validatePlantedYear("1950", NOW)).toBeNull();
    expect(validatePlantedYear("2026", NOW)).toBeNull();
    expect(validatePlantedYear("1949", NOW)).toContain("1950");
    expect(validatePlantedYear("2027", NOW)).toContain("năm nay");
  });
  it("không phải số nguyên", () => {
    for (const bad of ["abc", "20.5", "-2000", "1e3"]) {
      expect(validatePlantedYear(bad, NOW)).not.toBeNull();
    }
  });
});

describe("diện tích, ảnh", () => {
  it("validateAreaHa: tối đa 4 chữ số trước, 2 sau dấu phẩy", () => {
    for (const ok of ["", "0", "1,5", "12.25", "9999.99"]) expect(validateAreaHa(ok)).toBeNull();
    for (const bad of ["-1", "1,234", "12345", "abc"]) expect(validateAreaHa(bad)).not.toBeNull();
  });
  it("parsePhotoUrls bỏ dòng trống", () => {
    expect(parsePhotoUrls("/media/a.jpg\r\n\n  https://x.vn/b.png  \n")).toEqual([
      "/media/a.jpg",
      "https://x.vn/b.png",
    ]);
  });
  it("validatePhotoUrls chặn javascript:, data:, http: và quá 10 ảnh", () => {
    expect(validatePhotoUrls(["/media/a.jpg", "https://x.vn/b.png"])).toBeNull();
    for (const bad of [
      "javascript:alert(1)",
      "data:text/html,x",
      "http://x.vn/a.png",
      "a.jpg",
      "https://",
    ]) {
      expect(validatePhotoUrls([bad])).not.toBeNull();
    }
    expect(validatePhotoUrls(Array.from({ length: 11 }, () => "/media/a.jpg"))).toContain("10");
  });
});

describe("buildPlotBody", () => {
  it("dựng thân đúng kiểu: số cân giữ chuỗi, năm là số", () => {
    const result = buildPlotBody(
      values({
        area_ha: "1,5",
        planted_year: "2015",
        coordinates: " 21.0285791, 105.8541934 ",
        photo_urls: "/media/a.jpg\nhttps://x.vn/b.png",
        is_default: true,
      }),
      NOW,
    );
    expect(result).toEqual({
      ok: true,
      body: {
        area_id: 7,
        area_ha: "1.5",
        planted_year: 2015,
        coordinates: "21.0285791, 105.8541934",
        photo_urls: ["/media/a.jpg", "https://x.vn/b.png"],
        is_default: true,
      },
    });
  });
  it("để trống thì null (sửa đồi: xoá toạ độ gửi null)", () => {
    expect(buildPlotBody(values(), NOW)).toEqual({
      ok: true,
      body: {
        area_id: 7,
        area_ha: null,
        planted_year: null,
        coordinates: null,
        photo_urls: [],
        is_default: false,
      },
    });
  });
  it("ô mặc định bị khoá (null) thì không gửi is_default", () => {
    const result = buildPlotBody(values({ is_default: null }), NOW);
    expect(result.ok && "is_default" in result.body).toBe(false);
  });
  it("lỗi năm trồng và các lỗi khác báo theo trường, không gọi API", () => {
    const result = buildPlotBody(
      values({ area_id: "", planted_year: "1900", coordinates: "xyz", photo_urls: "javascript:x" }),
      NOW,
    );
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(Object.keys(result.errors).sort()).toEqual([
        "area_id",
        "coordinates",
        "photo_urls",
        "planted_year",
      ]);
      expect(result.errors.planted_year).toContain("1950");
    }
  });
});

describe("tiện ích", () => {
  it("countActivePlots và nhãn tình trạng", () => {
    expect(
      countActivePlots([{ status: "ACTIVE" }, { status: "INACTIVE" }, { status: "ACTIVE" }]),
    ).toBe(2);
    expect(plotStatusLabel({ status: "ACTIVE", is_default: true })).toBe("Mặc định");
    expect(plotStatusLabel({ status: "ACTIVE", is_default: false })).toBe("Đang dùng");
    expect(plotStatusLabel({ status: "INACTIVE", is_default: false })).toBe("Ngừng dùng");
  });
  it("currentYearVn theo giờ Việt Nam: 31/12 17:30 UTC đã là năm sau", () => {
    expect(currentYearVn(new Date("2026-12-31T16:59:00Z"))).toBe(2026);
    expect(currentYearVn(new Date("2026-12-31T17:30:00Z"))).toBe(2027);
  });
});
