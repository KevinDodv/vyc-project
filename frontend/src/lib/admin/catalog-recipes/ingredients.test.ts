import { describe, expect, it } from "vitest";
import { upperCaseInput } from "./ingredients";

function fakeInput(value: string, caret: number) {
  const input = {
    value,
    selectionStart: caret,
    selectionEnd: caret,
    moved: null as [number, number] | null,
    setSelectionRange(start: number, end: number) {
      input.moved = [start, end];
    },
  };
  return input;
}

describe("upperCaseInput: mã phụ liệu", () => {
  it("đổi sang chữ in hoa và giữ vị trí con trỏ", () => {
    const input = fakeInput("tT1", 1);
    upperCaseInput(input as unknown as HTMLInputElement);
    expect(input.value).toBe("TT1");
    expect(input.moved).toEqual([1, 1]);
  });
  it("đã in hoa thì không đụng", () => {
    const input = fakeInput("DPG", 3);
    upperCaseInput(input as unknown as HTMLInputElement);
    expect(input.moved).toBeNull();
  });
});
