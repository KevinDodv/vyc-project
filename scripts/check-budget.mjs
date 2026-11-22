#!/usr/bin/env node
// Ngân sách dung lượng đọc tĩnh sau `pnpm build` (docs/kien-truc/van-hanh.md 9.1, frontend-seo.md 8.2).
// Chỉ kiểm những gì đọc được từ frontend/dist; CSS < 15 KB và byte đã nén đo ở job `lighthouse`.
//   1. dist/client/_astro không có runtime framework; HTML prerender không có astro-island.
//   2. Không có fonts.googleapis.com / fonts.gstatic.com trong dist.
//   3. Tổng .woff2 mà CSS công khai tham chiếu <= 50 KB.
// Dùng: node scripts/check-budget.mjs [thư-mục-dist]   (mặc định frontend/dist)
import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { basename, dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const dist = resolve(process.argv[2] ?? join(root, "frontend", "dist"));
const FONT_BUDGET = 50 * 1024;
const FRAMEWORK = /(?:^|[^a-z])(preact|react|vue|svelte|solid)(?:[^a-z]|$)/i;
const TEXT_EXT = /\.(?:css|js|mjs|cjs|html|json|txt|xml|svg)$/i;

if (!existsSync(dist)) {
  console.error(`Không thấy ${dist}. Chạy "pnpm build" trước.`);
  process.exit(2);
}

function* walk(dir) {
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const path = join(dir, entry.name);
    if (entry.isDirectory()) yield* walk(path);
    else yield path;
  }
}

const rel = (path) => path.slice(dist.length + 1).replaceAll("\\", "/");
const errors = [];
const files = [...walk(dist)];

// 1. Framework trong bundle client và astro-island trong HTML.
const clientAstro = join(dist, "client", "_astro");
if (existsSync(clientAstro)) {
  for (const file of readdirSync(clientAstro)) {
    if (FRAMEWORK.test(file)) errors.push(`bundle có tên giống framework: client/_astro/${file}`);
  }
}
for (const file of files) {
  if (file.endsWith(".html") && readFileSync(file, "utf8").includes("astro-island")) {
    errors.push(`HTML có astro-island (hydrate framework): ${rel(file)}`);
  }
}

// 2. Không gọi Google Fonts.
for (const file of files) {
  if (!TEXT_EXT.test(file)) continue;
  const text = readFileSync(file, "utf8");
  for (const host of ["fonts.googleapis.com", "fonts.gstatic.com"]) {
    if (text.includes(host)) errors.push(`${rel(file)} tham chiếu ${host}`);
  }
}

// 3. Font woff2 mà CSS công khai (mọi CSS không phải của Admin) tham chiếu.
const fonts = new Map();
if (existsSync(clientAstro)) {
  for (const file of readdirSync(clientAstro)) {
    if (!file.endsWith(".css") || file.startsWith("Admin")) continue;
    const css = readFileSync(join(clientAstro, file), "utf8");
    for (const match of css.matchAll(/url\(\s*["']?([^"')]+\.woff2)["']?\s*\)/g)) {
      const target = join(clientAstro, basename(match[1]));
      if (existsSync(target)) fonts.set(target, statSync(target).size);
    }
  }
}
const fontTotal = [...fonts.values()].reduce((sum, size) => sum + size, 0);
if (fontTotal > FONT_BUDGET) {
  errors.push(`font woff2 công khai ${fontTotal} B vượt ngưỡng ${FONT_BUDGET} B`);
}

console.log(`Đã quét ${files.length} file trong ${dist}; font công khai ${fontTotal} B / ${FONT_BUDGET} B.`);
if (errors.length > 0) {
  for (const message of errors) console.error(`✗ ${message}`);
  process.exit(1);
}
console.log("Ngân sách tĩnh: đạt.");
