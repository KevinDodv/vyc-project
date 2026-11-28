import { defineConfig, devices } from "@playwright/test";

// Cấu hình riêng cho frontend/e2e (playwright.config.ts gốc chỉ nhìn tests/e2e).
// Chạy: cd frontend && npx playwright test -c e2e/playwright.config.ts
// Cần stack đã dựng sẵn như tests/e2e/sample-flow.spec.ts (E2E_BASE_URL, tài khoản OWNER).
export default defineConfig({
  testDir: ".",
  testMatch: "**/*.spec.ts",
  fullyParallel: false,
  workers: 1,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? [["list"], ["html", { open: "never" }]] : "list",
  outputDir: "../test-results",
  use: {
    baseURL: process.env.E2E_BASE_URL ?? "http://localhost:4321",
    trace: "retain-on-failure",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
});
