// Màn sản phẩm (form đầy đủ + tab Website), chứng nhận, tài khoản, cài đặt (task #96).
// Chạy trên stack đã dựng sẵn:
//   cd frontend && E2E_OWNER_PASSWORD=... npx playwright test -c e2e/playwright.config.ts catalog-products
//
// Biến môi trường (xem tests/e2e/sample-flow.spec.ts):
//   E2E_BASE_URL, E2E_OWNER_USERNAME (mặc định e2e-owner), E2E_OWNER_PASSWORD
//   E2E_SHOTS=1: chụp ảnh vào ../.proteam/evidence/f4-*.png
// Mỗi lần chạy dùng mã/tên riêng theo `stamp` nên chạy lại trên cùng DB không đụng nhau.
import { type APIResponse, expect, type Page, test } from "@playwright/test";

const USERNAME = process.env.E2E_OWNER_USERNAME ?? "e2e-owner";
const PASSWORD = process.env.E2E_OWNER_PASSWORD ?? "";
const SHOTS = process.env.E2E_SHOTS === "1";
const HIDE_DEV_TOOLBAR = "astro-dev-toolbar { display: none !important; }";

const stamp = Date.now().toString(36);

/** Mở một trang quản lý; bị chuyển về đăng nhập thì đăng nhập rồi mở lại. */
async function open(page: Page, path: string): Promise<void> {
  await page.goto(path);
  if (/dang-nhap/.test(page.url())) {
    await page.getByLabel("Tên đăng nhập").fill(USERNAME);
    await page.getByLabel("Mật khẩu").fill(PASSWORD);
    await page.getByRole("button", { name: "Đăng nhập" }).click();
    await expect(page).not.toHaveURL(/dang-nhap/);
    await page.goto(path);
  }
}

async function shot(page: Page, name: string): Promise<void> {
  if (!SHOTS) return;
  await page.screenshot({
    path: `../.proteam/evidence/f4-${name}.png`,
    fullPage: true,
    style: HIDE_DEV_TOOLBAR,
  });
}

/** Gọi API bằng chính phiên đăng nhập của trang (kèm CSRF) để dựng dữ liệu mà giao diện chưa tạo được. */
async function call(
  page: Page,
  method: "GET" | "POST" | "PATCH",
  path: string,
  data?: unknown,
): Promise<APIResponse> {
  const cookies = await page.context().cookies();
  const csrf = cookies.find((cookie) => cookie.name === "csrftoken")?.value ?? "";
  return page.context().request.fetch(`/api/v1${path}`, {
    method,
    data,
    headers: { "X-CSRFToken": csrf },
  });
}

async function created<T>(response: APIResponse): Promise<T> {
  expect(response.ok(), `${response.url()} → ${await response.text()}`).toBe(true);
  return (await response.json()) as T;
}

const save = (page: Page) => page.getByRole("button", { name: "Lưu", exact: true }).click();

type AreaNode = { id: number; level: string; status: string; children: AreaNode[] };

function firstCommune(nodes: AreaNode[]): AreaNode | undefined {
  for (const node of nodes) {
    if (node.level === "COMMUNE" && node.status === "ACTIVE") return node;
    const found = firstCommune(node.children);
    if (found) return found;
  }
  return undefined;
}

test.describe.configure({ mode: "serial" });
test.beforeEach(() => {
  test.skip(!PASSWORD, "Đặt E2E_OWNER_PASSWORD (và E2E_OWNER_USERNAME) của tài khoản OWNER");
});

