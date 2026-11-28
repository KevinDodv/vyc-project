/** Nạp dữ liệu cho các trang người bán và khách hàng. Mỗi hàm trả kết quả có kiểu để trang quyết định:
 *  chuyển về đăng nhập, báo 404, báo «chưa tải được», hay vẽ. Không có nhánh «lỗi thì vẽ danh sách rỗng». */

import { type ListQuery, listApiQuery } from "../catalog";
import type { CustomerOut } from "./customers";
import { type FetchOutcome, getJson } from "./server";
import {
  type AreaChoice,
  type AreaNode,
  findTwins,
  flattenAreas,
  type PlotOut,
  type SupplierOut,
} from "./suppliers";

export type PageOf<T> = { items: T[]; total: number; page: number; page_size: number };

export type SupplierListData =
  | { kind: "ok"; page: PageOf<SupplierOut>; waiting: number | null }
  | { kind: "unauthorized" }
  | { kind: "unavailable" };

/** Danh sách người bán kèm số người chờ duyệt (cho nhãn «Chờ duyệt (n)»). */
export async function loadSupplierList(
  request: Request,
  query: ListQuery,
  pending: boolean,
): Promise<SupplierListData> {
  const [list, waiting] = await Promise.all([
    getJson<PageOf<SupplierOut>>(request, "/suppliers", {
      ...listApiQuery(query),
      approved: pending ? "false" : undefined,
    }),
    getJson<PageOf<SupplierOut>>(request, "/suppliers", { approved: "false", page_size: 1 }),
  ]);
  if (list.kind === "unauthorized" || waiting.kind === "unauthorized") {
    return { kind: "unauthorized" };
  }
  if (list.kind !== "ok") return { kind: "unavailable" };
  return {
    kind: "ok",
    page: list.data,
    waiting: waiting.kind === "ok" ? waiting.data.total : null,
  };
}

export type AreasData =
  | { kind: "ok"; areas: AreaChoice[] }
  | { kind: "unauthorized" }
  | { kind: "unavailable" };

export async function loadAreas(request: Request): Promise<AreasData> {
  const result = await getJson<AreaNode[]>(request, "/areas");
  if (result.kind === "ok") return { kind: "ok", areas: flattenAreas(result.data) };
  return result.kind === "unauthorized" ? { kind: "unauthorized" } : { kind: "unavailable" };
}

export type SupplierDetailData =
  | {
      kind: "ok";
      supplier: SupplierOut;
      plots: PlotOut[];
      areas: AreaChoice[];
      /** Người bán trùng tên + địa bàn (chỉ cảnh báo). `null` khi chưa kiểm được. */
      twins: SupplierOut[] | null;
    }
  | { kind: "not_found" }
  | { kind: "unauthorized" }
  | { kind: "unavailable" };

function failure(results: ReadonlyArray<FetchOutcome<unknown>>): SupplierDetailData | null {
  if (results.some((r) => r.kind === "unauthorized")) return { kind: "unauthorized" };
  if (results[0]?.kind === "not_found") return { kind: "not_found" };
  if (results.some((r) => r.kind !== "ok")) return { kind: "unavailable" };
  return null;
}

export async function loadSupplierDetail(
  request: Request,
  id: number,
): Promise<SupplierDetailData> {
  const [supplier, plots, areas] = await Promise.all([
    getJson<SupplierOut>(request, `/suppliers/${id}`),
    getJson<PlotOut[]>(request, `/suppliers/${id}/plots`),
    getJson<AreaNode[]>(request, "/areas"),
  ]);
  const failed = failure([supplier, plots, areas]);
  if (failed) return failed;
  if (supplier.kind !== "ok" || plots.kind !== "ok" || areas.kind !== "ok") {
    return { kind: "unavailable" };
  }
  // Cùng địa bàn: lấy mọi người bán ở thôn này rồi so tên không dấu (API tìm theo từ khoá, không theo tên đúng).
  const sameArea = await getJson<PageOf<SupplierOut>>(request, "/suppliers", {
    area_id: supplier.data.area_id,
    page_size: 200,
  });
  return {
    kind: "ok",
    supplier: supplier.data,
    plots: plots.data,
    areas: flattenAreas(areas.data),
    twins: sameArea.kind === "ok" ? findTwins(supplier.data, sameArea.data.items) : null,
  };
}

export type CustomerListData =
  | { kind: "ok"; page: PageOf<CustomerOut> }
  | { kind: "unauthorized" }
  | { kind: "unavailable" };

export async function loadCustomerList(
  request: Request,
  query: ListQuery,
): Promise<CustomerListData> {
  const result = await getJson<PageOf<CustomerOut>>(request, "/customers", listApiQuery(query));
  if (result.kind === "ok") return { kind: "ok", page: result.data };
  return result.kind === "unauthorized" ? { kind: "unauthorized" } : { kind: "unavailable" };
}

export type CustomerDetailData =
  | { kind: "ok"; customer: CustomerOut }
  | { kind: "not_found" }
  | { kind: "unauthorized" }
  | { kind: "unavailable" };

export async function loadCustomer(request: Request, id: number): Promise<CustomerDetailData> {
  const result = await getJson<CustomerOut>(request, `/customers/${id}`);
  if (result.kind === "ok") return { kind: "ok", customer: result.data };
  return { kind: result.kind };
}
