import { fileURLToPath } from "node:url";
import { defineConfig } from "vitest/config";

export default defineConfig({
  resolve: {
    alias: {
      // Module ảo của Astro không có trong vitest: thay bằng giá trị cố định cho test.
      "astro:env/server": fileURLToPath(
        new URL("./tests/stubs/astro-env-server.ts", import.meta.url),
      ),
    },
  },
  test: {
    include: ["src/**/*.test.ts", "tests/**/*.test.ts"],
  },
});
