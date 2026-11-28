/** Logic thuần của màn sản phẩm /quan-ly/san-pham (TK mục 5, dòng Sản phẩm; backend.md 8):
 *  trạng thái, query danh sách, tuỳ chọn công thức, kiểm form và dựng thân POST/PATCH. */

import type { components } from "../../api/v1";
import { DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE } from "../catalog";
import type { FieldErrors } from "../form";
import { SEO_DESCRIPTION_LIMIT, SEO_TITLE_LIMIT, seoLength } from "./seo";
import { isValidSlug, SLUG_MAX } from "./slug";

type Schemas = components["schemas"];
export type ProductOwner = Schemas["ProductOwnerOut"];
export type ProductImage = Schemas["ProductImage"];
export type BuyLink = Schemas["BuyLink"];
export type ProductWarning = Schemas["ProductWarning"];
export type RecipeSummary = Schemas["RecipeOut"];
export type GoodsType = Schemas["GoodsTypeOut"];

export type ProductStatus = "DRAFT" | "PUBLISHED" | "HIDDEN";

export const PRODUCT_STATUS_LABEL: Record<ProductStatus, string> = {
  DRAFT: "Nháp",
  PUBLISHED: "Đã đăng",
  HIDDEN: "Đang ẩn",
};

export const PRODUCT_STATUS_TONE: Record<ProductStatus, string> = {
  DRAFT: "badge-neutral",
  PUBLISHED: "badge-success",
  HIDDEN: "badge-ghost",
};

export const PRODUCT_STATUS_FILTER: ReadonlyArray<{ value: ProductStatus | ""; label: string }> = [
  { value: "", label: "Tất cả" },
  { value: "DRAFT", label: PRODUCT_STATUS_LABEL.DRAFT },
  { value: "PUBLISHED", label: PRODUCT_STATUS_LABEL.PUBLISHED },
  { value: "HIDDEN", label: PRODUCT_STATUS_LABEL.HIDDEN },
];

export const BUY_CHANNELS: ReadonlyArray<{ value: BuyLink["channel"]; label: string }> = [
  { value: "shopee", label: "Shopee" },
  { value: "tiktok", label: "TikTok Shop" },
  { value: "zalo", label: "Zalo" },
  { value: "other", label: "Kênh khác" },
];

export function isProductStatus(value: unknown): value is ProductStatus {
  return value === "DRAFT" || value === "PUBLISHED" || value === "HIDDEN";
}

export const PRODUCT_LIST_PATH = "/quan-ly/san-pham";

// --- Danh sách -----------------------------------------------------------------------------------

export type ProductListQuery = {
  q: string;
  status: ProductStatus | "";
  page: number;
  pageSize: number;
};

function positiveInt(raw: string | null, fallback: number): number {
  if (raw === null || !/^\d+$/.test(raw)) return fallback;
  const n = Number(raw);
  return Number.isSafeInteger(n) && n >= 1 ? n : fallback;
}

/** `?q=&status=&page=&page_size=`; giá trị sai về mặc định. */
export function parseProductListQuery(params: URLSearchParams): ProductListQuery {
  const status = params.get("status");
  return {
    q: (params.get("q") ?? "").trim(),
    status: isProductStatus(status) ? status : "",
    page: positiveInt(params.get("page"), 1),
    pageSize: Math.min(positiveInt(params.get("page_size"), DEFAULT_PAGE_SIZE), MAX_PAGE_SIZE),
  };
}

export function productListUrl(query: Partial<ProductListQuery>): string {
  const params = new URLSearchParams();
  if (query.q) params.set("q", query.q);
  if (query.status) params.set("status", query.status);
  if (query.page && query.page > 1) params.set("page", String(query.page));
  if (query.pageSize && query.pageSize !== DEFAULT_PAGE_SIZE) {
    params.set("page_size", String(query.pageSize));
  }
  const text = params.toString();
  return text ? `${PRODUCT_LIST_PATH}?${text}` : PRODUCT_LIST_PATH;
}

