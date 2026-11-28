// Tải ảnh ở form sản phẩm (task #101): POST /api/v1/images rồi PATCH `images` của sản phẩm.
// Chạy trên stack đã dựng sẵn, `/media/` phải được phục vụ (dev: DJANGO_DEBUG=1):
//   cd frontend && E2E_OWNER_PASSWORD=... npx playwright test -c e2e/playwright.config.ts catalog-product-images
//
// Biến môi trường: E2E_BASE_URL, E2E_OWNER_USERNAME (mặc định e2e-owner), E2E_OWNER_PASSWORD,
//   E2E_SHOTS=1: chụp ảnh vào ../.proteam/evidence/101-*.png
import { crc32, deflateSync } from "node:zlib";
import { expect, type Locator, type Page, test } from "@playwright/test";

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

async function shot(target: Page | Locator, name: string): Promise<void> {
  if (!SHOTS) return;
  await target.screenshot({
    path: `../.proteam/evidence/101-${name}.png`,
    style: HIDE_DEV_TOOLBAR,
  });
}

/** Gọi API bằng chính phiên đăng nhập của trang (kèm CSRF) để dựng dữ liệu. */
async function call<T>(page: Page, method: "GET" | "POST", path: string, data?: unknown) {
  const cookies = await page.context().cookies();
  const csrf = cookies.find((cookie) => cookie.name === "csrftoken")?.value ?? "";
  const response = await page.context().request.fetch(`/api/v1${path}`, {
    method,
    data,
    headers: { "X-CSRFToken": csrf },
  });
  expect(response.ok(), `${response.url()} → ${await response.text()}`).toBe(true);
  return (await response.json()) as T;
}

/** JPEG thật do trình duyệt vẽ: nền màu và một dòng chữ để nhìn ra thứ tự trong ảnh chụp. */
async function jpeg(page: Page, name: string, color: string) {
  const url = await page.evaluate(
    ([fill, text]) => {
      const canvas = document.createElement("canvas");
      canvas.width = 1200;
      canvas.height = 1200;
      const context = canvas.getContext("2d");
      if (!context) throw new Error("Không có canvas 2d");
      context.fillStyle = fill as string;
      context.fillRect(0, 0, 1200, 1200);
      context.fillStyle = "#fff";
      context.font = "bold 360px sans-serif";
      context.textAlign = "center";
      context.fillText(text as string, 600, 720);
      return canvas.toDataURL("image/jpeg", 0.9);
    },
    [color, name],
  );
  const buffer = Buffer.from(url.split(",")[1] ?? "", "base64");
  return { name: `${name}-${stamp}.jpg`, mimeType: "image/jpeg", buffer };
}

/** PNG chỉ khai kích thước 8000×6000 (48 triệu điểm ảnh): backend phải từ chối trước khi giải nén. */
function hugePng() {
  const chunk = (type: string, data: Buffer) => {
    const body = Buffer.concat([Buffer.from(type, "ascii"), data]);
    const out = Buffer.alloc(body.length + 8);
    out.writeUInt32BE(data.length, 0);
    body.copy(out, 4);
    out.writeUInt32BE(crc32(body), body.length + 4);
    return out;
  };
  const header = Buffer.alloc(13);
  header.writeUInt32BE(8000, 0);
  header.writeUInt32BE(6000, 4);
  header.set([8, 2, 0, 0, 0], 8);
  const buffer = Buffer.concat([
    Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]),
    chunk("IHDR", header),
    chunk("IDAT", deflateSync(Buffer.alloc(1))),
    chunk("IEND", Buffer.alloc(0)),
  ]);
  return { name: "qua-nhieu-diem-anh.png", mimeType: "image/png", buffer };
}

/** Ảnh thu nhỏ đã tải được thật (tức `/media/` phục vụ file vừa ghi). */
async function expectLoaded(thumb: Locator): Promise<void> {
  await expect(thumb).toBeVisible();
  await expect
    .poll(() => thumb.evaluate((img: HTMLImageElement) => img.complete && img.naturalWidth))
    .toBeGreaterThan(0);
}

test.beforeEach(() => {
  test.skip(!PASSWORD, "Đặt E2E_OWNER_PASSWORD (và E2E_OWNER_USERNAME) của tài khoản OWNER");
});

