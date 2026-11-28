// Render component bằng Astro Container API (frontend-seo.md 8.3). vitest.config.ts không nạp plugin Astro,
// nên file này tự dựng một Vite server theo cấu hình Astro rồi nạp từng .astro qua ssrLoadModule.

import { getViteConfig } from "astro/config";
import { experimental_AstroContainer as AstroContainer } from "astro/container";
import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { createViteServer } from "vitest/node";
import type { FieldDef } from "../../../lib/admin/catalog";

let server: Awaited<ReturnType<typeof createViteServer>>;
let container: AstroContainer;

type Props = Record<string, unknown>;

async function render(
  path: string,
  options: { props?: Props; slots?: Record<string, string>; locals?: Props; url?: string } = {},
): Promise<string> {
  const mod = await server.ssrLoadModule(path);
  return container.renderToString(mod.default, {
    props: options.props,
    slots: options.slots,
    locals: options.locals,
    request: options.url ? new Request(`http://localhost${options.url}`) : undefined,
  });
}

const BADGE = "/src/components/admin/catalog/StatusBadge.astro";
const LIST = "/src/components/admin/catalog/CatalogList.astro";
const FORM = "/src/components/admin/catalog/CatalogForm.astro";
const LAYOUT = "/src/layouts/Admin.astro";

beforeAll(async () => {
  const config = await getViteConfig({})({ command: "serve", mode: "test" });
  server = await createViteServer({
    ...config,
    server: { middlewareMode: true },
    appType: "custom",
  });
  container = await AstroContainer.create();
}, 60000);

afterAll(async () => {
  await server.close();
});

describe("StatusBadge", () => {
  it("ACTIVE → Đang dùng, INACTIVE → Ngừng dùng", async () => {
    const active = await render(BADGE, { props: { status: "ACTIVE" } });
    expect(active).toContain("Đang dùng");
    expect(active).toContain("badge-success");
    const inactive = await render(BADGE, { props: { status: "INACTIVE" } });
    expect(inactive).toContain("Ngừng dùng");
    expect(inactive).toContain("badge-ghost");
  });
  it("trạng thái lạ hiện nguyên chữ, cho phép đổi nhãn", async () => {
    expect(await render(BADGE, { props: { status: "DRAFT" } })).toContain("DRAFT");
    const custom = await render(BADGE, {
      props: { status: "ACTIVE", labels: { ACTIVE: "Đang bán" } },
    });
    expect(custom).toContain("Đang bán");
  });
});

const columns = [
  { key: "code", label: "Mã", mono: true },
  { key: "name", label: "Tên" },
  { key: "items", label: "Số mục", numeric: true },
  { key: "is_food", label: "Là thực phẩm", format: (v: unknown) => (v ? "✔ Có" : "") },
  { key: "status", label: "Tình trạng" },
];
const rows = [
  { id: 1, code: "TP-TD", name: "Tinh dầu", items: 7, is_food: false, status: "ACTIVE" },
  { id: 2, code: "TP-ONG", name: "Ống <quế>", items: 0, is_food: true, status: "INACTIVE" },
];
const listProps = {
  columns,
  rows,
  total: 2,
  page: 1,
  pageSize: 50,
  basePath: "/quan-ly/loai-hang",
  caption: "Danh sách loại hàng",
};

describe("CatalogList", () => {
  it("OWNER: bảng, ô tìm, lọc trạng thái, nút Thêm, dòng bấm được", async () => {
    const html = await render(LIST, { props: { ...listProps, role: "OWNER" } });
    expect(html).toContain('name="q"');
    expect(html).toContain('name="status"');
    expect(html).toContain("Đang dùng");
    expect(html).toContain("Ngừng dùng");
    expect(html).toContain('href="/quan-ly/loai-hang/moi"');
    expect(html).toContain("+ Thêm");
    expect(html).toContain('data-href="/quan-ly/loai-hang/1"');
    expect(html).toContain('data-href="/quan-ly/loai-hang/2"');
    expect(html).toContain("✔ Có");
    expect(html).toContain("Dòng 1–2 trên 2");
    expect(html).toContain("Danh sách loại hàng");
  });
  it("WORKSHOP: không có nút Thêm", async () => {
    const html = await render(LIST, { props: { ...listProps, role: "WORKSHOP" } });
    expect(html).not.toContain("+ Thêm");
    expect(html).toContain('data-href="/quan-ly/loai-hang/1"');
  });
  it("escape dữ liệu (không chèn HTML từ tên)", async () => {
    const html = await render(LIST, { props: { ...listProps, role: "OWNER" } });
    expect(html).toContain("Ống &lt;quế&gt;");
    expect(html).not.toContain("<quế>");
  });
  it("giữ q và status đang lọc, chọn đúng option", async () => {
    const html = await render(LIST, {
      props: { ...listProps, role: "OWNER", query: { q: "tinh dầu", status: "ACTIVE" } },
    });
    expect(html).toContain('value="tinh dầu"');
    expect(html).toMatch(/<option value="ACTIVE"[^>]*selected/);
  });
  it("rỗng thì hiện emptyText và không có phân trang số", async () => {
    const html = await render(LIST, {
      props: { ...listProps, rows: [], total: 0, emptyText: "Chưa có loại hàng" },
    });
    expect(html).toContain("Chưa có loại hàng");
    expect(html).toContain("Không có dòng nào");
    expect(html).not.toContain("btn join-item");
  });
  it("phân trang theo page/page_size, giữ bộ lọc trong liên kết", async () => {
    const html = await render(LIST, {
      props: { ...listProps, total: 120, page: 2, query: { q: "que", status: "ACTIVE" } },
    });
    expect(html).toContain("Dòng 51–100 trên 120");
    expect(html).toContain('aria-current="page"');
    expect(html).toContain('href="/quan-ly/loai-hang?q=que&amp;status=ACTIVE"');
    expect(html).toContain('href="/quan-ly/loai-hang?q=que&amp;status=ACTIVE&amp;page=3"');
  });
  it("rowHref, newHref tuỳ chỉnh", async () => {
    const html = await render(LIST, {
      props: {
        ...listProps,
        role: "OWNER",
        rowHref: (row: { id: number }) => `/quan-ly/loai-hang/sua?id=${row.id}`,
        newHref: "/quan-ly/loai-hang/them",
      },
    });
    expect(html).toContain('data-href="/quan-ly/loai-hang/sua?id=1"');
    expect(html).toContain('href="/quan-ly/loai-hang/them"');
  });
});

