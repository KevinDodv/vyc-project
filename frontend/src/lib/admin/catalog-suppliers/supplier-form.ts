/** Hành vi phía trình duyệt của form người bán và bảng đồi (task #94).
 *  Phần thuần (dựng thân request, kiểm đầu vào) tách khỏi phần DOM để vitest chạy không cần trình duyệt.
 *  Gọi API qua `scripts/admin/api.ts` nên mọi lệnh ghi tự kèm X-CSRFToken. */

import { api } from "../../../scripts/admin/api";
import {
  clearErrors,
  type FieldErrors,
  type ParsedError,
  parseApiError,
  REQUIRED_MESSAGE,
  showErrors,
} from "../form";
import { PLOT_ERROR_ALIASES, remapErrors, SUPPLIER_ERROR_ALIASES } from "./errors";
import {
  buildPlotBody,
  COORDINATES_HINT,
  currentYearVn,
  type PlotFormValues,
  parseCoordinates,
} from "./plots";
import { allowedAreaLevels, normalizeStream, streamRule } from "./suppliers";

// ----------------------------------------------------------------------------- phần thuần

export type SupplierFormValues = {
  name: string;
  kind: string;
  area_id: string;
  phone: string;
  stream: string;
  public_consent: boolean;
};

export type SupplierBody = {
  name: string;
  kind: string;
  area_id: number;
  phone: string | null;
  stream?: string;
  public_consent?: boolean;
};

export type SupplierBodyResult =
  | { ok: true; body: SupplierBody }
  | { ok: false; errors: FieldErrors };

/** Dựng thân POST/PATCH người bán. OWNER gửi đủ trường; WORKSHOP (thêm nhanh) chỉ gửi tên, kiểu, thôn, SĐT,
 *  còn luồng và «cho khách thấy tên» do máy chủ tự đặt. Luồng luôn được đưa về giá trị hợp lệ với kiểu. */
export function buildSupplierBody(
  values: SupplierFormValues,
  opts: { owner: boolean; activePlots: number },
): SupplierBodyResult {
  const errors: FieldErrors = {};
  const name = values.name.trim();
  if (!name) errors.name = REQUIRED_MESSAGE;
  if (!values.kind) errors.kind = REQUIRED_MESSAGE;
  if (!/^\d+$/.test(values.area_id.trim())) errors.area_id = REQUIRED_MESSAGE;
  if (Object.keys(errors).length > 0) return { ok: false, errors };

  const body: SupplierBody = {
    name,
    kind: values.kind,
    area_id: Number(values.area_id.trim()),
    phone: values.phone.trim() || null,
  };
  if (opts.owner) {
    body.stream = normalizeStream(values.kind, opts.activePlots, values.stream);
    body.public_consent = values.public_consent;
  }
  return { ok: true, body };
}

export type Sender = (method: "POST" | "PATCH", path: string, body: unknown) => Promise<unknown>;

const defaultSender: Sender = (method, path, body) =>
  method === "POST" ? api.post(path, body) : api.patch(path, body);

export type SendResult = { ok: true; data: unknown } | { ok: false; error: ParsedError };

/** Gửi một lần, gom kết quả, không ném lỗi. Lỗi đổi tên trường theo `aliases` để khớp ô trên form. */
export async function sendJson(
  method: "POST" | "PATCH",
  path: string,
  body: unknown,
  aliases: Record<string, string>,
  send: Sender = defaultSender,
): Promise<SendResult> {
  try {
    return { ok: true, data: await send(method, path, body) };
  } catch (error) {
    return { ok: false, error: remapErrors(parseApiError(error), aliases) };
  }
}

/** «Duyệt người bán»: lưu những gì đang có trên form rồi mới duyệt, để chủ đổi luồng xong bấm Duyệt
 *  ngay không bị mất thay đổi. Lưu lỗi thì không duyệt. */
export async function saveThenApprove(
  id: number | string,
  body: SupplierBody,
  send: Sender = defaultSender,
): Promise<SendResult> {
  const saved = await sendJson("PATCH", `/suppliers/${id}`, body, SUPPLIER_ERROR_ALIASES, send);
  if (!saved.ok) return saved;
  return sendJson("POST", `/suppliers/${id}/approve`, undefined, SUPPLIER_ERROR_ALIASES, send);
}

export function supplierPath(id: number | string): string {
  return `/quan-ly/nguoi-ban/${id}`;
}

/** Id trong kết quả POST /suppliers; không có thì null. */
export function createdId(data: unknown): number | null {
  if (typeof data !== "object" || data === null) return null;
  const id = (data as { id?: unknown }).id;
  return typeof id === "number" && Number.isSafeInteger(id) ? id : null;
}

// ----------------------------------------------------------------------------- DOM

type Navigate = (url: string) => void;
const go: Navigate = (url) => window.location.assign(url);

function control<T extends HTMLElement>(form: ParentNode, name: string): T | null {
  return form.querySelector<T>(`[name="${name}"]`);
}

function text(form: ParentNode, name: string): string {
  const el = control<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>(form, name);
  return el ? el.value : "";
}

