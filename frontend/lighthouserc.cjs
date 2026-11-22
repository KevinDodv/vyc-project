// Lighthouse CI chạy trên stack compose.ci.yml qua Caddy (byte đã nén). Ngưỡng: frontend-seo.md 8.1, 8.2.
// Mọi assertion lấy TRUNG VỊ 3 lần chạy: mặc định LHCI lấy lần tốt nhất ("optimistic"), trái với chỉ tiêu.
// Chạy: pnpm dlx @lhci/cli@0.16.1 autorun --config=lighthouserc.cjs (job `lighthouse` trong ci.yml).
const err = (options) => ["error", { ...options, aggregationMethod: "median" }];

const BASE = process.env.LHCI_BASE_URL ?? "http://localhost";

module.exports = {
  ci: {
    collect: {
      url: [
        `${BASE}/`,
        `${BASE}/san-pham/tinh-dau-que-van-yen-10ml`,
        // Thêm khi có trang: /san-pham, /chinh-sach-bao-mat (khung chưa có).
        // GĐ2: thêm `${BASE}/q/<serial seed>` cùng seed serial ISSUED (khung chưa đo /q/).
      ],
      numberOfRuns: 3,
      // Runner CI chạy Chrome trong container không đặc quyền.
      settings: { chromeFlags: "--no-sandbox --headless=new" },
    },
    assert: {
      assertMatrix: [
        {
          matchingUrlPattern: ".*",
          assertions: {
            "categories:performance": err({ minScore: 0.95 }),
            "categories:accessibility": err({ minScore: 0.95 }),
            "categories:best-practices": err({ minScore: 0.95 }),
            "largest-contentful-paint": err({ maxNumericValue: 2500 }),
            "cumulative-layout-shift": err({ maxNumericValue: 0.1 }),
            "total-blocking-time": err({ maxNumericValue: 200 }),
            "resource-summary:stylesheet:size": err({ maxNumericValue: 15360 }),
            "resource-summary:script:size": err({ maxNumericValue: 3072 }),
            "resource-summary:third-party:count": err({ maxNumericValue: 0 }),
          },
        },
        {
          // /q/ có noindex nên không đòi SEO = 100.
          matchingUrlPattern: "^(?!.*/q/).*$",
          assertions: { "categories:seo": err({ minScore: 1 }) },
        },
        {
          matchingUrlPattern: ".*/san-pham/[^/]+$",
          assertions: {
            "resource-summary:total:size": err({ maxNumericValue: 204800 }),
            "resource-summary:font:size": err({ maxNumericValue: 51200 }),
            "resource-summary:image:size": err({ maxNumericValue: 122880 }),
            "resource-summary:document:size": err({ maxNumericValue: 30720 }),
          },
        },
        {
          // Chưa khớp URL nào tới GĐ2.
          matchingUrlPattern: ".*/q/.*",
          assertions: { "resource-summary:total:size": err({ maxNumericValue: 307200 }) },
        },
        {
          matchingUrlPattern: "^https?://[^/]+/$",
          assertions: { "resource-summary:total:size": err({ maxNumericValue: 256000 }) },
        },
      ],
    },
    upload: { target: "filesystem", outputDir: ".lighthouseci" },
  },
};
