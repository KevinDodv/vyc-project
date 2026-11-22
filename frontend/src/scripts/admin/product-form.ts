/** Luồng mẫu: POST /api/v1/products (DRAFT) rồi PATCH /api/v1/products/{id} {status: "PUBLISHED"}.
 *  Kiểu tay vì openapi/v1.json chưa có; khi có thì sinh lại bằng `pnpm gen:api` và thay bằng kiểu sinh. */
export type ProductCreateBody = {
  sku: string;
  name: string;
  slug: string;
  goods_type_id: number;
  size_label: string;
  unit: string;
  retail_price?: number;
  short_desc?: string;
};

export type ProductStatus = "DRAFT" | "PUBLISHED" | "HIDDEN";

export type ProductResult = {
  id: number;
  slug: string;
  name: string;
  status: ProductStatus;
};

export const STATUS_LABEL: Record<ProductStatus, string> = {
  DRAFT: "Nháp",
  PUBLISHED: "Đã đăng",
  HIDDEN: "Đang ẩn",
};

/** Lấy giá trị form thành thân request. Trường số để trống thì bỏ; trả chuỗi lỗi nếu nhập sai. */
export function readProductForm(data: FormData): ProductCreateBody | string {
  const text = (key: string) => String(data.get(key) ?? "").trim();
  const goodsType = Number(text("goods_type_id"));
  if (!Number.isInteger(goodsType) || goodsType < 1) return "Mã loại hàng phải là số nguyên dương";
  const body: ProductCreateBody = {
    sku: text("sku"),
    name: text("name"),
    slug: text("slug"),
    goods_type_id: goodsType,
    size_label: text("size_label"),
    unit: text("unit"),
  };
  if (!body.sku || !body.name || !body.slug || !body.size_label || !body.unit) {
    return "Điền đủ mã SKU, tên, slug, quy cách và đơn vị";
  }
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(body.slug)) {
    return "Slug chỉ gồm chữ thường không dấu, số và dấu gạch nối";
  }
  const price = text("retail_price");
  if (price) {
    const value = Number(price);
    if (!Number.isInteger(value) || value < 0) return "Giá bán lẻ phải là số nguyên không âm";
    body.retail_price = value;
  }
  const desc = text("short_desc");
  if (desc) body.short_desc = desc;
  return body;
}
