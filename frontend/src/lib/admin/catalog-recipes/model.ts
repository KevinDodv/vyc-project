/** Kiểu, nhãn và hàm thuần cho màn phụ liệu và công thức (task #95; TK mục 5, BR-21, BR-26).
 *  Kiểu theo lib/api/v1.d.ts. Đơn vị phụ liệu cố định là gram (BR-21); tỷ trọng g/ml chỉ để tham khảo. */

import type { components } from "../../api/v1";
import type { AdminRole, FieldOption, StatusFilter } from "../catalog";
import { altGroupLabel } from "./math";

export type IngredientOut = components["schemas"]["IngredientOut"];
export type RecipeOut = components["schemas"]["RecipeOut"];
export type RecipeDetailOut = components["schemas"]["RecipeDetailOut"];
export type RecipeItemOut = components["schemas"]["RecipeItemOut"];

export type IngredientKind =
  | "ESSENTIAL_OIL"
  | "SOLVENT"
  | "WAX"
  | "MINERAL"
  | "BOTANICAL"
  | "BLEND"
  | "OTHER";

export const INGREDIENT_KIND_LABEL: Record<IngredientKind, string> = {
  ESSENTIAL_OIL: "Tinh dầu",
  SOLVENT: "Dung môi",
  WAX: "Sáp",
  MINERAL: "Khoáng",
  BOTANICAL: "Thực vật",
  BLEND: "Hương nền, dung dịch tẩm",
  OTHER: "Khác",
};

export const INGREDIENT_KIND_OPTIONS: FieldOption[] = (
  Object.keys(INGREDIENT_KIND_LABEL) as IngredientKind[]
).map((value) => ({ value, label: INGREDIENT_KIND_LABEL[value] }));

export function ingredientKindLabel(value: unknown): string {
  return typeof value === "string" && value in INGREDIENT_KIND_LABEL
    ? INGREDIENT_KIND_LABEL[value as IngredientKind]
    : String(value ?? "");
}

export type RecipeStatus = "DRAFT" | "ACTIVE" | "RETIRED";
export type RecipeStatusFilter = RecipeStatus | "";

export const RECIPE_STATUS_LABEL: Record<RecipeStatus, string> = {
  DRAFT: "Nháp",
  ACTIVE: "Đang dùng",
  RETIRED: "Đã ngừng",
};

export const RECIPE_STATUS_OPTIONS: ReadonlyArray<{ value: RecipeStatusFilter; label: string }> = [
  { value: "", label: "Tất cả" },
  { value: "DRAFT", label: RECIPE_STATUS_LABEL.DRAFT },
  { value: "ACTIVE", label: RECIPE_STATUS_LABEL.ACTIVE },
  { value: "RETIRED", label: RECIPE_STATUS_LABEL.RETIRED },
];

export function isRecipeStatus(value: unknown): value is RecipeStatus {
  return value === "DRAFT" || value === "ACTIVE" || value === "RETIRED";
}

export function recipeStatusLabel(value: unknown): string {
  return isRecipeStatus(value) ? RECIPE_STATUS_LABEL[value] : String(value ?? "");
}

export type OutputKind = "PRODUCT" | "INTERMEDIATE";

export const OUTPUT_KIND_LABEL: Record<OutputKind, string> = {
  PRODUCT: "Thành phẩm",
  INTERMEDIATE: "Bán thành phẩm",
};

export function outputKindLabel(value: unknown): string {
  return value === "PRODUCT" || value === "INTERMEDIATE"
    ? OUTPUT_KIND_LABEL[value]
    : String(value ?? "");
}

/** Số nhóm lựa chọn có sẵn trong ô chọn (Nhóm 1..4); nhóm cao hơn đã lưu vẫn hiện được. */
export const ALT_GROUP_CHOICES = [1, 2, 3, 4] as const;

export function altGroupOptions(current: number | null): FieldOption[] {
  const groups: number[] = [...ALT_GROUP_CHOICES];
  if (current !== null && !groups.includes(current)) groups.push(current);
  return groups.map((g) => ({ value: g, label: altGroupLabel(g) }));
}

/** Bỏ dấu và hạ chữ thường để tìm không phân biệt dấu ("quế" khớp "que"). */
export function fold(text: string): string {
  return text
    .normalize("NFD")
    .replace(/\p{M}/gu, "")
    .replaceAll("đ", "d")
    .replaceAll("Đ", "D")
    .toLocaleLowerCase("vi");
}

export function matchesQuery(q: string, ...fields: Array<string | null | undefined>): boolean {
  const needle = fold(q.trim());
  if (!needle) return true;
  return fields.some((f) => f && fold(f).includes(needle));
}

export function filterIngredients(
  items: readonly IngredientOut[],
  filter: { q?: string; status?: StatusFilter },
): IngredientOut[] {
  return items
    .filter((i) => matchesQuery(filter.q ?? "", i.code, i.name))
    .filter((i) => !filter.status || i.status === filter.status);
}

/** Danh sách công thức theo mã (A→Z) rồi phiên bản mới trước; lọc từ khoá (mã, tên) và trạng thái. */
export function filterRecipes(
  items: readonly RecipeOut[],
  filter: { q?: string; status?: RecipeStatusFilter },
): RecipeOut[] {
  return items
    .filter((r) => matchesQuery(filter.q ?? "", r.code, r.name))
    .filter((r) => !filter.status || r.status === filter.status)
    .sort((a, b) => a.code.localeCompare(b.code) || b.version - a.version);
}

export function paginate<T>(items: readonly T[], page: number, pageSize: number): T[] {
  const size = Math.max(pageSize, 1);
  const start = (Math.max(page, 1) - 1) * size;
  return items.slice(start, start + size);
}

/** Việc được làm trên một công thức. Chỉ OWNER ghi (TK mục 9); bản đã khoá thì form chỉ đọc (BR-26).
 *  Bản nháp đã có lệnh dùng: không sửa được nhưng vẫn kích hoạt được; chưa kích hoạt thì API không cho
 *  tạo phiên bản mới (RECIPE_DRAFT_EXISTS). */
export type RecipeAbilities = {
  /** Sửa được dòng và đầu trang: OWNER, bản nháp, chưa có lệnh sản xuất dùng. */
  edit: boolean;
  activate: boolean;
  retire: boolean;
  newVersion: boolean;
};

export function recipeAbilities(
  role: AdminRole | undefined,
  recipe: { status: string; editable: boolean } | null,
): RecipeAbilities {
  const owner = role === "OWNER";
  if (recipe === null) return { edit: owner, activate: false, retire: false, newVersion: false };
  const draft = recipe.status === "DRAFT";
  return {
    edit: owner && draft && recipe.editable,
    activate: owner && draft,
    retire: owner && recipe.status === "ACTIVE",
    newVersion: owner && !draft,
  };
}
