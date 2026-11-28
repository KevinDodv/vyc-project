// Màn người bán (đồi quế, duyệt) và khách hàng (task #94). Chạy trên stack đã dựng sẵn:
//   cd frontend && E2E_OWNER_PASSWORD=... E2E_WORKSHOP_PASSWORD=... npx playwright test -c e2e/playwright.config.ts catalog-suppliers
//
// Biến môi trường:
//   E2E_BASE_URL, E2E_OWNER_USERNAME (mặc định e2e-owner), E2E_OWNER_PASSWORD
//   E2E_WORKSHOP_USERNAME (mặc định e2e-xuong), E2E_WORKSHOP_PASSWORD: thiếu thì bỏ qua bài người bán
//   E2E_SHOTS=1: chụp ảnh vào ../.proteam/evidence/f2-*.png
// Cần ít nhất 1 xã đang dùng (migration đã nạp sẵn); thôn thử được tạo qua API.
// Mỗi lần chạy dùng tên riêng theo `stamp` nên chạy lại trên cùng DB không đụng nhau.
import { expect, type Page, test } from "@playwright/test";

const OWNER = process.env.E2E_OWNER_USERNAME ?? "e2e-owner";
const OWNER_PASSWORD = process.env.E2E_OWNER_PASSWORD ?? "";
const WORKSHOP = process.env.E2E_WORKSHOP_USERNAME ?? "e2e-xuong";
const WORKSHOP_PASSWORD = process.env.E2E_WORKSHOP_PASSWORD ?? "";
const SHOTS = process.env.E2E_SHOTS === "1";
const HIDE_DEV_TOOLBAR = "astro-dev-toolbar { display: none !important; }";

const stamp = Date.now().toString(36);
const village = `E2E Thôn NB ${stamp}`;
const supplier = `E2E Người bán ${stamp}`;

async function login(page: Page, username: string, password: string): Promise<void> {
  await page.context().clearCookies();
  await page.goto("/quan-ly/dang-nhap");
  await page.getByLabel("Tên đăng nhập").fill(username);
  await page.getByLabel("Mật khẩu").fill(password);
  await page.getByRole("button", { name: "Đăng nhập" }).click();
  await expect(page).not.toHaveURL(/dang-nhap/);
}

async function shot(page: Page, name: string): Promise<void> {
  if (!SHOTS) return;
  await page.screenshot({
    path: `../.proteam/evidence/f2-${name}.png`,
    fullPage: true,
    style: HIDE_DEV_TOOLBAR,
  });
}

/** Tạo một thôn thuộc xã đầu tiên bằng API (màn địa bàn thuộc task khác). */
async function createVillage(page: Page): Promise<void> {
  await page.goto("/quan-ly/nguoi-ban/moi");
  const commune = await page
    .locator('#sf-area_id option[data-level="COMMUNE"]')
    .first()
    .getAttribute("value");
  expect(commune, "cần ít nhất 1 xã").toBeTruthy();
  const csrf = (await page.context().cookies()).find((c) => c.name === "csrftoken")?.value ?? "";
  const response = await page.request.post("/api/v1/areas", {
    data: { code: `e2e-nb-${stamp}`, level: "VILLAGE", name: village, parent_id: Number(commune) },
    headers: { "X-CSRFToken": csrf, Origin: new URL(page.url()).origin },
  });
  expect(response.status()).toBe(201);
}

async function selectVillage(page: Page, selector: string): Promise<void> {
  const value = await page
    .locator(`${selector} option`, { hasText: village })
    .getAttribute("value");
  await page.locator(selector).selectOption(value ?? "");
}

test.describe.configure({ mode: "serial" });