export function productListApiQuery(query: ProductListQuery): Record<string, string | number> {
  const out: Record<string, string | number> = { page: query.page, page_size: query.pageSize };
  if (query.q) out.q = query.q;
  if (query.status) out.status = query.status;
  return out;
}

// --- Công thức -----------------------------------------------------------------------------------

export type RecipeOption = { value: string; label: string; inactive: boolean };

/** Tuỳ chọn «mã công thức»: mỗi mã một dòng (bản ACTIVE mới nhất), chỉ công thức ra thành phẩm.
 *  Mã đang gắn với sản phẩm mà không còn bản ACTIVE vẫn giữ trong danh sách, đánh dấu để người sửa thấy
 *  (backend chỉ nhận mã có bản ACTIVE khi đổi; giữ nguyên mã cũ thì không bị chặn). */
export function recipeOptions(
  recipes: readonly RecipeSummary[],
  currentCode: string | null,
): RecipeOption[] {
  const best = new Map<string, RecipeSummary>();
  for (const recipe of recipes) {
    if (recipe.output_kind !== "PRODUCT" || recipe.status !== "ACTIVE") continue;
    const seen = best.get(recipe.code);
    if (!seen || recipe.version > seen.version) best.set(recipe.code, recipe);
  }
  const options: RecipeOption[] = [...best.values()]
    .sort((a, b) => a.code.localeCompare(b.code))
    .map((r) => ({
      value: r.code,
      label: `${r.code} — ${r.name} (v${r.version})`,
      inactive: false,
    }));
  if (currentCode && !best.has(currentCode)) {
    options.unshift({
      value: currentCode,
      label: `${currentCode} (hiện không có bản ACTIVE)`,
      inactive: true,
    });
  }
  return options;
}

// --- Form ----------------------------------------------------------------------------------------

export type ProductImageInput = ProductImage;

/** Giá trị thô của form (chuỗi như người dùng gõ), chưa kiểm. */
export type ProductInput = {
  sku: string;
  name: string;
  goods_type_id: string;
  size_label: string;
  unit: string;
  recipe_code: string;
  shelf_life_months: string;
  requires_retention_sample: boolean;
  retail_price: string;
  featured_rank: string;
  serial_tracked: boolean;
  slug: string;
  short_desc: string;
  story_md: string;
  usage_md: string;
  seo_title: string;
  seo_description: string;
  status: string;
  images: ProductImageInput[];
  buy_links: { channel: string; url: string }[];
};

export type ProductMode = "create" | "edit";

export type BuildResult =
  | { ok: true; body: Record<string, unknown> }
  | { ok: false; errors: FieldErrors };

const SKU_PATTERN = /^[A-Za-z0-9][A-Za-z0-9_-]*$/;
const CHANNELS = new Set<string>(BUY_CHANNELS.map((c) => c.value));

function intIn(raw: string, min: number, max: number | null): number | null {
  if (!/^\d+$/.test(raw)) return null;
  const n = Number(raw);
  return Number.isSafeInteger(n) && n >= min && (max === null || n <= max) ? n : null;
}

/** Kiểm cùng luật với `ProductIn`/`ProductPatch` để báo lỗi ngay trên trường, trước khi gọi API.
 *  Lỗi trả theo tên trường của API; riêng ảnh và link mua là `images.<n>` và `buy_links.<n>`.
 *  Khi tạo: bỏ trường để trống (backend tự điền mặc định). Khi sửa: trường nullable để trống thì gửi null
 *  (xoá giá trị), trường NOT NULL không bao giờ gửi null. */
