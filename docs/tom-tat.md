# Tóm tắt – Hệ thống Quế Văn Yên

Nguồn: [lo-trinh-chuyen-doi-so.md](lo-trinh-chuyen-doi-so.md) (19/11/2026) và [thiet-ke-chi-tiet.md](thiet-ke-chi-tiet.md) (20/11/2026). Hai bản markdown chuyển tự động từ docx; phần sản xuất trong thiết kế đã sửa ngày 21/11/2026 theo sổ tay sản xuất bản 2 (17/11/2026), tóm tắt và lộ trình sửa theo.

## Mục tiêu
Thương hiệu thành phẩm quế Văn Yên (tinh dầu, túi thơm, sau này trà, bột) có **QR đến từng chai/túi**, quét ra đồi quế, hộ trồng, ngày sản xuất. Nền móng là số hóa thu mua và kho thay sổ tay/Zalo. Đội Qwork tự làm, cho một doanh nghiệp (không làm nền tảng đa DN).

## Module / chức năng (thiết kế chi tiết, GĐ1–3)
- **Danh mục (phân hệ 1):** địa bàn, loại hàng, nguyên liệu và hạng, bảng giá theo ngày, người bán và đồi quế, khách hàng, sản phẩm (kèm nội dung SEO), chứng nhận, tài khoản.
- **Nhập/xuất hàng (phân hệ 4):** phiếu nhập (4 thao tác: người bán, loại, hạng, số cân), xuất quế khô theo hạng và cân, xuất thành phẩm bằng quét serial, quà tặng kèm đơn, quản lý đơn, tồn kho và kiểm kê, thông tin người mua (che tên và số điện thoại).
- **Truy xuất (phân hệ 2):** vùng nguyên liệu (bản đồ), lệnh sản xuất theo công thức, cuộn tem và gán tem theo đoạn đầu–cuối, thu hồi lô (cả theo lô phụ liệu hoặc lô quế), tra cứu hai chiều, báo cáo hiệu suất, lưu mẫu và thử lưu hương.
  - **Công thức và kho phụ liệu:** danh mục công thức cân theo gram (QC1/QC2, RQ1/RQ2, TQ1/TQ2, hương nền TT1/TT2, dung dịch tẩm, sáp thơm, viên thạch cao, túi vỏ quế), có phiên bản, thành phần lồng nhau. Kho phụ liệu theo gram (cam ngọt, tuyết tùng, hoắc hương, hồi, DPG, sáp đậu nành, sáp ong, thạch cao…, cả bán thành phẩm tự làm như dầu quế đã ủ, hương nền, dung dịch tẩm); mỗi lần xuất cho lệnh ghi gram thực tế và trừ tồn lô.
  - **Lệnh sản xuất 4 bước:** chọn công thức và cỡ mẻ → đưa nguyên liệu vào (lô quế cả lô theo kg, lô phụ liệu theo gram) → **ủ** (trạng thái CURING, chưa đủ ngày thì không hoàn thành được; theo sổ tay: 21 hoặc 28 ngày cho tinh dầu khuếch tán, dầu quế 4–6 tuần…) → nhập đầu ra là lô thành phẩm hoặc lô bán thành phẩm. Lệnh không có công thức (trà, ống quế) vẫn chạy như cũ.
  - **Lưu mẫu và thử lưu hương:** lưu 1 chai mỗi lô trong 12 tháng (áp cho 6 công thức tinh dầu khuếch tán); đợt thử lưu hương 28 ngày cho sáp thơm, viên thạch cao, túi vỏ quế, máy tự chấm PASS/FAIL theo 4 tiêu chí; thời gian lưu hương chỉ in lên bao bì khi đã đo thật.
- **Website + trang truy xuất (phân hệ 3):** trang sản phẩm chuẩn SEO (JSON-LD, sitemap, feed Merchant Center), trang `/q/<serial>`, GA4/Ads.
- Có thêm: 2 vai trò (OWNER, WORKSHOP) và PUBLIC, danh sách API, quy tắc BR-01..31, kịch bản nghiệm thu AC-01..38 (đã gồm phần sản xuất theo sổ tay ở mục 5, 9, 10, 12, 13); số cuối cùng lấy theo thiết kế chi tiết.