const fields: FieldDef[] = [
  { name: "code", label: "Mã", required: true, value: "TP-TD", mono: true, hint: "Chữ hoa" },
  { name: "name", label: "Tên", required: true, value: "Tinh dầu" },
  {
    name: "group",
    label: "Nhóm",
    type: "select",
    required: true,
    value: "FINISHED",
    options: [
      { value: "MATERIAL", label: "Nguyên liệu" },
      { value: "FINISHED", label: "Thành phẩm" },
    ],
  },
  { name: "is_food", label: "Là thực phẩm", type: "checkbox", value: true },
  { name: "note", label: "Ghi chú", type: "textarea", value: "" },
  { name: "sort", label: "Thứ tự", type: "int", value: 3, min: 0 },
];
const formProps = {
  title: "Sửa loại hàng: Tinh dầu",
  fields,
  apiPath: "/goods-types/3",
  method: "PATCH",
  redirect: "/quan-ly/loai-hang",
  backHref: "/quan-ly/loai-hang",
  status: "ACTIVE",
};

describe("CatalogForm", () => {
  it("OWNER sửa: có Lưu và Ngừng dùng, dấu * ở trường bắt buộc, chỗ hiện lỗi dưới từng trường", async () => {
    const html = await render(FORM, { props: { ...formProps, role: "OWNER" } });
    expect(html).toContain("Lưu");
    expect(html).toContain('data-action="deactivate"');
    expect(html).toContain("Ngừng dùng");
    expect(html).toContain('data-api-path="/goods-types/3"');
    expect(html).toContain('data-method="PATCH"');
    expect(html).toContain('data-deactivate-path="/goods-types/3"');
    expect(html).toContain('data-redirect="/quan-ly/loai-hang"');
    // Dấu * cho 3 trường bắt buộc, không cho trường tuỳ chọn.
    expect(html.match(/aria-hidden="true">\*</g)).toHaveLength(3);
    for (const name of ["code", "name", "group", "is_food", "note", "sort"]) {
      expect(html).toContain(`data-error-for="${name}"`);
    }
    expect(html).toContain("data-form-error");
    expect(html).toContain('role="alert"');
    expect(html).toContain('value="TP-TD"');
    expect(html).toMatch(/<option value="FINISHED"[^>]*selected/);
    expect(html).toMatch(/type="checkbox"[^>]*checked|checked[^>]*type="checkbox"/);
    expect(html).toContain('data-kind="boolean"');
    expect(html).toContain('data-kind="int"');
    expect(html).not.toMatch(/<input[^>]*disabled/);
  });
  it("WORKSHOP: ẩn Lưu và Ngừng dùng, khoá ô nhập, nói rõ chỉ xem", async () => {
    const html = await render(FORM, { props: { ...formProps, role: "WORKSHOP" } });
    expect(html).not.toContain('data-action="save"');
    expect(html).not.toContain('data-action="deactivate"');
    expect(html).not.toContain("data-deactivate-path");
    expect(html).toContain("bạn chỉ xem");
    expect(html).toMatch(/<input[^>]*disabled/);
    expect(html).toContain("Đóng");
  });
  it("không có vai (chưa đăng nhập) cũng xử lý như WORKSHOP", async () => {
    const html = await render(FORM, { props: { ...formProps } });
    expect(html).not.toContain('data-action="save"');
  });
  it("tạo mới (POST, không status): có Lưu, không có Ngừng dùng", async () => {
    const html = await render(FORM, {
      props: {
        ...formProps,
        role: "OWNER",
        method: "POST",
        status: undefined,
        apiPath: "/goods-types",
        title: "Thêm loại hàng",
      },
    });
    expect(html).toContain('data-action="save"');
    expect(html).not.toContain('data-action="deactivate"');
    expect(html).toContain('data-method="POST"');
  });
  it("bản ghi đã ngừng dùng thì nút là Dùng lại, đặt lại ACTIVE", async () => {
    const html = await render(FORM, {
      props: { ...formProps, role: "OWNER", status: "INACTIVE" },
    });
    expect(html).toContain("Dùng lại");
    expect(html).toContain('data-next-status="ACTIVE"');
  });
  it("ô readonly bị khoá kể cả với OWNER; banner và nội dung thêm qua slot", async () => {
    const html = await render(FORM, {
      props: {
        ...formProps,
        role: "OWNER",
        fields: [{ name: "code", label: "Mã", required: true, readonly: true, value: "NL-QUE" }],
      },
      slots: { banner: '<div id="b">Cảnh báo</div>', default: '<div id="extra">Bảng con</div>' },
    });
    expect(html).toMatch(/<input[^>]*disabled/);
    expect(html).toContain('id="b"');
    expect(html).toContain('id="extra"');
  });
  it("mật khẩu không được đổ lại vào value", async () => {
    const html = await render(FORM, {
      props: {
        ...formProps,
        role: "OWNER",
        fields: [{ name: "password", label: "Mật khẩu", type: "password", value: "bi-mat" }],
      },
    });
    expect(html).not.toContain("bi-mat");
    expect(html).toContain('data-kind="password"');
  });
  it("escape giá trị trường", async () => {
    const html = await render(FORM, {
      props: {
        ...formProps,
        role: "OWNER",
        fields: [{ name: "name", label: "Tên", value: '"><script>alert(1)</script>' }],
      },
    });
    // Dấu " trong giá trị phải thành &quot; để không thoát khỏi thuộc tính value.
    expect(html).toContain('value="&quot;>');
    expect(html).not.toContain('value="">');
  });
});

