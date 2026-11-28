/** Nạp dữ liệu cho các trang sản phẩm ở phía máy chủ. */

import { adminApi, callApi } from "./admin-api";
import type { Plot } from "./certificate";
import { collectPages, findPlots, PAGE_SIZE, type PlotLookup } from "./lookup";
import {
  type GoodsType,
  type ProductOwner,
  type RecipeOption,
  type RecipeSummary,
  recipeOptions,
} from "./product";

export type FormOptions =
  | { kind: "ok"; goodsTypes: GoodsType[]; recipes: RecipeOption[] }
  | { kind: "unavailable" };

/** Loại hàng nhóm PRODUCT và công thức thành phẩm đang dùng cho hai ô chọn của form. */
export async function loadFormOptions(
  request: Request,
  currentRecipeCode: string | null,
): Promise<FormOptions> {
  const api = adminApi(request);
  const [types, recipes] = await Promise.all([
    callApi<GoodsType[]>(() =>
      api.GET("/api/v1/goods-types", { params: { query: { grp: "PRODUCT" } } }),
    ),
    callApi<RecipeSummary[]>(() =>
      api.GET("/api/v1/recipes", {
        params: { query: { output_kind: "PRODUCT", status: "ACTIVE" } },
      }),
    ),
  ]);
  if (types.kind !== "ok" || recipes.kind !== "ok") return { kind: "unavailable" };
  return {
    kind: "ok",
    goodsTypes: types.data,
    recipes: recipeOptions(recipes.data, currentRecipeCode),
  };
}

export type ProductLoad =
  | { kind: "ok"; product: ProductOwner }
  | { kind: "not_found" }
  | { kind: "unavailable" };

export async function loadProduct(request: Request, id: string): Promise<ProductLoad> {
  if (!/^\d{1,9}$/.test(id)) return { kind: "not_found" };
  const api = adminApi(request);
  const out = await callApi(() =>
    api.GET("/api/v1/products/{product_id}", { params: { path: { product_id: Number(id) } } }),
  );
  if (out.kind === "not_found") return out;
  if (out.kind !== "ok") return { kind: "unavailable" };
  // Trang này chỉ OWNER vào được (middleware), nên bản trả về là ProductOwnerOut có giá bán lẻ.
  return { kind: "ok", product: out.data as ProductOwner };
}

export type ProductChoice = { id: number; sku: string; name: string };

export type ProductChoices = { kind: "ok"; products: ProductChoice[] } | { kind: "unavailable" };

/** Danh sách rút gọn mọi sản phẩm cho ô «Áp dụng cho» và cột «Áp dụng cho» của chứng nhận. */
export async function loadProductChoices(request: Request): Promise<ProductChoices> {
  const api = adminApi(request);
  const items = await collectPages(async (page) => {
    const out = await callApi(() =>
      api.GET("/api/v1/products", { params: { query: { page, page_size: PAGE_SIZE } } }),
    );
    return out.kind === "ok" ? out.data : null;
  });
  if (items === null) return { kind: "unavailable" };
  return { kind: "ok", products: items.map((p) => ({ id: p.id, sku: p.sku, name: p.name })) };
}

export type SupplierChoice = { id: number; code: string; name: string; plots_count: number };

export type SupplierChoices = { kind: "ok"; suppliers: SupplierChoice[] } | { kind: "unavailable" };

/** Mọi người bán (kể cả đã ngừng dùng, vì đồi đang gắn chứng nhận có thể thuộc về họ). */
export async function loadSupplierChoices(request: Request): Promise<SupplierChoices> {
  const api = adminApi(request);
  const items = await collectPages(async (page) => {
    const out = await callApi(() =>
      api.GET("/api/v1/suppliers", { params: { query: { page, page_size: PAGE_SIZE } } }),
    );
    return out.kind === "ok" ? out.data : null;
  });
  if (items === null) return { kind: "unavailable" };
  return {
    kind: "ok",
    suppliers: items.map(({ id, code, name, plots_count }) => ({ id, code, name, plots_count })),
  };
}

/** Tra mã và người bán của các đồi theo id (xem `findPlots`). Lỗi thì đồi đó vắng trong kết quả. */
export function loadPlots(
  request: Request,
  suppliers: readonly SupplierChoice[],
  plotIds: ReadonlyArray<number | null>,
): Promise<PlotLookup> {
  const api = adminApi(request);
  return findPlots(suppliers, plotIds, async (supplierId) => {
    const out = await callApi<Plot[]>(() =>
      api.GET("/api/v1/suppliers/{supplier_id}/plots", {
        params: { path: { supplier_id: supplierId } },
      }),
    );
    return out.kind === "ok" ? out.data : null;
  });
}
