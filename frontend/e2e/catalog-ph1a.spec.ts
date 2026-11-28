// Màn danh mục PH1a (task #93): địa bàn, loại hàng, nguyên liệu + hạng, bảng giá. Chạy trên stack đã dựng sẵn.
//
// File nằm ở frontend/e2e/ (cấu hình riêng e2e/playwright.config.ts; cấu hình gốc chỉ nhìn tests/e2e/).
// Chạy trong frontend/:
//   E2E_OWNER_PASSWORD=... pnpm exec playwright test -c e2e/playwright.config.ts catalog-ph1a
//
// Biến môi trường (xem tests/e2e/sample-flow.spec.ts):
//   E2E_BASE_URL, E2E_OWNER_USERNAME (mặc định e2e-owner), E2E_OWNER_PASSWORD
//   E2E_WORKSHOP_USERNAME, E2E_WORKSHOP_PASSWORD: có thì chạy thêm bài «WORKSHOP chỉ xem»
//   E2E_SHOTS=1: chụp ảnh vào ../.proteam/evidence/f1-*.png
// Mỗi lần chạy dùng mã/tên riêng theo `stamp` nên chạy lại trên cùng DB không đụng nhau.
import { expect, type Page, test } from "@playwright/test";

const USERNAME = process.env.E2E_OWNER_USERNAME ?? "e2e-owner";
const PASSWORD = process.env.E2E_OWNER_PASSWORD ?? "";
const SHOTS = process.env.E2E_SHOTS === "1";
const HIDE_DEV_TOOLBAR = "astro-dev-toolbar { display: none !important; }";

const stamp = Date.now().toString(36);

async function login(page: Page, username: string, password: string): Promise<void> {
  await page.getByLabel("Tên đăng nhập").fill(username);
  await page.getByLabel("Mật khẩu").fill(password);
  await page.getByRole("button", { name: "Đăng nhập" }).click();
  await expect(page).not.toHaveURL(/dang-nhap/);
}

/** Mở một trang quản lý; bị chuyển về đăng nhập thì đăng nhập rồi mở lại. */
async function open(page: Page, path: string): Promise<void> {
  await page.goto(path);
  if (/dang-nhap/.test(page.url())) {
    test.skip(!PASSWORD, "Đặt E2E_OWNER_PASSWORD (và E2E_OWNER_USERNAME) của tài khoản OWNER");
    await login(page, USERNAME, PASSWORD);
    await page.goto(path);
  }
}

async function shot(page: Page, name: string): Promise<void> {
  if (!SHOTS) return;
  await page.screenshot({
    path: `../.proteam/evidence/f1-${name}.png`,
    fullPage: true,
    style: HIDE_DEV_TOOLBAR,
  });
}

const save = (page: Page) => page.getByRole("button", { name: "Lưu", exact: true }).click();

test.describe.configure({ mode: "serial" });

