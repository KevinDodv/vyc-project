/** Form tạo địa bàn: ô «Thuộc» chỉ hiện các địa bàn đúng cấp trên của cấp đang chọn (task #93).
 *  Đây chỉ là gợi ý cho gọn; API vẫn kiểm cấp cha (AREA_PARENT_INVALID). */

import { isAreaLevel, PARENT_LEVEL } from "./areas";

/** Cấp của cha ứng với cấp đang chọn; null khi là tỉnh (không có cha) hoặc chưa chọn. */
export function wantedParentLevel(level: string): string | null {
  return isAreaLevel(level) ? PARENT_LEVEL[level] : null;
}

type OptionLike = { value: string; hidden: boolean; disabled: boolean };

/** Ẩn các lựa chọn sai cấp; trả về true nếu lựa chọn đang chọn bị ẩn (cần xoá). */
export function applyParentFilter(
  options: ArrayLike<OptionLike>,
  levels: Record<string, string>,
  level: string,
): boolean {
  const wanted = wantedParentLevel(level);
  let selectedHidden = false;
  for (const option of Array.from(options)) {
    if (option.value === "") continue;
    const hide = wanted === null || levels[option.value] !== wanted;
    option.hidden = hide;
    option.disabled = hide;
  }
  const selected = Array.from(options).find((o) => (o as unknown as HTMLOptionElement).selected);
  if (selected && selected.value !== "" && selected.hidden) selectedHidden = true;
  return selectedHidden;
}

export function bindAreaParent(root: ParentNode = document): void {
  const level = root.querySelector<HTMLSelectElement>("#f-level");
  const parent = root.querySelector<HTMLSelectElement>("#f-parent_id");
  const data = root.querySelector<HTMLScriptElement>("#area-parent-levels");
  if (!level || !parent || !data?.textContent) return;
  let levels: Record<string, string> = {};
  try {
    levels = JSON.parse(data.textContent) as Record<string, string>;
  } catch {
    return;
  }
  const apply = () => {
    if (applyParentFilter(parent.options, levels, level.value)) parent.value = "";
    if (wantedParentLevel(level.value) === null) parent.value = "";
  };
  level.addEventListener("change", apply);
  apply();
}
