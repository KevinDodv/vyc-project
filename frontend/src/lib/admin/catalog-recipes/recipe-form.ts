/** Hành vi phía trình duyệt của form công thức (task #95): bảng thành phần, % khối lượng tính sẵn,
 *  mẻ chuẩn tự cộng, ô thử scale, lưu nháp, «Kích hoạt», «Ngừng», «Tạo phiên bản mới».
 *  TypeScript thuần, không framework (frontend-seo.md 3.2). Phần tính toán là hàm thuần để vitest kiểm;
 *  phần DOM (`bindRecipeForm`) chỉ đọc/ghi giá trị ô theo `data-*` do `_RecipeForm.astro` render. */

import { api } from "../../../scripts/admin/api";
import { sanitizeNext } from "../../../scripts/admin/next";
import {
  clearErrors,
  type ParsedError,
  parseApiError,
  REQUIRED_MESSAGE,
  showErrors,
} from "../form";
import {
  altGroupLabel,
  computeBaseBatch,
  displayGram,
  displayPct,
  formatGram,
  itemPctBasis,
  parseGram,
  type RecipeLine,
  scaleLine,
} from "./math";

// ------------------------------------------------------------------ dữ liệu thuần

export type ItemState = {
  ingredientId: number | null;
  /** Chữ người dùng gõ ở ô gram. */
  qtyText: string;
  altGroup: number | null;
  isOptional: boolean;
  note: string;
};

export type ItemBody = {
  ingredient_id: number;
  qty_g: string;
  alt_group: number | null;
  is_optional: boolean;
  note: string | null;
};

export const HEADER_FIELDS = [
  "code",
  "name",
  "output_kind",
  "output_ingredient_id",
  "base_label",
  "cure_min_days",
  "cure_max_days",
  "retain_months",
  "note",
] as const;
export type HeaderField = (typeof HEADER_FIELDS)[number];
export type HeaderValues = Record<HeaderField, string>;

const INT_FIELDS: ReadonlySet<HeaderField> = new Set([
  "output_ingredient_id",
  "cure_min_days",
  "cure_max_days",
  "retain_months",
]);

export const ITEMS_ERROR_FIELD = "items";

export function isBlankItem(item: ItemState): boolean {
  return item.ingredientId === null && item.qtyText.trim() === "" && item.note.trim() === "";
}

/** Bỏ dòng hoàn toàn trống (người dùng bấm «Thêm dòng» rồi không điền). */
export function nonBlankItems(items: readonly ItemState[]): ItemState[] {
  return items.filter((i) => !isBlankItem(i));
}

export function itemsToLines(items: readonly ItemState[]): RecipeLine[] {
  return items.map((i) => ({ centi: parseGram(i.qtyText), altGroup: i.altGroup }));
}

/** Kiểm nhanh trước khi gửi; thông điệp khác của API (trùng phụ liệu, nhóm lẻ, vòng lặp) do máy chủ báo. */
export function validateItems(items: readonly ItemState[]): string | null {
  for (const [index, item] of items.entries()) {
    const line = index + 1;
    if (item.ingredientId === null) return `Dòng ${line}: chọn phụ liệu`;
    if (parseGram(item.qtyText) === null) {
      return `Dòng ${line}: gram phải là số lớn hơn 0 và nhỏ hơn 100 000 000, tối đa 2 số lẻ`;
    }
  }
  return null;
}

/** Thân PUT /recipes/{id}/items (thứ tự mảng là line_no). Gọi sau `validateItems`. */
export function itemsToBody(items: readonly ItemState[]): ItemBody[] {
  const out: ItemBody[] = [];
  for (const item of items) {
    const centi = parseGram(item.qtyText);
    if (item.ingredientId === null || centi === null) continue;
    out.push({
      ingredient_id: item.ingredientId,
      qty_g: formatGram(centi),
      alt_group: item.altGroup,
      is_optional: item.isOptional,
      note: item.note.trim() || null,
    });
  }
  return out;
}

function headerValue(field: HeaderField, raw: string): string | number | null {
  const text = raw.trim();
  if (!text) return null;
  if (INT_FIELDS.has(field)) return /^\d+$/.test(text) ? Number(text) : text;
  return text;
}

