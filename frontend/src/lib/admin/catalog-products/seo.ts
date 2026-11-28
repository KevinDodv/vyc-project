/** Bộ đếm ký tự SEO (TK mục 5, dòng Sản phẩm): tiêu đề ≤ 60 (cứng 70), mô tả ≤ 160 (cứng 170).
 *  «Khuyến nghị» chỉ cảnh báo; «cứng» là giới hạn cột DB và API, vượt thì không cho lưu. */

export type SeoLimit = { soft: number; hard: number };

export const SEO_TITLE_LIMIT: SeoLimit = { soft: 60, hard: 70 };
export const SEO_DESCRIPTION_LIMIT: SeoLimit = { soft: 160, hard: 170 };

export type SeoLevel = "ok" | "warn" | "over";

export type SeoCount = {
  length: number;
  level: SeoLevel;
  /** Dòng chữ hiện cạnh ô nhập, ví dụ «62/60 (tối đa 70)». */
  label: string;
  /** Giải thích khi không «ok»; rỗng khi ổn. */
  message: string;
};

/** Độ dài theo ký tự Unicode (cùng cách đếm `max_length` của backend), tính trên chữ đã bỏ khoảng trắng hai đầu
 *  vì form gửi đi bản đã cắt. Không dùng `.length` nên emoji và chữ có dấu tổ hợp không bị đếm hai lần dấu phụ. */
export function seoLength(text: string): number {
  return Array.from(text.trim()).length;
}

export function seoCount(text: string, limit: SeoLimit): SeoCount {
  const length = seoLength(text);
  const label = `${length}/${limit.soft} (tối đa ${limit.hard})`;
  if (length > limit.hard) {
    return {
      length,
      level: "over",
      label,
      message: `Quá giới hạn ${limit.hard} ký tự, bớt ${length - limit.hard} ký tự mới lưu được`,
    };
  }
  if (length > limit.soft) {
    return {
      length,
      level: "warn",
      label,
      message: `Dài hơn khuyến nghị ${limit.soft} ký tự, Google có thể cắt bớt khi hiển thị`,
    };
  }
  return { length, level: "ok", label, message: "" };
}