test("Sản phẩm: tạo đủ trường, slug tự sinh và sửa được, bộ đếm SEO chặn quá giới hạn cứng", async ({
  page,
}) => {
  const sku = `F4-${stamp}`.toUpperCase();
  const name = `Tinh dầu quế Đặc biệt ${stamp}`;
  const slug = page.locator("#f-slug");

  await open(page, "/quan-ly/san-pham");
  await page.getByRole("link", { name: "+ Thêm sản phẩm" }).click();
  await expect(page).toHaveURL(/\/quan-ly\/san-pham\/moi$/);

  await page.locator("#f-sku").fill(sku);
  await page.locator("#f-name").fill(name);
  await page.locator("#f-goods_type_id").selectOption({ index: 1 });
  await page.locator("#f-size_label").fill("10 ml");
  await page.locator("#f-unit").fill("chai");
  await page.locator("#f-shelf_life_months").fill("24");
  await page.locator("#f-requires_retention_sample").check();
  // Ô chọn công thức chỉ có công thức thành phẩm đang dùng (mục đầu là «Không nối công thức»).
  const recipes = page.locator("#f-recipe_code option");
  if ((await recipes.count()) > 1) await page.locator("#f-recipe_code").selectOption({ index: 1 });
  await shot(page, "san-pham-moi-thong-tin");

  // Bàn phím: mũi tên phải từ tab «Thông tin» mở tab «Website».
  await page.getByRole("tab", { name: "Thông tin" }).press("ArrowRight");
  await expect(page.getByRole("tab", { name: "Website" })).toBeFocused();
  await expect(slug).toBeVisible();
  await expect(slug).toHaveValue(`tinh-dau-que-dac-biet-${stamp}`);
  // Sửa tay rồi đổi tên: slug giữ nguyên bản sửa tay.
  await slug.fill(`f4-tu-sua-${stamp}`);
  await page.getByRole("tab", { name: "Thông tin" }).click();
  await page.locator("#f-name").fill(`${name} mới`);
  await page.getByRole("tab", { name: "Website" }).click();
  await expect(slug).toHaveValue(`f4-tu-sua-${stamp}`);

  const titleCount = page.locator('[data-seo-counter="seo_title"]');
  const descCount = page.locator('[data-seo-counter="seo_description"]');
  await page.locator("#f-seo_title").fill("a".repeat(60));
  await expect(titleCount).toHaveAttribute("data-level", "ok");
  await page.locator("#f-seo_title").fill("a".repeat(65));
  await expect(titleCount).toHaveAttribute("data-level", "warn");
  await page.locator("#f-seo_title").fill("a".repeat(71));
  await expect(titleCount).toHaveAttribute("data-level", "over");
  await page.locator("#f-seo_description").fill("b".repeat(171));
  await expect(descCount).toHaveAttribute("data-level", "over");

  // Lưu từ tab «Thông tin»: lỗi ở tab Website phải tự mở tab đó.
  await page.getByRole("tab", { name: "Thông tin" }).click();
  await save(page);
  await expect(page.locator("#panel-website")).toBeVisible();
  await expect(page.locator("#f-seo_title-error")).toContainText("tối đa 70");
  await expect(page.locator("#f-seo_description-error")).toContainText("tối đa 170");
  await shot(page, "san-pham-seo-qua-gioi-han");

  await page
    .locator("#f-seo_title")
    .fill("Tinh dầu quế Văn Yên nguyên chất chưng cất từ vỏ quế rừng 10 ml");
  await page.locator("#f-seo_description").fill("Tinh dầu quế chưng cất tại Văn Yên.");
  await shot(page, "san-pham-website-canh-bao-seo");
  await save(page);
  await expect(page).toHaveURL(/\/quan-ly\/san-pham\/\d+\?saved=1$/);
  await expect(page.locator("[data-saved]")).toBeVisible();
  await expect(page.locator("#f-sku")).toHaveValue(sku);
  await expect(page.locator("#f-shelf_life_months")).toHaveValue("24");
  await expect(page.locator("#f-requires_retention_sample")).toBeChecked();
  await expect(page.locator("#f-slug")).toHaveValue(`f4-tu-sua-${stamp}`);
});

