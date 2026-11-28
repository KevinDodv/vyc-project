/** Tính % khối lượng, mẻ chuẩn và lượng cân theo batch_g cho màn công thức (BR-26; backend `services/recipes.py`).
 *  Gram là số thập phân 2 chữ số (numeric(10,2) ở DB) nên tính trên số nguyên «phần trăm gram» (centigram),
 *  không dùng số thực: cùng kết quả với `Decimal` + `ROUND_HALF_UP` của backend. */

/** Tối đa của cột numeric(10,2), tính bằng gram. */
export const MAX_GRAM_CENTI = 9_999_999_999;

export type RecipeLine = {
  /** Gram đã đọc thành centigram (1,25 g = 125); null khi ô trống hoặc sai. */
  centi: number | null;
  /** Số nhóm lựa chọn: các dòng cùng số là phương án thay nhau; null là dòng bắt buộc. */
  altGroup: number | null;
};

/** Đọc ô gram: chấp nhận "12", "12.5", "12,5", tối đa 2 chữ số lẻ, lớn hơn 0. Sai thì null. */
export function parseGram(text: string): number | null {
  const match = /^(\d{1,8})(?:[.,](\d{1,2}))?$/.exec(text.trim());
  if (!match) return null;
  const whole = match[1] ?? "0";
  const frac = (match[2] ?? "").padEnd(2, "0");
  const centi = Number(whole) * 100 + Number(frac || "0");
  return centi > 0 && centi <= MAX_GRAM_CENTI ? centi : null;
}

/** Centigram → chuỗi hai số lẻ, dấu chấm ("1250" → "12.50"), đúng dạng API trả và nhận. */
export function formatGram(centi: number): string {
  const sign = centi < 0 ? "-" : "";
  const abs = Math.abs(Math.round(centi));
  return `${sign}${Math.floor(abs / 100)}.${String(abs % 100).padStart(2, "0")}`;
}

/** Hiện cho người dùng Việt: dấu phẩy thập phân, bỏ ",00" thừa. "12.50" → "12,5". */
export function displayGram(centi: number): string {
  const text = formatGram(centi).replace(/\.?0+$/, "");
  return text.replace(".", ",");
}

/** a / b làm tròn nửa lên (số dương). */
function divRoundHalfUp(a: number, b: number): number {
  return Math.floor((2 * a + b) / (2 * b));
}

/** Mẻ chuẩn = Σ gram các dòng bắt buộc + mỗi nhóm lựa chọn lấy phương án nặng nhất (BR-26c).
 *  Dòng chưa nhập gram thì chưa tính. Trả centigram. */
export function computeBaseBatch(lines: readonly RecipeLine[]): number {
  let total = 0;
  const groups = new Map<number, number>();
  for (const line of lines) {
    if (line.centi === null) continue;
    if (line.altGroup === null) total += line.centi;
    else groups.set(line.altGroup, Math.max(groups.get(line.altGroup) ?? 0, line.centi));
  }
  for (const value of groups.values()) total += value;
  return total;
}

/** % khối lượng của một dòng trên mẻ chuẩn, 2 số lẻ, tính theo phần vạn (1% = 100). null khi chưa tính được. */
export function itemPctBasis(centi: number | null, baseCenti: number): number | null {
  if (centi === null || baseCenti <= 0) return null;
  return divRoundHalfUp(centi * 10_000, baseCenti);
}

/** "12.34" từ phần vạn (1234). */
export function formatPct(basis: number): string {
  return formatGram(basis);
}

/** Hiện cho người dùng: "33,33 %". */
export function displayPct(basis: number | null): string {
  return basis === null ? "–" : `${formatGram(basis).replace(".", ",")} %`;
}

/** Lượng cân gợi ý của một dòng khi làm mẻ `batchCenti` (BR-26f): gram * batch / mẻ chuẩn, làm tròn 2 số lẻ. */
export function scaleLine(centi: number, batchCenti: number, baseCenti: number): number | null {
  if (baseCenti <= 0) return null;
  // centi * batchCenti có thể tới ~1e20: vượt số nguyên an toàn, dùng BigInt.
  const num = BigInt(centi) * BigInt(batchCenti);
  const den = BigInt(baseCenti);
  return Number((2n * num + den) / (2n * den));
}

/** Nhãn nhóm lựa chọn: 1 → "Nhóm 1". Không ghi «TT1», «TT2»: đó là mã hai phụ liệu cùng nằm trong một nhóm. */
export function altGroupLabel(group: number): string {
  return `Nhóm ${group}`;
}
