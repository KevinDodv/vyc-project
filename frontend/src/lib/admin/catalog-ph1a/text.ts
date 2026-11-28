/** Hàm chữ dùng chung cho các màn PH1a (task #93). */

/** Bỏ dấu, đổi đ → d, chữ thường: «Lào Cai» khớp «lao cai». */
export function fold(text: string): string {
  return text
    .normalize("NFD")
    .replace(/\p{M}/gu, "")
    .replace(/đ/g, "d")
    .replace(/Đ/g, "d")
    .toLocaleLowerCase("vi")
    .trim();
}

/** Dòng có khớp từ khoá không (không dấu, không phân biệt hoa thường). Từ khoá rỗng khớp mọi dòng. */
export function matchesQuery(q: string, ...fields: Array<string | null | undefined>): boolean {
  const needle = fold(q);
  if (!needle) return true;
  return fields.some((f) => f != null && fold(f).includes(needle));
}

/** "2025-07-01" → "01/07/2025". Không đúng dạng thì trả nguyên chuỗi; rỗng thì "". */
export function formatIsoDate(iso: string | null | undefined): string {
  if (!iso) return "";
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso);
  return m ? `${m[3]}/${m[2]}/${m[1]}` : iso;
}

/** Ngày hôm nay theo giờ Việt Nam, dạng YYYY-MM-DD (cùng quy ước `today_vn` của backend). */
export function todayVn(now: Date = new Date()): string {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: "Asia/Ho_Chi_Minh",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(now);
}

/** Chỉ nhận ngày thật dạng YYYY-MM-DD; sai thì null (không ném lỗi). */
export function parseIsoDate(raw: string | null | undefined): string | null {
  if (!raw) return null;
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(raw);
  if (!m) return null;
  const [y, mo, d] = [Number(m[1]), Number(m[2]), Number(m[3])];
  const date = new Date(Date.UTC(y, mo - 1, d));
  const ok =
    date.getUTCFullYear() === y && date.getUTCMonth() === mo - 1 && date.getUTCDate() === d;
  return ok ? raw : null;
}

/** Cộng/trừ ngày trên chuỗi YYYY-MM-DD. */
export function addDays(iso: string, days: number): string {
  const [y = 0, m = 1, d = 1] = iso.split("-").map(Number);
  const date = new Date(Date.UTC(y, m - 1, d + days));
  return date.toISOString().slice(0, 10);
}
