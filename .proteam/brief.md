# VYC – Hệ thống Quế Văn Yên

Cơ sở làm thành phẩm từ quế Văn Yên: thu mua, kho, sản xuất, truy xuất QR, website SEO.

Tài liệu: docs/tom-tat.md, docs/thiet-ke-chi-tiet.md (TK), docs/lo-trinh-chuyen-doi-so.md. Kiến trúc: docs/kien-truc/. Mockup đã duyệt: docs/mockup/ (không sửa), nhận xét cụm A: docs/mockup/nhan-xet/a-nhap-xuat-kho.md. Tham khảo chỉ đọc: D:\Sản phẩm quế.

Stack: backend/ (Django 5 + Ninja, uv, pytest, ruff, mypy, import-linter), frontend/ (Astro SSR, Tailwind + daisyUI, pnpm, biome, vitest, Playwright), deploy/. App: core ← accounts ← catalog ← operations ← website.

Hiện trạng: PH1 Danh mục xong. Đợt 2 (topic này): GĐ1 nhập quế (TK 6.2, AC-01..05), xuất quế khô (6.3, AC-06), tồn kho NL + kiểm kê (6.5, AC-07) trong operations (models/receiving.py, sales.py), màn dưới /quan-ly. Phụ liệu, thành phẩm, lệnh SX: GĐ2.

Quy ước: make check xanh trước review; chỉ task gom sinh lại openapi/*.json và lib/api/*.d.ts; mỗi app mỗi lúc một task thêm migration; config/api.py, core/, menu.ts mỗi lúc một task giữ; không pnpm install trong task có scope. Test BR đặt tên theo mã BR. In: Astro dựng HTML + QR, API print trả JSON. Số: phẩy/chấm đơn là thập phân, hiển thị 1.180,5. Tài liệu tiếng Việt. Không sửa docx/pdf/xlsx gốc. docs/_tools/tmp/ không commit. Đội không push.
