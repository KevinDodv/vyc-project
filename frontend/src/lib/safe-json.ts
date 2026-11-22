// Ký tự U+2028 và U+2029 dựng bằng mã số, không viết dạng escape trong mã nguồn,
// để công cụ sửa file không đổi chúng thành ký tự thật (xem ghi chú ở frontend-seo.md 3.2).
const LINE_SEPARATOR = String.fromCharCode(0x2028);
const PARAGRAPH_SEPARATOR = String.fromCharCode(0x2029);

/** JSON.stringify rồi thay "<" (U+003C) bằng dãy 6 ký tự gồm dấu gạch ngược, "u003c";
 *  U+2028 và U+2029 cũng thành dãy 6 ký tự ASCII tương ứng (u2028, u2029).
 *  Kết quả vẫn là JSON hợp lệ, JSON.parse ra đúng giá trị gốc.
 *  Mọi JSON đặt trong thẻ script (page-data, JSON-LD) phải đi qua hàm này (frontend-seo.md 3.2). */
export function safeJson(value: unknown): string {
  const json = JSON.stringify(value) ?? "null";
  return json
    .replaceAll("<", "\\u003c")
    .replaceAll(LINE_SEPARATOR, "\\u2028")
    .replaceAll(PARAGRAPH_SEPARATOR, "\\u2029");
}
