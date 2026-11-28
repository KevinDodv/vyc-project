/** Hành vi trình duyệt của lưới bảng giá (PriceGrid.astro, task #93): đọc các ô, kiểm, PUT /prices/{date}. */

import { ApiRequestError, api } from "../../../scripts/admin/api";
import { GENERIC_ERROR, parseApiError } from "../form";
import { type CellInput, type PriceItemBody, preparePrices } from "./prices";

type Put = (path: string, body: { items: PriceItemBody[] }) => Promise<unknown>;

/** Đọc lưới: mỗi hạng có hai ô `data-price-buy`/`data-price-sell` mang `data-grade-id`,
 *  và giá lúc mở trang ở `data-initial`. */
export function readGrid(root: ParentNode): {
  cells: CellInput[];
  initial: Array<{ grade_id: number; buy_price: number | null; sell_price: number | null }>;
} {
  const cells = new Map<number, CellInput>();
  const initial = new Map<
    number,
    { grade_id: number; buy_price: number | null; sell_price: number | null }
  >();
  const num = (text: string | undefined): number | null =>
    text && /^\d+$/.test(text) ? Number(text) : null;
  for (const input of Array.from(root.querySelectorAll<HTMLInputElement>("input[data-price]"))) {
    const id = Number(input.dataset.gradeId);
    if (!Number.isInteger(id)) continue;
    const side = input.dataset.price === "buy" ? "buy" : "sell";
    const cell = cells.get(id) ?? { grade_id: id, buy: "", sell: "" };
    cell[side] = input.value;
    cells.set(id, cell);
    const start = initial.get(id) ?? { grade_id: id, buy_price: null, sell_price: null };
    if (side === "buy") start.buy_price = num(input.dataset.initial);
    else start.sell_price = num(input.dataset.initial);
    initial.set(id, start);
  }
  return { cells: [...cells.values()], initial: [...initial.values()] };
}

function clear(form: HTMLElement): void {
  for (const el of Array.from(form.querySelectorAll<HTMLElement>("[data-price-error]"))) {
    el.textContent = "";
    el.hidden = true;
  }
  for (const el of Array.from(form.querySelectorAll("[aria-invalid]")))
    el.removeAttribute("aria-invalid");
  const box = form.querySelector<HTMLElement>("[data-form-error]");
  if (box) {
    box.textContent = "";
    box.hidden = true;
  }
}

function showGeneral(form: HTMLElement, message: string): void {
  const box = form.querySelector<HTMLElement>("[data-form-error]");
  if (!box) return;
  box.textContent = message;
  box.hidden = false;
  box.focus();
}

export function bindPriceForm(
  form: HTMLFormElement,
  put: Put = (path, body) => api.put(path, body),
  navigate: (url: string) => void = (url) => window.location.assign(url),
): void {
  const date = form.dataset.date;
  if (!date) return;
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    clear(form);
    const { cells, initial } = readGrid(form);
    const prepared = preparePrices(cells, initial);
    if (!prepared.ok) {
      if (prepared.empty) {
        showGeneral(form, "Chưa sửa ô giá nào. Sửa giá rồi bấm Lưu.");
        return;
      }
      let first: HTMLElement | null = null;
      for (const err of prepared.errors) {
        const slot = form.querySelector<HTMLElement>(
          `[data-price-error="${err.grade_id}-${err.field}"]`,
        );
        const input = form.querySelector<HTMLElement>(
          `input[data-price="${err.field}"][data-grade-id="${err.grade_id}"]`,
        );
        if (slot) {
          slot.textContent = err.message;
          slot.hidden = false;
        }
        input?.setAttribute("aria-invalid", "true");
        first ??= input;
      }
      first?.focus();
      return;
    }
    const buttons = Array.from(form.querySelectorAll<HTMLButtonElement>("button[data-action]"));
    for (const b of buttons) b.disabled = true;
    try {
      await put(`/prices/${date}`, { items: prepared.items });
      navigate(`/quan-ly/bang-gia?date=${encodeURIComponent(date)}&saved=1`);
    } catch (error) {
      for (const b of buttons) b.disabled = false;
      const parsed =
        error instanceof ApiRequestError
          ? parseApiError(error)
          : { fields: {}, general: GENERIC_ERROR };
      const parts = [parsed.general, ...Object.values(parsed.fields)].filter(Boolean);
      showGeneral(form, parts.join(". ") || GENERIC_ERROR);
    }
  });
}

/** Ô «Ngày áp dụng» tự chuyển trang. Chọn trên lịch (không gõ phím) thì chuyển ngay. Đang gõ thì Chrome
 *  bắn `change` sau mỗi phím đã thành ngày hợp lệ (năm 0002, tháng 1 trước 12), nên đợi rời ô; Enter do
 *  form tự gửi. */
export function bindDateAutosubmit(input: HTMLInputElement): void {
  let typing = false;
  const submit = () => {
    if (input.value && input.value !== input.defaultValue) input.form?.requestSubmit();
  };
  input.addEventListener("pointerdown", () => {
    typing = false;
  });
  input.addEventListener("keydown", (event) => {
    if (event.key !== "Enter" && event.key !== "Tab") typing = true;
  });
  input.addEventListener("change", () => {
    if (!typing) submit();
  });
  input.addEventListener("blur", submit);
}

export function bindAllPriceForms(root: ParentNode = document): void {
  for (const form of Array.from(root.querySelectorAll<HTMLFormElement>("form[data-price-form]"))) {
    bindPriceForm(form);
  }
  for (const input of Array.from(
    root.querySelectorAll<HTMLInputElement>("input[data-autosubmit]"),
  )) {
    bindDateAutosubmit(input);
  }
}
