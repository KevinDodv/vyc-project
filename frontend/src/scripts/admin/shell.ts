import { api } from "./api";
import { LOGIN_PATH } from "./next";

/** Nút «Đăng xuất» trong khung trang quản lý. */
for (const button of document.querySelectorAll<HTMLButtonElement>("[data-logout]")) {
  button.addEventListener("click", async () => {
    button.disabled = true;
    try {
      await api.post("/auth/logout");
    } catch {
      // Phiên đã hết hạn thì cũng coi như đã thoát: vẫn về trang đăng nhập.
    }
    window.location.assign(LOGIN_PATH);
  });
}
