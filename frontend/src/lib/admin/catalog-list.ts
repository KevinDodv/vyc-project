/** Hành vi phía trình duyệt của CatalogList.astro: bấm dòng mở form sửa, đổi bộ lọc là tìm lại. */

import { sanitizeNext } from "../../scripts/admin/next";

const INTERACTIVE = "a, button, input, select, textarea, label, summary";

/** Có nên chuyển trang khi bấm vào `target` trong một dòng: không khi bấm đúng liên kết, nút hay ô nhập. */
export function shouldOpenRow(target: Element | null): boolean {
  return target === null || target.closest(INTERACTIVE) === null;
}

export function bindCatalogList(
  root: ParentNode = document,
  navigate: (url: string) => void = (url) => window.location.assign(url),
): void {
  for (const table of Array.from(root.querySelectorAll<HTMLElement>("[data-catalog-list]"))) {
    table.addEventListener("click", (event) => {
      const target = event.target instanceof Element ? event.target : null;
      const row = target?.closest<HTMLElement>("tr[data-href]");
      if (!row || !shouldOpenRow(target)) return;
      const href = sanitizeNext(row.dataset.href ?? null);
      if (href) navigate(href);
    });
  }
  for (const select of Array.from(
    root.querySelectorAll<HTMLSelectElement>("select[data-autosubmit]"),
  )) {
    select.addEventListener("change", () => select.form?.requestSubmit());
  }
}