test("Địa bàn: tạo tỉnh › xã › thôn, trùng tên báo ở ô Tên, sửa, ngừng dùng", async ({ page }) => {
  const province = `E2E Tỉnh ${stamp}`;
  const commune = `E2E Xã ${stamp}`;
  const village = `E2E Thôn ${stamp}`;

  await open(page, "/quan-ly/dia-ban/moi");
  await page.locator("#f-level").selectOption("PROVINCE");
  await page.locator("#f-code").fill(`e2e-t-${stamp}`);
  await page.locator("#f-name").fill(province);
  await save(page);
  await expect(page).toHaveURL(/\/quan-ly\/dia-ban$/);
  await expect(page.getByRole("link", { name: province })).toBeVisible();

  // Xã thuộc tỉnh vừa tạo; ô «Thuộc» chỉ còn tỉnh khi chọn cấp Xã.
  await page.goto("/quan-ly/dia-ban/moi");
  await page.locator("#f-level").selectOption("COMMUNE");
  const visibleParents = await page.locator("#f-parent_id option:not([hidden])").allTextContents();
  expect(visibleParents.every((t) => t.startsWith("Tỉnh:") || t.startsWith("— Chọn"))).toBe(true);
  await page.locator("#f-parent_id").selectOption({ label: `Tỉnh: ${province}` });
  await page.locator("#f-code").fill(`e2e-x-${stamp}`);
  await page.locator("#f-name").fill(commune);
  await save(page);
  await expect(page).toHaveURL(/\/quan-ly\/dia-ban$/);

  // Thôn thuộc xã.
  await page.goto("/quan-ly/dia-ban/moi");
  await page.locator("#f-level").selectOption("VILLAGE");
  await page.locator("#f-parent_id").selectOption({ label: `Xã: ${province} › ${commune}` });
  await page.locator("#f-code").fill(`e2e-v-${stamp}`);
  await page.locator("#f-name").fill(village);
  await save(page);
  await expect(page).toHaveURL(/\/quan-ly\/dia-ban$/);

  // Cây: tìm theo tên thì còn tỉnh, xã, thôn theo đúng thứ tự.
  await page.goto(`/quan-ly/dia-ban?q=${encodeURIComponent(`E2E`)}`);
  const names = await page.locator("[data-catalog-list] tbody tr td:first-child").allInnerTexts();
  const ours = names.map((t) => t.replace(/ /g, " ").trim()).filter((t) => t.includes(stamp));
  expect(ours).toEqual([province, `└ ${commune}`, `└ ${village}`]);
  await shot(page, "dia-ban-cay");

  // Trùng tên trong cùng cấp trên: lỗi hiện đúng dưới ô Tên, không chuyển trang.
  await page.goto("/quan-ly/dia-ban/moi");
  await page.locator("#f-level").selectOption("COMMUNE");
  await page.locator("#f-parent_id").selectOption({ label: `Tỉnh: ${province}` });
  await page.locator("#f-code").fill(`e2e-x2-${stamp}`);
  await page.locator("#f-name").fill(commune);
  await save(page);
  await expect(page.locator('[data-error-for="name"]')).toContainText("đã có");
  await expect(page.locator("#f-name")).toHaveAttribute("aria-invalid", "true");
  await expect(page).toHaveURL(/\/dia-ban\/moi$/);
  await shot(page, "dia-ban-trung-ten");

  // Trùng mã: lỗi dưới ô Mã.
  await page.locator("#f-name").fill(`${commune} khác`);
  await page.locator("#f-code").fill(`e2e-x-${stamp}`);
  await save(page);
  await expect(page.locator('[data-error-for="code"]')).toContainText("đã có");

  // Sửa tên xã, rồi ngừng dùng.
  await page.goto(`/quan-ly/dia-ban?q=${encodeURIComponent(commune)}`);
  await page.getByRole("link", { name: commune }).click();
  await expect(page.locator("#f-code")).toBeDisabled();
  await page.locator("#f-name").fill(`${commune} (sửa)`);
  await save(page);
  await expect(page).toHaveURL(/\/quan-ly\/dia-ban$/);
  await page.goto(`/quan-ly/dia-ban?q=${encodeURIComponent(`${commune} (sửa)`)}`);
  await page.getByRole("link", { name: `${commune} (sửa)` }).click();
  await shot(page, "dia-ban-sua");
  await page.getByRole("button", { name: "Ngừng dùng" }).click();
  await expect(page).toHaveURL(/\/quan-ly\/dia-ban$/);
  await page.goto(`/quan-ly/dia-ban?status=INACTIVE&q=${encodeURIComponent(commune)}`);
  await expect(page.locator('[data-catalog-list] [data-status="INACTIVE"]')).toHaveCount(1);
});

