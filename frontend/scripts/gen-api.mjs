// Sinh kiểu TS từ backend/openapi/*.json bằng openapi-typescript (frontend-seo.md 5.4).
// Mỗi file OpenAPI có thật thì sinh một file .d.ts; file nào backend chưa xuất thì bỏ qua và báo.
// Không có file nào thì thoát mã 1 để CI không lặng lẽ qua mặt.
import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const targets = [
  { spec: "../backend/openapi/public.json", out: "src/lib/api/public.d.ts" },
  { spec: "../backend/openapi/v1.json", out: "src/lib/api/v1.d.ts" },
];

let generated = 0;
for (const { spec, out } of targets) {
  const specPath = resolve(root, spec);
  if (!existsSync(specPath)) {
    console.warn(`Bỏ qua ${spec}: backend chưa xuất file này.`);
    continue;
  }
  const bin = resolve(root, "node_modules/openapi-typescript/bin/cli.js");
  const run = spawnSync(process.execPath, [bin, specPath, "-o", resolve(root, out)], {
    stdio: "inherit",
  });
  if (run.status !== 0) process.exit(run.status ?? 1);
  generated += 1;
}

if (generated === 0) {
  console.error("Không có file OpenAPI nào trong backend/openapi/.");
  process.exit(1);
}
