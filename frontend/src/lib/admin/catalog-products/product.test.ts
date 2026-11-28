import { describe, expect, it } from "vitest";
import {
  buildProductBody,
  diffBody,
  type ProductInput,
  parseProductListQuery,
  productListApiQuery,
  productListUrl,
  type RecipeSummary,
  readImages,
  recipeOptions,
} from "./product";

const base: ProductInput = {
  sku: "Q100",
  name: "Tinh dầu quế 10 ml",
  goods_type_id: "2",
  size_label: "10 ml",
  unit: "chai",
  recipe_code: "",
  shelf_life_months: "",
  requires_retention_sample: false,
  retail_price: "",
  featured_rank: "",
  serial_tracked: true,
  slug: "tinh-dau-que-10-ml",
  short_desc: "",
  story_md: "",
  usage_md: "",
  seo_title: "",
  seo_description: "",
  status: "DRAFT",
  images: [],
  buy_links: [],
};

const image = {
  url: "/media/ab/12345678.webp",
  alt: "Chai tinh dầu",
  key: "ab/12345678",
  w: 800,
  h: 800,
  widths: [400, 800],
};

describe("buildProductBody", () => {
  it("tạo mới: bỏ trường để trống, không gửi null, không gửi status", () => {
    const r = buildProductBody({ ...base, retail_price: "250000", recipe_code: "Q100" }, "create");
    expect(r.ok).toBe(true);
    if (!r.ok) return;
    expect(r.body).toMatchObject({
      sku: "Q100",
      goods_type_id: 2,
      retail_price: 250000,
      recipe_code: "Q100",
      serial_tracked: true,
      images: [],
      buy_links: [],
    });
    expect(r.body).not.toHaveProperty("shelf_life_months");
    expect(r.body).not.toHaveProperty("seo_title");
    expect(r.body).not.toHaveProperty("status");
    expect(Object.values(r.body)).not.toContain(null);
  });

  it("sửa: trường nullable để trống gửi null để xoá, trường NOT NULL không bao giờ null, có status", () => {
    const r = buildProductBody({ ...base, status: "PUBLISHED" }, "edit");
    expect(r.ok).toBe(true);
    if (!r.ok) return;
    expect(r.body.shelf_life_months).toBeNull();
    expect(r.body.recipe_code).toBeNull();
    expect(r.body.seo_title).toBeNull();
    expect(r.body.status).toBe("PUBLISHED");
    for (const key of [
      "sku",
      "name",
      "slug",
      "goods_type_id",
      "size_label",
      "unit",
      "images",
      "buy_links",
      "serial_tracked",
      "requires_retention_sample",
    ]) {
      expect(r.body[key]).not.toBeNull();
      expect(r.body[key]).not.toBeUndefined();
    }
  });

  it("thiếu trường bắt buộc báo lỗi theo tên trường", () => {
    const r = buildProductBody(
      { ...base, sku: " ", name: "", goods_type_id: "", size_label: "", unit: "", slug: "" },
      "create",
    );
    expect(r.ok).toBe(false);
    if (r.ok) return;
    expect(Object.keys(r.errors).sort()).toEqual([
      "goods_type_id",
      "name",
      "size_label",
      "sku",
      "slug",
      "unit",
    ]);
  });

  it("slug và SKU sai định dạng", () => {
    const r = buildProductBody({ ...base, slug: "Tinh Dầu", sku: "-Q1" }, "create");
    expect(r.ok).toBe(false);
    if (r.ok) return;
    expect(r.errors.slug).toContain("không dấu");
    expect(r.errors.sku).toBeDefined();
  });

  it("số ngoài khoảng: hạn dùng 1–240, thứ tự nổi bật 1–999, giá không âm", () => {
    const r = buildProductBody(
      { ...base, shelf_life_months: "241", featured_rank: "0", retail_price: "-5" },
      "create",
    );
    expect(r.ok).toBe(false);
    if (r.ok) return;
    expect(r.errors.shelf_life_months).toBeDefined();
    expect(r.errors.featured_rank).toBeDefined();
    expect(r.errors.retail_price).toBeDefined();
    const ok = buildProductBody(
      { ...base, shelf_life_months: "24", featured_rank: "1", retail_price: "0" },
      "create",
    );
    expect(ok.ok).toBe(true);
  });

  it("SEO: 70 và 170 còn lưu được, 71 và 171 bị chặn ngay trên trường", () => {
    expect(
      buildProductBody(
        { ...base, seo_title: "a".repeat(70), seo_description: "b".repeat(170) },
        "create",
      ).ok,
    ).toBe(true);
    const r = buildProductBody(
      { ...base, seo_title: "a".repeat(71), seo_description: "b".repeat(171) },
      "create",
    );
    expect(r.ok).toBe(false);
    if (r.ok) return;
    expect(r.errors.seo_title).toContain("70");
    expect(r.errors.seo_description).toContain("170");
  });

  it("ảnh bắt buộc có alt: alt trống hoặc toàn khoảng trắng báo lỗi images.<n>", () => {
    const r = buildProductBody({ ...base, images: [image, { ...image, alt: "  " }] }, "edit");
    expect(r.ok).toBe(false);
    if (r.ok) return;
    expect(r.errors["images.1"]).toContain("Ảnh 2");
    expect(r.errors["images.0"]).toBeUndefined();
    const ok = buildProductBody(
      { ...base, images: [{ ...image, alt: " Chai tinh dầu " }] },
      "edit",
    );
    expect(ok.ok && (ok.body.images as { alt: string }[])[0]?.alt).toBe("Chai tinh dầu");
  });

  it("link mua: bỏ dòng trống, kiểm kênh và https", () => {
    const r = buildProductBody(
      {
        ...base,
        buy_links: [
          { channel: "shopee", url: "https://shopee.vn/x" },
          { channel: "", url: "" },
        ],
      },
      "create",
    );
    expect(r.ok && r.body.buy_links).toEqual([{ channel: "shopee", url: "https://shopee.vn/x" }]);
    const bad = buildProductBody(
      { ...base, buy_links: [{ channel: "zalo", url: "zalo.me/abc" }] },
      "create",
    );
    expect(bad.ok).toBe(false);
    if (bad.ok) return;
    expect(bad.errors["buy_links.0"]).toBeDefined();
  });
});

