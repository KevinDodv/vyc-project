/** Gửi form danh mục và đổ lỗi API theo trường (task #86; lỗi theo backend.md 3.2: `{code, message, details}`).
 *  Gọi API qua `scripts/admin/api.ts` nên mọi lệnh ghi tự kèm X-CSRFToken. TypeScript thuần, không framework. */

import { ApiRequestError, api } from "../../scripts/admin/api";
import { sanitizeNext } from "../../scripts/admin/next";
import type { CatalogStatus } from "./catalog";

/** Kiểu giá trị của một ô, khai bằng `data-kind` trên input (CatalogForm tự đặt). */
export type FieldKind = "text" | "int" | "decimal" | "boolean" | "password";

export type FormBody = Record<string, string | number | boolean | null>;

export const GENERIC_ERROR = "Không kết nối được máy chủ, bạn thử lại sau ít phút";
export const REQUIRED_MESSAGE = "Trường này bắt buộc";

export type FieldErrors = Record<string, string>;
export type ParsedError = { fields: FieldErrors; general: string | null };

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

/** Tách lỗi API thành lỗi theo trường và lỗi chung.
 *  - 400 `VALIDATION_ERROR`: `details.errors = [{field, message}]`, mỗi trường lấy lỗi đầu tiên.
 *  - Lỗi nghiệp vụ có `details.field` (chuỗi): gắn vào trường đó.
 *  - Còn lại (CSRF, 403, 409 không nêu trường, lỗi mạng): lỗi chung, giữ nguyên `message` của API. */
export function parseApiError(error: unknown): ParsedError {
  if (!(error instanceof ApiRequestError)) return { fields: {}, general: GENERIC_ERROR };
  const fields: FieldErrors = {};
  const list = error.details.errors;
  if (error.code === "VALIDATION_ERROR" && Array.isArray(list)) {
    const unnamed: string[] = [];
    for (const item of list) {
      if (!isRecord(item) || typeof item.message !== "string") continue;
      const field = typeof item.field === "string" ? item.field : "";
      if (!field) unnamed.push(item.message);
      else if (!(field in fields)) fields[field] = item.message;
    }
    if (Object.keys(fields).length > 0 || unnamed.length > 0) {
      return { fields, general: unnamed.length ? unnamed.join(". ") : null };
    }
  }
  const field = error.details.field;
  if (typeof field === "string" && field) {
    fields[field] = error.message;
    return { fields, general: null };
  }
  return { fields, general: error.message };
}

/** Dựng thân request từ FormData. `kinds` liệt kê MỌI trường của form (cả checkbox chưa tích).
 *  text/decimal để trống → null; int → số nguyên (không đọc được thì giữ chuỗi cho API báo lỗi);
 *  decimal giữ dạng chuỗi và đổi "," thành "." (số cân là chuỗi, frontend-seo.md 10); boolean → true/false;
 *  password để trống thì bỏ hẳn khỏi thân (sửa tài khoản mà không đổi mật khẩu). */
export function formToBody(data: FormData, kinds: Record<string, FieldKind>): FormBody {
  const body: FormBody = {};
  for (const [name, kind] of Object.entries(kinds)) {
    const raw = data.get(name);
    if (kind === "boolean") {
      body[name] = raw !== null;
      continue;
    }
    const text = typeof raw === "string" ? raw.trim() : "";
    if (kind === "password") {
      if (text && typeof raw === "string") body[name] = raw;
      continue;
    }
    if (!text) {
      body[name] = null;
      continue;
    }
    if (kind === "int") {
      body[name] = /^-?\d+$/.test(text) ? Number(text) : text;
    } else if (kind === "decimal") {
      body[name] = text.replace(",", ".");
    } else {
      body[name] = text;
    }
  }
  return body;
}

/** Tên các trường bắt buộc mà FormData đang để trống. */
export function missingRequired(data: FormData, required: readonly string[]): string[] {
  return required.filter((name) => {
    const raw = data.get(name);
    return typeof raw !== "string" || raw.trim() === "";
  });
}

type Container = { querySelectorAll(selector: string): ArrayLike<HTMLElement> };

/** Xoá mọi lỗi đang hiện trong form. */
export function clearErrors(form: Container): void {
  for (const slot of Array.from(form.querySelectorAll("[data-error-for]"))) {
    slot.textContent = "";
    slot.hidden = true;
  }
  for (const control of Array.from(form.querySelectorAll("[aria-invalid]"))) {
    control.removeAttribute("aria-invalid");
  }
  for (const box of Array.from(form.querySelectorAll("[data-form-error]"))) {
    box.textContent = "";
    box.hidden = true;
  }
}

/** Hiện lỗi ngay dưới trường (`[data-error-for="<tên>"]`). Tên kiểu `grades.0.name` thử khớp đúng tên rồi
 *  tới đoạn đầu (`grades`). Trường không có chỗ hiện thì chuyển xuống lỗi chung `[data-form-error]`,
 *  kèm tên trường để không mất thông tin. Trả về phần tử lỗi đầu tiên để focus. */