test("Loại hàng: tạo, trùng mã, sửa, ngừng dùng", async ({ page }) => {
  const code = `E2E_NL_${stamp}`.toUpperCase();
  const name = `E2E Nguyên liệu ${stamp}`;

  await open(page, "/quan-ly/loai-hang/moi");
  await page.locator("#f-code").fill(code);
  await page.locator("#f-name").fill(name);
  await page.locator("#f-grp").selectOption("MATERIAL");
  await save(page);
  await expect(page).toHaveURL(/\/quan-ly\/loai-hang$/);
  await expect(page.getByRole("link", { name: code })).toBeVisible();

  // Bỏ trống tên: báo «bắt buộc» ngay dưới ô, chưa gọi API.
  await page.goto("/quan-ly/loai-hang/moi");
  await page.locator("#f-code").fill(`${code}_B`);
  await save(page);
  await expect(page.locator('[data-error-for="name"]')).toContainText("bắt buộc");

  // Trùng mã.
  await page.locator("#f-name").fill("Tên bất kỳ");
  await page.locator("#f-grp").selectOption("PRODUCT");
  await page.locator("#f-code").fill(code);
  await save(page);
  await expect(page.locator('[data-error-for="code"]')).toContainText("đã có");
  await shot(page, "loai-hang-trung-ma");

  // Sửa: mã khoá, đổi tên và tích «Là thực phẩm».
  await page.goto(`/quan-ly/loai-hang?q=${encodeURIComponent(code)}`);
  await page.getByRole("link", { name: code }).click();
  await expect(page.locator("#f-code")).toBeDisabled();
  await page.locator("#f-name").fill(`${name} (sửa)`);
  await page.locator("#f-is_food").check();
  await save(page);
  await expect(page).toHaveURL(/\/quan-ly\/loai-hang$/);
  await page.goto(`/quan-ly/loai-hang?q=${encodeURIComponent(code)}`);
  await expect(page.locator("[data-catalog-list] tbody")).toContainText(`${name} (sửa)`);
  await expect(page.locator("[data-catalog-list] tbody")).toContainText("✔ Có");
  await shot(page, "loai-hang-ds");

  // Ngừng dùng rồi dùng lại.
  await page.getByRole("link", { name: code }).click();
  await page.getByRole("button", { name: "Ngừng dùng" }).click();
  await expect(page).toHaveURL(/\/quan-ly\/loai-hang$/);
  await page.goto(`/quan-ly/loai-hang?status=INACTIVE&q=${encodeURIComponent(code)}`);
  await expect(page.locator('[data-catalog-list] [data-status="INACTIVE"]')).toHaveCount(1);
  await page.getByRole("link", { name: code }).click();
  await page.getByRole("button", { name: "Dùng lại" }).click();
  await expect(page).toHaveURL(/\/quan-ly\/loai-hang$/);
  await page.goto(`/quan-ly/loai-hang?status=ACTIVE&q=${encodeURIComponent(code)}`);
  await expect(page.locator('[data-catalog-list] [data-status="ACTIVE"]')).toHaveCount(1);
});

