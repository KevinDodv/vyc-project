/** Hành vi phía trình duyệt riêng của form chứng nhận (phần gửi và báo lỗi do `lib/admin/form.ts` lo):
 *  - «Áp dụng cho»: chỉ hiện ô của đích đang chọn và đánh dấu nó bắt buộc, để lỗi bỏ trống hiện đúng ô
 *    đang thấy (API gắn lỗi «chọn đúng một nơi» vào `product_id`, ô có thể đang ẩn). Đổi đích thì xoá ô
 *    bên kia để khi lưu gửi `null`.
 *  - Đồi quế: chọn người bán rồi chọn đồi theo mã.
 *  - Số sao chỉ dùng cho OCOP: đổi sang loại khác thì xoá và ẩn. */

import { api } from "../../../scripts/admin/api";
import { type Plot, plotOptions, type SelectOption } from "./certificate";

export type TargetKind = "product" | "plot";

export function targetKindOf(
  radios: ReadonlyArray<{ value: string; checked: boolean }>,
): TargetKind {
  return radios.find((r) => r.checked)?.value === "plot" ? "plot" : "product";
}

function bindTargets(group: HTMLElement): void {
  const radios = Array.from(group.querySelectorAll<HTMLInputElement>('input[type="radio"]'));
  const sides = (["product", "plot"] as const).map((kind) => ({
    kind,
    box: group.querySelector<HTMLElement>(`[data-target-${kind}]`),
    control: group.querySelector<HTMLSelectElement>(`[name="${kind}_id"]`),
  }));
  const apply = (clear: boolean): void => {
    const chosen = targetKindOf(radios);
    for (const { kind, box, control } of sides) {
      const on = kind === chosen;
      if (box) box.hidden = !on;
      control?.toggleAttribute("data-required", on);
      control?.setAttribute("aria-required", String(on));
      if (!on && clear && control) control.value = "";
    }
  };
  for (const radio of radios) radio.addEventListener("change", () => apply(true));
  apply(false);
}

export type PlotLoader = (supplierId: string) => Promise<Plot[]>;

const defaultLoader: PlotLoader = (id) => api.get<Plot[]>(`/suppliers/${id}/plots`);

/** Các mục của ô «Đồi quế» sau khi chọn người bán; mục đầu luôn rỗng để chưa chọn thì bị chặn khi lưu. */
export async function plotChoices(
  supplierId: string,
  currentId: number | null,
  load: PlotLoader,
): Promise<SelectOption[]> {
  if (!supplierId) return [{ value: "", label: "— Chọn người bán trước —" }];
  try {
    const options = plotOptions(await load(supplierId), currentId);
    const head = options.length ? "— Chọn đồi —" : "Người bán này chưa có đồi đang dùng";
    return [{ value: "", label: head }, ...options];
  } catch {
    return [{ value: "", label: "Chưa tải được đồi, bạn chọn lại người bán" }];
  }
}

function fill(select: HTMLSelectElement, options: readonly SelectOption[]): void {
  select.replaceChildren(...options.map((o) => new Option(o.label, o.value)));
}

function bindPlotPicker(group: HTMLElement, load: PlotLoader = defaultLoader): void {
  const supplier = group.querySelector<HTMLSelectElement>('[name="_supplier_id"]');
  const plot = group.querySelector<HTMLSelectElement>('[name="plot_id"]');
  if (!supplier || !plot) return;
  const currentId = Number(group.dataset.currentPlot) || null;
  let latest = 0;
  supplier.addEventListener("change", async () => {
    const turn = ++latest;
    // Không khoá ô trong lúc tải: ô bị khoá sẽ rơi khỏi thân request.
    fill(plot, [{ value: "", label: "Đang tải…" }]);
    const options = await plotChoices(supplier.value, currentId, load);
    if (turn === latest) fill(plot, options);
  });
}

function bindStars(form: ParentNode): void {
  const kind = form.querySelector<HTMLSelectElement>('[name="kind"]');
  const stars = form.querySelector<HTMLSelectElement>('[name="stars"]');
  const box = form.querySelector<HTMLElement>("[data-stars]");
  if (!kind || !stars || !box) return;
  const apply = (): void => {
    const ocop = kind.value === "OCOP";
    box.hidden = !ocop;
    if (!ocop) stars.value = "";
  };
  kind.addEventListener("change", apply);
  apply();
}

export function bindCertificateForms(root: ParentNode = document): void {
  for (const group of Array.from(root.querySelectorAll<HTMLElement>("[data-cert-target]"))) {
    bindTargets(group);
    bindPlotPicker(group);
    const form = group.closest("form");
    if (form) bindStars(form);
  }
}
