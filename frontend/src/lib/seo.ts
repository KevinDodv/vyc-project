import type { components } from "./api/public";
import { BRAND, BUSINESS } from "./business";
import type { ImageRef } from "./image";
import { absoluteUrl } from "./url";

export type PublicProductOut = components["schemas"]["PublicProductOut"];
export type Crumb = { name: string; path: string };

/** Tham số của SeoHead và SiteLayout (frontend-seo.md 6.1). */
export interface SeoProps {
  /** Đã ghép theo TK 8.2: seo_title || `${name} | ${BRAND}` */
  title: string;
  /** ≤ 160 ký tự */
  description: string;
  /** Đường dẫn canonical, không query */
  path: string;
  /** og_image của sản phẩm; trống thì truyền url ảnh đầu */
  ogImage?: string | null;
  type?: "website" | "product" | "article";
  /** /q/, 404, 500 */
  noindex?: boolean;
  /** Ảnh LCP, preload AVIF */
  preloadImage?: ImageRef;
  preloadSizes?: string;
  jsonLd?: object[];
}

const SCHEMA_AVAILABILITY = {
  in_stock: "https://schema.org/InStock",
  out_of_stock: "https://schema.org/OutOfStock",
} as const;

/** Tiêu đề trang theo TK 8.2: seo_title nếu có, không thì "<tên> | <thương hiệu>". */
export function buildTitle(seoTitle: string | null | undefined, name: string): string {
  const custom = seoTitle?.trim();
  return custom ? custom : `${name} | ${BRAND}`;
}

/** Mô tả ≤ 160 ký tự: cắt ở ranh giới từ và thêm "…" khi dài hơn. */
export function clampDescription(text: string, max = 160): string {
  const clean = text.replace(/\s+/g, " ").trim();
  if (clean.length <= max) return clean;
  const cut = clean.slice(0, max - 1);
  const lastSpace = cut.lastIndexOf(" ");
  return `${(lastSpace > max / 2 ? cut.slice(0, lastSpace) : cut).trimEnd()}…`;
}

/** null khi retail_price trống: không có Offer trong JSON-LD, không vào feed (frontend-seo.md 6.2, 7.5).
 *  Trang, JSON-LD và feed đọc giá và tình trạng qua đúng hàm này; không tính lại ở nơi khác. */
export function offerOf(
  p: Pick<PublicProductOut, "retail_price" | "availability">,
): { price: number; availability: "in_stock" | "out_of_stock" } | null {
  if (p.retail_price === null || p.retail_price === undefined) return null;
  return { price: p.retail_price, availability: p.availability };
}

/** Product + Offer. Không tự tạo AggregateRating (TK 8.2). */
export function productJsonLd(p: PublicProductOut, url: string): object {
  const offer = offerOf(p);
  const images = p.images.map((img) => absoluteUrl(img.url));
  if (images.length === 0 && p.og_image) images.push(absoluteUrl(p.og_image));
  return {
    "@context": "https://schema.org",
    "@type": "Product",
    name: p.name,
    image: images.length > 0 ? images : undefined,
    description: p.short_description ?? p.seo_description ?? undefined,
    sku: p.sku,
    brand: { "@type": "Brand", name: BRAND },
    offers: offer
      ? {
          "@type": "Offer",
          price: offer.price,
          priceCurrency: "VND",
          availability: SCHEMA_AVAILABILITY[offer.availability],
          url,
          itemCondition: "https://schema.org/NewCondition",
        }
      : undefined,
  };
}

/** BreadcrumbList dựng từ cùng mảng Crumb[] mà Breadcrumb.astro hiển thị. */
export function breadcrumbJsonLd(items: Crumb[]): object {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: items.map((item, i) => ({
      "@type": "ListItem",
      position: i + 1,
      name: item.name,
      item: absoluteUrl(item.path),
    })),
  };
}

/** Chỉ dùng ở trang chủ. Trường nào còn là chỗ giữ chỗ thì vẫn xuất; sếp điền số thật ở business.ts. */
export function organizationJsonLd(): object {
  return {
    "@context": "https://schema.org",
    "@type": "Organization",
    name: BUSINESS.name,
    url: absoluteUrl("/"),
    logo: absoluteUrl(BUSINESS.logoPath),
    address: BUSINESS.address,
    telephone: BUSINESS.phone,
    email: BUSINESS.email,
    sameAs: BUSINESS.sameAs.length > 0 ? [...BUSINESS.sameAs] : undefined,
  };
}