/** Công thức thành phẩm không có phụ liệu làm ra (RECIPE_OUTPUT_FORBIDDEN): xoá giá trị khi chọn «Thành phẩm». */
export function normalizeHeader(values: HeaderValues): HeaderValues {
  return values.output_kind === "INTERMEDIATE" ? values : { ...values, output_ingredient_id: "" };
}

export type HeaderBody = Record<string, string | number | null>;

/** Thân POST /recipes (chưa gồm `items`). */
export function headerToCreateBody(values: HeaderValues): HeaderBody {
  const v = normalizeHeader(values);
  const body: HeaderBody = {};
  for (const field of HEADER_FIELDS) body[field] = headerValue(field, v[field]);
  return body;
}

/** Thân PATCH /recipes/{id}: chỉ trường đã đổi; mã và phiên bản không đổi được. Rỗng thì không có gì để gửi. */
export function headerToPatchBody(initial: HeaderValues, current: HeaderValues): HeaderBody {
  const a = normalizeHeader(initial);
  const b = normalizeHeader(current);
  const body: HeaderBody = {};
  for (const field of HEADER_FIELDS) {
    if (field === "code") continue;
    if (a[field].trim() !== b[field].trim()) body[field] = headerValue(field, b[field]);
  }
  return body;
}

function itemKey(item: ItemState): unknown[] {
  const centi = parseGram(item.qtyText);
  return [
    item.ingredientId,
    centi === null ? item.qtyText.trim() : centi,
    item.altGroup,
    item.isOptional,
    item.note.trim(),
  ];
}

/** Hai danh sách dòng có cùng nội dung không (bỏ dòng trống, so gram theo giá trị: "12,5" = "12.50"). */
export function sameItems(a: readonly ItemState[], b: readonly ItemState[]): boolean {
  return (
    JSON.stringify(nonBlankItems(a).map(itemKey)) === JSON.stringify(nonBlankItems(b).map(itemKey))
  );
}

export type FormView = {
  /** Mẻ chuẩn tự cộng (centigram). */
  baseCenti: number;
  /** % khối lượng từng dòng, cùng thứ tự với `items`; "–" khi chưa tính được. */
  pcts: string[];
};

/** `savedBaseCenti` là mẻ chuẩn đang lưu ở máy chủ: không còn dòng nào thì máy chủ giữ số đó
 *  (công thức sơ chế như SC-VQH), nên form cũng hiện đúng số đó thay vì 0. */
export function computeView(
  items: readonly ItemState[],
  savedBaseCenti: number | null = null,
): FormView {
  const lines = itemsToLines(items);
  const summed = computeBaseBatch(lines);
  const baseCenti = nonBlankItems(items).length === 0 ? (savedBaseCenti ?? summed) : summed;
  return {
    baseCenti,
    pcts: lines.map((l) => displayPct(itemPctBasis(l.centi, baseCenti))),
  };
}

export type ScaleRow = { label: string; baseText: string; suggestedText: string; group: string };
export type ScaleView =
  | { kind: "empty" }
  | { kind: "error"; message: string }
  | { kind: "ok"; batchText: string; rows: ScaleRow[] };

/** Bảng «thử scale»: lượng cân gợi ý của từng dòng khi làm mẻ `batchText` gram (BR-26f). */
export function computeScale(
  items: readonly ItemState[],
  batchText: string,
  labelOf: (ingredientId: number) => string,
): ScaleView {
  if (batchText.trim() === "") return { kind: "empty" };
  const batch = parseGram(batchText);
  if (batch === null) {
    return {
      kind: "error",
      message: "Mẻ cần làm phải là số gram lớn hơn 0 và nhỏ hơn 100 000 000, tối đa 2 số lẻ",
    };
  }
  const lines = itemsToLines(items);
  const base = computeBaseBatch(lines);
  if (base <= 0) return { kind: "error", message: "Chưa có dòng nào có gram để tính" };
  const rows: ScaleRow[] = [];
  for (const [index, item] of items.entries()) {
    const centi = lines[index]?.centi ?? null;
    if (item.ingredientId === null || centi === null) continue;
    const suggested = scaleLine(centi, batch, base);
    const group =
      item.altGroup !== null ? altGroupLabel(item.altGroup) : item.isOptional ? "Tuỳ chọn" : "";
    rows.push({
      label: labelOf(item.ingredientId),
      baseText: displayGram(centi),
      suggestedText: suggested === null ? "–" : displayGram(suggested),
      group,
    });
  }
  return { kind: "ok", batchText: displayGram(batch), rows };
}

