/** Màn loại hàng hóa (task #93). Kiểu theo lib/api/v1.d.ts; API trả mảng thường, lọc từ khoá làm ở trang. */

import type { components } from "../../api/v1";
import type { FieldDef, FieldOption, StatusFilter } from "../catalog";
import { matchesQuery } from "./text";

export type GoodsTypeOut = components["schemas"]["GoodsTypeOut"];

export type GoodsGroup = "MATERIAL" | "PRODUCT";

export const GROUP_LABEL: Record<GoodsGroup, string> = {
  MATERIAL: "Nguyên liệu",
  PRODUCT: "Thành phẩm",
};

export const GROUP_OPTIONS: FieldOption[] = (Object.keys(GROUP_LABEL) as GoodsGroup[]).map((v) => ({
  value: v,
  label: GROUP_LABEL[v],
}));

export function groupLabel(value: unknown): string {
  return value === "MATERIAL" || value === "PRODUCT" ? GROUP_LABEL[value] : String(value ?? "");
}

export function yesNo(value: unknown): string {
  return value ? "✔ Có" : "";
}

export type GoodsTypeRow = {
  id: number;
  code: string;
  name: string;
  grp: string;
  is_food: boolean;
  status: "ACTIVE" | "INACTIVE";
};

export function toRow(item: GoodsTypeOut): GoodsTypeRow {
  return {
    id: item.id,
    code: item.code,
    name: item.name,
    grp: item.grp,
    is_food: item.is_food,
    status: item.status === "INACTIVE" ? "INACTIVE" : "ACTIVE",
  };
}

/** Lọc theo từ khoá (mã hoặc tên, không dấu) và tình trạng. API đã sắp theo nhóm rồi tên. */
export function filterGoodsTypes(
  items: readonly GoodsTypeOut[],
  filter: { q?: string; status?: StatusFilter },
): GoodsTypeRow[] {
  return items
    .filter((i) => matchesQuery(filter.q ?? "", i.code, i.name))
    .filter((i) => !filter.status || i.status === filter.status)
    .map(toRow);
}

export function createFields(): FieldDef[] {
  return [
    {
      name: "code",
      label: "Mã",
      required: true,
      mono: true,
      maxlength: 40,
      hint: "Chữ, số, gạch nối; không đổi được sau khi tạo",
    },
    { name: "name", label: "Tên", required: true, maxlength: 200 },
    { name: "grp", label: "Nhóm", type: "select", required: true, options: GROUP_OPTIONS },
    { name: "is_food", label: "Là thực phẩm", type: "checkbox", value: false },
  ];
}

export function editFields(item: GoodsTypeOut): FieldDef[] {
  return [
    { name: "code", label: "Mã", value: item.code, mono: true, readonly: true },
    { name: "name", label: "Tên", value: item.name, required: true, maxlength: 200 },
    {
      name: "grp",
      label: "Nhóm",
      type: "select",
      value: item.grp,
      required: true,
      options: GROUP_OPTIONS,
      hint: "Không đổi nhóm được khi đã có sản phẩm hoặc nguyên liệu dùng loại hàng này",
    },
    { name: "is_food", label: "Là thực phẩm", type: "checkbox", value: item.is_food },
  ];
}