test("Sản phẩm: ảnh bắt buộc alt, cảnh báo công thức hết bản ACTIVE, sửa các trường khác vẫn lưu được", async ({
  page,
}) => {
  await open(page, "/quan-ly/san-pham");
  const ingredients = await created<{ items?: { id: number }[] } | { id: number }[]>(
    await call(page, "GET", "/ingredients"),
  );
  const ingredient = (Array.isArray(ingredients) ? ingredients : (ingredients.items ?? []))[0];
  expect(ingredient, "DB có sẵn nguyên liệu (migration seed)").toBeDefined();
  const code = `F4-${stamp}`.toUpperCase();
  const recipe = await created<{ id: number }>(
    await call(page, "POST", "/recipes", {
      code,
      name: `Công thức thử ${stamp}`,
      output_kind: "PRODUCT",
      items: [{ ingredient_id: ingredient?.id, qty_g: "100" }],
    }),
  );
  await created(await call(page, "POST", `/recipes/${recipe.id}/activate`, {}));
  const types = await created<{ id: number }[]>(
    await call(page, "GET", "/goods-types?grp=PRODUCT"),
  );
  const product = await created<{ id: number }>(
    await call(page, "POST", "/products", {
      sku: `F4A-${stamp}`.toUpperCase(),
      name: `Túi thơm quế ${stamp}`,
      slug: `f4-tui-thom-${stamp}`,
      goods_type_id: types[0]?.id,
      size_label: "50 g",
      unit: "túi",
      recipe_code: code,
      images: [
        {
          url: "/media/f4/f4f4f4f4.webp",
          key: "f4/f4f4f4f4",
          alt: "Túi thơm",
          w: 800,
          h: 800,
          widths: [400],
        },
      ],
    }),
  );
  await created(await call(page, "PATCH", `/products/${product.id}`, { status: "PUBLISHED" }));
  await created(await call(page, "POST", `/recipes/${recipe.id}/retire`, {}));

  await open(page, `/quan-ly/san-pham/${product.id}`);
  await expect(page.locator("[data-warnings]")).toContainText(code);
  await expect(page.locator("#f-recipe_code")).toHaveValue(code);

  await page.getByRole("tab", { name: "Website" }).click();
  await page.locator("input[data-image-alt]").fill("");
  await save(page);
  await expect(page.locator("#f-images-error")).toContainText("alt");
  await shot(page, "san-pham-thieu-alt-canh-bao-cong-thuc");

  await page.locator("input[data-image-alt]").fill("Túi thơm quế buộc dây đỏ");
  await page.getByRole("button", { name: "+ Thêm link mua" }).click();
  await page.locator("[data-buylink-row] select").selectOption({ index: 0 });
  await page.locator("[data-buylink-row] input").fill("https://shopee.vn/f4");
  await save(page);
  await expect(page).toHaveURL(/saved=1$/);
  await page.getByRole("tab", { name: "Website" }).click();
  await expect(page.locator("input[data-image-alt]")).toHaveValue("Túi thơm quế buộc dây đỏ");
  await expect(page.locator("[data-buylink-row] input")).toHaveValue("https://shopee.vn/f4");

  await page.goto(`/quan-ly/san-pham?q=F4A-${stamp}`);
  await expect(page.getByText("Công thức không ACTIVE")).toBeVisible();
  await shot(page, "san-pham-danh-sach");
});

test("Chứng nhận: báo lỗi ngày theo trường, tạo, sửa", async ({ page }) => {
  const number = `OCOP-${stamp}`.toUpperCase();

  await open(page, "/quan-ly/chung-nhan/moi");
  await page.locator("#f-kind").selectOption("OCOP");
  await page.locator("#f-number").fill(number);
  await page.locator("#f-issuer").fill("UBND tỉnh Yên Bái");
  await page.locator("#f-stars").selectOption("4");
  await page.locator("#f-issued_on").fill("2026-05-01");
  await page.locator("#f-expires_on").fill("2026-04-01");
  await page.locator("#f-product_id").selectOption({ index: 1 });
  await save(page);
  await expect(page.locator("[data-error-for]:visible, [data-form-error]:visible")).not.toHaveCount(
    0,
  );
  await expect(page).toHaveURL(/chung-nhan\/moi$/);
  await shot(page, "chung-nhan-loi-ngay");

  await page.locator("#f-expires_on").fill("2029-05-01");
  await save(page);
  await expect(page).toHaveURL(/\/quan-ly\/chung-nhan$/);
  await page.goto(`/quan-ly/chung-nhan?q=${number}`);
  await expect(page.getByRole("link", { name: number })).toBeVisible();
  await shot(page, "chung-nhan-danh-sach");

  await page.getByRole("link", { name: number }).click();
  await expect(page.locator("#f-expires_on")).toHaveValue("2029-05-01");
  await page.locator("#f-is_public").uncheck();
  await save(page);
  await expect(page).toHaveURL(/\/quan-ly\/chung-nhan$/);
});