/** Trường bắt buộc còn trống ở phần đầu form; `code` chỉ bắt buộc khi tạo mới. */
export function missingHeaderFields(values: HeaderValues, creating: boolean): HeaderField[] {
  const required: HeaderField[] = ["name", "output_kind", "cure_min_days"];
  if (creating) required.unshift("code");
  return required.filter((f) => values[f].trim() === "");
}

// ------------------------------------------------------------------ gửi thay đổi

type Send = (method: "POST" | "PATCH" | "PUT", path: string, body?: unknown) => Promise<unknown>;

/** Dữ liệu máy chủ đang giữ, theo những gì trang này biết. */
export type SavedDraft = {
  header: HeaderValues;
  items: ItemState[];
  baseCenti: number | null;
};

/** PATCH phần đầu nếu đổi rồi PUT dòng nếu đổi. Lệnh nào thành công thì ghi ngay vào `saved`, để khi
 *  lệnh sau lỗi, lần bấm tiếp vẫn so với đúng dữ liệu máy chủ. `items` đã bỏ dòng trống và đã kiểm. */
export async function sendDraftChanges(
  recipeId: number,
  saved: SavedDraft,
  header: HeaderValues,
  items: ItemState[],
  send: Send,
): Promise<void> {
  const patch = headerToPatchBody(saved.header, header);
  if (Object.keys(patch).length > 0) {
    await send("PATCH", `/recipes/${recipeId}`, patch);
    saved.header = header;
  }
  if (!sameItems(saved.items, items)) {
    await send("PUT", `/recipes/${recipeId}/items`, { items: itemsToBody(items) });
    saved.items = items;
    if (items.length > 0) saved.baseCenti = computeBaseBatch(itemsToLines(items));
  }
}

// ------------------------------------------------------------------ DOM

export type RecipeFormDeps = {
  send: Send;
  navigate: (url: string) => void;
};

const defaultDeps: RecipeFormDeps = {
  send: (method, path, body) =>
    method === "POST"
      ? api.post(path, body)
      : method === "PUT"
        ? api.put(path, body)
        : api.patch(path, body),
  navigate: (url) => window.location.assign(url),
};

/** Lỗi kiểm ở trình duyệt (trước khi gọi API), cùng dạng với lỗi API để dùng chung `showErrors`. */
class FormProblem extends Error {
  readonly parsed: ParsedError;
  constructor(parsed: ParsedError) {
    super("form problem");
    this.parsed = parsed;
  }
}

function control(root: ParentNode, name: string): HTMLInputElement | HTMLSelectElement | null {
  return root.querySelector<HTMLInputElement | HTMLSelectElement>(`[name="${name}"]`);
}

function readHeader(form: HTMLFormElement): HeaderValues {
  const values = {} as HeaderValues;
  for (const field of HEADER_FIELDS) values[field] = control(form, field)?.value ?? "";
  return values;
}

function toIntOrNull(text: string): number | null {
  return /^\d+$/.test(text.trim()) ? Number(text) : null;
}

function readRow(row: HTMLElement): ItemState {
  const get = (field: string) =>
    row.querySelector<HTMLInputElement | HTMLSelectElement>(`[data-field="${field}"]`);
  const optional = get("optional");
  return {
    ingredientId: toIntOrNull(get("ingredient")?.value ?? ""),
    qtyText: get("qty")?.value ?? "",
    altGroup: toIntOrNull(get("alt")?.value ?? ""),
    isOptional: optional instanceof HTMLInputElement ? optional.checked : false,
    note: get("note")?.value ?? "",
  };
}

function rowsOf(form: HTMLFormElement): HTMLElement[] {
  return Array.from(form.querySelectorAll<HTMLElement>("[data-item-body] > tr[data-item-row]"));
}

function readItems(form: HTMLFormElement): ItemState[] {
  return rowsOf(form).map(readRow);
}

/** Phụ liệu (id) → "TD — Tinh dầu quế" của các dòng đang chọn, đọc từ chính ô chọn trên từng dòng
 *  (`querySelector` không đi vào nội dung `<template>` nên không đọc được từ mẫu dòng). */