export function buildProductBody(input: ProductInput, mode: ProductMode): BuildResult {
  const errors: FieldErrors = {};
  const trim = (s: string) => s.trim();
  const text = (name: keyof ProductInput, label: string, max: number): string => {
    const value = trim(String(input[name]));
    if (!value) errors[name] = `${label} là bắt buộc`;
    else if (Array.from(value).length > max) errors[name] = `${label} tối đa ${max} ký tự`;
    return value;
  };

  const sku = text("sku", "Mã SKU", 40);
  if (sku && !SKU_PATTERN.test(sku)) {
    errors.sku = "SKU chỉ gồm chữ, số, gạch nối và gạch dưới, bắt đầu bằng chữ hoặc số";
  }
  const name = text("name", "Tên sản phẩm", 200);
  const sizeLabel = text("size_label", "Quy cách", 200);
  const unit = text("unit", "Đơn vị", 200);

  const goodsRaw = trim(input.goods_type_id);
  const goodsType = intIn(goodsRaw, 1, null);
  if (!goodsRaw) errors.goods_type_id = "Chọn loại hàng";
  else if (goodsType === null) errors.goods_type_id = "Loại hàng không hợp lệ";

  const slug = trim(input.slug);
  if (!slug) errors.slug = "Slug là bắt buộc";
  else if (!isValidSlug(slug)) {
    errors.slug = `Slug chỉ gồm chữ thường không dấu, số và dấu gạch nối, tối đa ${SLUG_MAX} ký tự`;
  }

  const optionalInt = (
    key: "shelf_life_months" | "featured_rank",
    label: string,
    min: number,
    max: number,
  ): number | null => {
    const raw = trim(input[key]);
    if (!raw) return null;
    const n = intIn(raw, min, max);
    if (n === null) errors[key] = `${label} là số nguyên từ ${min} đến ${max}`;
    return n;
  };
  const shelfLife = optionalInt("shelf_life_months", "Hạn dùng (tháng)", 1, 240);
  const featuredRank = optionalInt("featured_rank", "Thứ tự nổi bật", 1, 999);

  const priceRaw = trim(input.retail_price);
  let price: number | null = null;
  if (priceRaw) {
    price = intIn(priceRaw, 0, null);
    if (price === null) errors.retail_price = "Giá bán lẻ là số nguyên không âm (đồng)";
  }

  const maxLen = (key: keyof ProductInput, label: string, max: number): string => {
    const value = trim(String(input[key]));
    if (Array.from(value).length > max) errors[key] = `${label} tối đa ${max} ký tự`;
    return value;
  };
  const shortDesc = maxLen("short_desc", "Mô tả ngắn", 500);
  const story = maxLen("story_md", "Câu chuyện", 20000);
  const usage = maxLen("usage_md", "Cách dùng", 20000);
  const seoTitle = trim(input.seo_title);
  if (seoLength(seoTitle) > SEO_TITLE_LIMIT.hard) {
    errors.seo_title = `Tiêu đề SEO tối đa ${SEO_TITLE_LIMIT.hard} ký tự`;
  }
  const seoDescription = trim(input.seo_description);
  if (seoLength(seoDescription) > SEO_DESCRIPTION_LIMIT.hard) {
    errors.seo_description = `Mô tả SEO tối đa ${SEO_DESCRIPTION_LIMIT.hard} ký tự`;
  }

  const images: ProductImage[] = [];
  input.images.forEach((image, index) => {
    const alt = trim(image.alt);
    if (!alt) errors[`images.${index}`] = `Ảnh ${index + 1}: bắt buộc có mô tả (alt)`;
    else if (Array.from(alt).length > 200)
      errors[`images.${index}`] = `Ảnh ${index + 1}: alt tối đa 200 ký tự`;
    images.push({ ...image, alt });
  });

  const buyLinks: BuyLink[] = [];
  input.buy_links.forEach((link, index) => {
    const url = trim(link.url);
    if (!url && !link.channel) return;
    if (!CHANNELS.has(link.channel)) {
      errors[`buy_links.${index}`] = `Link mua ${index + 1}: chọn kênh bán`;
    } else if (!/^https?:\/\/\S+$/i.test(url)) {
      errors[`buy_links.${index}`] = `Link mua ${index + 1}: địa chỉ phải bắt đầu bằng https://`;
    } else {
      buyLinks.push({ channel: link.channel as BuyLink["channel"], url });
    }
  });

  if (Object.keys(errors).length > 0) return { ok: false, errors };

  const nullable = <T>(value: T | null | "", edit: boolean): T | null | undefined =>
    value === null || value === "" ? (edit ? null : undefined) : value;
  const edit = mode === "edit";
  const body: Record<string, unknown> = {
    sku,
    name,
    slug,
    goods_type_id: goodsType,
    size_label: sizeLabel,
    unit,
    requires_retention_sample: input.requires_retention_sample,
    serial_tracked: input.serial_tracked,
    images,
    buy_links: buyLinks,
    shelf_life_months: nullable(shelfLife, edit),
    featured_rank: nullable(featuredRank, edit),
    retail_price: nullable(price, edit),
    recipe_code: nullable(trim(input.recipe_code), edit),
    short_desc: nullable(shortDesc, edit),
    story_md: nullable(story, edit),
    usage_md: nullable(usage, edit),
    seo_title: nullable(seoTitle, edit),
    seo_description: nullable(seoDescription, edit),
  };
  if (edit && isProductStatus(input.status)) body.status = input.status;
  for (const key of Object.keys(body)) if (body[key] === undefined) delete body[key];
  return { ok: true, body };
}