test("Người bán: xưởng thêm nhanh, chủ thêm đồi, đổi luồng, duyệt", async ({ page }) => {
  test.skip(
    !OWNER_PASSWORD || !WORKSHOP_PASSWORD,
    "Đặt E2E_OWNER_PASSWORD và E2E_WORKSHOP_PASSWORD",
  );
  await login(page, OWNER, OWNER_PASSWORD);
  await createVillage(page);

  // Xưởng thêm nhanh: không có ô luồng; người bán chờ duyệt.
  await login(page, WORKSHOP, WORKSHOP_PASSWORD);
  await page.goto("/quan-ly/nguoi-ban/moi");
  await expect(page.locator("#sf-stream")).toHaveCount(0);
  await page.locator("#sf-name").fill(supplier);
  await page.locator("#sf-kind").selectOption("FARMER");
  await selectVillage(page, "#sf-area_id");
  await page.getByRole("button", { name: "Lưu nhanh" }).click();
  await expect(page).toHaveURL(/\/quan-ly\/nguoi-ban\/\d+\?moi=1$/);
  await expect(page.locator("[data-pending-banner]")).toBeVisible();
  const path = new URL(page.url()).pathname;
  await expect(page.locator('[data-action="approve"]')).toHaveCount(0);

  // Trùng tên + thôn: vẫn lưu được, có cảnh báo.
  await page.goto("/quan-ly/nguoi-ban/moi");
  await page.locator("#sf-name").fill(supplier);
  await page.locator("#sf-kind").selectOption("FARMER");
  await selectVillage(page, "#sf-area_id");
  await page.getByRole("button", { name: "Lưu nhanh" }).click();
  await expect(page.locator("[data-duplicate-warning]")).toBeVisible();
  await shot(page, "03-canh-bao-trung-ten");

  // Chủ: lọc «Chờ duyệt», chưa có đồi thì không chọn được luồng kiểm soát.
  await login(page, OWNER, OWNER_PASSWORD);
  await page.goto(`/quan-ly/nguoi-ban/cho-duyet?q=${encodeURIComponent(supplier)}`);
  await expect(page.locator("tbody tr")).toHaveCount(2);
  await page.goto(path);
  await expect(page.locator('#sf-stream option[value="CONTROLLED"]')).toBeDisabled();

  // Đồi: năm trồng sai báo ngay dưới ô, sửa đúng thì lưu và thành đồi mặc định.
  await page.locator('[data-open-dialog="plot-new"]').click();
  await selectVillage(page, "#pn-area_id");
  await page.locator("#pn-planted_year").fill("1900");
  await page.locator("#pn-coordinates").fill("21.912345, 104.567890");
  await page.getByRole("button", { name: "Lưu đồi" }).click();
  await expect(page.locator("#pn-planted_year-error")).toContainText("1950");
  await expect(page.locator("#pn-planted_year")).toHaveAttribute("aria-invalid", "true");
  await shot(page, "06-loi-nam-trong");
  await page.locator("#pn-planted_year").fill("2012");
  await page.getByRole("button", { name: "Lưu đồi" }).click();
  await expect(page.locator("[data-plots] tbody tr")).toHaveCount(1);
  await expect(page.locator("[data-plots] tbody tr")).toContainText("Mặc định");

  // Thương lái thì khoá luồng thường; đổi lại hộ dân thì chọn được kiểm soát.
  await page.locator("#sf-kind").selectOption("TRADER");
  await expect(page.locator("#sf-stream")).toBeDisabled();
  await expect(page.locator("#sf-stream")).toHaveValue("GENERAL");
  await page.locator("#sf-kind").selectOption("FARMER");
  await page.locator("#sf-stream").selectOption("CONTROLLED");

  // Bấm Duyệt ngay (chưa bấm Lưu): luồng vừa đổi vẫn được lưu.
  await page.getByRole("button", { name: "Duyệt người bán" }).click();
  await expect(page).toHaveURL(/\?da-duyet=1$/);
  await expect(page.locator("[data-pending-banner]")).toHaveCount(0);
  await expect(page.locator("#sf-stream")).toHaveValue("CONTROLLED");
  await shot(page, "08-da-duyet");

  // Luồng kiểm soát phải còn đồi: ngừng đồi cuối bị từ chối.
  page.on("dialog", (dialog) => dialog.accept());
  await page.locator('[data-plot-action="deactivate"]').click();
  await expect(page.locator("[data-plots-error]")).toContainText("ít nhất 1 đồi");
});

test("Khách hàng: tạo, thiếu tên báo ở ô Tên, sửa, ngừng dùng", async ({ page }) => {
  test.skip(!OWNER_PASSWORD, "Đặt E2E_OWNER_PASSWORD");
  const name = `E2E Khách ${stamp}`;
  const rows = page.locator("[data-catalog-list] tbody tr");
  const save = () => page.getByRole("button", { name: "Lưu", exact: true }).click();
  await login(page, OWNER, OWNER_PASSWORD);

  await page.goto("/quan-ly/khach-hang/moi");
  await save();
  await expect(page.locator('[data-error-for="name"]')).toBeVisible();
  await expect(page.locator('[data-error-for="kind"]')).toBeVisible();
  await shot(page, "12-khach-hang-thieu-truong");
  await page.locator("#f-name").fill(name);
  await page.locator("#f-kind").selectOption("AGENT");
  await page.locator("#f-phone").fill("0987654321");
  await save();
  await expect(page).toHaveURL(/\/quan-ly\/khach-hang$/);

  await page.goto(`/quan-ly/khach-hang?q=${encodeURIComponent(name)}`);
  await expect(rows).toContainText("Đại lý");
  await shot(page, "13-khach-hang-ds");
  await rows.getByRole("link").click(); // cột đầu (mã KH) là liên kết mở form
  await page.locator("#f-address").fill("Mậu A, Lào Cai");
  await save();
  await expect(page).toHaveURL(/\/quan-ly\/khach-hang$/);

  await page.goto(`/quan-ly/khach-hang?q=${encodeURIComponent(name)}`);
  await expect(rows).toContainText("Mậu A");
  await rows.getByRole("link").click(); // cột đầu (mã KH) là liên kết mở form
  await page.getByRole("button", { name: "Ngừng dùng" }).click();
  await expect(page).toHaveURL(/\/quan-ly\/khach-hang$/);
  await page.goto(`/quan-ly/khach-hang?q=${encodeURIComponent(name)}&status=INACTIVE`);
  await expect(rows).toContainText("Ngừng dùng");
});
