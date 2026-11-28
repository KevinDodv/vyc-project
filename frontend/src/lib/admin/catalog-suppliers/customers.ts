/** Màn khách hàng (task #94): nhãn kiểu khách, cột danh sách, trường form. Chỉ OWNER vào (TK mục 2, 5). */

import type { components } from "../../api/v1";
import type { FieldDef, FieldOption } from "../catalog";

export type CustomerOut = components["schemas"]["CustomerOut"];

export type CustomerKind = "EXPORTER" | "AGENT" | "CORPORATE" | "RETAIL" | "MARKETPLACE";

export const CUSTOMER_KIND_LABEL: Record<CustomerKind, string> = {
  EXPORTER: "DN xuất khẩu",
  AGENT: "Đại lý",
  CORPORATE: "Quà tặng DN",
  RETAIL: "Khách lẻ",
  MARKETPLACE: "Sàn",
};

export const CUSTOMER_KIND_OPTIONS: FieldOption[] = (
  Object.keys(CUSTOMER_KIND_LABEL) as CustomerKind[]
).map((k) => ({ value: k, label: CUSTOMER_KIND_LABEL[k] }));

export function customerKindLabel(kind: string): string {
  return kind in CUSTOMER_KIND_LABEL ? CUSTOMER_KIND_LABEL[kind as CustomerKind] : kind;
}

export const CUSTOMERS_PATH = "/quan-ly/khach-hang";

export type CustomerRow = {
  id: number;
  status: "ACTIVE" | "INACTIVE";
  code: string;
  name: string;
  kind: string;
  phone: string;
  address: string;
};

export function toCustomerRow(c: CustomerOut): CustomerRow {
  return {
    id: c.id,
    status: c.status === "INACTIVE" ? "INACTIVE" : "ACTIVE",
    code: c.code,
    name: c.name,
    kind: customerKindLabel(c.kind),
    phone: c.phone ?? "",
    address: c.address ?? "",
  };
}

export const CUSTOMER_COLUMNS = [
  { key: "code", label: "Mã", mono: true },
  { key: "name", label: "Tên" },
  { key: "kind", label: "Kiểu" },
  { key: "phone", label: "Số điện thoại" },
  { key: "address", label: "Địa chỉ" },
  { key: "status", label: "Tình trạng" },
];

/** Trường form khách hàng. Mã KH-NNNN tự sinh nên không có ô nhập; sửa thì hiện mã ở tiêu đề. */
export function customerFields(customer?: CustomerOut): FieldDef[] {
  return [
    {
      name: "name",
      label: "Tên khách hàng",
      required: true,
      maxlength: 200,
      value: customer?.name ?? "",
    },
    {
      name: "kind",
      label: "Kiểu khách",
      type: "select",
      required: true,
      options: CUSTOMER_KIND_OPTIONS,
      value: customer?.kind ?? "",
    },
    {
      name: "phone",
      label: "Số điện thoại",
      maxlength: 30,
      value: customer?.phone ?? "",
    },
    {
      name: "address",
      label: "Địa chỉ",
      type: "textarea",
      maxlength: 500,
      value: customer?.address ?? "",
    },
  ];
}
