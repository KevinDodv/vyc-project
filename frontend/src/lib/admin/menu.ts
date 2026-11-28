/** Menu «Danh mục» của app quản lý và nhãn người dùng trên thanh trên (TK mục 2, 5; frontend-seo.md 1.1, 5.5).
 *  Chỉ là lớp ẩn mục cho gọn: quyền thật kiểm ở middleware và API. */

export type AdminRole = "OWNER" | "WORKSHOP";

export type MenuItem = {
  href: string;
  label: string;
  /** true: ẩn với WORKSHOP. false: WORKSHOP vẫn vào xem (TK mục 2: danh mục «chỉ xem», công thức và phụ liệu không thấy giá). */
  ownerOnly: boolean;
};

export const ROLE_LABEL: Record<AdminRole, string> = {
  OWNER: "Chủ doanh nghiệp",
  WORKSHOP: "Xưởng",
};

/** Thứ tự theo mockup (31-admin.html), route theo brief task #86 (dưới /quan-ly, không có /danh-muc). */
export const CATALOG_MENU: readonly MenuItem[] = [
  { href: "/quan-ly/nguoi-ban", label: "Người bán & đồi quế", ownerOnly: false },
  { href: "/quan-ly/san-pham", label: "Sản phẩm", ownerOnly: true },
  { href: "/quan-ly/nguyen-lieu", label: "Nguyên liệu & hạng", ownerOnly: false },
  { href: "/quan-ly/cong-thuc", label: "Công thức", ownerOnly: false },
  { href: "/quan-ly/phu-lieu", label: "Phụ liệu", ownerOnly: false },
  { href: "/quan-ly/dia-ban", label: "Địa bàn", ownerOnly: false },
  { href: "/quan-ly/khach-hang", label: "Khách & kênh bán", ownerOnly: true },
  { href: "/quan-ly/loai-hang", label: "Loại hàng hóa", ownerOnly: false },
  { href: "/quan-ly/bang-gia", label: "Bảng giá", ownerOnly: true },
  { href: "/quan-ly/chung-nhan", label: "Chứng nhận", ownerOnly: true },
  { href: "/quan-ly/tai-khoan", label: "Tài khoản", ownerOnly: true },
  { href: "/quan-ly/cai-dat", label: "Cài đặt", ownerOnly: true },
];

export function visibleMenu(role: AdminRole | undefined): MenuItem[] {
  if (!role) return [];
  return CATALOG_MENU.filter((item) => role === "OWNER" || !item.ownerOnly);
}

/** Mục đang mở: đúng đường dẫn hoặc trang con của nó (`/quan-ly/loai-hang/3`), không nhầm tiền tố chung chữ. */
export function isActivePath(href: string, pathname: string): boolean {
  const path = pathname.length > 1 ? pathname.replace(/\/+$/, "") : pathname;
  return path === href || path.startsWith(`${href}/`);
}

export function isCatalogPath(pathname: string): boolean {
  return CATALOG_MENU.some((item) => isActivePath(item.href, pathname));
}

function sameText(a: string, b: string): boolean {
  return a.trim().toLocaleLowerCase("vi") === b.trim().toLocaleLowerCase("vi");
}

/** Tên và huy hiệu vai trên thanh trên. Tài khoản chủ tạo bằng `create_owner` có họ tên mặc định
 *  «Chủ doanh nghiệp» trùng nhãn vai; hiện cả hai thì chữ lặp hai lần (#915), nên khi trùng chỉ hiện một. */
export function userLabel(user: { full_name: string; role: AdminRole }): {
  name: string;
  roleBadge: string | null;
} {
  const roleLabel = ROLE_LABEL[user.role];
  const name = user.full_name.trim();
  if (!name) return { name: roleLabel, roleBadge: null };
  return { name, roleBadge: sameText(name, roleLabel) ? null : roleLabel };
}