## Đối tượng dữ liệu chính
Hai nhánh đi vào lệnh sản xuất:
- **Quế:** người bán (supplier) → đồi (plot) → phiếu nhập (receipt) → **lô nguyên liệu** (material_lot, cả lô, kg).
- **Phụ liệu:** nơi bán → phiếu nhập phụ liệu (ingredient_receipt) → **lô phụ liệu** (ingredient_lot, theo gram, trừ dần). Lô phụ liệu cũng có thể là đầu ra của một lệnh khác (bán thành phẩm tự làm), nên truy xuất đi đệ quy nhiều tầng.

Cả hai → lệnh sản xuất (production_order, dùng công thức recipe/recipe_item, dòng xuất phụ liệu production_ingredient) → **lô thành phẩm** (product_lot) → **serial** (thuộc cuộn tem) → phiếu xuất (issue) → người mua (buyer). Mỗi nhánh truy xuất kết thúc ở lô quế (rồi người bán, đồi) hoặc ở phiếu nhập phụ liệu (nơi bán). Bảng mới cho sản xuất: ingredient, ingredient_receipt, ingredient_lot, recipe, recipe_item, production_ingredient, retained_sample, scent_trial, scent_trial_sample, scent_trial_reading, scent_trial_score; tổng 29 bảng nghiệp vụ (18 cũ + 11 mới). Danh mục: area, material, grade, price, product, certificate, customer. Hệ thống: app_user, audit_log, scan_event, code_counter, setting. Luồng nguồn hàng CONTROLLED/GENERAL: lô quế GENERAL bị chặn khỏi sản xuất (lô phụ liệu không có luồng).

**Mẫu mã lô (chốt theo sổ tay, lý do ở BR-20 của thiết kế chi tiết):** lô thành phẩm `<mã công thức>-YYMMDD-NN` (ví dụ QC1-261117-01; thay mẫu cũ TP-<SKU>-YYMM-NN; lệnh không có công thức dùng `<SKU>-YYMMDD-NN`, theo BR-20), lô phụ liệu và bán thành phẩm `<mã phụ liệu>-YYMM-NN` (ví dụ Q-2611-01). Mã mẻ sinh ngay lúc bắt đầu ủ để dán lên lọ ủ. Mã lô phụ liệu và nơi bán phụ liệu chỉ dùng nội bộ (OWNER; nơi bán ẩn với WORKSHOP), không ra API hay trang công khai.

## Stack
Chưa chốt: "theo stack đội Qwork đang dùng". Giả định trong tài liệu: web app, API REST/JSON, PostgreSQL, một VPS; website render phía máy chủ; Leaflet + OpenStreetMap. **Không nêu ngôn ngữ/framework.**

## Giai đoạn (12/2026 – 6/2028, ~11,5 người-tháng theo lộ trình gốc; ước lại ~12,5 sau khi thêm sản xuất theo sổ tay; GĐ2 4,5 là ước đã duyệt, đầu GĐ2 lập WBS rồi chỉnh)
| GĐ | Thời gian | Nội dung |
| --- | --- | --- |
| 0 | 12/2026–1/2027 | Chuẩn hóa mã, BRD/ERD/WBS, bắt đầu hồ sơ ATTP |
| 1 | 2–5/2027 | Danh mục + nhập hàng, tồn kho, công nợ, xuất quế khô |
| 2 | 5–9/2027 | Sản xuất theo công thức (kho phụ liệu, ủ, lưu mẫu, thử lưu hương) + truy xuất + QR serial. Khối lượng tăng, xem rủi ro trong lộ trình |
| 3 | 8–12/2027 | Website SEO, Ads, kênh bán |
| 4 | 1–6/2028 | OCOP, hữu cơ, trà/bột (ngoài phạm vi thiết kế chi tiết) |

