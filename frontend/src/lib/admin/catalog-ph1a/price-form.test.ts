import { describe, expect, it, vi } from "vitest";
import { bindDateAutosubmit } from "./price-form";

/** Ô ngày giả: đủ addEventListener, value, defaultValue và form.requestSubmit. */
function dateInput() {
  const requestSubmit = vi.fn();
  const input = Object.assign(new EventTarget(), {
    value: "2026-11-20",
    defaultValue: "2026-11-20",
    form: { requestSubmit },
  });
  bindDateAutosubmit(input as unknown as HTMLInputElement);
  const fire = (type: string, key?: string) =>
    input.dispatchEvent(Object.assign(new Event(type), { key }));
  return { input, fire, requestSubmit };
}

describe("bindDateAutosubmit", () => {
  it("chọn trên lịch thì chuyển ngay", () => {
    const { input, fire, requestSubmit } = dateInput();
    fire("pointerdown");
    input.value = "2026-11-10";
    fire("change");
    expect(requestSubmit).toHaveBeenCalledTimes(1);
  });
  it("đang gõ phím thì đợi rời ô", () => {
    const { input, fire, requestSubmit } = dateInput();
    fire("keydown", "2");
    input.value = "0002-11-20";
    fire("change");
    expect(requestSubmit).not.toHaveBeenCalled();
    input.value = "2025-11-20";
    fire("blur");
    expect(requestSubmit).toHaveBeenCalledTimes(1);
  });
  it("không đổi ngày thì rời ô không tải lại", () => {
    const { fire, requestSubmit } = dateInput();
    fire("keydown", "Tab");
    fire("blur");
    expect(requestSubmit).not.toHaveBeenCalled();
  });
});
