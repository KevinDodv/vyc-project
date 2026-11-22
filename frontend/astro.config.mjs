import node from "@astrojs/node";
import tailwindcss from "@tailwindcss/vite";
import { defineConfig, envField } from "astro/config";

// Biến môi trường đọc LÚC CHẠY (không PUBLIC_): một image dùng cho cả staging và prod.
// Phải là access "secret": Astro nhúng cứng biến "public" vào bundle lúc build (đã thử: bỏ qua process.env).
// Xem docs/kien-truc/frontend-seo.md mục 5.1.
export default defineConfig({
  output: "server",
  adapter: node({ mode: "standalone" }),
  server: { port: 4321 },
  env: {
    schema: {
      API_INTERNAL_URL: envField.string({
        context: "server",
        access: "secret",
        default: "http://localhost:8000",
      }),
      SITE_URL: envField.string({
        context: "server",
        access: "secret",
        default: "http://localhost:4321",
      }),
      GTM_ID: envField.string({
        context: "server",
        access: "secret",
        default: "",
      }),
    },
  },
  vite: {
    plugins: [tailwindcss()],
    // Chỉ dev: trình duyệt gọi /api và /media cùng origin; production do Caddy chuyển.
    server: {
      proxy: {
        "/api": "http://localhost:8000",
        "/media": "http://localhost:8000",
      },
    },
  },
});