test("Nguyên liệu: tạo kèm hạng, trùng mã, thêm hạng, ngừng dùng", async ({ page }) => {
  const code = `E2E${stamp}`.toUpperCase();
  const name = `E2E Nguyên liệu ${stamp}`;

  await open(page, "/quan-ly/nguyen-lieu");
  await expect(page.locator("[data-catalog-list]")).toBeVisible();
  await shot(page, "nguyen-lieu-ds");

  await page.goto("/quan-ly/nguyen-lieu/moi");
  await page.locator("#f-code").fill(code);
  await page.locator("#f-name").fill(name);
  // Loại hàng chỉ liệt kê nhóm nguyên liệu đang dùng (có loại vừa tạo ở bài trước).
  await page.locator("#f-goods_type_id").selectOption({ label: `E2E Nguyên liệu ${stamp} (sửa)` });
  await page.locator("[data-grade-name]").first().fill("Loại 1");
  await page.getByRole("button", { name: "+ Thêm hạng" }).click();
  await expect(page.locator("[data-grade-rank]").nth(1)).toHaveValue("2");
  await page.locator("[data-grade-name]").nth(1).fill("Loại 2");

  // Hai hạng cùng bậc: báo ở bảng hạng, chưa gọi API.
  await page.locator("[data-grade-rank]").nth(1).fill("1");
  await save(page);
  await expect(page.locator('[data-error-for="grades"]')).toContainText("cùng một bậc");
  await page.locator("[data-grade-rank]").nth(1).fill("2");
  await save(page);
  await expect(page).toHaveURL(/\/quan-ly\/nguyen-lieu$/);
  await expect(page.locator("[data-catalog-list] tbody")).toContainText("Loại 1 · Loại 2");

  // Trùng mã: lỗi dưới ô Mã.
  await page.goto("/quan-ly/nguyen-lieu/moi");
  await page.locator("#f-code").fill(code);
  await page.locator("#f-name").fill("Tên khác");
  await page.locator("#f-goods_type_id").selectOption({ label: `E2E Nguyên liệu ${stamp} (sửa)` });
  await page.locator("[data-grade-name]").first().fill("Loại 1");
  await save(page);
  await expect(page.locator('[data-error-for="code"]')).toContainText("đã có");
  await shot(page, "nguyen-lieu-trung-ma");

  // Sửa: mã khoá, bậc hạng đã lưu khoá, thêm hạng 3.
  await page.goto(`/quan-ly/nguyen-lieu?q=${code}`);
  await page.getByRole("link", { name: code }).click();
  await expect(page.locator("#f-code")).toBeDisabled();
  await expect(page.locator("[data-grade-rank]").first()).toHaveAttribute("readonly", "");
  await page.getByRole("button", { name: "+ Thêm hạng" }).click();
  await page.locator("[data-grade-name]").nth(2).fill("Loại 3");
  await save(page);
  await expect(page).toHaveURL(/\/quan-ly\/nguyen-lieu$/);
  await page.goto(`/quan-ly/nguyen-lieu?q=${code}`);
  await expect(page.locator("[data-catalog-list] tbody")).toContainText("Loại 1 · Loại 2 · Loại 3");
  await page.getByRole("link", { name: code }).click();
  await shot(page, "nguyen-lieu-sua");

  // Ngừng dùng hạng 3 (bỏ tích «Đang dùng»), rồi ngừng dùng cả nguyên liệu để lưới giá chỉ còn nguyên liệu gốc.
  await page.locator("[data-grade-active]").nth(2).uncheck();
  await save(page);
  await expect(page).toHaveURL(/\/quan-ly\/nguyen-lieu$/);
  await page.goto(`/quan-ly/nguyen-lieu?q=${code}`);
  await expect(page.locator("[data-catalog-list] tbody")).toContainText("Loại 3 (ngừng)");
  await page.getByRole("link", { name: code }).click();
  await page.getByRole("button", { name: "Ngừng dùng" }).click();
  await expect(page).toHaveURL(/\/quan-ly\/nguyen-lieu$/);
  await page.goto(`/quan-ly/nguyen-lieu?status=INACTIVE&q=${code}`);
  await expect(page.locator('[data-catalog-list] [data-status="INACTIVE"]')).toHaveCount(1);
});

test("Bảng giá: lưới, điền sẵn giá gần nhất, sửa ô, lịch sử, lỗi nhập", async ({ page }) => {
  const day1 = "2021-03-15";
  const day2 = "2021-03-20";
  const buy = page.locator('input[data-price="buy"]').first();
  const sell = page.locator('input[data-price="sell"]').first();
  // Giá đổi theo lần chạy: DB còn giá lần trước thì ô vẫn là «đã sửa» và được lưu.
  const buyValue = 100_000 + (Date.now() % 90_000);
  const sellValue = buyValue + 27_000;
  const grouped = (n: number) => n.toLocaleString("vi-VN");

  await open(page, `/quan-ly/bang-gia?date=${day1}`);
  // Lưới: mỗi hạng đang dùng có ô giá mua và giá bán.
  const cells = await page.locator("[data-cell]").count();
  expect(cells).toBeGreaterThanOrEqual(6);
  expect(await page.locator('input[data-price="buy"]').count()).toBe(cells);
  expect(await page.locator('input[data-price="sell"]').count()).toBe(cells);

  // Chưa sửa gì: báo, không gọi API.
  await page.getByRole("button", { name: "Lưu giá" }).click();
  await expect(page.locator("[data-form-error]")).toContainText("Chưa sửa ô giá nào");

  // Giá âm và chữ: lỗi hiện ngay dưới ô.
  await buy.fill("-5");
  await sell.fill("abc");
  await page.getByRole("button", { name: "Lưu giá" }).click();
  await expect(page.locator('[data-price-error$="-buy"]:not([hidden])')).toContainText(
    "không được âm",
  );
  await expect(page.locator('[data-price-error$="-sell"]:not([hidden])')).toContainText(
    "số nguyên",
  );
  await expect(buy).toHaveAttribute("aria-invalid", "true");
  await shot(page, "bang-gia-loi");

  // Số lẻ hay dấu ngăn đặt sai: báo lỗi, không nuốt dấu rồi lưu thành số khác.
  await buy.fill("250,5");
  await sell.fill("12.5.3");
  await page.getByRole("button", { name: "Lưu giá" }).click();
  for (const side of ["buy", "sell"]) {
    await expect(page.locator(`[data-price-error$="-${side}"]:not([hidden])`)).toContainText(
      "số nguyên",
    );
  }

  // Nhập đúng, có dấu chấm ngăn nghìn.
  await buy.fill(grouped(buyValue));
  await sell.fill(String(sellValue));
  await page.getByRole("button", { name: "Lưu giá" }).click();
  await expect(page.locator("[data-saved]")).toContainText("15/03/2021");
  await expect(buy).toHaveValue(grouped(buyValue));
  await expect(sell).toHaveValue(grouped(sellValue));

  // Lịch sử 30 ngày có ngày vừa lưu.
  await expect(page.locator(`[data-price-history] tr[data-date="${day1}"]`)).toContainText(
    grouped(buyValue),
  );
  await shot(page, "bang-gia-lich-su");

  // Ngày sau mở ra đã điền sẵn giá ngày gần nhất, ghi chú nguồn giá.
  await page.goto(`/quan-ly/bang-gia?date=${day2}`);
  await expect(buy).toHaveValue(grouped(buyValue));
  await expect(page.locator("[data-cell-note]").first()).toContainText("Giá ngày 15/03/2021");

  // Chọn ngày bằng ô ngày: tự chuyển trang.
  await page.locator('input[name="date"]').fill(day1);
  await expect(page).toHaveURL(new RegExp(`date=${day1}`));
  await shot(page, "bang-gia");
});