export function showErrors(
  form: Container,
  parsed: ParsedError,
  labels: Record<string, string> = {},
): HTMLElement | null {
  const slots = new Map<string, HTMLElement>();
  for (const slot of Array.from(form.querySelectorAll("[data-error-for]"))) {
    const name = slot.getAttribute("data-error-for");
    if (name) slots.set(name, slot);
  }
  const controls = Array.from(form.querySelectorAll("[name]"));
  const general: string[] = [];
  if (parsed.general) general.push(parsed.general);
  let first: HTMLElement | null = null;

  for (const [field, message] of Object.entries(parsed.fields)) {
    const head = field.split(".")[0] ?? field;
    const key = slots.has(field) ? field : slots.has(head) ? head : null;
    const slot = key === null ? undefined : slots.get(key);
    if (!slot || key === null) {
      general.push(`${labels[field] ?? labels[head] ?? field}: ${message}`);
      continue;
    }
    slot.textContent = message;
    slot.hidden = false;
    const control = controls.find((c) => c.getAttribute("name") === key);
    if (control) {
      control.setAttribute("aria-invalid", "true");
      first ??= control;
    }
  }

  const box = Array.from(form.querySelectorAll("[data-form-error]"))[0];
  if (box && general.length > 0) {
    box.textContent = general.join(". ");
    box.hidden = false;
    first ??= box;
  }
  return first;
}

export type SubmitDeps = {
  send: (method: "POST" | "PATCH", path: string, body: FormBody) => Promise<unknown>;
};

const defaultDeps: SubmitDeps = {
  send: (method, path, body) => (method === "POST" ? api.post(path, body) : api.patch(path, body)),
};

export type SubmitResult = { ok: true; data: unknown } | { ok: false; error: ParsedError };

/** Gửi một lần và gom kết quả; không ném lỗi. */
export async function submitBody(
  method: "POST" | "PATCH",
  path: string,
  body: FormBody,
  deps: SubmitDeps = defaultDeps,
): Promise<SubmitResult> {
  try {
    return { ok: true, data: await deps.send(method, path, body) };
  } catch (error) {
    return { ok: false, error: parseApiError(error) };
  }
}

/** Đích sau khi lưu: chỉ nhận đường dẫn trong /quan-ly (cùng quy tắc với `next` của trang đăng nhập). */
export function redirectTarget(raw: string | undefined): string | null {
  return sanitizeNext(raw ?? null);
}

function readKinds(form: HTMLFormElement): {
  kinds: Record<string, FieldKind>;
  required: string[];
} {
  const kinds: Record<string, FieldKind> = {};
  const required: string[] = [];
  for (const control of Array.from(form.querySelectorAll<HTMLElement>("[data-kind]"))) {
    const name = control.getAttribute("name");
    const kind = control.getAttribute("data-kind") as FieldKind | null;
    if (!name || !kind) continue;
    // Ô bị khoá (WORKSHOP, mã không đổi được) không có trong thân PATCH: để trống thì thành null và xoá mất giá trị.
    if (control.hasAttribute("disabled") || control.hasAttribute("readonly")) continue;
    kinds[name] = kind;
    if (control.hasAttribute("data-required")) required.push(name);
  }
  return { kinds, required };
}

function readLabels(form: HTMLFormElement): Record<string, string> {
  const labels: Record<string, string> = {};
  for (const control of Array.from(form.querySelectorAll<HTMLElement>("[data-label]"))) {
    const name = control.getAttribute("name");
    const label = control.getAttribute("data-label");
    if (name && label) labels[name] = label;
  }
  return labels;
}

function setBusy(form: HTMLFormElement, busy: boolean): void {
  for (const button of Array.from(
    form.querySelectorAll<HTMLButtonElement>("button[data-action]"),
  )) {
    button.disabled = busy;
  }
}

/** Gắn hành vi cho một form `[data-catalog-form]` do CatalogForm.astro render:
 *  - submit: kiểm trường bắt buộc, gửi `data-method` tới `data-api-path`, thành công thì chuyển tới `data-redirect`;
 *  - nút `[data-action="deactivate"]`: PATCH `{status}` tới `data-deactivate-path`, rồi cũng chuyển trang. */
export function bindCatalogForm(
  form: HTMLFormElement,
  deps: SubmitDeps = defaultDeps,
  navigate: (url: string) => void = (url) => window.location.assign(url),
): void {
  const apiPath = form.dataset.apiPath;
  const method = form.dataset.method === "PATCH" ? "PATCH" : "POST";
  const redirect = redirectTarget(form.dataset.redirect);
  const labels = readLabels(form);

  const finish = (result: SubmitResult): void => {
    if (result.ok) {
      navigate(redirect ?? window.location.pathname);
      return;
    }
    setBusy(form, false);
    showErrors(form, result.error, labels)?.focus();
  };

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!apiPath) return;
    clearErrors(form);
    const { kinds, required } = readKinds(form);
    const data = new FormData(form);
    const missing = missingRequired(data, required);
    if (missing.length > 0) {
      const fields: FieldErrors = {};
      for (const name of missing) fields[name] = REQUIRED_MESSAGE;
      showErrors(form, { fields, general: null }, labels)?.focus();
      return;
    }
    setBusy(form, true);
    finish(await submitBody(method, apiPath, formToBody(data, kinds), deps));
  });

  const toggle = form.querySelector<HTMLButtonElement>('button[data-action="deactivate"]');
  toggle?.addEventListener("click", async () => {
    const path = form.dataset.deactivatePath;
    const next: CatalogStatus = toggle.dataset.nextStatus === "ACTIVE" ? "ACTIVE" : "INACTIVE";
    if (!path) return;
    clearErrors(form);
    setBusy(form, true);
    finish(await submitBody("PATCH", path, { status: next }, deps));
  });
}

/** Gắn cho mọi form danh mục trong trang. */
export function bindAllCatalogForms(root: ParentNode = document): void {
  for (const form of Array.from(
    root.querySelectorAll<HTMLFormElement>("form[data-catalog-form]"),
  )) {
    bindCatalogForm(form);
  }
}
