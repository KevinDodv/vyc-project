/** Phần dùng chung của màn danh mục: trạng thái, quyền sửa, query danh sách, phân trang.
 *  Khớp `core/pagination` ở backend: `?page=1&page_size=50`, tối đa 200 (backend.md 3.3). */

import type { AdminRole } from "./menu";

export type { AdminRole };

export type CatalogStatus = "ACTIVE" | "INACTIVE";
export type StatusFilter = CatalogStatus | "";

export const STATUS_LABEL: Record<CatalogStatus, string> = {
  ACTIVE: "Đang dùng",
  INACTIVE: "Ngừng dùng",
};

export const STATUS_FILTER_OPTIONS: ReadonlyArray<{ value: StatusFilter; label: string }> = [
  { value: "", label: "Tất cả" },
  { value: "ACTIVE", label: STATUS_LABEL.ACTIVE },
  { value: "INACTIVE", label: STATUS_LABEL.INACTIVE },
];

export const DEFAULT_PAGE_SIZE = 50;
export const MAX_PAGE_SIZE = 200;

/** Chỉ OWNER sửa danh mục (TK mục 5). Không rõ vai thì coi như không được sửa. */
export function canEditCatalog(role: AdminRole | undefined): boolean {
  return role === "OWNER";
}

export function isCatalogStatus(value: unknown): value is CatalogStatus {
  return value === "ACTIVE" || value === "INACTIVE";
}

export type ListQuery = { q: string; status: StatusFilter; page: number; pageSize: number };

function toPositiveInt(raw: string | null, fallback: number): number {
  if (raw === null || !/^\d+$/.test(raw)) return fallback;
  const n = Number(raw);
  return Number.isSafeInteger(n) && n >= 1 ? n : fallback;
}

/** Đọc `?q=&status=&page=&page_size=` của trang danh sách. Giá trị sai thì về mặc định, không ném lỗi. */
export function parseListQuery(params: URLSearchParams): ListQuery {
  const status = params.get("status");
  return {
    q: (params.get("q") ?? "").trim(),
    status: isCatalogStatus(status) ? status : "",
    page: toPositiveInt(params.get("page"), 1),
    pageSize: Math.min(toPositiveInt(params.get("page_size"), DEFAULT_PAGE_SIZE), MAX_PAGE_SIZE),
  };
}

function toSearch(query: Partial<ListQuery>, withPageSize: boolean): string {
  const params = new URLSearchParams();
  if (query.q) params.set("q", query.q);
  if (query.status) params.set("status", query.status);
  if (query.page && query.page > 1) params.set("page", String(query.page));
  if (withPageSize && query.pageSize && query.pageSize !== DEFAULT_PAGE_SIZE) {
    params.set("page_size", String(query.pageSize));
  }
  const text = params.toString();
  return text ? `?${text}` : "";
}

/** Đường dẫn trang danh sách có query, bỏ tham số bằng mặc định. */
export function listPageUrl(basePath: string, query: Partial<ListQuery>): string {
  return `${basePath}${toSearch(query, true)}`;
}

/** Query gọi API danh sách (cùng tên tham số với URL trang, luôn có page và page_size). */
export function listApiQuery(query: ListQuery): Record<string, string | number> {
  const out: Record<string, string | number> = { page: query.page, page_size: query.pageSize };
  if (query.q) out.q = query.q;
  if (query.status) out.status = query.status;
  return out;
}

export type PageInfo = {
  page: number;
  totalPages: number;
  /** Số thứ tự dòng đầu và cuối của trang (0 và 0 khi rỗng). */
  from: number;
  to: number;
  hasPrev: boolean;
  hasNext: boolean;
};

export function pageInfo(page: number, pageSize: number, total: number): PageInfo {
  const size = Math.max(pageSize, 1);
  const totalPages = Math.max(Math.ceil(total / size), 1);
  const current = Math.min(Math.max(page, 1), totalPages);
  const from = total === 0 ? 0 : (current - 1) * size + 1;
  const to = Math.min(current * size, total);
  return {
    page: current,
    totalPages,
    from,
    to,
    hasPrev: current > 1,
    hasNext: current < totalPages,
  };
}

/** Dãy số trang hiển thị: luôn có trang đầu, cuối và hai trang kề trang hiện tại; chỗ cách quãng là "gap". */
export function pageNumbers(page: number, totalPages: number): Array<number | "gap"> {
  const keep = new Set<number>([1, totalPages]);
  for (let p = page - 2; p <= page + 2; p++) if (p >= 1 && p <= totalPages) keep.add(p);
  const sorted = [...keep].sort((a, b) => a - b);
  const out: Array<number | "gap"> = [];
  let prev = 0;
  for (const p of sorted) {
    if (prev && p - prev > 1) out.push("gap");
    out.push(p);
    prev = p;
  }
  return out;
}

export type FieldType =
  | "text"
  | "textarea"
  | "int"
  | "decimal"
  | "select"
  | "checkbox"
  | "password";

export type FieldOption = { value: string | number; label: string };

/** Mô tả một trường của CatalogForm. `type` mặc định "text". */
export type FieldDef = {
  name: string;
  label: string;
  type?: FieldType;
  required?: boolean;
  /** Giá trị hiện tại (form sửa). checkbox: true/false. */
  value?: string | number | boolean | null;
  hint?: string;
  placeholder?: string;
  options?: FieldOption[];
  maxlength?: number;
  min?: number;
  /** Chữ in kiểu mã (đơn cách), dùng cho cột mã. */
  mono?: boolean;
  /** Trải hết hai cột của lưới form. */
  wide?: boolean;
  /** Khoá ô này kể cả với OWNER (ví dụ mã đã có lô thì không đổi). */
  readonly?: boolean;
};

/** Kiểu gửi API tương ứng với loại ô (xem `formToBody` ở form.ts). */
export function fieldKind(
  type: FieldType | undefined,
): "text" | "int" | "decimal" | "boolean" | "password" {
  switch (type) {
    case "int":
    case "decimal":
    case "password":
      return type;
    case "checkbox":
      return "boolean";
    default:
      return "text";
  }
}
