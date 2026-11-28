/** Hành vi phía trình duyệt của form sản phẩm (`_ProductForm.astro`): chuyển tab, bộ đếm SEO, slug tự sinh,
 *  danh sách ảnh (alt bắt buộc, xem product-images.ts) và link mua, rồi gửi POST/PATCH
 *  /api/v1/products. TypeScript thuần. */

import { api } from "../../../scripts/admin/api";
import { clearErrors, GENERIC_ERROR, parseApiError, showErrors } from "../form";
import { buildProductBody, diffBody, type ProductInput, type ProductMode } from "./product";
import { bindProductImages, readImageRows } from "./product-images";
import { SEO_DESCRIPTION_LIMIT, SEO_TITLE_LIMIT, type SeoLimit, seoCount } from "./seo";
import { slugify } from "./slug";

const COUNTERS: Record<string, SeoLimit> = {
  seo_title: SEO_TITLE_LIMIT,
  seo_description: SEO_DESCRIPTION_LIMIT,
};

const LEVEL_CLASS: Record<string, string> = {
  ok: "text-base-content/70",
  warn: "text-warning",
  over: "text-error",
};

function control(form: HTMLFormElement, name: string): HTMLInputElement | null {
  return form.querySelector<HTMLInputElement>(`[name="${name}"]`);
}

function value(form: HTMLFormElement, name: string): string {
  return control(form, name)?.value ?? "";
}

function checked(form: HTMLFormElement, name: string): boolean {
  return control(form, name)?.checked ?? false;
}

/** Đọc form thành giá trị thô. */
export function readProductInput(form: HTMLFormElement): ProductInput {
  const links = Array.from(form.querySelectorAll<HTMLElement>("[data-buylink-row]")).map((row) => ({
    channel: row.querySelector<HTMLSelectElement>("select")?.value ?? "",
    url: row.querySelector<HTMLInputElement>("input")?.value ?? "",
  }));
  return {
    sku: value(form, "sku"),
    name: value(form, "name"),
    goods_type_id: value(form, "goods_type_id"),
    size_label: value(form, "size_label"),
    unit: value(form, "unit"),
    recipe_code: value(form, "recipe_code"),
    shelf_life_months: value(form, "shelf_life_months"),
    requires_retention_sample: checked(form, "requires_retention_sample"),
    retail_price: value(form, "retail_price"),
    featured_rank: value(form, "featured_rank"),
    serial_tracked: checked(form, "serial_tracked"),
    slug: value(form, "slug"),
    short_desc: value(form, "short_desc"),
    story_md: value(form, "story_md"),
    usage_md: value(form, "usage_md"),
    seo_title: value(form, "seo_title"),
    seo_description: value(form, "seo_description"),
    status: value(form, "status"),
    images: readImageRows(form),
    buy_links: links,
  };
}

function selectTab(form: HTMLFormElement, name: string): void {
  for (const tab of Array.from(form.querySelectorAll<HTMLElement>("[data-tab]"))) {
    const on = tab.dataset.tab === name;
    tab.setAttribute("aria-selected", String(on));
    tab.tabIndex = on ? 0 : -1;
    tab.classList.toggle("btn-primary", on);
    tab.classList.toggle("btn-ghost", !on);
  }
  for (const panel of Array.from(form.querySelectorAll<HTMLElement>("[data-panel]"))) {
    panel.hidden = panel.dataset.panel !== name;
  }
}

/** Vị trí tab nhận focus khi bấm phím ở tab thứ `index`; phím không dùng cho tab thì null. */
function tabIndexAfterKey(key: string, index: number, count: number): number | null {
  if (key === "ArrowRight") return (index + 1) % count;
  if (key === "ArrowLeft") return (index - 1 + count) % count;
  if (key === "Home") return 0;
  if (key === "End") return count - 1;
  return null;
}

/** Bấm chuột hoặc dùng phím mũi tên: tab không được chọn có tabIndex -1 nên bàn phím chỉ tới được bằng mũi tên. */
function bindTabs(form: HTMLFormElement): void {
  const tabs = Array.from(form.querySelectorAll<HTMLElement>("[data-tab]"));
  tabs.forEach((tab, index) => {
    tab.addEventListener("click", () => selectTab(form, tab.dataset.tab ?? "general"));
    tab.addEventListener("keydown", (event) => {
      const next = tabIndexAfterKey(event.key, index, tabs.length);
      const target = next === null ? undefined : tabs[next];
      if (!target) return;
      event.preventDefault();
      selectTab(form, target.dataset.tab ?? "general");
      target.focus();
    });
  });
}

function updateCounters(form: HTMLFormElement): void {
  for (const [name, limit] of Object.entries(COUNTERS)) {
    const field = control(form, name);
    const out = form.querySelector<HTMLElement>(`[data-seo-counter="${name}"]`);
    if (!field || !out) continue;
    const result = seoCount(field.value, limit);
    out.textContent = result.message ? `${result.label}. ${result.message}` : result.label;
    out.className = `text-sm ${LEVEL_CLASS[result.level]}`;
    out.dataset.level = result.level;
  }
}

function bindRemovals(form: HTMLFormElement): void {
  form.addEventListener("click", (event) => {
    const target = event.target instanceof Element ? event.target : null;
    const button = target?.closest<HTMLElement>("[data-remove-row]");
    if (button) button.closest("[data-buylink-row]")?.remove();
  });
}

