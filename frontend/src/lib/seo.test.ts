import { describe, expect, it } from "vitest";
import { product } from "./fixtures";
import { safeJson } from "./safe-json";
import {
  breadcrumbJsonLd,
  buildTitle,
  clampDescription,
  offerOf,
  organizationJsonLd,
  productJsonLd,
} from "./seo";

const ORIGIN = "https://quevanyen.example";

describe("buildTitle (TK 8.2)", () => {
  it("dùng seo_title nếu có", () => {
    expect(buildTitle("Mua tinh dầu quế", "Tinh dầu quế")).toBe("Mua tinh dầu quế");
  });
  it("không thì ghép tên | thương hiệu", () => {
    expect(buildTitle(null, "Tinh dầu quế")).toBe("Tinh dầu quế | Quế Văn Yên");
    expect(buildTitle("   ", "Tinh dầu quế")).toBe("Tinh dầu quế | Quế Văn Yên");
  });
});

describe("clampDescription", () => {
  it("giữ nguyên khi ≤ 160", () => {
    expect(clampDescription("ngắn")).toBe("ngắn");
  });
  it("cắt còn ≤ 160 ký tự", () => {
    const out = clampDescription("quế ".repeat(100));
    expect(out.length).toBeLessThanOrEqual(160);
    expect(out.endsWith("…")).toBe(true);
  });
});

describe("offerOf", () => {
  it("null khi chưa có giá", () => {
    expect(offerOf(product({ retail_price: null }))).toBeNull();
  });
  it("lấy giá và tình trạng từ DTO", () => {
    expect(offerOf(product({ retail_price: 95000, availability: "out_of_stock" }))).toEqual({
      price: 95000,
      availability: "out_of_stock",
    });
  });
});

describe("productJsonLd", () => {
  const url = `${ORIGIN}/san-pham/tinh-dau-que-10ml`;
  it("Product + Offer đủ trường", () => {
    const ld = JSON.parse(JSON.stringify(productJsonLd(product(), url)));
    expect(ld["@type"]).toBe("Product");
    expect(ld.sku).toBe("TD-Q-10");
    expect(ld.image).toEqual([`${ORIGIN}/media/img/3f/3fa9abc-1440.webp`]);
    expect(ld.offers).toEqual({
      "@type": "Offer",
      price: 120000,
      priceCurrency: "VND",
      availability: "https://schema.org/InStock",
      url,
      itemCondition: "https://schema.org/NewCondition",
    });
    expect(ld.aggregateRating).toBeUndefined();
  });
  it("hết hàng thì OutOfStock", () => {
    const ld = JSON.parse(
      JSON.stringify(productJsonLd(product({ availability: "out_of_stock" }), url)),
    );
    expect(ld.offers.availability).toBe("https://schema.org/OutOfStock");
  });
  it("không có giá thì không có offers", () => {
    const ld = JSON.parse(JSON.stringify(productJsonLd(product({ retail_price: null }), url)));
    expect(ld.offers).toBeUndefined();
  });
  it("tên chứa </script> vẫn nhúng an toàn qua safeJson", () => {
    const html = safeJson(productJsonLd(product({ name: "</script><b>x" }), url));
    expect(html).not.toContain("<");
    expect(JSON.parse(html).name).toBe("</script><b>x");
  });
});

describe("breadcrumbJsonLd", () => {
  it("đánh số từ 1 và dùng URL tuyệt đối", () => {
    const ld = breadcrumbJsonLd([
      { name: "Trang chủ", path: "/" },
      { name: "Sản phẩm", path: "/san-pham" },
    ]) as { itemListElement: { position: number; item: string; name: string }[] };
    expect(ld.itemListElement.map((i) => i.position)).toEqual([1, 2]);
    expect(ld.itemListElement[1]?.item).toBe(`${ORIGIN}/san-pham`);
  });
});

describe("organizationJsonLd", () => {
  it("có tên và url tuyệt đối", () => {
    const ld = organizationJsonLd() as { "@type": string; url: string };
    expect(ld["@type"]).toBe("Organization");
    expect(ld.url).toBe(`${ORIGIN}/`);
  });
});