describe("diffBody", () => {
  it("chỉ giữ khoá đã đổi, nên không gửi lại recipe_code cũ", () => {
    const before = { name: "A", recipe_code: "Q100", images: [image] };
    const after = { name: "B", recipe_code: "Q100", images: [image] };
    expect(diffBody(before, after)).toEqual({ name: "B" });
    expect(diffBody(before, before)).toEqual({});
  });
  it("giá trị chuyển thành null vẫn được giữ", () => {
    expect(diffBody({ recipe_code: "Q100" }, { recipe_code: null })).toEqual({ recipe_code: null });
  });
});

describe("recipeOptions", () => {
  const recipe = (code: string, version: number, status: string, kind = "PRODUCT"): RecipeSummary =>
    ({
      id: version,
      code,
      version,
      name: `Công thức ${code}`,
      output_kind: kind,
      status,
    }) as RecipeSummary;
  it("mỗi mã một dòng với bản ACTIVE mới nhất, bỏ bán thành phẩm và bản không ACTIVE", () => {
    const options = recipeOptions(
      [
        recipe("TQ", 1, "ACTIVE"),
        recipe("TQ", 2, "ACTIVE"),
        recipe("Q100", 1, "ACTIVE"),
        recipe("BTP", 1, "ACTIVE", "INTERMEDIATE"),
        recipe("X", 1, "DRAFT"),
      ],
      null,
    );
    expect(options.map((o) => o.value)).toEqual(["Q100", "TQ"]);
    expect(options[1]?.label).toContain("v2");
  });
  it("mã đang gắn mà hết bản ACTIVE vẫn hiện, đánh dấu để thấy cảnh báo", () => {
    const options = recipeOptions([recipe("Q100", 1, "ACTIVE")], "OLD");
    expect(options[0]).toMatchObject({ value: "OLD", inactive: true });
    expect(options[0]?.label).toContain("không có bản ACTIVE");
  });
});

describe("danh sách", () => {
  it("đọc query, giá trị sai về mặc định", () => {
    const q = parseProductListQuery(
      new URLSearchParams("q= Q100 &status=PUBLISHED&page=3&page_size=999"),
    );
    expect(q).toEqual({ q: "Q100", status: "PUBLISHED", page: 3, pageSize: 200 });
    expect(parseProductListQuery(new URLSearchParams("status=ACTIVE&page=-1"))).toMatchObject({
      status: "",
      page: 1,
      pageSize: 50,
    });
  });
  it("URL và query API bỏ tham số mặc định", () => {
    expect(productListUrl({ q: "", status: "", page: 1, pageSize: 50 })).toBe("/quan-ly/san-pham");
    expect(productListUrl({ q: "tinh dầu", status: "DRAFT", page: 2, pageSize: 50 })).toBe(
      "/quan-ly/san-pham?q=tinh+d%E1%BA%A7u&status=DRAFT&page=2",
    );
    expect(productListApiQuery({ q: "x", status: "HIDDEN", page: 2, pageSize: 50 })).toEqual({
      page: 2,
      page_size: 50,
      q: "x",
      status: "HIDDEN",
    });
  });
});

describe("readImages", () => {
  it("bỏ phần tử thiếu trường, giữ alt rỗng để người sửa điền", () => {
    const list = readImages([image, { url: "/media/x" }, { ...image, alt: undefined }]);
    expect(list).toHaveLength(2);
    expect(list[1]?.alt).toBe("");
  });
});
