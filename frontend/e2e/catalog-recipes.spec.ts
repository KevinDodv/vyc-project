// Màn phụ liệu và công thức (task #95; TK mục 5, BR-21, BR-26). Chạy trên stack đã dựng sẵn.
//
// Chạy: cd frontend && npx playwright test -c e2e/playwright.config.ts catalog-recipes
//
// Biến môi trường (như catalog-ph1a.spec.ts):
//   E2E_BASE_URL, E2E_OWNER_USERNAME (mặc định e2e-owner), E2E_OWNER_PASSWORD
//   E2E_WORKSHOP_USERNAME, E2E_WORKSHOP_PASSWORD: có thì chạy thêm bài «WORKSHOP chỉ xem»
//   E2E_SHOTS=1: chụp ảnh vào ../.proteam/evidence/f3-*.png
// Mỗi lần chạy dùng mã/tên riêng theo `stamp` nên chạy lại trên cùng DB không đụng nhau.
import { expect, type Page, test } from "@playwright/test";

const USERNAME = process.env.E2E_OWNER_USERNAME ?? "e2e-owner";
const PASSWORD = process.env.E2E_OWNER_PASSWORD ?? "";
const SHOTS = process.env.E2E_SHOTS === "1";
const HIDE_DEV_TOOLBAR = "astro-dev-toolbar { display: none !important; }";

const stamp = Date.now().toString(36).toUpperCase();
// Mã phụ liệu tối đa 6 ký tự: một chữ phân biệt + 5 ký tự cuối của stamp.
const ingredient = (letter: string) => {
  const code = `${letter}${stamp.slice(-5)}`;
  const name = `E2E phụ liệu ${letter} ${stamp}`;
  return { code, name, label: `${code} — ${name}` };
};
const [A, B, C, D, E] = ["A", "B", "C", "D", "E"].map(ingredient) as [
  ReturnType<typeof ingredient>,
  ReturnType<typeof ingredient>,
  ReturnType<typeof ingredient>,
  ReturnType<typeof ingredient>,
  ReturnType<typeof ingredient>,
];
const RECIPE = `E2E-A-${stamp}`;
const LOOP = `E2E-B-${stamp}`;

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
    path: `../.proteam/evidence/f3-${name}.png`,
    fullPage: true,
    style: HIDE_DEV_TOOLBAR,
  });
}

const rows = (page: Page) => page.locator("[data-item-body] > tr[data-item-row]");

type Line = { label: string; gram: string; alt?: string; optional?: boolean };

async function addLine(page: Page, line: Line): Promise<void> {
  await page.getByRole("button", { name: "+ Thêm dòng" }).click();
  const row = rows(page).last();
  await row.locator('[data-field="ingredient"]').selectOption({ label: line.label });
  await row.locator('[data-field="qty"]').fill(line.gram);
  if (line.alt) await row.locator('[data-field="alt"]').selectOption({ label: line.alt });
  if (line.optional) await row.locator('[data-field="optional"]').check();
}

const pcts = (page: Page) => page.locator("[data-item-body] [data-pct]");
const total = (page: Page) => page.locator("[data-base-total]");
const button = (page: Page, name: string) => page.getByRole("button", { name, exact: true });
const badge = (page: Page) => page.locator("[data-recipe-form] [data-status].badge");

test.describe.configure({ mode: "serial" });

test("Phụ liệu: đơn vị gram, tỷ trọng tham khảo, trùng mã báo ở ô Mã", async ({ page }) => {
  for (const item of [A, B, C, D, E]) {
    await open(page, "/quan-ly/phu-lieu/moi");
    await page.locator("#f-code").fill(item.code.toLowerCase());
    await expect(page.locator("#f-code")).toHaveValue(item.code);
    await page.locator("#f-name").fill(item.name);
    await page.locator("#f-kind").selectOption("BLEND");
    if (item === A) {
      await expect(page.locator("[data-unit-note]")).toContainText("gram");
      await page.locator("#f-density_g_ml").fill("0,95");
      await shot(page, "phu-lieu-moi");
    }
    await button(page, "Lưu").click();
    await expect(page).toHaveURL(/\/quan-ly\/phu-lieu$/);
  }

  await page.goto(`/quan-ly/phu-lieu?q=${A.code}`);
  const row = page.locator("[data-catalog-list] tbody tr").first();
  await expect(row).toContainText(A.name);
  await expect(row).toContainText("0,95");
  await expect(row).toContainText("Hương nền, dung dịch tẩm");
  await shot(page, "phu-lieu-ds");

  await page.goto("/quan-ly/phu-lieu/moi");
  await page.locator("#f-code").fill(A.code);
  await page.locator("#f-name").fill(`${A.name} khác`);
  await page.locator("#f-kind").selectOption("BLEND");
  await button(page, "Lưu").click();
  await expect(page.locator('[data-error-for="code"]')).toBeVisible();
  await expect(page).toHaveURL(/\/phu-lieu\/moi$/);
});