test("Bảng giá không có ngày hợp lệ thì dùng hôm nay", async ({ page }) => {
  await open(page, "/quan-ly/bang-gia?date=khong-phai-ngay");
  await expect(page.locator('input[name="date"]')).toHaveValue(/^\d{4}-\d{2}-\d{2}$/);
});

test("WORKSHOP chỉ xem: không có nút Thêm, ô khoá, không có Lưu", async ({ browser }) => {
  const username = process.env.E2E_WORKSHOP_USERNAME;
  const password = process.env.E2E_WORKSHOP_PASSWORD;
  test.skip(!username || !password, "Đặt E2E_WORKSHOP_USERNAME và E2E_WORKSHOP_PASSWORD");
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.goto("/quan-ly/dia-ban");
  await login(page, username ?? "", password ?? "");
  for (const path of ["/quan-ly/dia-ban", "/quan-ly/loai-hang", "/quan-ly/nguyen-lieu"]) {
    await page.goto(path);
    await expect(page.locator("[data-catalog-list]")).toBeVisible();
    await expect(page.getByRole("link", { name: "+ Thêm" })).toHaveCount(0);
  }
  // Mở form sửa: ô khoá, không có Lưu, không có Ngừng dùng.
  await page.goto("/quan-ly/loai-hang");
  await page.locator("[data-catalog-list] tbody tr a").first().click();
  await expect(page.locator("#f-name")).toBeDisabled();
  await expect(page.getByRole("button", { name: "Lưu", exact: true })).toHaveCount(0);
  await expect(page.getByRole("button", { name: "Ngừng dùng" })).toHaveCount(0);
  // Mở thẳng trang tạo: về danh sách.
  await page.goto("/quan-ly/loai-hang/moi");
  await expect(page).toHaveURL(/\/quan-ly\/loai-hang$/);
  // Nguyên liệu: bảng hạng khoá, không có nút thêm hạng.
  await page.goto("/quan-ly/nguyen-lieu");
  await page.locator("[data-catalog-list] tbody tr a").first().click();
  await expect(page.locator("[data-grade-name]").first()).toBeDisabled();
  await expect(page.getByRole("button", { name: "+ Thêm hạng" })).toHaveCount(0);
  // Bảng giá là màn của chủ: xưởng bị chặn (middleware).
  const response = await page.goto("/quan-ly/bang-gia");
  expect(response?.status()).toBe(403);
  await context.close();
});
