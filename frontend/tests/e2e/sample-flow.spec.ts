// Luồng mẫu (backend.md mục 8, frontend-seo.md 8.3): OWNER đăng nhập → tạo sản phẩm → đăng →
// trang công khai /san-pham/<slug> có tên, giá, JSON-LD, canonical; đổi slug thì slug cũ trả 301.
//
// Biến môi trường (xem playwright.config.ts):
//   E2E_BASE_URL         origin của frontend, mặc định http://localhost:4321
//   E2E_SITE_URL         SITE_URL của frontend (canonical), mặc định bằng E2E_BASE_URL
//   E2E_OWNER_USERNAME   tài khoản OWNER có sẵn trong DB, mặc định e2e-owner
//   E2E_OWNER_PASSWORD   mật khẩu của tài khoản đó (bắt buộc)
//   E2E_GOODS_TYPE_ID    id loại hàng, mặc định 2 (TINH_DAU theo migration seed catalog 0002)
import { expect, test } from "@playwright/test";

const USERNAME = process.env.E2E_OWNER_USERNAME ?? "e2e-owner";
const PASSWORD = process.env.E2E_OWNER_PASSWORD ?? "";
const GOODS_TYPE_ID = process.env.E2E_GOODS_TYPE_ID ?? "2";
const SITE_URL = (
  process.env.E2E_SITE_URL ??
  process.env.E2E_BASE_URL ??
  "http://localhost:4321"
).replace(/\/$/, "");

const PRICE = 250000;
// Thanh công cụ của astro dev che đáy ảnh chụp; ẩn đi cho ảnh bằng chứng.
const HIDE_DEV_TOOLBAR = "astro-dev-toolbar { display: none !important; }";

type JsonLd = { "@type": string; [key: string]: unknown };

test("OWNER đăng nhập, tạo và đăng sản phẩm, trang công khai hiện đúng", async ({
  page,
  context,
  baseURL,
}) => {
  test.skip(!PASSWORD, "Đặt E2E_OWNER_PASSWORD (và E2E_OWNER_USERNAME) của tài khoản OWNER");

  // Mỗi lần chạy một slug/SKU riêng để chạy lại trên cùng DB không đụng nhau.
  const stamp = Date.now().toString(36);
  const slug = `e2e-tinh-dau-${stamp}`;
  const newSlug = `e2e-tinh-dau-moi-${stamp}`;
  const sku = `E2E-${stamp}`.toUpperCase();
  const name = `Tinh dầu quế E2E ${stamp}`;

  // --- Chưa đăng nhập: /quan-ly/san-pham chuyển về trang đăng nhập.
  await page.goto("/quan-ly/san-pham");
  await expect(page).toHaveURL(/\/quan-ly\/dang-nhap/);

  // --- Đăng nhập OWNER qua form.
  await page.getByLabel("Tên đăng nhập").fill(USERNAME);
  await page.getByLabel("Mật khẩu").fill(PASSWORD);
  await page.getByRole("button", { name: "Đăng nhập" }).click();
  await expect(page).not.toHaveURL(/dang-nhap/);

  // --- Tạo sản phẩm: nháp, trang công khai chưa có.
  await page.goto("/quan-ly/san-pham");
  await page.locator('input[name="sku"]').fill(sku);
  await page.locator('input[name="name"]').fill(name);
  await page.locator('input[name="slug"]').fill(slug);
  await page.locator('input[name="goods_type_id"]').fill(GOODS_TYPE_ID);
  await page.locator('input[name="size_label"]').fill("10 ml");
  await page.locator('input[name="unit"]').fill("chai");
  await page.locator('input[name="retail_price"]').fill(String(PRICE));
  await page.locator('input[name="short_desc"]').fill("Tinh dầu quế chưng cất từ vỏ quế Văn Yên.");
  await page.getByRole("button", { name: "Tạo sản phẩm" }).click();
  await expect(page.locator("#product-result-name")).toHaveText(name);
  await expect(page.locator("#product-result-status")).toHaveText("Nháp");
  expect((await context.request.get(`/san-pham/${slug}`)).status()).toBe(404);

  // --- Đăng.
  await page.getByRole("button", { name: "Đăng", exact: true }).click();
  await expect(page.locator("#product-result-status")).toHaveText("Đã đăng");
  await expect(page.locator("#product-result-href")).toHaveText(`/san-pham/${slug}`);
  await page.screenshot({
    path: "../.proteam/evidence/khung-quan-ly-san-pham.png",
    fullPage: true,
    style: HIDE_DEV_TOOLBAR,
  });

  // --- Trang công khai: tên, giá, canonical, JSON-LD.
  await page.goto(`/san-pham/${slug}`);
  await expect(page.getByRole("heading", { level: 1 })).toHaveText(name);
  await expect(page.getByText(/250\.000/).first()).toBeVisible();
  await expect(page.locator('link[rel="canonical"]')).toHaveAttribute(
    "href",
    `${SITE_URL}/san-pham/${slug}`,
  );

  const blocks = await page.locator('script[type="application/ld+json"]').allTextContents();
  const nodes = blocks.map((text) => JSON.parse(text) as JsonLd);
  const product = nodes.find((node) => node["@type"] === "Product");
  expect(product, "có JSON-LD Product").toBeTruthy();
  expect(product?.name).toBe(name);
  expect(product?.sku).toBe(sku);
  expect(product?.offers).toMatchObject({ "@type": "Offer", price: PRICE, priceCurrency: "VND" });
  expect(nodes.some((node) => node["@type"] === "BreadcrumbList")).toBe(true);
  await page.screenshot({
    path: "../.proteam/evidence/khung-san-pham-cong-khai.png",
    fullPage: true,
    style: HIDE_DEV_TOOLBAR,
  });

  // --- Đổi slug (giao diện chưa có màn sửa nên gọi API bằng chính phiên đăng nhập, có CSRF):
  // slug cũ trả 301 về slug mới, slug mới trả 200.
  const cookies = await context.cookies();
  const csrf = cookies.find((cookie) => cookie.name === "csrftoken")?.value ?? "";
  expect(csrf, "có cookie csrftoken sau đăng nhập").not.toBe("");
  const list = await context.request.get(`/api/v1/products?q=${encodeURIComponent(sku)}`);
  expect(list.ok()).toBe(true);
  const items = ((await list.json()) as { items: { id: number; slug: string }[] }).items;
  const id = items.find((item) => item.slug === slug)?.id;
  expect(id, "tìm thấy sản phẩm vừa tạo").toBeDefined();
  const renamed = await context.request.patch(`/api/v1/products/${id}`, {
    data: { slug: newSlug },
    headers: { "X-CSRFToken": csrf },
  });
  expect(renamed.status()).toBe(200);

  const old = await context.request.get(`/san-pham/${slug}`, { maxRedirects: 0 });
  expect(old.status()).toBe(301);
  expect(new URL(old.headers().location ?? "", baseURL).pathname).toBe(`/san-pham/${newSlug}`);
  expect((await context.request.get(`/san-pham/${newSlug}`)).status()).toBe(200);
});

test("Slug không tồn tại trả 404", async ({ request }) => {
  const response = await request.get("/san-pham/khong-co-san-pham-nay");
  expect(response.status()).toBe(404);
});