test("Công thức: tạo, % và mẻ chuẩn, scale, kích hoạt, bản mới, vòng lặp, ngừng", async ({
  page,
}) => {
  await open(page, "/quan-ly/cong-thuc/moi");
  await page.locator("#f-code").fill(RECIPE.toLowerCase());
  await expect(page.locator("#f-code")).toHaveValue(RECIPE);
  await page.locator("#f-name").fill(`E2E bán thành phẩm A ${stamp}`);
  await expect(page.locator("#f-output_ingredient_id")).toBeHidden();
  await page.locator("#f-output_kind").selectOption("INTERMEDIATE");
  await page.locator("#f-output_ingredient_id").selectOption({ label: A.label });

  await addLine(page, { label: B.label, gram: "25" });
  await addLine(page, { label: C.label, gram: "75" });
  await expect(total(page)).toHaveText("100 g");
  await expect(pcts(page)).toHaveText(["25,00 %", "75,00 %"]);

  // Nhóm lựa chọn chỉ có một dòng: API từ chối, lỗi hiện dưới bảng thành phần.
  await addLine(page, { label: D.label, gram: "10", alt: "Nhóm 1" });
  await button(page, "Tạo công thức").click();
  await expect(page.locator('[data-error-for="items"]')).toContainText("chỉ có một dòng");

  // Hai phương án cùng Nhóm 1: mẻ chuẩn chỉ cộng phương án nặng nhất (100 + 30).
  await addLine(page, { label: E.label, gram: "30", alt: "Nhóm 1" });
  await expect(total(page)).toHaveText("130 g");
  await expect(pcts(page)).toHaveText(["19,23 %", "57,69 %", "7,69 %", "23,08 %"]);

  // Thử scale: mẻ 260 g gấp đôi mẻ chuẩn.
  await page.locator("[data-scale-batch]").fill("260");
  await expect(page.locator("[data-scale-body] tr td:last-child")).toHaveText([
    "50",
    "150",
    "20",
    "60",
  ]);
  await expect(page.locator("[data-scale-body] tr td:first-child")).toHaveText([
    B.label,
    C.label,
    D.label,
    E.label,
  ]);
  await shot(page, "cong-thuc-moi");

  await button(page, "Tạo công thức").click();
  await expect(page).toHaveURL(/\/quan-ly\/cong-thuc\/\d+$/);
  const v1Url = page.url();
  await expect(page.locator("#recipe-form-title")).toHaveText(`${RECIPE} · phiên bản 1`);
  await expect(badge(page)).toHaveText("Nháp");
  // Số máy chủ trả về khớp số tính ở trình duyệt.
  await expect(total(page)).toHaveText("130 g");
  await expect(pcts(page)).toHaveText(["19,23 %", "57,69 %", "7,69 %", "23,08 %"]);

  await button(page, "Kích hoạt").click();
  await expect(badge(page)).toHaveText("Đang dùng");
  await expect(page.locator("[data-locked]")).toContainText("đã khoá");
  await expect(page.locator("#f-name")).toBeDisabled();
  await expect(rows(page).first().locator('[data-field="qty"]')).toBeDisabled();
  await expect(button(page, "+ Thêm dòng")).toHaveCount(0);
  await expect(button(page, "Lưu nháp")).toHaveCount(0);
  await expect(button(page, "Kích hoạt")).toHaveCount(0);
  // Bản khoá vẫn thử scale được.
  await page.locator("[data-scale-batch]").fill("65");
  await expect(page.locator("[data-scale-body] tr td:last-child").first()).toHaveText("12,5");
  await shot(page, "cong-thuc-khoa");

  await button(page, "Tạo phiên bản mới").click();
  await expect(page.locator("#recipe-form-title")).toHaveText(`${RECIPE} · phiên bản 2`);
  expect(page.url()).not.toBe(v1Url);
  const v2Url = page.url();
  await expect(badge(page)).toHaveText("Nháp");
  await expect(page.locator("#f-name")).toBeEnabled();
  await rows(page).first().locator('[data-field="qty"]').fill("45,5");
  await expect(total(page)).toHaveText("150,5 g");
  const saved = page.waitForResponse(
    (r) => r.request().method() === "PUT" && /\/recipes\/\d+\/items$/.test(r.url()),
  );
  await button(page, "Lưu nháp").click();
  expect((await saved).status()).toBe(200);
  await page.goto(v2Url);
  await expect(rows(page).first().locator('[data-field="qty"]')).toHaveValue("45,5");
  await shot(page, "cong-thuc-ban-moi");

  // Xoá hết dòng rồi «Kích hoạt»: dòng rỗng đã lưu, mẻ chuẩn giữ số máy chủ đang giữ, kích hoạt bị từ chối.
  for (let left = await rows(page).count(); left > 0; left -= 1) {
    await rows(page).first().getByRole("button", { name: "Xoá dòng" }).click();
  }
  await expect(total(page)).toHaveText("150,5 g");
  await button(page, "Kích hoạt").click();
  await expect(page.locator("[data-recipe-form] [role=alert]:visible").first()).toContainText(
    "chưa có dòng thành phần",
  );
  // Thêm lại đúng các dòng cũ: vẫn phải lưu lại rồi mới kích hoạt.
  await addLine(page, { label: B.label, gram: "45,5" });
  await addLine(page, { label: C.label, gram: "75" });
  await addLine(page, { label: D.label, gram: "10", alt: "Nhóm 1" });
  await addLine(page, { label: E.label, gram: "30", alt: "Nhóm 1" });
  await button(page, "Kích hoạt").click();
  await expect(badge(page)).toHaveText("Đang dùng");
  await expect(rows(page)).toHaveCount(4);
  await expect(total(page)).toHaveText("150,5 g");

  // Danh sách theo mã và phiên bản: v2 đang dùng đứng trước, v1 đã ngừng.
  await page.goto(`/quan-ly/cong-thuc?q=${encodeURIComponent(RECIPE)}`);
  const listRows = page.locator("[data-catalog-list] tbody tr");
  await expect(listRows).toHaveCount(2);
  await expect(listRows.nth(0)).toContainText("v2");
  await expect(listRows.nth(0)).toContainText("Đang dùng");
  await expect(listRows.nth(1)).toContainText("v1");
  await expect(listRows.nth(1)).toContainText("Đã ngừng");
  await shot(page, "cong-thuc-ds");

  // Vòng lặp: A làm từ B, giờ B lại làm từ A.
  await page.goto("/quan-ly/cong-thuc/moi");
  await page.locator("#f-code").fill(LOOP);
  await page.locator("#f-name").fill(`E2E vòng lặp ${stamp}`);
  await page.locator("#f-output_kind").selectOption("INTERMEDIATE");
  await page.locator("#f-output_ingredient_id").selectOption({ label: B.label });
  await addLine(page, { label: A.label, gram: "10" });
  await button(page, "Tạo công thức").click();
  const loopError = page.locator('[data-error-for="items"]');
  await expect(loopError).toContainText("Công thức không được tự chứa chính nó");
  await expect(loopError).toContainText(`${B.code} → ${A.code} → ${B.code}`);
  await expect(page).toHaveURL(/\/cong-thuc\/moi$/);
  await expect(button(page, "Tạo công thức")).toBeEnabled();
  await shot(page, "cong-thuc-vong-lap");

  await page.goto(v2Url);
  await button(page, "Ngừng").click();
  await expect(badge(page)).toHaveText("Đã ngừng");
  await expect(button(page, "Ngừng")).toHaveCount(0);
  await expect(button(page, "Tạo phiên bản mới")).toBeVisible();
});

