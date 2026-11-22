// Thông tin doanh nghiệp dùng chung cho footer, JSON-LD và /q/ (frontend-seo.md 7.4).
// NỘI DUNG GIỮ CHỖ: sếp cung cấp số liệu thật trước khi gửi xét duyệt Google Ads (mục 12, điểm 2).
export const BRAND = "Quế Văn Yên";

export const BUSINESS = {
  name: "Quế Văn Yên",
  address: "[Địa chỉ giữ chỗ] Văn Yên, Yên Bái",
  phone: "[SĐT giữ chỗ]",
  email: "[email giữ chỗ]",
  taxId: "[MST giữ chỗ]",
  logoPath: "/logo.svg",
  /** Shopee, TikTok Shop, Zalo OA: điền khi có link thật. */
  sameAs: [] as string[],
} as const;

export const POLICY_LINKS = [
  { href: "/chinh-sach-bao-mat", label: "Chính sách bảo mật" },
  { href: "/chinh-sach-doi-tra", label: "Chính sách đổi trả" },
  { href: "/chinh-sach-van-chuyen", label: "Chính sách vận chuyển" },
  { href: "/lien-he", label: "Liên hệ" },
] as const;
