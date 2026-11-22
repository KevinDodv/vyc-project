import { defineConfig, devices } from "@playwright/test";

// Test đầu cuối chạy trên stack đã dựng sẵn (compose dev hoặc compose.ci.yml), không tự bật server:
// frontend ở E2E_BASE_URL, API cùng origin qua proxy (Caddy hoặc proxy của astro dev).
// Tài khoản OWNER có sẵn trong DB (make seed hoặc manage.py create_owner); xem tests/e2e/sample-flow.spec.ts.
export default defineConfig({
  testDir: "./tests/e2e",
  testMatch: "**/*.spec.ts",
  fullyParallel: false,
  workers: 1,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? [["list"], ["html", { open: "never" }]] : "list",
  outputDir: "test-results",
  use: {
    baseURL: process.env.E2E_BASE_URL ?? "http://localhost:4321",
    trace: "retain-on-failure",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
});
