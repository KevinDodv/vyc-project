import { ApiRequestError, api, refreshCsrf } from "./api";
import { ADMIN_HOME, sanitizeNext } from "./next";

const form = document.querySelector<HTMLFormElement>("#login-form");
const errorBox = document.querySelector<HTMLElement>("#login-error");

function showError(message: string): void {
  if (!errorBox) return;
  errorBox.textContent = message;
  errorBox.hidden = false;
}

if (form) {
  const submit = form.querySelector<HTMLButtonElement>("button[type=submit]");
  // Lấy cookie csrftoken ngay khi mở trang; lỗi ở đây thì lúc gửi form api.ts sẽ thử lại.
  refreshCsrf().catch(() => undefined);

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (errorBox) errorBox.hidden = true;
    const data = new FormData(form);
    const username = String(data.get("username") ?? "").trim();
    const password = String(data.get("password") ?? "");
    if (!username || !password) {
      showError("Nhập tên đăng nhập và mật khẩu");
      return;
    }
    if (submit) submit.disabled = true;
    try {
      await api.post("/auth/login", { username, password });
      const next = sanitizeNext(new URLSearchParams(window.location.search).get("next"));
      window.location.assign(next ?? ADMIN_HOME);
    } catch (error) {
      showError(
        error instanceof ApiRequestError
          ? error.message
          : "Không kết nối được máy chủ, bạn thử lại sau ít phút",
      );
      if (submit) submit.disabled = false;
    }
  });
}
