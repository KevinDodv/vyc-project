/** Hàm chữ riêng của màn người bán (task #94). Cùng quy tắc `fold` của backend (services/suppliers.py). */

/** Bỏ dấu, đ → d, hạ chữ, gộp khoảng trắng: «Nguyễn  Văn Hùng» khớp «nguyen van hung». */
export function fold(text: string): string {
  return text
    .replaceAll("đ", "d")
    .replaceAll("Đ", "D")
    .normalize("NFD")
    .replace(/\p{M}/gu, "")
    .toLocaleLowerCase("vi")
    .split(/\s+/)
    .filter(Boolean)
    .join(" ");
}