function ingredientLabels(form: HTMLFormElement): Map<number, string> {
  const labels = new Map<number, string>();
  for (const row of rowsOf(form)) {
    const select = row.querySelector<HTMLSelectElement>("select[data-field='ingredient']");
    const option = select?.selectedOptions[0];
    const id = toIntOrNull(option?.value ?? "");
    if (id !== null) labels.set(id, option?.textContent?.trim() ?? String(id));
  }
  return labels;
}

function setText(root: ParentNode, selector: string, text: string): void {
  const el = root.querySelector<HTMLElement>(selector);
  if (el) el.textContent = text;
}

function renderPcts(
  form: HTMLFormElement,
  items: readonly ItemState[],
  savedBaseCenti: number | null,
): void {
  const view = computeView(items, savedBaseCenti);
  for (const [index, row] of rowsOf(form).entries()) {
    setText(row, "[data-pct]", view.pcts[index] ?? "–");
    setText(row, "[data-line-no]", String(index + 1));
  }
  setText(form, "[data-base-total]", `${displayGram(view.baseCenti)} g`);
}

function renderScale(form: HTMLFormElement, items: readonly ItemState[]): void {
  const input = form.querySelector<HTMLInputElement>("[data-scale-batch]");
  const body = form.querySelector<HTMLElement>("[data-scale-body]");
  const message = form.querySelector<HTMLElement>("[data-scale-message]");
  const table = form.querySelector<HTMLElement>("[data-scale-table]");
  if (!input || !body || !message) return;
  const labels = ingredientLabels(form);
  const view = computeScale(items, input.value, (id) => labels.get(id) ?? `#${id}`);
  body.replaceChildren();
  message.hidden = true;
  message.textContent = "";
  if (table) table.hidden = view.kind !== "ok";
  if (view.kind === "empty") return;
  if (view.kind === "error") {
    message.textContent = view.message;
    message.hidden = false;
    return;
  }
  for (const r of view.rows) {
    const tr = document.createElement("tr");
    const cells: ReadonlyArray<readonly [string, boolean]> = [
      [r.label, false],
      [r.group, false],
      [r.baseText, true],
      [r.suggestedText, true],
    ];
    for (const [text, numeric] of cells) {
      const td = document.createElement("td");
      td.textContent = text;
      if (numeric) td.className = "text-end font-mono";
      tr.append(td);
    }
    body.append(tr);
  }
}

function setBusy(form: HTMLFormElement, busy: boolean): void {
  for (const button of Array.from(
    form.querySelectorAll<HTMLButtonElement>("button[data-action]"),
  )) {
    button.disabled = busy;
  }
}

const LABELS: Record<string, string> = {
  code: "Mã công thức",
  name: "Tên công thức",
  output_kind: "Loại đầu ra",
  output_ingredient_id: "Phụ liệu làm ra",
  cure_min_days: "Ngày ủ tối thiểu",
  cure_max_days: "Ngày ủ tối đa",
  retain_months: "Tháng lưu mẫu",
  items: "Thành phần",
};

function showFailure(form: HTMLFormElement, error: unknown): void {
  const parsed = error instanceof FormProblem ? error.parsed : parseApiError(error);
  setBusy(form, false);
  const first = showErrors(form, parsed, LABELS);
  first?.focus();
  form
    .querySelector<HTMLElement>("[data-error-for]:not([hidden]), [data-form-error]:not([hidden])")
    ?.scrollIntoView?.({ block: "center" });
}

function detailUrl(data: unknown): string | null {
  if (typeof data !== "object" || data === null) return null;
  const id = (data as { id?: unknown }).id;
  return typeof id === "number" ? sanitizeNext(`/quan-ly/cong-thuc/${id}`) : null;
}

/** Ô «Phụ liệu làm ra» chỉ hiện khi loại đầu ra là bán thành phẩm. */
function toggleOutput(form: HTMLFormElement): void {
  const kind = control(form, "output_kind")?.value;
  const wrapper = form.querySelector<HTMLElement>("[data-field='output_ingredient_id']");
  if (wrapper) wrapper.hidden = kind !== "INTERMEDIATE";
}

