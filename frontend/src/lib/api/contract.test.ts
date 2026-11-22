// Hợp đồng kiểu giữa client viết tay (scripts/admin) và OpenAPI sinh ra (v1.d.ts, public.d.ts).
// Kiểm lúc `astro check`: backend đổi tên/kiểu trường mà client không theo thì lệnh này đỏ.
import { describe, expect, it } from "vitest";
import type { ProductCreateBody, ProductResult } from "../../scripts/admin/product-form";
import type { components } from "./v1";

type V1 = components["schemas"];
// Trường có @default hiện là bắt buộc trong kiểu sinh; client để backend tự điền.
type ProductInBody = Omit<V1["ProductIn"], "requires_retention_sample" | "serial_tracked">;

// Thân tạo sản phẩm của form phải nhận được bởi ProductIn.
const createBody: ProductCreateBody = {
  sku: "TD10",
  name: "Tinh dầu quế",
  slug: "tinh-dau-que",
  goods_type_id: 2,
  size_label: "10 ml",
  unit: "chai",
  retail_price: 250000,
  short_desc: "Mô tả ngắn",
};
const asProductIn: ProductInBody = createBody;

// Mọi trường client đọc lại (id, slug, name, status) phải có trong ProductOut và bản của OWNER.
type Assert<T extends true> = T;
type ResultKeysExist = Assert<
  keyof ProductResult extends keyof V1["ProductOut"] & keyof V1["ProductOwnerOut"] ? true : false
>;

const resultKeysExist: ResultKeysExist = true;
const login: V1["LoginIn"] = { username: "owner", password: "x" };

describe("hợp đồng OpenAPI v1", () => {
  it("form tạo sản phẩm khớp ProductIn, kết quả khớp ProductOut", () => {
    expect(asProductIn.sku).toBe("TD10");
    expect(resultKeysExist).toBe(true);
    expect(login.username).toBe("owner");
  });
});
