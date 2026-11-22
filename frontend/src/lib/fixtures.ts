import type { PublicProductOut } from "./seo";

/** Dữ liệu giả cho test. */
export function product(over: Partial<PublicProductOut> = {}): PublicProductOut {
  return {
    slug: "tinh-dau-que-10ml",
    sku: "TD-Q-10",
    name: "Tinh dầu quế 10 ml",
    spec: "10 ml",
    unit: "chai",
    retail_price: 120000,
    availability: "in_stock",
    short_description: "Tinh dầu quế nguyên chất.",
    story_html: null,
    usage_html: null,
    images: [
      {
        url: "/media/img/3f/3fa9abc-1440.webp",
        alt: "Tinh dầu quế 10 ml",
        key: "3f/3fa9abc",
        w: 1440,
        h: 1080,
        widths: [480, 960, 1440],
      },
    ],
    og_image: "/media/img/3f/3fa9abc-og.jpg",
    buy_links: [],
    seo_title: null,
    seo_description: null,
    updated_at: "2026-11-20T03:00:00Z",
    origin: null,
    ...over,
  };
}