function setBusy(form: HTMLElement, busy: boolean): void {
  for (const button of Array.from(
    form.querySelectorAll<HTMLButtonElement>("button[data-action]"),
  )) {
    button.disabled = busy;
  }
}

function labelsOf(form: ParentNode): Record<string, string> {
  const labels: Record<string, string> = {};
  for (const el of Array.from(form.querySelectorAll<HTMLElement>("[data-label]"))) {
    const name = el.getAttribute("name");
    const label = el.getAttribute("data-label");
    if (name && label) labels[name] = label;
  }
  return labels;
}

/** Áp quy tắc theo kiểu: ô luồng (khoá hoặc tắt «kiểm soát») và danh sách thôn/xã được chọn. */
export function applyKindRules(form: HTMLFormElement): void {
  const kind = text(form, "kind");
  const activePlots = Number(form.dataset.activePlots ?? "0");

  const stream = control<HTMLSelectElement>(form, "stream");
  if (stream) {
    const rule = streamRule(kind, activePlots);
    const current = normalizeStream(kind, activePlots, stream.value);
    stream.replaceChildren();
    for (const option of rule.options) {
      const el = document.createElement("option");
      el.value = option.value;
      el.textContent = option.label;
      el.disabled = option.disabled;
      el.selected = option.value === current;
      stream.append(el);
    }
    stream.disabled = rule.locked;
    const hint = form.querySelector<HTMLElement>("[data-stream-hint]");
    if (hint) {
      hint.textContent = rule.hint;
      hint.hidden = rule.hint === "";
    }
  }

  const area = control<HTMLSelectElement>(form, "area_id");
  if (area) {
    const levels = new Set<string>(kind ? allowedAreaLevels(kind) : ["COMMUNE", "VILLAGE"]);
    for (const option of Array.from(area.options)) {
      const level = option.dataset.level;
      if (!level) continue;
      const allowed = levels.has(level);
      option.hidden = !allowed;
      option.disabled = !allowed;
    }
    if (area.selectedOptions[0]?.disabled) area.value = "";
  }
}

function readSupplierValues(form: HTMLFormElement): SupplierFormValues {
  const consent = control<HTMLInputElement>(form, "public_consent");
  return {
    name: text(form, "name"),
    kind: text(form, "kind"),
    area_id: text(form, "area_id"),
    phone: text(form, "phone"),
    stream: text(form, "stream"),
    public_consent: consent?.checked ?? false,
  };
}

function reportError(form: HTMLFormElement, error: ParsedError): void {
  setBusy(form, false);
  showErrors(form, error, labelsOf(form))?.focus();
}

export function bindSupplierForm(
  form: HTMLFormElement,
  send: Sender = defaultSender,
  navigate: Navigate = go,
): void {
  const creating = form.dataset.mode === "create";
  const owner = form.dataset.owner === "1";
  const id = form.dataset.supplierId ?? "";
  const activePlots = Number(form.dataset.activePlots ?? "0");

  applyKindRules(form);
  control(form, "kind")?.addEventListener("change", () => applyKindRules(form));

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearErrors(form);
    const result = buildSupplierBody(readSupplierValues(form), { owner, activePlots });
    if (!result.ok) {
      showErrors(form, { fields: result.errors, general: null }, labelsOf(form))?.focus();
      return;
    }
    setBusy(form, true);
    const sent = creating
      ? await sendJson("POST", "/suppliers", result.body, SUPPLIER_ERROR_ALIASES, send)
      : await sendJson("PATCH", `/suppliers/${id}`, result.body, SUPPLIER_ERROR_ALIASES, send);
    if (!sent.ok) return reportError(form, sent.error);
    const newId = creating ? createdId(sent.data) : Number(id);
    navigate(
      newId ? `${supplierPath(newId)}?${creating ? "moi" : "da-luu"}=1` : "/quan-ly/nguoi-ban",
    );
  });

  form
    .querySelector<HTMLButtonElement>('button[data-action="deactivate"]')
    ?.addEventListener("click", async (event) => {
      const next = (event.currentTarget as HTMLElement).dataset.nextStatus;
      clearErrors(form);
      setBusy(form, true);
      const sent = await sendJson(
        "PATCH",
        `/suppliers/${id}`,
        { status: next === "ACTIVE" ? "ACTIVE" : "INACTIVE" },
        SUPPLIER_ERROR_ALIASES,
        send,
      );
      if (!sent.ok) return reportError(form, sent.error);
      navigate(`${supplierPath(id)}?da-luu=1`);
    });

  form
    .querySelector<HTMLButtonElement>('button[data-action="approve"]')
    ?.addEventListener("click", async () => {
      clearErrors(form);
      const result = buildSupplierBody(readSupplierValues(form), { owner, activePlots });
      if (!result.ok) {
        showErrors(form, { fields: result.errors, general: null }, labelsOf(form))?.focus();
        return;
      }
      setBusy(form, true);
      const sent = await saveThenApprove(id, result.body, send);
      if (!sent.ok) return reportError(form, sent.error);
      navigate(`${supplierPath(id)}?da-duyet=1`);
    });
}

