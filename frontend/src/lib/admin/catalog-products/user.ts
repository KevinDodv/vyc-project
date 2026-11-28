/** Logic thuần của màn /quan-ly/tai-khoan (TK mục 5, dòng Tài khoản). */

import { ROLE_LABEL } from "../menu";

export const PASSWORD_MIN_LENGTH = 8;

export const ROLE_OPTIONS = [
  { value: "OWNER", label: "Chủ DN (OWNER)" },
  { value: "WORKSHOP", label: "Xưởng (WORKSHOP)" },
] as const;

export function roleLabel(role: string): string {
  return role === "OWNER" || role === "WORKSHOP" ? ROLE_LABEL[role] : role;
}

/** Không tự ngừng dùng chính mình (TK mục 5). Backend cũng chặn (409 CANNOT_DEACTIVATE_SELF); màn ẩn nút để khỏi bấm nhầm. */
export function isSelf(currentUserId: number | undefined, targetId: number): boolean {
  return currentUserId !== undefined && currentUserId === targetId;
}

/** «Ngừng dùng» chỉ hiện cho tài khoản khác. «Dùng lại» luôn hiện (tài khoản đang ngừng không thể là chính mình). */
export function canToggleStatus(
  currentUserId: number | undefined,
  target: { id: number; status: string },
): boolean {
  return target.status !== "ACTIVE" || !isSelf(currentUserId, target.id);
}

/** Lần đăng nhập cuối theo giờ Việt Nam, dạng 22/11/2026 09:30; chưa từng đăng nhập thì «Chưa đăng nhập». */
export function formatLastLogin(value: string | null | undefined): string {
  if (!value) return "Chưa đăng nhập";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  const parts = new Intl.DateTimeFormat("en-GB", {
    timeZone: "Asia/Ho_Chi_Minh",
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    hourCycle: "h23",
  }).formatToParts(date);
  const get = (type: string) => parts.find((p) => p.type === type)?.value ?? "";
  return `${get("day")}/${get("month")}/${get("year")} ${get("hour")}:${get("minute")}`;
}
