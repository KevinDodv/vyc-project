import { describe, expect, it } from "vitest";
import { shouldOpenRow } from "./catalog-list";

function target(matchesInteractive: boolean): Element {
  return { closest: () => (matchesInteractive ? ({} as Element) : null) } as unknown as Element;
}

describe("shouldOpenRow", () => {
  it("bấm vào ô thường thì mở form sửa", () => {
    expect(shouldOpenRow(target(false))).toBe(true);
  });
  it("bấm vào liên kết, nút hay ô nhập thì để yên cho phần tử đó xử lý", () => {
    expect(shouldOpenRow(target(true))).toBe(false);
  });
  it("không có phần tử đích thì mở", () => {
    expect(shouldOpenRow(null)).toBe(true);
  });
});