// ----------------------------------------------------------------------------- bảng đồi

function readPlotValues(form: HTMLFormElement): PlotFormValues {
  const def = control<HTMLInputElement>(form, "is_default");
  return {
    area_id: text(form, "area_id"),
    area_ha: text(form, "area_ha"),
    planted_year: text(form, "planted_year"),
    coordinates: text(form, "coordinates"),
    photo_urls: text(form, "photo_urls"),
    // Ô bị khoá (đồi đang là mặc định, hoặc đã ngừng dùng) thì không gửi.
    is_default: !def || def.disabled ? null : def.checked,
  };
}

function bindCoordinatesPreview(form: HTMLFormElement): void {
  const input = control<HTMLInputElement>(form, "coordinates");
  const preview = form.querySelector<HTMLElement>("[data-coord-preview]");
  if (!input || !preview) return;
  const update = (): void => {
    const value = input.value.trim();
    if (!value) {
      preview.textContent = COORDINATES_HINT;
      preview.classList.remove("text-success", "text-error");
      return;
    }
    const parsed = parseCoordinates(value);
    preview.textContent = parsed.ok
      ? `Vĩ độ ${parsed.lat} · Kinh độ ${parsed.lng}`
      : parsed.message;
    preview.classList.toggle("text-success", parsed.ok);
    preview.classList.toggle("text-error", !parsed.ok);
  };
  input.addEventListener("input", update);
  update();
}

export function bindPlotForm(
  form: HTMLFormElement,
  send: Sender = defaultSender,
  navigate: Navigate = go,
  now: Date = new Date(),
): void {
  const supplierId = form.dataset.supplierId ?? "";
  const plotId = form.dataset.plotId;
  bindCoordinatesPreview(form);

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearErrors(form);
    const result = buildPlotBody(readPlotValues(form), currentYearVn(now));
    if (!result.ok) {
      showErrors(form, { fields: result.errors, general: null }, labelsOf(form))?.focus();
      return;
    }
    setBusy(form, true);
    const sent = plotId
      ? await sendJson(
          "PATCH",
          `/suppliers/${supplierId}/plots/${plotId}`,
          result.body,
          PLOT_ERROR_ALIASES,
          send,
        )
      : await sendJson(
          "POST",
          `/suppliers/${supplierId}/plots`,
          result.body,
          PLOT_ERROR_ALIASES,
          send,
        );
    if (!sent.ok) return reportError(form, sent.error);
    navigate(`${supplierPath(supplierId)}?da-luu=1`);
  });
}

/** Nút trên từng dòng đồi: «Đặt làm mặc định», «Ngừng dùng», «Dùng lại». */
export function bindPlotActions(
  root: ParentNode = document,
  send: Sender = defaultSender,
  navigate: Navigate = go,
): void {
  const box = root.querySelector<HTMLElement>("[data-plots-error]");
  for (const button of Array.from(
    root.querySelectorAll<HTMLButtonElement>("button[data-plot-action]"),
  )) {
    button.addEventListener("click", async () => {
      const { supplierId, plotId, plotAction } = button.dataset;
      if (!supplierId || !plotId) return;
      const body =
        plotAction === "default"
          ? { is_default: true }
          : { status: plotAction === "reactivate" ? "ACTIVE" : "INACTIVE" };
      if (box) {
        box.textContent = "";
        box.hidden = true;
      }
      button.disabled = true;
      const sent = await sendJson(
        "PATCH",
        `/suppliers/${supplierId}/plots/${plotId}`,
        body,
        PLOT_ERROR_ALIASES,
        send,
      );
      if (sent.ok) return navigate(`${supplierPath(supplierId)}?da-luu=1`);
      button.disabled = false;
      if (box) {
        const { fields, general } = sent.error;
        box.textContent = [general, ...Object.values(fields)].filter(Boolean).join(". ");
        box.hidden = false;
      }
    });
  }
}

/** Gắn mọi thứ có trong trang người bán. */
export function bindSupplierPage(root: Document = document): void {
  for (const form of Array.from(
    root.querySelectorAll<HTMLFormElement>("form[data-supplier-form]"),
  )) {
    bindSupplierForm(form);
  }
  for (const form of Array.from(root.querySelectorAll<HTMLFormElement>("form[data-plot-form]"))) {
    bindPlotForm(form);
  }
  bindPlotActions(root);
  bindDialogs(root);
}

/** Nút mở và đóng hộp thoại `<dialog>` (form đồi quế). */
export function bindDialogs(root: Document = document): void {
  for (const button of Array.from(root.querySelectorAll<HTMLElement>("[data-open-dialog]"))) {
    button.addEventListener("click", () => {
      const dialog = root.getElementById(button.dataset.openDialog ?? "");
      if (dialog instanceof HTMLDialogElement && !dialog.open) dialog.showModal();
    });
  }
  for (const button of Array.from(root.querySelectorAll<HTMLElement>("[data-close-dialog]"))) {
    button.addEventListener("click", () => {
      const dialog = root.getElementById(button.dataset.closeDialog ?? "");
      if (dialog instanceof HTMLDialogElement) dialog.close();
    });
  }
}