test("Chứng nhận đồi quế: bỏ trống báo lỗi tại ô đồi, chọn người bán rồi chọn đồi theo mã", async ({
  page,
}) => {
  const number = `HC-${stamp}`.toUpperCase();
  await open(page, "/quan-ly/chung-nhan");
  // Migration chỉ seed tỉnh và xã, nên tự tạo một thôn.
  const tree = await created<AreaNode[]>(await call(page, "GET", "/areas"));
  const commune = firstCommune(tree);
  expect(commune, "DB có sẵn xã (migration seed)").toBeDefined();
  const village = await created<{ id: number }>(
    await call(page, "POST", "/areas", {
      code: `F4${stamp}`.toUpperCase(),
      level: "VILLAGE",
      name: `Thôn thử ${stamp}`,
      parent_id: commune?.id,
    }),
  );
  const areaId = village.id;
  const supplier = await created<{ id: number; code: string }>(
    await call(page, "POST", "/suppliers", {
      name: `Hộ trồng quế ${stamp}`,
      kind: "FAMILY",
      area_id: areaId,
    }),
  );
  const plot = await created<{ id: number; code: string }>(
    await call(page, "POST", `/suppliers/${supplier.id}/plots`, {
      area_id: areaId,
      area_ha: "1.5",
    }),
  );

  await page.goto("/quan-ly/chung-nhan/moi");
  await page.locator("#f-kind").selectOption("ORGANIC");
  await expect(page.locator("#f-stars")).toBeHidden();
  await page.locator("#f-number").fill(number);
  await page.getByLabel("Đồi quế", { exact: true }).first().check();
  await expect(page.locator("#f-product_id")).toBeHidden();
  await save(page);
  await expect(page.locator("#f-plot_id-error")).toBeVisible();
  await expect(page).toHaveURL(/chung-nhan\/moi$/);
  await shot(page, "chung-nhan-doi-bo-trong");

  await page.locator("#f-_supplier_id").selectOption(String(supplier.id));
  await expect(page.locator(`#f-plot_id option[value="${plot.id}"]`)).toContainText(plot.code);
  await page.locator("#f-plot_id").selectOption(String(plot.id));
  await shot(page, "chung-nhan-doi-chon-theo-ma");
  await save(page);
  await expect(page).toHaveURL(/\/quan-ly\/chung-nhan$/);

  await page.goto(`/quan-ly/chung-nhan?q=${number}`);
  await expect(page.getByRole("cell", { name: `Đồi ${plot.code}` })).toBeVisible();
  await shot(page, "chung-nhan-doi-danh-sach");

  await page.getByRole("link", { name: number }).click();
  await expect(page.locator("#f-_supplier_id")).toHaveValue(String(supplier.id));
  await expect(page.locator("#f-plot_id")).toHaveValue(String(plot.id));
  await shot(page, "chung-nhan-doi-sua");
  await save(page);
  await expect(page).toHaveURL(/\/quan-ly\/chung-nhan$/);
});

test("Tài khoản: không tự ngừng dùng chính mình; tạo, ngừng dùng và dùng lại người khác", async ({
  page,
}) => {
  const username = `f4.xuong.${stamp}`;

  await open(page, "/quan-ly/tai-khoan");
  const me = await created<{ id: number }>(await call(page, "GET", "/auth/me"));
  await page.goto(`/quan-ly/tai-khoan/${me.id}`);
  await expect(page.locator("[data-self-note]")).toBeVisible();
  await expect(page.getByRole("button", { name: "Ngừng dùng" })).toHaveCount(0);
  await shot(page, "tai-khoan-chinh-minh");
  const blocked = await call(page, "PATCH", `/users/${me.id}`, { status: "INACTIVE" });
  expect(blocked.status()).toBe(409);

  await page.goto("/quan-ly/tai-khoan/moi");
  await page.locator("#f-username").fill(username);
  await page.locator("#f-full_name").fill(`Thợ xưởng ${stamp}`);
  await page.locator("#f-password").fill("ngan");
  await save(page);
  await expect(page.locator("#f-password-error")).toBeVisible();
  await page.locator("#f-password").fill("MatKhau-f4-2026");
  await save(page);
  await expect(page).toHaveURL(/\/quan-ly\/tai-khoan$/);

  await page.goto(`/quan-ly/tai-khoan?q=${username}`);
  await page.getByRole("link", { name: username }).click();
  await page.getByRole("button", { name: "Ngừng dùng" }).click();
  await expect(page).toHaveURL(/\/quan-ly\/tai-khoan$/);
  await page.goto(`/quan-ly/tai-khoan?q=${username}`);
  await shot(page, "tai-khoan-danh-sach-ngung-dung");
  await page.getByRole("link", { name: username }).click();
  await page.getByRole("button", { name: "Dùng lại" }).click();
  await expect(page).toHaveURL(/\/quan-ly\/tai-khoan$/);
});

test("Cài đặt: chặn giá trị ngoài khoảng, lưu và đọc lại", async ({ page }) => {
  await open(page, "/quan-ly/cai-dat");
  const field = page.locator("#f-scan_warning_threshold");
  const original = await field.inputValue();

  await field.fill("0");
  await save(page);
  await expect(page.locator("#f-scan_warning_threshold-error")).toBeVisible();
  await shot(page, "cai-dat-loi");

  const next = String(Number(original) + 1);
  await field.fill(next);
  await save(page);
  await expect(page.locator("[data-saved-note]")).toBeVisible();
  await shot(page, "cai-dat-da-luu");
  await page.reload();
  await expect(field).toHaveValue(next);

  // Trả lại giá trị cũ để không đổi cấu hình của stack đang chạy.
  await field.fill(original);
  await save(page);
  await expect(page.locator("[data-saved-note]")).toBeVisible();
});