test("Công thức seed: SC-VQH không có dòng vẫn ghi 100 g, DDT ghi «Nhóm 1»", async ({ page }) => {
  await open(page, "/quan-ly/cong-thuc?q=SC-VQH");
  await page.locator("[data-catalog-list] tbody tr a").first().click();
  await expect(page.locator("#recipe-form-title")).toContainText("SC-VQH");
  await expect(rows(page)).toHaveCount(0);
  await expect(total(page)).toHaveText("100 g");
  await page.locator("[data-scale-batch]").fill("50");
  await expect(total(page)).toHaveText("100 g");
  await shot(page, "cong-thuc-sc-vqh");

  await page.goto("/quan-ly/cong-thuc?q=DDT");
  await page.locator("[data-catalog-list] tbody tr a").first().click();
  await expect(page.locator("#recipe-form-title")).toContainText("DDT");
  const selected = page.locator('[data-item-body] [data-field="alt"] option:checked');
  await expect(selected).toHaveText(["—", "Nhóm 1", "Nhóm 1"]);
  await shot(page, "cong-thuc-ddt-nhom");
});

test("WORKSHOP chỉ xem phụ liệu và công thức", async ({ browser }) => {
  const username = process.env.E2E_WORKSHOP_USERNAME;
  const password = process.env.E2E_WORKSHOP_PASSWORD;
  test.skip(!username || !password, "Đặt E2E_WORKSHOP_USERNAME và E2E_WORKSHOP_PASSWORD");
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.goto("/quan-ly/cong-thuc");
  await login(page, username ?? "", password ?? "");
  for (const path of ["/quan-ly/phu-lieu", "/quan-ly/cong-thuc"]) {
    await page.goto(path);
    await expect(page.locator("[data-catalog-list]")).toBeVisible();
    await expect(page.getByRole("link", { name: "+ Thêm" })).toHaveCount(0);
    await page.goto(`${path}/moi`);
    await expect(page).toHaveURL(new RegExp(`${path}$`));
  }
  await page.goto(`/quan-ly/cong-thuc?q=${encodeURIComponent(RECIPE)}`);
  await page.locator("[data-catalog-list] tbody tr a").first().click();
  await expect(page.locator("[data-locked]")).toContainText("chỉ xem");
  await expect(page.locator("#f-name")).toBeDisabled();
  for (const name of ["Lưu nháp", "Kích hoạt", "Ngừng", "Tạo phiên bản mới", "+ Thêm dòng"]) {
    await expect(button(page, name)).toHaveCount(0);
  }
  await shot(page, "cong-thuc-workshop");
  await context.close();
});
