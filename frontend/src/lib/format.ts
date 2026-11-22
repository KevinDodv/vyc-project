// Định dạng hiển thị (frontend-seo.md mục 10). Không tính toán trên số cân dạng chuỗi.
const vnd = new Intl.NumberFormat("vi-VN");

/** Tiền là số nguyên VND: 120000 → "120.000 ₫". */
export function formatVnd(amount: number): string {
  return `${vnd.format(amount)} ₫`;
}

/** Số cân, gram là chuỗi thập phân ("120.50"): chỉ đổi dấu thập phân sang dấu phẩy, không parseFloat. */
export function formatDecimalString(value: string): string {
  return value.replace(".", ",");
}
