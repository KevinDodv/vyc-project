import { describe, expect, it } from "vitest";
import { applyParentFilter, wantedParentLevel } from "./area-parent";

const opt = (value: string, selected = false) => ({
  value,
  hidden: false,
  disabled: false,
  selected,
});

describe("wantedParentLevel", () => {
  it("xã → tỉnh, thôn → xã, tỉnh và rỗng → không có cha", () => {
    expect(wantedParentLevel("COMMUNE")).toBe("PROVINCE");
    expect(wantedParentLevel("VILLAGE")).toBe("COMMUNE");
    expect(wantedParentLevel("PROVINCE")).toBeNull();
    expect(wantedParentLevel("")).toBeNull();
  });
});

describe("applyParentFilter", () => {
  const levels = { "1": "PROVINCE", "3": "COMMUNE" };
  it("chỉ giữ địa bàn đúng cấp cha, luôn giữ ô «— Chọn —»", () => {
    const options = [opt(""), opt("1"), opt("3")];
    applyParentFilter(options, levels, "COMMUNE");
    expect(options.map((o) => o.hidden)).toEqual([false, false, true]);
    expect(options.map((o) => o.disabled)).toEqual([false, false, true]);
  });
  it("báo lựa chọn đang chọn bị ẩn", () => {
    const options = [opt(""), opt("1", true), opt("3")];
    expect(applyParentFilter(options, levels, "VILLAGE")).toBe(true);
    expect(options[2]?.hidden).toBe(false);
  });
  it("cấp tỉnh: ẩn hết", () => {
    const options = [opt(""), opt("1"), opt("3")];
    applyParentFilter(options, levels, "PROVINCE");
    expect(options.slice(1).every((o) => o.hidden)).toBe(true);
  });
});