## Câu hỏi mở / chỗ mơ hồ
- **Đã chốt 3 điểm sổ tay không ghi, theo ủy quyền của sếp (#799)** (đổi sau không cần sửa cấu trúc dữ liệu):
  1. Dầu quế chưng tại xưởng hay nhận từ gia đình? Đã chốt: hỗ trợ cả hai nguồn (chưng cần công thức CHUNG-QM). Chưng tại xưởng thì QR truy xuất nối được về lô quế; nhận từ ngoài thì chuỗi dừng ở nơi bán dầu và trang công khai không có đồi.
  2. Hạn dùng sáp thơm, viên thạch cao, túi vỏ quế: sổ tay chỉ ghi 18 tháng (tinh dầu khuếch tán) và 24 tháng (dầu quế 100%). Đã chốt: để trống, nhập tay mỗi lô (BR-11).
  3. Lưu mẫu 12 tháng áp cho sản phẩm nào ngoài 6 công thức tinh dầu khuếch tán? Đã chốt: chỉ 6 công thức đó, có cờ bật thêm (BR-29).
- Tài liệu liệt kê 10 câu mở chờ chủ DN (mục 13): khổ tem và máy in, A5 hay giấy nhiệt, **tên miền QR (phải chốt trước khi in tem đầu)**, các ngưỡng cảnh báo, hạn dùng, danh sách sản phẩm/thôn/hộ, hộ nào cho hiện tên, giá vốn có tính bao bì không.
- Lộ trình GĐ1 ghi "phiếu thu mua **trên điện thoại**", nhưng nhập liệu ở máy tính xưởng; lộ trình nói "5 danh mục", thiết kế có 9 màn hình danh mục.
- Quản lý người mua cuối (BR-22..25, AC-20..24) có trong thiết kế nhưng lộ trình không nhắc.
- Chưa rõ nguồn tiền cho phần mềm/thiết bị (8–16 triệu): lộ trình nói tách khỏi vốn 10 triệu.
- Giá vốn thành phẩm hiện chỉ tính tiền quế (BR-10); phụ liệu đã có kho và gram từng lệnh nhưng chưa vào giá vốn, chờ chủ DN quyết (câu mở về bao bì và phụ liệu).
- Chưa có ngôn ngữ/framework, quy trình triển khai, người cụ thể của đội Qwork.

## Bối cảnh từ D:\Sản phẩm quế (chỉ đọc)
Chiến lược 1 năm/5 năm: năm 1 chỉ 3 sản phẩm phi thực phẩm (tinh dầu phối 10 ml, túi thơm vụn quế, hộp quà 290/490/790 nghìn), bán qua TikTok Shop, Shopee, B2B quà Tết; mục tiêu 5 năm: thành phẩm ~30% doanh thu, 15–20 SKU. Vốn thực tế **10 triệu đồng, 1 người làm**: giai đoạn lab ~7,03 triệu (còn 2,97 triệu), giai đoạn 2 tự xoay vòng, doanh thu năm đầu kịch bản cơ sở ~292,8 triệu, lợi nhuận ~132 triệu (chưa tính lương chủ). Lưu ý: chiến lược nói năm 1 chưa làm website bán hàng riêng (chỉ landing page), trong khi lộ trình làm website SEO ở GĐ3.

## Phần không đọc được
- Sơ đồ/hình trong 2 tài liệu (kiến trúc 4 phân hệ, lộ trình, ERD, vòng đời lô và tem): chỉ còn dòng chú thích; ERD cần vẽ lại cho 29 bảng, vòng đời lệnh sản xuất và lô phụ liệu cần vẽ thêm.
- PDF «Công thức sản xuất Tinh dầu & Túi thơm» (sổ tay bản 2): đội đã trích chữ để sửa thiết kế (bản trích docs/_tools/tmp/so-tay.txt, không commit); hình và bảng trong PDF chưa kiểm.
- xlsx và docx chiến lược chỉ lấy chữ/số; công thức Excel và định dạng không kiểm.
