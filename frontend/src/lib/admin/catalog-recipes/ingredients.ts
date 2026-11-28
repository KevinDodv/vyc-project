/** Trường form và cột danh sách của màn phụ liệu (task #95; TK mục 5 «Phụ liệu», BR-20, BR-21).
 *  Đơn vị cố định là gram; `density_g_ml` chỉ là tỷ trọng tham khảo khi đổi ml ↔ gram, không dùng để tính kho. */

import type { FieldDef } from "../catalog";
import { INGREDIENT_KIND_OPTIONS, type IngredientOut } from "./model";

export const UNIT_NOTE =
  "Đơn vị tính cố định là gram. Ô tỷ trọng (g/ml) chỉ để tham khảo khi đổi từ ml sang gram; sổ kho và công thức luôn tính bằng gram.";

export function checkMark(value: unknown): string {
  return value ? "✔ Có" : "";
}

/** Hiện tỷ trọng cho người Việt: dấu phẩy, bỏ số 0 thừa ("0.950" → "0,95"). */
export function densityText(value: unknown): string {
  if (typeof value !== "string" || value === "") return "";
  return value.includes(".")
    ? value.replace(/0+$/, "").replace(/\.$/, "").replace(".", ",")
    : value;
}

function baseFields(item?: IngredientOut): FieldDef[] {
  return [
    {
      name: "code",
      label: "Mã phụ liệu",
      required: true,
      mono: true,
      maxlength: 6,
      value: item?.code ?? "",
      placeholder: "TD",
      hint: "Chữ in hoa hoặc số, tối đa 6 ký tự. Đã có lô thì không đổi mã được.",
    },
    {
      name: "name",
      label: "Tên phụ liệu",
      required: true,
      maxlength: 200,
      value: item?.name ?? "",
    },
    {
      name: "kind",
      label: "Loại",
      type: "select",
      required: true,
      value: item?.kind ?? "",
      options: INGREDIENT_KIND_OPTIONS,
    },
    {
      name: "density_g_ml",
      label: "Tỷ trọng tham khảo (g/ml)",
      type: "decimal",
      value: item?.density_g_ml ?? "",
      placeholder: "0,95",
      hint: "Để trống nếu không cần. Chỉ tham khảo, không dùng để tính tồn kho.",
    },
    {
      name: "shelf_life_months",
      label: "Hạn dùng (tháng)",
      type: "int",
      min: 1,
      value: item?.shelf_life_months ?? "",
    },
    {
      name: "track_stock",
      label: "Theo dõi tồn kho",
      type: "checkbox",
      value: item?.track_stock ?? true,
      hint: "Đã có lô thì không bật lại được.",
    },
    {
      name: "requires_coa",
      label: "Cần phiếu kiểm nghiệm (COA)",
      type: "checkbox",
      value: item?.requires_coa ?? false,
    },
  ];
}

/** Mã phụ liệu luôn chữ in hoa (API chỉ nhận chữ hoa và số): đổi ngay khi gõ, giữ vị trí con trỏ. */
export function upperCaseInput(input: HTMLInputElement): void {
  const upper = input.value.toUpperCase();
  if (upper === input.value) return;
  const { selectionStart, selectionEnd } = input;
  input.value = upper;
  input.setSelectionRange(selectionStart, selectionEnd);
}

export function bindUpperCaseCode(root: ParentNode = document): void {
  const input = root.querySelector<HTMLInputElement>('[data-catalog-form] input[name="code"]');
  input?.addEventListener("input", () => upperCaseInput(input));
}

export function createFields(): FieldDef[] {
  return baseFields();
}

export function editFields(item: IngredientOut): FieldDef[] {
  return baseFields(item);
}
