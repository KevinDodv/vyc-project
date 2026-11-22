import type { components } from "./api/public";

type Channel = components["schemas"]["BuyLink"]["channel"];

const LABELS: Record<Channel, string> = {
  shopee: "Shopee",
  tiktok: "TikTok Shop",
  zalo: "Zalo",
  other: "cửa hàng",
};

export function buyLinkLabel(channel: Channel): string {
  return LABELS[channel];
}

/** Gắn utm_source=website vào link sàn (TK 8.3), làm ở server lúc render nên không cần JS.
 *  URL hỏng thì trả nguyên chuỗi (backend đã chỉ cho http/https lọt ra). */
export function withUtm(url: string): string {
  try {
    const u = new URL(url);
    if (!u.searchParams.has("utm_source")) u.searchParams.set("utm_source", "website");
    return u.toString();
  } catch {
    return url;
  }
}