describe("Admin layout: menu Danh mục và nhãn người dùng", () => {
  const owner = { id: 1, username: "chu", full_name: "Chủ doanh nghiệp", role: "OWNER" };
  const workshop = { id: 2, username: "xuong", full_name: "Trần Thị B", role: "WORKSHOP" };

  const countOf = (html: string, text: string) => html.split(text).length - 1;

  it("OWNER: đủ 12 mục menu dẫn tới /quan-ly/...", async () => {
    const html = await render(LAYOUT, {
      props: { title: "Thử" },
      locals: { user: owner },
      url: "/quan-ly",
    });
    for (const slug of [
      "dia-ban",
      "loai-hang",
      "nguyen-lieu",
      "bang-gia",
      "nguoi-ban",
      "khach-hang",
      "phu-lieu",
      "cong-thuc",
      "san-pham",
      "chung-nhan",
      "tai-khoan",
      "cai-dat",
    ]) {
      expect(html).toContain(`href="/quan-ly/${slug}"`);
    }
    expect(html).toContain("Danh mục");
  });
  it("#915: «Chủ doanh nghiệp» chỉ xuất hiện một lần trên nav", async () => {
    const html = await render(LAYOUT, {
      props: { title: "Thử" },
      locals: { user: owner },
      url: "/quan-ly",
    });
    expect(countOf(html, "Chủ doanh nghiệp")).toBe(1);
  });
  it("họ tên khác nhãn vai thì vẫn có huy hiệu vai", async () => {
    const html = await render(LAYOUT, {
      props: { title: "Thử" },
      locals: { user: { ...owner, full_name: "Đỗ Văn A" } },
      url: "/quan-ly",
    });
    expect(html).toContain("Đỗ Văn A");
    expect(countOf(html, "Chủ doanh nghiệp")).toBe(1);
  });
  it("WORKSHOP: ẩn mục OWNER-only, vẫn thấy công thức và phụ liệu", async () => {
    const html = await render(LAYOUT, {
      props: { title: "Thử" },
      locals: { user: workshop },
      url: "/quan-ly",
    });
    for (const slug of [
      "bang-gia",
      "tai-khoan",
      "cai-dat",
      "khach-hang",
      "san-pham",
      "chung-nhan",
    ]) {
      expect(html).not.toContain(`href="/quan-ly/${slug}"`);
    }
    for (const slug of [
      "cong-thuc",
      "phu-lieu",
      "dia-ban",
      "loai-hang",
      "nguyen-lieu",
      "nguoi-ban",
    ]) {
      expect(html).toContain(`href="/quan-ly/${slug}"`);
    }
    expect(html).toContain("Xưởng");
  });
  it("đánh dấu mục đang mở", async () => {
    const html = await render(LAYOUT, {
      props: { title: "Thử" },
      locals: { user: owner },
      url: "/quan-ly/loai-hang/3",
    });
    expect(html).toMatch(/aria-current="page"[^>]*>Loại hàng hóa/);
  });
  it("chưa đăng nhập (trang đăng nhập): không có menu", async () => {
    const html = await render(LAYOUT, {
      props: { title: "Đăng nhập" },
      url: "/quan-ly/dang-nhap",
    });
    expect(html).not.toContain("Danh mục");
    expect(html).not.toContain("data-logout");
  });
});