/** Gắn hành vi cho `form[data-recipe-form]`. Form chỉ đọc (`data-readonly`) chỉ cần tính % và thử scale. */
export function bindRecipeForm(form: HTMLFormElement, deps: RecipeFormDeps = defaultDeps): void {
  const recipeId = toIntOrNull(form.dataset.recipeId ?? "");
  const readonly = form.hasAttribute("data-readonly");
  const saved: SavedDraft = {
    header: readHeader(form),
    items: readItems(form),
    baseCenti: parseGram(form.dataset.savedBase ?? ""),
  };

  const refresh = (): void => {
    const items = readItems(form);
    renderPcts(form, items, saved.baseCenti);
    renderScale(form, items);
  };
  refresh();
  toggleOutput(form);

  form.addEventListener("input", (event) => {
    const target = event.target;
    // Mã công thức luôn chữ in hoa (API chỉ nhận chữ hoa, số, dấu gạch ngang).
    if (target instanceof HTMLInputElement && target.name === "code") {
      target.value = target.value.toUpperCase();
    }
    refresh();
  });
  // Enter trong ô thử scale chỉ để tính, không được lưu form.
  form.querySelector("[data-scale-batch]")?.addEventListener("keydown", (event) => {
    if ((event as KeyboardEvent).key === "Enter") event.preventDefault();
  });
  form.addEventListener("change", (event) => {
    const target = event.target;
    if (target instanceof HTMLSelectElement && target.name === "output_kind") toggleOutput(form);
    refresh();
  });

  form.addEventListener("click", (event) => {
    const target = event.target instanceof Element ? event.target : null;
    const button = target?.closest<HTMLButtonElement>("button[data-action]");
    if (!button || !form.contains(button) || readonly) return;
    const action = button.dataset.action;
    if (action === "add-item") {
      const template = form.querySelector<HTMLTemplateElement>("template[data-item-template]");
      const body = form.querySelector<HTMLElement>("[data-item-body]");
      if (!template || !body) return;
      body.append(template.content.cloneNode(true));
      refresh();
      rowsOf(form).at(-1)?.querySelector<HTMLElement>("[data-field='ingredient']")?.focus();
    } else if (action === "remove-item") {
      button.closest("tr")?.remove();
      refresh();
    }
  });

  const run = async (work: () => Promise<string | null>): Promise<void> => {
    clearErrors(form);
    setBusy(form, true);
    try {
      deps.navigate((await work()) ?? window.location.pathname);
    } catch (error) {
      showFailure(form, error);
    }
  };

  /** Lưu nháp: tạo mới (POST kèm dòng) hoặc PATCH phần đầu nếu đổi rồi PUT dòng nếu đổi.
   *  Trả đường dẫn để chuyển tới (null = ở lại trang này). */
  const save = async (): Promise<string | null> => {
    const header = readHeader(form);
    const missing = missingHeaderFields(header, recipeId === null);
    if (missing.length > 0) {
      throw new FormProblem({
        fields: Object.fromEntries(missing.map((f) => [f, REQUIRED_MESSAGE])),
        general: null,
      });
    }
    const items = nonBlankItems(readItems(form));
    const problem = validateItems(items);
    if (problem) throw new FormProblem({ fields: { [ITEMS_ERROR_FIELD]: problem }, general: null });

    if (recipeId === null) {
      const data = await deps.send("POST", "/recipes", {
        ...headerToCreateBody(header),
        items: itemsToBody(items),
      });
      return detailUrl(data);
    }
    await sendDraftChanges(recipeId, saved, header, items, deps.send);
    return null;
  };

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    if (!readonly) void run(save);
  });

  const onClick = (name: string, work: () => Promise<string | null>): void => {
    form
      .querySelector<HTMLButtonElement>(`button[data-action="${name}"]`)
      ?.addEventListener("click", () => void run(work));
  };

  if (recipeId !== null) {
    // Kích hoạt lưu phần đang sửa trước, để bản được kích hoạt đúng là bản đang nhìn thấy.
    onClick("activate", async () => {
      if (!readonly) await save();
      await deps.send("POST", `/recipes/${recipeId}/activate`);
      return null;
    });
    onClick("retire", async () => {
      await deps.send("POST", `/recipes/${recipeId}/retire`);
      return null;
    });
    onClick("new-version", async () =>
      detailUrl(await deps.send("POST", `/recipes/${recipeId}/new-version`)),
    );
  }
}

export function bindAllRecipeForms(root: ParentNode = document): void {
  for (const form of Array.from(root.querySelectorAll<HTMLFormElement>("form[data-recipe-form]"))) {
    bindRecipeForm(form);
  }
}