function bindBuyLinks(form: HTMLFormElement): void {
  const list = form.querySelector<HTMLElement>("[data-buylinks]");
  const template = form.querySelector<HTMLTemplateElement>("template[data-buylink-template]");
  const add = form.querySelector<HTMLElement>("[data-add-buylink]");
  add?.addEventListener("click", () => {
    if (!list || !template) return;
    const row = template.content.cloneNode(true) as DocumentFragment;
    list.append(row);
    list.querySelector<HTMLInputElement>("[data-buylink-row]:last-child input")?.focus();
  });
}

export type ProductFormDeps = {
  send: (mode: ProductMode, path: string, body: Record<string, unknown>) => Promise<{ id: number }>;
};

const defaultDeps: ProductFormDeps = {
  send: (mode, path, body) =>
    mode === "edit" ? api.patch<{ id: number }>(path, body) : api.post<{ id: number }>(path, body),
};

function setBusy(form: HTMLFormElement, busy: boolean): void {
  for (const button of Array.from(
    form.querySelectorAll<HTMLButtonElement>("button[data-action]"),
  )) {
    button.disabled = busy;
  }
}

/** Đánh dấu tab nào đang có lỗi để người dùng không bỏ sót lỗi ở tab đang ẩn. */
function markTabErrors(form: HTMLFormElement): string | null {
  let firstTab: string | null = null;
  for (const tab of Array.from(form.querySelectorAll<HTMLElement>("[data-tab]"))) {
    const panel = form.querySelector<HTMLElement>(`[data-panel="${tab.dataset.tab}"]`);
    const bad = panel?.querySelector('[aria-invalid="true"], [data-error-for]:not([hidden])');
    tab.querySelector<HTMLElement>("[data-tab-flag]")?.toggleAttribute("hidden", !bad);
    if (bad && firstTab === null) firstTab = tab.dataset.tab ?? null;
  }
  return firstTab;
}

export function bindProductForm(
  form: HTMLFormElement,
  deps: ProductFormDeps = defaultDeps,
  navigate: (url: string) => void = (url) => window.location.assign(url),
): void {
  const mode: ProductMode = form.dataset.mode === "edit" ? "edit" : "create";
  const id = form.dataset.id ?? "";
  let initialBody: Record<string, unknown> | null = null;
  if (mode === "edit" && form.dataset.initial) {
    try {
      const built = buildProductBody(JSON.parse(form.dataset.initial) as ProductInput, "edit");
      if (built.ok) initialBody = built.body;
    } catch {
      initialBody = null;
    }
  }

  const labels: Record<string, string> = {
    images: "Ảnh",
    buy_links: "Link mua",
  };
  for (const el of Array.from(form.querySelectorAll<HTMLElement>("[data-label][name]"))) {
    const name = el.getAttribute("name");
    if (name) labels[name] = el.dataset.label ?? name;
  }

  bindTabs(form);
  selectTab(form, "general");

  // Slug: tạo mới thì theo tên cho tới khi người dùng tự sửa; sửa sản phẩm thì không tự đổi (đổi slug
  // làm đường dẫn cũ chuyển 301), chỉ đổi khi bấm «Sinh lại từ tên».
  const nameField = control(form, "name");
  const slugField = control(form, "slug");
  let slugTouched = mode === "edit" || (slugField?.value ?? "") !== "";
  slugField?.addEventListener("input", () => {
    slugTouched = true;
  });
  nameField?.addEventListener("input", () => {
    if (!slugTouched && slugField) slugField.value = slugify(nameField.value);
  });
  form.querySelector("[data-slug-regen]")?.addEventListener("click", () => {
    if (slugField && nameField) slugField.value = slugify(nameField.value);
    slugTouched = true;
  });

  for (const name of Object.keys(COUNTERS)) {
    control(form, name)?.addEventListener("input", () => updateCounters(form));
  }
  updateCounters(form);
  bindRemovals(form);
  bindBuyLinks(form);
  bindProductImages(form);

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearErrors(form);
    markTabErrors(form);
    const built = buildProductBody(readProductInput(form), mode);
    if (!built.ok) {
      const first = showErrors(form, { fields: built.errors, general: null }, labels);
      const tab = markTabErrors(form);
      if (tab) selectTab(form, tab);
      first?.focus();
      return;
    }
    const body = mode === "edit" && initialBody ? diffBody(initialBody, built.body) : built.body;
    if (mode === "edit" && Object.keys(body).length === 0) {
      showErrors(form, { fields: {}, general: "Chưa có thay đổi nào để lưu" }, labels);
      return;
    }
    setBusy(form, true);
    try {
      const saved = await deps.send(mode, mode === "edit" ? `/products/${id}` : "/products", body);
      navigate(`/quan-ly/san-pham/${saved.id}?saved=1`);
    } catch (error) {
      setBusy(form, false);
      const parsed = parseApiError(error);
      const first = showErrors(form, parsed, labels);
      const tab = markTabErrors(form);
      if (tab) selectTab(form, tab);
      first?.focus();
      if (!first && !parsed.general)
        showErrors(form, { fields: {}, general: GENERIC_ERROR }, labels);
    }
  });
}

export function bindAllProductForms(root: ParentNode = document): void {
  for (const form of Array.from(
    root.querySelectorAll<HTMLFormElement>("form[data-product-form]"),
  )) {
    bindProductForm(form);
  }
}
