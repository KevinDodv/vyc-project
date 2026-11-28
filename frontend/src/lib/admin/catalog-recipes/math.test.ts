import { describe, expect, it } from "vitest";
import {
  altGroupLabel,
  computeBaseBatch,
  displayGram,
  displayPct,
  formatGram,
  formatPct,
  itemPctBasis,
  parseGram,
  scaleLine,
} from "./math";

const line = (g: string, altGroup: number | null = null) => ({ centi: parseGram(g), altGroup });

describe("parseGram", () => {
  it("đọc số nguyên, dấu chấm và dấu phẩy", () => {
    expect(parseGram("12")).toBe(1200);
    expect(parseGram("12.5")).toBe(1250);
    expect(parseGram("12,5")).toBe(1250);
    expect(parseGram(" 0.05 ")).toBe(5);
    expect(parseGram("99999999.99")).toBe(9_999_999_999);
  });
  it("không nhận số không, âm, quá 2 số lẻ, quá cột numeric(10,2), chữ", () => {
    for (const bad of [
      "",
      "0",
      "0.00",
      "-1",
      "1.234",
      "100000000",
      "1e3",
      "abc",
      "1.",
      ".5",
      "1 2",
    ]) {
      expect(parseGram(bad), bad).toBeNull();
    }
  });
});

describe("định dạng", () => {
  it("formatGram luôn hai số lẻ, dấu chấm (dạng API)", () => {
    expect(formatGram(1250)).toBe("12.50");
    expect(formatGram(5)).toBe("0.05");
    expect(formatGram(0)).toBe("0.00");
    expect(formatPct(3333)).toBe("33.33");
  });
  it("displayGram bỏ số 0 thừa, dùng dấu phẩy", () => {
    expect(displayGram(1250)).toBe("12,5");
    expect(displayGram(1200)).toBe("12");
    expect(displayGram(10000)).toBe("100");
    expect(displayGram(100005)).toBe("1000,05");
    expect(displayGram(50)).toBe("0,5");
  });
  it("displayPct", () => {
    expect(displayPct(3333)).toBe("33,33 %");
    expect(displayPct(10000)).toBe("100,00 %");
    expect(displayPct(null)).toBe("–");
  });
  it("nhãn nhóm lựa chọn", () => {
    expect(altGroupLabel(1)).toBe("Nhóm 1");
    expect(altGroupLabel(2)).toBe("Nhóm 2");
  });
});

describe("computeBaseBatch (BR-26c)", () => {
  it("cộng các dòng bắt buộc", () => {
    expect(computeBaseBatch([line("60"), line("30"), line("10")])).toBe(10_000);
  });
  it("mỗi nhóm lựa chọn chỉ tính một phương án: phương án nặng nhất", () => {
    // 50 + max(20, 30) + max(10, 5) = 90
    const lines = [line("50"), line("20", 1), line("30", 1), line("10", 2), line("5", 2)];
    expect(computeBaseBatch(lines)).toBe(9_000);
  });
  it("dòng chưa nhập gram thì chưa tính; danh sách rỗng là 0", () => {
    expect(computeBaseBatch([line("10"), line(""), line("abc", 1)])).toBe(1_000);
    expect(computeBaseBatch([])).toBe(0);
  });
  it("tuỳ chọn vẫn cộng vào mẻ như dòng thường (backend không loại dòng tuỳ chọn)", () => {
    expect(computeBaseBatch([line("10"), line("2.5")])).toBe(1_250);
  });
  it("không sai số thực: 0,1 + 0,2 = 0,3", () => {
    expect(computeBaseBatch([line("0.1"), line("0.2")])).toBe(30);
  });
});

describe("itemPctBasis (% khối lượng, nửa lên)", () => {
  it("tròn số", () => {
    expect(itemPctBasis(6000, 10_000)).toBe(6000);
    expect(itemPctBasis(10_000, 10_000)).toBe(10_000);
  });
  it("làm tròn 2 số lẻ: 1/3 và 2/3", () => {
    expect(itemPctBasis(100, 300)).toBe(3333);
    expect(itemPctBasis(200, 300)).toBe(6667);
  });
  it("đúng nửa thì lên: 0,005 % → 0,01 %", () => {
    expect(itemPctBasis(1, 20_000)).toBe(1);
    expect(itemPctBasis(1, 20_001)).toBe(0);
  });
  it("chưa tính được thì null", () => {
    expect(itemPctBasis(null, 100)).toBeNull();
    expect(itemPctBasis(100, 0)).toBeNull();
  });
  it("dòng thuộc nhóm lựa chọn chia cho mẻ chuẩn: 30/90", () => {
    expect(itemPctBasis(3_000, 9_000)).toBe(3333);
  });
});

describe("scaleLine (BR-26f)", () => {
  it("gram * mẻ / mẻ chuẩn, 2 số lẻ", () => {
    // 33,33 g của mẻ 100 g, làm mẻ 250,50 g → 83,49165 → 83,49
    expect(scaleLine(3333, 25_050, 10_000)).toBe(8349);
    expect(scaleLine(6000, 50_000, 10_000)).toBe(30_000);
  });
  it("đúng nửa thì lên: 0,01 g * 50 / 100 = 0,005 → 0,01", () => {
    expect(scaleLine(1, 5_000, 10_000)).toBe(1);
  });
  it("mẻ chuẩn không hợp lệ thì null; số lớn không tràn", () => {
    expect(scaleLine(100, 100, 0)).toBeNull();
    expect(scaleLine(9_999_999_999, 9_999_999_999, 9_999_999_999)).toBe(9_999_999_999);
  });
});
