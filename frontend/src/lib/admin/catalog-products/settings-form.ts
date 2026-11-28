/** Hành vi phía trình duyệt của form cài đặt (`cai-dat/index.astro`): kiểm ô, gom `label_size` lồng nhau,
 *  PATCH /api/v1/settings rồi báo «Đã lưu» ngay trên trang. */

import { api } from "../../../scripts/admin/api";
import { clearErrors, type FieldErrors, parseApiError, showErrors } from "../form";
import {
  buildSettingsBody,
  mapSettingsErrorField,
  type NumericKey,
  SETTINGS_LIMITS,
  type SettingsInput,
} from "./settings";

function read(form: HTMLFormElement): SettingsInput {
  const get = (name: string) =>
    form.querySelector<HTMLInputElement | HTMLSelectElement>(`[name="${name}"]`)?.value ?? "";
  const input = { print_format: get("print_format") } as SettingsInput;
  for (const key of Object.keys(SETTINGS_LIMITS) as NumericKey[]) input[key] = get(key);
  return input;
}

export type SettingsDeps = { save: (body: unknown) => Promise<unknown> };

const defaultDeps: SettingsDeps = { save: (body) => api.patch("/settings", body) };

export function bindSettingsForm(form: HTMLFormElement, deps: SettingsDeps = defaultDeps): void {
  const labels: Record<string, string> = {};
  for (const [key, limit] of Object.entries(SETTINGS_LIMITS)) labels[key] = limit.label;
  labels.print_format = "Khổ giấy in";
  const done = form.querySelector<HTMLElement>("[data-saved-note]");

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearErrors(form);
    if (done) done.hidden = true;
    const built = buildSettingsBody(read(form));
    if (!built.ok) {
      showErrors(form, { fields: built.errors, general: null }, labels)?.focus();
      return;
    }
    const buttons = Array.from(form.querySelectorAll<HTMLButtonElement>("button[data-action]"));
    for (const b of buttons) b.disabled = true;
    try {
      await deps.save(built.body);
      if (done) done.hidden = false;
    } catch (error) {
      const parsed = parseApiError(error);
      const fields: FieldErrors = {};
      for (const [field, message] of Object.entries(parsed.fields)) {
        fields[mapSettingsErrorField(field)] = message;
      }
      showErrors(form, { fields, general: parsed.general }, labels)?.focus();
    } finally {
      for (const b of buttons) b.disabled = false;
    }
  });
}

export function bindAllSettingsForms(root: ParentNode = document): void {
  for (const form of Array.from(
    root.querySelectorAll<HTMLFormElement>("form[data-settings-form]"),
  )) {
    bindSettingsForm(form);
  }
}