test("Sản phẩm: tải ảnh, thấy ảnh thu nhỏ, đổi thứ tự, gỡ, báo lỗi tiếng Việt", async ({
  page,
}) => {
  await open(page, "/quan-ly/san-pham");
  const types = await call<{ id: number }[]>(page, "GET", "/goods-types?grp=PRODUCT");
  const product = await call<{ id: number }>(page, "POST", "/products", {
    sku: `IMG-${stamp}`.toUpperCase(),
    name: `Tinh dầu thử ảnh ${stamp}`,
    slug: `thu-anh-${stamp}`,
    goods_type_id: types[0]?.id,
    size_label: "10 ml",
    unit: "chai",
  });
  const path = `/quan-ly/san-pham/${product.id}`;
  await open(page, path);
  await page.getByRole("tab", { name: "Website" }).click();

  const field = page.locator('[data-field="images"]');
  const input = page.getByLabel("Tải ảnh lên");
  const rows = field.locator("[data-image-row]");
  const alts = field.locator("input[data-image-alt]");
  const uploadError = field.locator("[data-image-upload-error]");
  const save = page.getByRole("button", { name: "Lưu", exact: true });
  await expect(field.getByText("Chưa có ảnh.")).toBeVisible();

  await input.setInputFiles(await jpeg(page, "A", "#8b4513"));
  await expect(rows).toHaveCount(1);
  await expectLoaded(rows.first().locator("img"));
  await expect(alts.first()).toBeFocused();
  await expect(field.getByText("Chưa có ảnh.")).toBeHidden();
  await shot(field, "tai-mot-anh");

  // Alt bắt buộc như trước.
  await save.click();
  await expect(page.locator("#f-images-error")).toContainText("alt");
  await alts.first().fill("Ảnh A");
  await save.click();
  await expect(page).toHaveURL(/saved=1$/);
  await page.getByRole("tab", { name: "Website" }).click();
  await expect(alts.first()).toHaveValue("Ảnh A");
  await expectLoaded(rows.first().locator("img"));
  await shot(field, "da-luu");

  // Thêm ảnh thứ hai, đưa lên đầu.
  await input.setInputFiles(await jpeg(page, "B", "#2e6b30"));
  await expect(rows).toHaveCount(2);
  await alts.nth(1).fill("Ảnh B");
  await expect(page.getByRole("button", { name: "Chuyển ảnh 1 lên" })).toBeDisabled();
  await expect(page.getByRole("button", { name: "Chuyển ảnh 2 xuống" })).toBeDisabled();
  await page.getByRole("button", { name: "Chuyển ảnh 2 lên" }).click();
  await expect(alts.nth(0)).toHaveValue("Ảnh B");
  await expect(alts.nth(1)).toHaveValue("Ảnh A");
  await expectLoaded(rows.nth(0).locator("img"));
  await shot(field, "doi-thu-tu");
  await save.click();
  await expect(page).toHaveURL(/saved=1$/);
  await expect
    .poll(async () => {
      const saved = await call<{ images: { alt: string }[] }>(
        page,
        "GET",
        `/products/${product.id}`,
      );
      return saved.images.map((image) => image.alt);
    })
    .toEqual(["Ảnh B", "Ảnh A"]);

  // Lỗi: sai loại (chặn ở trình duyệt), quá 10 MB (chặn ở trình duyệt).
  await open(page, path);
  await page.getByRole("tab", { name: "Website" }).click();
  await input.setInputFiles([
    { name: "bang-gia.pdf", mimeType: "application/pdf", buffer: Buffer.from("%PDF-1.4") },
    { name: "qua-lon.jpg", mimeType: "image/jpeg", buffer: Buffer.alloc(10 * 1024 * 1024 + 1) },
  ]);
  await expect(uploadError).toContainText("bang-gia.pdf: Chỉ nhận ảnh JPEG, PNG hoặc WebP");
  await expect(uploadError).toContainText("qua-lon.jpg: Ảnh quá 10 MB");
  await expect(rows).toHaveCount(2);
  await shot(field, "loi-chan-o-trinh-duyet");

  // Lỗi từ API thật: file hỏng sát 10 MB (thân request đi qua được proxy) và quá 40 triệu điểm ảnh.
  await input.setInputFiles([
    { name: "hong.jpg", mimeType: "image/jpeg", buffer: Buffer.alloc(10 * 1024 * 1024 - 1) },
    hugePng(),
  ]);
  await expect(uploadError).toContainText(
    "hong.jpg: File không phải ảnh JPEG, PNG, WebP hoặc đã hỏng",
  );
  await expect(uploadError).toContainText("qua-nhieu-diem-anh.png: Ảnh quá 40 triệu điểm ảnh");
  await expect(rows).toHaveCount(2);
  await expect(save).toBeEnabled();
  await shot(field, "loi-tu-api");

  // Gỡ ảnh rồi lưu.
  await page.getByRole("button", { name: "Gỡ ảnh 1" }).click();
  await expect(rows).toHaveCount(1);
  await expect(alts.first()).toHaveValue("Ảnh A");
  await save.click();
  await expect(page).toHaveURL(/saved=1$/);
  await page.getByRole("tab", { name: "Website" }).click();
  await expect(rows).toHaveCount(1);
  await expect(alts.first()).toHaveValue("Ảnh A");
});
