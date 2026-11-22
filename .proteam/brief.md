# VYC – Hệ thống Quế Văn Yên

Hệ thống cho cơ sở làm thành phẩm từ quế Văn Yên (tinh dầu, túi thơm): thu mua và kho, sản xuất, truy xuất QR tới từng chai/túi, website SEO. Một doanh nghiệp.

Tài liệu: docs/tom-tat.md (đọc trước), docs/thiet-ke-chi-tiet.md, docs/lo-trinh-chuyen-doi-so.md. Kiến trúc: docs/kien-truc/ (README, backend.md, frontend-seo.md, van-hanh.md), coi là đã duyệt theo ủy quyền của sếp (#798). Mockup đã duyệt: docs/mockup/ (không sửa).

Tham khảo chỉ đọc: D:\Sản phẩm quế.

Stack: monorepo backend/ (Django >= 5.1 + Django Ninja, uv, pytest-django, ruff, mypy, import-linter), frontend/ (Astro SSR adapter Node, Tailwind + daisyUI, pnpm, biome, vitest, Playwright), deploy/ (docker compose, Caddy, Postgres 16), 1 VPS trong nước 2 vCPU/4 GB. App Django: core ← accounts ← catalog ← operations ← website. Trang công khai không có JS framework.

Hiện trạng: đang dựng khung code (luồng mẫu đăng nhập → sản phẩm → /san-pham/<slug>). Git nhánh main, sếp tự push lên GitHub KevinDodv/vyc-project; đội không push.

Quy ước: README kiến trúc mục 3; `make check` xanh trước khi review; không sửa tay openapi/*.json và lib/api/*.d.ts. Tài liệu tiếng Việt. Không sửa docx/pdf/xlsx gốc. docs/_tools/tmp/ không commit.
