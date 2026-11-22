# Thay đổi cụm B (sản xuất): task #25

Người làm: Nhung (designer) · 21/11/2026. Sửa 7 màn cũ và thêm 9 màn mới trong `de-xuat/man/b-san-xuat/`. Không đụng `app.css`, `goc/`, `nhan-xet*`, `vo.html`, cụm A và C. CSS: dùng `app.css`; chỗ cần thêm class (`annot`, `chip`, `rowwarn`, `rowerr`, `dim`, `two`, `dot`) thì đặt `<style>` trong từng màn.

Mã vấn đề B-nn theo `docs/mockup/nhan-xet.md`. Căn cứ nghiệp vụ theo TK mục 4, 6.5a, 7.2–7.5 và sổ tay (ST).

## 1. Thứ tự màn trong menu

Màn mới chèn bằng `sau` trong `_ds.json`; `ghep` cho 56 màn, key không trùng.

| Nhóm | Thứ tự |
|---|---|
| Xưởng | … `receipt-list` → **`ingr-receipt`** → … `inv-kk` → **`ingr-stock`** → `prod-list` → `prod-order` → **`cure-list`** → **`cure-detail`** → `prod-done` → `labels` |
| Chủ DN | … `products` → **`recipe-list`** → **`recipe-edit`** → `prod-owner` → `rolls` → `plots-lots` → **`lot-detail`** → **`retain-list`** → **`scent-trial`** → `trace` … |

## 2. Từng vấn đề B-nn

| Mã | Xử lý | Ở đâu |
|---|---|---|
| B-01 critical | Dựng lại màn lệnh theo 4 bước TK 7.2: công thức và cỡ mẻ → nguyên liệu theo gram → ủ → nhập kết quả. Ví dụ là lệnh túi thơm TUI (mẻ 40 túi, 1.100 g). Bước «chọn loại sau sàng» bỏ, có dòng giải thích | `16-prod-order` |
| B-02 | Form tạo lệnh: «Làm gì» (sản phẩm / bán thành phẩm), công thức (bản đang dùng), nhóm TT1/TT2 (ví dụ chú thích), cỡ mẻ gram, bảng lượng cân gợi ý (QC2 mẻ 1 lít = 921,70 g) | `24-prod-owner` |
| B-03 | Bảng thành phần: gợi ý (g), ô quét lô, gram thực tế, trạng thái đủ / thiếu / lệch; banner vàng lệch quá ±0,05 g; «+ Thêm dòng ngoài công thức»; nút «Đã pha xong» khóa tới khi đủ dòng. Banner cam chưa COA nằm ở màn nhập phụ liệu và tồn phụ liệu | `16-prod-order`, `06b-ingr-receipt`, `14b-ingr-stock` |
| B-04 | Thêm trạng thái ủ: thẻ «Mẻ đang ủ» ở 15 và 24, danh sách và chi tiết ủ mới, nút «Hoàn thành» chỉ ở chi tiết ủ khi đủ ngày. Bốn mẻ mẫu: QC2 (đủ ngày), DDT 48 giờ, TUI 5 ngày, QC1 21 ngày | `15`, `24`, `16b-cure-list`, `16c-cure-detail` |
| B-05 (=A-01) | Mã lô theo 1.4: `Q100-261120-01/-02`, thêm `QC2-261023-01`, `QC1-261117-01`, `TUI-261120-01`. Mã mẻ sinh khi bắt đầu ủ (nói rõ ở 16); màn 26 có cột «Công thức» và «Ngày pha» | `15`, `16`, `17`, `18`, `24`, `26` |
| B-06 | Bỏ «Mẻ chưng cất» và hiệu suất 1,92%. Màn 17 là mẻ QC2 hoàn thành, hiện gram phụ liệu, số chai, ngày pha, ngày xong ủ; ghi «không dùng quế thô nên không có hiệu suất». Không vẽ lệnh chưng (chờ sếp chốt) | `17` |
| B-07 | Thêm cột «Công thức» và «Lưu mẫu»; dữ liệu theo sổ tay: Q100-10 (24 tháng), TD-QC1-10 và TD-QC2-10 (18 tháng), TT25, SAP-55, VTC-20 hạn «chưa có». Form sửa có «Công thức mặc định», «Đơn vị đếm», «Lưu mẫu mỗi lô» và «Cách dùng và cảnh báo». Trà mờ đi kèm «Giai đoạn 4» (A-17) | `23-products`, `24-prod-owner` |
| B-08 | Màn 17: khối «Chai lưu mẫu» (vị trí, nút Lưu), cảnh báo «Chưa lưu mẫu» không chặn gán tem, «90 chai chưa gồm chai lưu mẫu». Màn 26: cột «Mẫu lưu». Màn mới «Mẫu lưu» + tab «Lô chưa lưu mẫu» | `17`, `26`, `26c-retain-list` |
| B-09 | Danh sách công thức (16 dòng, kể cả QC1 v2 nháp) và form khai QC1 v2: thông tin, thành phần gram, % tự tính, nhóm lựa chọn, tùy chọn; nhân bản thay vì sửa bản đang dùng | `23b-recipe-list`, `23c-recipe-edit` |
| B-10 (=A-02) | Phiếu nhập phụ liệu (tab «Phụ liệu», nút chọn mã, gram, số lô NCC, hạn, COA, tem lô, **không có cột giá**) và tồn phụ liệu (lô, gram, hạn: cam dưới 60 ngày, đỏ quá hạn, chấm vàng chưa COA; dòng xám «Bao bì: chưa quản lý» theo A-03) | `06b-ingr-receipt`, `14b-ingr-stock` |
| B-11 | Danh sách ủ (còn N ngày, nhắc lắc chai) và chi tiết ủ (tick lắc chai, ngửi kiểm tra 4 bước, «Đạt», «Ủ thêm 7 ngày»; chú thích chủ DN bỏ qua kiểm tra ngày ủ phải ghi lý do) | `16b-cure-list`, `16c-cure-detail` |
| B-12 | Cột đổi thành «Giá quế / đơn vị», hiệu suất «—» khi lô chỉ dùng phụ liệu; chú thích dưới bảng. Theo mặc định #3: không tính giá phụ liệu | `26-plots-lots` |
| B-13 | Màn «Chi tiết mẻ» mở từ mã lô QC2: ngày pha, ngày xong ủ, người làm, bảng gram thực tế so với gợi ý theo từng lô phụ liệu, ngửi kiểm tra, mẫu lưu, nút Thu hồi và tra cứu | `26b-lot-detail` |
| B-14 | Màn thử lưu hương: danh sách đợt thử, lưới ngày 0–28 (khối lượng, điểm trung bình), đánh giá 4 tiêu chí PASS/FAIL tự tính, chọn biến thể PASS, số tuần đo thật, ghi chú chỉ in lên bao bì khi PASS | `26d-scent-trial` |
| B-15 | Túi thơm 25 g theo mặc định #4; số mẫu theo công thức TUI (VQH 480, DG 320, HT 200, DDT 100 g). Đơn vị đếm có chai / túi / viên / tấm ở form sản phẩm | `16`, `23` |
| B-16 (=A-17) | Màn 24: TRA100 bị khóa kèm «giai đoạn 4, chờ giấy tờ ATTP»; màn 23 giữ dòng Trà, mờ, ghi giai đoạn | `23`, `24` |
| B-17 | Cùng một lệnh LSX-2611-003 nay là «đã nhập 3/4 thành phần» ở 15, 16 và 24 | `15`, `16`, `24` |
| B-18 | Màn 18: thêm 2 lô, dòng «Chai lưu mẫu không dán tem», mã lô mới. Nhãn thành phẩm in ra không làm ở đây (C-07, cụm C) | `18` |

