/** Hành vi trình duyệt của form nguyên liệu (MaterialForm.astro, task #93): bảng con hạng, gửi POST/PATCH
 *  kèm `grades`, ngừng dùng. CatalogForm không gửi được mảng nên màn này có form riêng, dùng lại
 *  `formToBody`, `showErrors`, `parseApiError` của lib/admin/form.ts. */

import { ApiRequestError, api } from "../../../scripts/admin/api";
import { sanitizeNext } from "../../../scripts/admin/next";
import {
  clearErrors,
  type FieldErrors,
  type FieldKind,
  formToBody,
  GENERIC_ERROR,
  missingRequired,
  parseApiError,
  REQUIRED_MESSAGE,
  showErrors,
} from "../form";
import { type GradeDraft, MAX_GRADES, materialBody, nextRank, validateGrades } from "./materials";

type Send = (method: "POST" | "PATCH", path: string, body: unknown) => Promise<unknown>;

const defaultSend: Send = (method, path, body) =>
  method === "POST" ? api.post(path, body) : api.patch(path, body);

/** Đọc bảng hạng từ DOM: mỗi `tr[data-grade-row]` có ô bậc, ô tên, và (hạng đã lưu) ô tình trạng. */
export function readDrafts(root: ParentNode): GradeDraft[] {
  return Array.from(root.querySelectorAll<HTMLElement>("tr[data-grade-row]")).map((row) => {
    const idText = row.dataset.gradeId ?? "";
    const rank = row.querySelector<HTMLInputElement>("[data-grade-rank]");
    const name = row.querySelector<HTMLInputElement>("[data-grade-name]");
    const active = row.querySelector<HTMLInputElement>("[data-grade-active]");
    return {
      id: /^\d+$/.test(idText) ? Number(idText) : null,
      rank: rank?.value ?? "",
      name: name?.value ?? "",
      status: active && !active.checked ? "INACTIVE" : "ACTIVE",
    };
  });
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
    if (!name || !kind || control.hasAttribute("disabled")) continue;
    kinds[name] = kind;
    if (control.hasAttribute("data-required")) required.push(name);
  }
  return { kinds, required };
}

function readLabels(form: HTMLFormElement): Record<string, string> {
  const labels: Record<string, string> = { grades: "Hạng" };
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

function refreshAddButton(form: HTMLFormElement): void {
  const add = form.querySelector<HTMLButtonElement>('button[data-action="add-grade"]');
  const count = form.querySelectorAll("tr[data-grade-row]").length;
  if (add) add.disabled = count >= MAX_GRADES;
}

function addRow(form: HTMLFormElement): void {
  const template = form.querySelector<HTMLTemplateElement>("template[data-grade-template]");
  const body = form.querySelector<HTMLElement>("[data-grade-rows]");
  if (!template || !body) return;
  const fragment = template.content.cloneNode(true) as DocumentFragment;
  const rank = fragment.querySelector<HTMLInputElement>("[data-grade-rank]");
  if (rank) rank.value = String(nextRank(readDrafts(form)));
  body.append(fragment);
  body.querySelector<HTMLInputElement>("tr[data-grade-row]:last-child [data-grade-name]")?.focus();
  refreshAddButton(form);
}

export function bindMaterialForm(
  form: HTMLFormElement,
  send: Send = defaultSend,
  navigate: (url: string) => void = (url) => window.location.assign(url),
): void {
  const apiPath = form.dataset.apiPath;
  const method = form.dataset.method === "PATCH" ? "PATCH" : "POST";
  const redirect = sanitizeNext(form.dataset.redirect ?? null);
  const labels = readLabels(form);
  const done = () => navigate(redirect ?? window.location.pathname);

  const fail = (error: unknown) => {
    setBusy(form, false);
    const parsed =
      error instanceof ApiRequestError
        ? parseApiError(error)
        : { fields: {}, general: GENERIC_ERROR };
    showErrors(form, parsed, labels)?.focus();
  };

  form.addEventListener("click", (event) => {
    const target = event.target instanceof Element ? event.target : null;
    if (target?.closest('button[data-action="add-grade"]')) {
      event.preventDefault();
      addRow(form);
      return;
    }
    const remove = target?.closest<HTMLElement>('button[data-action="remove-grade"]');
    if (remove) {
      event.preventDefault();
      remove.closest("tr")?.remove();
      refreshAddButton(form);
    }
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!apiPath) return;
    clearErrors(form);
    const { kinds, required } = readKinds(form);
    const data = new FormData(form);
    const errors: FieldErrors = {};
    for (const name of missingRequired(data, required)) errors[name] = REQUIRED_MESSAGE;
    const drafts = readDrafts(form);
    const gradeError = validateGrades(drafts);
    if (gradeError) errors.grades = gradeError;
    if (Object.keys(errors).length > 0) {
      showErrors(form, { fields: errors, general: null }, labels)?.focus();
      return;
    }
    setBusy(form, true);
    try {
      await send(method, apiPath, materialBody(formToBody(data, kinds), drafts));
      done();
    } catch (error) {
      fail(error);
    }
  });

  form
    .querySelector<HTMLButtonElement>('button[data-action="deactivate"]')
    ?.addEventListener("click", async (event) => {
      const path = form.dataset.deactivatePath;
      const next =
        (event.currentTarget as HTMLElement).dataset.nextStatus === "ACTIVE"
          ? "ACTIVE"
          : "INACTIVE";
      if (!path) return;
      clearErrors(form);
      setBusy(form, true);
      try {
        await send("PATCH", path, { status: next });
        done();
      } catch (error) {
        fail(error);
      }
    });
  refreshAddButton(form);
}

export function bindAllMaterialForms(root: ParentNode = document): void {
  for (const form of Array.from(
    root.querySelectorAll<HTMLFormElement>("form[data-material-form]"),
  )) {
    bindMaterialForm(form);
  }
}