/** Ảnh hiện có của sản phẩm, đọc từ JSON API (`images` kiểu mở). Bỏ phần tử thiếu trường bắt buộc. */
export function readImages(raw: ReadonlyArray<Record<string, unknown>>): ProductImage[] {
  const out: ProductImage[] = [];
  for (const item of raw) {
    const { url, alt, key, w, h, widths } = item;
    if (
      typeof url === "string" &&
      typeof key === "string" &&
      typeof w === "number" &&
      typeof h === "number" &&
      Array.isArray(widths) &&
      widths.every((x) => typeof x === "number")
    ) {
      out.push({
        url,
        alt: typeof alt === "string" ? alt : "",
        key,
        w,
        h,
        widths: widths as number[],
      });
    }
  }
  return out;
}

/** Link mua hiện có, bỏ phần tử sai kiểu. */
export function readBuyLinks(raw: ReadonlyArray<Record<string, unknown>>): BuyLink[] {
  const out: BuyLink[] = [];
  for (const item of raw) {
    if (
      typeof item.url === "string" &&
      typeof item.channel === "string" &&
      CHANNELS.has(item.channel)
    ) {
      out.push({ channel: item.channel as BuyLink["channel"], url: item.url });
    }
  }
  return out;
}

export function formatVnd(value: number | null | undefined): string {
  if (value === null || value === undefined) return "";
  return `${new Intl.NumberFormat("vi-VN").format(value)} đ`;
}

/** Chỉ giữ khoá đã đổi so với bản gốc (PATCH thật sự một phần). Cần thiết vì backend kiểm lại mã công thức
 *  mỗi khi `recipe_code` có trong thân: sản phẩm có công thức đã hết bản ACTIVE mà gửi lại nguyên mã cũ sẽ bị 409. */
export function diffBody(
  before: Record<string, unknown>,
  after: Record<string, unknown>,
): Record<string, unknown> {
  const out: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(after)) {
    if (JSON.stringify(value) !== JSON.stringify(before[key])) out[key] = value;
  }
  return out;
}

/** Form sửa dựng lại từ sản phẩm đang có; dùng làm bản gốc cho `diffBody`. */
export function productToInput(product: ProductOwner): ProductInput {
  const str = (v: string | number | null | undefined) =>
    v === null || v === undefined ? "" : String(v);
  return {
    sku: product.sku,
    name: product.name,
    goods_type_id: String(product.goods_type_id),
    size_label: product.size_label,
    unit: product.unit,
    recipe_code: str(product.recipe_code),
    shelf_life_months: str(product.shelf_life_months),
    requires_retention_sample: product.requires_retention_sample,
    retail_price: str(product.retail_price),
    featured_rank: str(product.featured_rank),
    serial_tracked: product.serial_tracked,
    slug: product.slug,
    short_desc: str(product.short_desc),
    story_md: str(product.story_md),
    usage_md: str(product.usage_md),
    seo_title: str(product.seo_title),
    seo_description: str(product.seo_description),
    status: product.status,
    images: readImages(product.images),
    buy_links: readBuyLinks(product.buy_links),
  };
}