## 3. Chọn lựa tự quyết (ghi để Lead và sếp biết)

- **QC2-261023-01 là lô «hoàn thành hôm nay» ở màn 17.** Lý do: Q100 không ủ và không bật lưu mẫu (TK seed), nên không minh họa được ủ lẫn lưu mẫu. Lô Q100-261120-01/-02 vẫn giữ ở 15, 18, 26 để khớp cụm A và C. Hệ quả: màn 15 và 16b hiện QC2 «đủ ngày, chờ ngửi kiểm tra», màn 17, 18, 26 đã là sau khi hoàn thành. Chấp nhận như ảnh chụp các thời điểm khác nhau.
- **Số ngày «còn» ở QC1-261117-01 là 18, không phải 6.** Nhận xét B-04 và TK 7.2 ghi câu mẫu «còn 6 ngày» nhưng pha 17/11 + 21 ngày = 08/12, hôm nay 20/11 còn 18 ngày. Mockup dùng 18; câu mẫu của TK chỉ là ví dụ.
- **Giữ nguyên lệnh Q100 và mã lệnh:** LSX-2611-002 (Q100), -003 (túi nháp), thêm LSX-2610-002 (QC2). Các mã lệnh và lô mẫu khác (DDT-261119-01, TUI-261118-01, VQH-2611-01, CAM-2610-01…) do mình đặt theo BR-20, chưa có trong TK.
- **Mẫu lưu có dữ liệu cũ** (QC2-251105-01, QC1-251215-01…) để minh họa «hết hạn» và «dưới 30 ngày» mà vẫn đúng mốc hôm nay 20/11/2026.
- **Thử lưu hương dùng số giả** nhưng tính đúng 4 tiêu chí: 35% đạt cả 4, 25% đạt 2/4, 45% đạt 1/4.
- **Hai màn phụ liệu để trong thư mục `b-san-xuat`** (task #25 ghi gồm kho phụ liệu) nhưng chèn đúng chỗ cụm A bằng `sau: receipt-list` và `sau: inv-kk`. Cụm A đừng tạo trùng key `ingr-receipt`, `ingr-stock`.

## 4. Route mới cho vỏ (`_tools/vo.html`, ngoài vùng của mình)

Đặt các dòng này **trước** các dòng tổng quát cùng đầu đường dẫn trong mảng `map` của `route()`:

| Đường dẫn | Key màn | Đặt trước |
|---|---|---|
| `/^\/nhap-hang\/phu-lieu/` | `ingr_receipt` | `/^\/nhap-hang/` |
| `/^\/ton-kho\/phu-lieu/` | `ingr_stock` | `/^\/ton-kho/` |
| `/^\/san-xuat\/ua\/\d+/` | `cure_detail` | `/^\/san-xuat\/\d+/` |
| `/^\/san-xuat\/ua/` | `cure_list` | `/^\/san-xuat/` |
| `/^\/quan-ly\/cong-thuc\/\w+/` | `recipe_edit` | `/^\/quan-ly/` |
| `/^\/quan-ly\/cong-thuc/` | `recipe_list` | `/^\/quan-ly/` |
| `/^\/quan-ly\/lo-thanh-pham\/.+/` | `lot_detail` | `/^\/quan-ly\/lo-thanh-pham/` |
| `/^\/quan-ly\/mau-luu/` | `retain_list` | `/^\/quan-ly/` |
| `/^\/quan-ly\/thu-luu-huong/` | `scent_trial` | `/^\/quan-ly/` |

`/dong-goi?lot=3` (lô QC2) vẫn về `labels` như `?lot=2`. Cần thêm lối vào từ trang chủ xưởng (02) tới «Mẻ đang ủ», nhập và tồn phụ liệu; từ trang chủ chủ DN (19) tới Công thức, Mẫu lưu, Thử lưu hương.

## 5. Việc cho cụm khác (không làm ở đây)

- Cụm A: màn 02 (nút Mẻ đang ủ, Phụ liệu), tab «Phụ liệu» ở 03 và 12–14; màn 09–11 còn tên «Tinh dầu quế Văn Yên 10 ml», «Túi thơm 50 g», TRA100 (A-17); mã lô `TP-TD10-…` (A-01) cần khớp `Q100-261120-0x`.
- Cụm C: màn 19 thẻ «Mẻ đang ủ», «Lô chưa lưu mẫu», «Mẫu sắp hết hạn lưu»; 27 và 36–38 đổi mã lô và tên sản phẩm; 31 lối vào «Công thức».
- Kiểm cuối: chưa bấm trên trình duyệt qua vỏ (chỉ kiểm tách riêng từng màn bằng Chrome headless và đếm thẻ HTML đóng mở).

## 6. Sau khi sếp duyệt (#429, task #29)

- 23b: «+ Công thức mới» thành link `/quan-ly/cong-thuc/new`; ô QC1 v2 nháp là link `/quan-ly/cong-thuc/qc1-v2`. Cả hai khớp route `recipe_edit` ở vo.html:84.
- 15 và 24: bỏ ô «QC2-261023-01 · đã gán 0/90» khỏi «Lô thành phẩm cần gán tem». QC2 chỉ còn một trạng thái là «đủ ngày ủ, chờ ngửi» (khớp 16b, 16c). Lưu ý: 17, 26, 26b, 26c vẫn là màn sau khi hoàn thành mẻ (ngửi 20/11 đạt) nên là luồng tiếp theo, không phải cùng lúc.
- 26c: bỏ dòng RQ1-260412-02 (sản phẩm không có trong danh mục ở 23, và dòng tự mâu thuẫn nút «Hủy mẫu» với chữ «không hủy mẫu»).
- 26: thêm chú thích «Q100 không ủ nên không có sổ ghi mẻ».
- «50 g»: grep cụm B không còn; túi thơm đều 25 g.
- Sửa lại sau review (Minh #440, Ngan #443): QC2-261023-01 chỉ còn một trạng thái «đã ngửi đạt 20/11, lô đang dùng» (17, 18, 26, 26b, 26c). Mẻ «đủ ngày, chờ ngửi» ở 15, 24, 16b, 16c đổi sang mẻ khác là QC2-261023-02 (LSX-2610-003, cùng ngày pha). Link `/san-xuat/ua/1` giữ nguyên, là route mẫu của vỏ.
