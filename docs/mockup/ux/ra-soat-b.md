# Soát UX cụm B (sản xuất): task #33

Người soát: Tuan · 21/11/2026. Phạm vi: màn 15, 16, 16b, 16c, 17, 18, 23 (+23b, 23c), 24, 26 (+26b, 26c, 26d) trong `docs/mockup/de-xuat/man/b-san-xuat/` (viết tắt «b/»). Chỉ soát và đề xuất, **chưa sửa màn nào**. Phần sửa giao cho @Phuong (#36).

Căn cứ: sếp #460 (người dùng kém CNTT, ít bước nhất), chuẩn chung Lead #461. Chưa có `ux/ra-soat-a.md`, nên dùng chuẩn: vùng chạm ≥48 px, chữ ≥16 px, không viết tắt. `html{font-size:18px}` (`app.css:23`) nên 16 px ≈ 0,89 rem.

Cách đếm: **chạm** = một lần bấm hoặc quét tem; **gõ** = số ô phải gõ chữ/số (chỉ tính ô bắt buộc, ô điền sẵn không tính). TK = `docs/thiet-ke-chi-tiet.md`.

---

## 1. Bảng trước/sau theo việc hằng ngày

| # | Việc | Màn hiện nay | Hiện trạng (màn · chạm · gõ) | Đề xuất (màn · chạm · gõ) | Chỗ khó hiểu hiện nay |
|---|---|---|---|---|---|
| 1 | Bắt đầu mẻ theo công thức (chủ DN) | 24 → 16 | 1 màn · 4 chạm (chọn sản phẩm 2, công thức 0–2, Tạo lệnh 1) · 1 gõ (cỡ mẻ gram) | 1 màn · 3 chạm · 0 gõ | Phải tự đổi «1 lít» ra 921,7 g; tên sản phẩm kèm mã SKU |
| 2 | Ghi nguyên liệu và phụ liệu dùng (4 thành phần) | 16 bước 2 | 1 màn · ~8 chạm (4 quét + 4 chuyển ô) · 4 gõ gram | 1 màn · 4 quét · 4 gõ, chuyển ô tự động, bàn phím số tự bật | «Gợi ý (g)», VQH/DG/HT/DDT, «TARE», «Lệch +0,09 g» |
| 3 | Đưa vào ủ | 16 bước 3 | 1 màn · 1 chạm | 1 màn · 1 chạm (bỏ khối bước 4 mờ) | Khối «Nhập kết quả» mờ nằm ngay dưới, tưởng phải điền |
| 4 | Lắc chai trong lúc ủ (3 ngày/lần) | 16b → 16c | 2 màn · **không có chỗ bấm** (`16c:37` toàn ô tick bị khóa) | 1 màn · 1 chạm ngay ở danh sách | «Đến lượt lắc chai hôm nay» nhưng mở chi tiết cũng không biết bấm đâu |
| 5 | Ngửi kiểm tra | 16c bước ngửi | 1 màn (chung với nhập kết quả) · 9 chạm (4 ô chọn × 2 + «Đạt») · 0–1 gõ | 1 màn riêng · 1 chạm «Đạt» (chưa đạt: 2 chạm) · 0 gõ | 4 ô chọn; hai nút «Đạt, nhập kết quả» và «Hoàn thành lệnh» cùng một màn |
| 6 | Tạo lô thành phẩm (nhập kết quả) | 16c bước nhập | 1 màn · 1 chạm · 2 gõ (kg, số chai) + 2 ô ngày | 1 màn · 1 chạm · 2 gõ; ngày hiện thành chữ, có nút «Sửa» | Ô ngày, «Hạn dùng (tự tính 18 tháng, sửa được)» |
| 7 | Lưu mẫu | 17 (+26b, 26c) | 17: 1 màn · 2 chạm (Lưu mẫu, Sang gán tem) · 0 gõ (vị trí điền sẵn) | 1 màn · 1 chạm «Đã lấy chai lưu mẫu» (tự sang gán tem) | Hỏi «Đã lấy chưa?» nhưng không có nút «Chưa»; hai nút to ngang nhau |
| 8 | Gán tem | 15 → 18 | từ 17: 1 màn · 2 quét · 0 gõ. Từ trang chủ: +1 chạm chọn lô | giữ 2 quét (BR-12 cần 2 tem), thêm «Bước 1/2», «Bước 2/2» và kết quả to | «đoạn tem», «TEM CUỐI», «quét lại» là chữ nhỏ |

Tổng một mẻ tinh dầu 4 thành phần (từ tạo lệnh đến gán xong tem, không tính lắc chai): hiện ~**25 chạm + 7 gõ**, sau đề xuất ~**17 chạm + 7 gõ**. Phần còn lại là quét tem và gõ gram/số chai, đều là dữ liệu bắt buộc theo BR.

---

## 2. Đề xuất theo việc

Ký hiệu **trước→sau** là số chạm (c) và gõ (g). Căn cứ BR theo TK mục 7.2–7.5 và bảng BR.

### Việc 1. Bắt đầu mẻ (màn 24)

| Mã | File:dòng | Vấn đề | Đề xuất | Trước→sau | Căn cứ |
|---|---|---|---|---|---|
| B2-01 | `b/24-prod-owner.html:42` | Cỡ mẻ gõ bằng gram («921,7»); phải tự biết «1 lít = 921,7 g» | Hàng nút to «Làm bao nhiêu?»: `100 ml` · `500 ml` · `1 lít` · `Số khác` (chỉ «Số khác» mới hiện ô gõ). Gram vẫn tự tính và hiện ở bảng `:46-50`; túi thơm: nút «40 túi» (mẻ chuẩn TUI, `16:38`) | 4c+1g → 3c+0g | TK 7.2 (cỡ mẻ), `GET /recipes/{id}/scale?batch_g=` |
| B2-02 | `b/24-prod-owner.html:37` | Chọn sản phẩm bằng ô xổ 7 mục, kèm mã SKU «(TD-QC2-10)» | Nút to cho 6 sản phẩm làm được (Trà vẫn xám theo `:37`), bỏ mã SKU khỏi chữ chính, sản phẩm lần trước làm đứng đầu, chọn sẵn | 2c → 1c | #461 (chọn bằng nút) |
| B2-03 | `b/24-prod-owner.html:35,38` | «Làm gì» và «Công thức» chiếm 2 chỗ, mà công thức chỉ có 1 bản «đang dùng» | «Làm gì» đổi chữ đời thường: «Làm thành phẩm» / «Làm hương nền, dầu quế ủ…». Ô «Công thức» ẩn khi chỉ có 1 bản đang dùng, chỉ còn dòng chữ «Công thức QC2 v1 · ủ 28 ngày» | 0–2c → 0c | BR-26 (mỗi mã một bản ACTIVE) |
| B2-04 | `b/24-prod-owner.html:32-65` | Một màn gồm form dài + 3 danh sách; nút chính «+ Tạo lệnh» nằm giữa trang | Màn 24 chỉ có nút to «+ Bắt đầu mẻ mới» trên cùng, bấm mở form (một việc, một nút chính «Tạo lệnh»). Ba danh sách dùng chung với 15 | +1c nhưng form gọn, dùng được trên điện thoại | #461 (mỗi màn một việc chính) |
| B2-05 | `b/24-prod-owner.html:40` | Nhóm TT1/TT2 chỉ có trong chú thích | Công thức có nhóm lựa chọn: hiện 2 nút to bắt chọn, «Tạo lệnh» khóa tới khi chọn | 0c | BR-26 (nhóm lựa chọn) |
| B2-06 | `b/24-prod-owner.html:43-44` | «Ghi chú» để trống nằm cùng hàng với ô bắt buộc | Thu thành «+ Thêm ghi chú» (bấm mới mở ô); «Ngày» hiện chữ «Hôm nay 20/11/2026» kèm «Đổi» | 0g | ngày mặc định = hôm nay |

**CẦN SẾP QUYẾT (B2-07)**: nay chỉ chủ DN tạo lệnh (`TK:951` «tạo, hủy: OWNER»; `16:35`), nên màn 15 của xưởng không có nút bắt đầu mẻ; xưởng phải chờ chủ DN cho từng mẻ. **Mặc định: giữ nguyên (chỉ chủ DN tạo).** Phương án khác: xưởng bấm «Bắt đầu mẻ mới» với công thức đang dùng, chủ DN vẫn hủy lệnh. Đổi quyền là đổi nghiệp vụ nên không tự sửa.

### Việc 2. Ghi nguyên liệu và phụ liệu (màn 16)

| Mã | File:dòng | Vấn đề | Đề xuất | Trước→sau | Căn cứ |
|---|---|---|---|---|---|
| B2-10 | `b/16-prod-order.html:47-52` | Bảng 6 cột trên màn xưởng; «Gợi ý (g)» nhỏ, giống mục tuỳ chọn; mã VQH/DG/HT/DDT viết tắt | Mỗi thành phần một **thẻ lớn**, thứ tự cố định theo công thức: tên đầy đủ («Vỏ quế cắt hạt»), dòng to «Cân 480,00 g» (≥ 28 px như `.big-number`), lô gợi ý «Lấy lô VQH-2611-01, hạn gần nhất», ô «Quét tem», ô «Số cân thực tế». Bỏ mã viết tắt khỏi chữ chính (mã lô trên tem vẫn giữ) | 8c → 4 quét, 0 chạm chuyển ô | TK 7.2 «Lô phụ liệu» (gợi ý lô hạn gần nhất) |
| B2-11 | `b/16-prod-order.html:51` | Sau khi quét phải chạm sang ô gram; gõ xong phải chạm sang dòng kế | Quét xong tự nhảy vào ô gram (`inputmode="decimal"` đã có, bàn phím số tự bật); Enter nhảy sang ô quét kế; đủ thì thẻ xanh «Đủ» | −4c | #461 (bàn phím số) |
| B2-12 | `b/16-prod-order.html:45` | «TARE», «cân 0,01 g», câu dài | «Quét tem lô, rồi gõ số cân. Cân sai thì ghi số thật, không múc bớt ra.» Nhắc «trừ bì (TARE) trước mỗi thứ» thành dòng nhỏ riêng | chữ | chữ không viết tắt |
| B2-13 | `b/16-prod-order.html:52,56` | «Lệch +0,09 g» và banner «cho phép ±0,05 g» khó hiểu | Trong thẻ vàng: «Nhiều hơn 0,09 g so với cần cân (cho phép 0,05 g). Vẫn lưu được.» Bỏ banner riêng ở `:56` | chữ | TK 7.2 (cảnh báo vàng ±0,05 g, vẫn lưu) |
| B2-14 | `b/16-prod-order.html:49-52` | «✕ Bỏ» là `button.small` 44 px (`app.css:79`) | ≥ 48 px, chữ «Bỏ dòng này» | — | chuẩn chạm |
| B2-15 | `b/16-prod-order.html:57` | «+ Thêm dòng ngoài công thức» là `button.link` (`app.css:80`, <48 px) | Nút thường 48 px: «+ Thêm phụ liệu ngoài công thức» | — | TK 7.2 (dòng ngoài công thức) |
| B2-16 | `b/16-prod-order.html:51` | Tem không quét được thì không có đường lui | Dưới ô quét: «Tem không quét được → chọn lô» mở 3–5 nút lô còn tồn của phụ liệu đó | thêm đường lui | TK 7.2 (lô đúng phụ liệu) |

**CẦN SẾP QUYẾT (B2-17)**: bỏ quét tem khi chỉ còn **một** lô tồn (chạm «Đúng lô này» thay quét). Giảm 4 quét nhưng mất bằng chứng người xưởng cầm đúng lô. **Mặc định: không bỏ, vẫn quét** (truy xuất lô phụ liệu là cốt lõi, BR-01, BR-27); chỉ có nút lùi B2-16.

**CẦN SẾP QUYẾT (B2-18)**: nút «Đúng như cần cân» điền sẵn số cân bằng số gợi ý. **Mặc định: không làm.** Sổ tay yêu cầu cân thật 0,01 g và hệ thống đối chiếu thực tế/gợi ý (`b/26b:44-50`); điền sẵn làm số cân thành số giả. (Cân điện tử nối máy là việc giai đoạn sau.)

### Việc 3. Đưa vào ủ (màn 16)

| Mã | File:dòng | Vấn đề | Đề xuất | Trước→sau | Căn cứ |
|---|---|---|---|---|---|
| B2-20 | `b/16-prod-order.html:68-76` | Khối «4 Nhập kết quả (mở khi đủ ngày ủ)» mờ, 4 ô khóa nằm ngay trên màn pha, dễ tưởng phải điền | Bỏ khỏi màn 16 khi lệnh còn Nháp; kết quả chỉ ở màn nhập kết quả (B2-50) | 0c | TK 7.2 (hoàn thành chỉ khi CURING đủ ngày) |
| B2-21 | `b/16-prod-order.html:63-65` | Nút khóa kèm banner ở trên và chú thích dài ở dưới | Một khối: nút to «Đã pha xong, đưa vào ủ» luôn hiện; thiếu thì xám, ngay trên nút ghi «Còn thiếu: Hạt thạch cao» (bấm nhảy tới thẻ đó). Chú thích mã mẻ còn một dòng. Bấm xong: toast «Đã đưa vào ủ. Dán tem TUI-261120-01 lên lọ.» rồi về 15 | 1c → 1c | BR-26 (đủ dòng bắt buộc mới ủ) |

### Việc 4. Lắc chai (màn 15, 16b, 16c)

| Mã | File:dòng | Vấn đề | Đề xuất | Trước→sau | Căn cứ |
|---|---|---|---|---|---|
| B2-30 | `b/16c-cure-detail.html:36-37`, `b/16b-cure-list.html:39` | 16b báo «Đến lượt lắc chai hôm nay» nhưng 16c chỉ có ô tick **đã khóa** (kể cả 19/11); không có chỗ bấm «đã lắc» | Ở 16b, hàng đến lượt có nút to «Đã lắc chai hôm nay» ngay trong hàng (và thẻ tương ứng ở 15 `:37`). Ở 16c, ngày hôm nay là ô to bấm được, ngày trước khóa | 2 màn, 0 chạm làm được → 1 màn, 1c | sổ tay tr.6 (lắc chai 3 ngày/lần) |

**CẦN SẾP QUYẾT (B2-31)**: TK mục 4 chưa có trường lưu «đã lắc chai». Có lưu không? **Mặc định: chỉ nhắc, không lưu** (không đổi dữ liệu; nếu cần ghi thì vào `cure_check_note`).

### Việc 5. Ngửi kiểm tra (màn 16c)

| Mã | File:dòng | Vấn đề | Đề xuất | Trước→sau | Căn cứ |
|---|---|---|---|---|---|
| B2-40 | `b/16c-cure-detail.html:41-52` | 4 ô chọn (ngửi ngay, sau 1 giờ, sau 4 giờ, so mẫu chuẩn), mỗi ô mở rồi chọn = 8 chạm. TK chỉ có **một** trường `cure_check_note` (TK dòng 354, 809). Mốc «sau 1 giờ / 4 giờ» không thể làm cùng lúc trên một màn | Màn «Ngửi kiểm tra» riêng, 2 nút to: **«Đạt»** (xanh) và **«Chưa đạt, ủ thêm 7 ngày»**. «Muốn ghi thêm?» là ô tuỳ chọn, thu gọn. 4 mốc ngửi thành «Xem hướng dẫn ngửi» (nhắc theo sổ tay), không phải 4 ô chọn | 9c → 1c (Đạt) hoặc 2c (chưa đạt) | TK 7.2 (cure_check_note); sổ tay tr.6 |
| B2-41 | `b/16c-cure-detail.html:51,53` | «Ủ thêm» phải gõ lý do | Hộp lý do 3 nút: «Còn mùi gắt» · «Khác mẫu chuẩn» · «Lý do khác (gõ)» | 1g → 1c | TK 7.2 (lý do vào cure_check_note) |
| B2-42 | `b/16c-cure-detail.html:50,64` | Nút «Đạt, nhập kết quả» và «Hoàn thành lệnh» cùng màn | «Đạt» chuyển sang màn «Nhập kết quả» (B2-50); mỗi màn một nút chính | — | #461 |
| B2-43 | `b/16c-cure-detail.html:53` | «Bỏ qua kiểm tra ngày ủ» của chủ DN chỉ có trong chú thích | Nút thật (chỉ chủ DN thấy), hỏi lý do bắt buộc (nút chọn nhanh + gõ) | giữ | BR-28 (chủ DN bỏ qua, ghi lý do, audit) |

**CẦN SẾP QUYẾT (B2-44)**: bỏ 4 ô chọn ngửi khỏi form? **Mặc định: bỏ**, vì chỉ lưu vào một ô ghi chú, không đổi trường dữ liệu hay BR. Nếu sếp muốn ghi đủ 4 mốc: khối «Ghi chi tiết (không bắt buộc)» thu gọn, tự ghép thành ghi chú.

### Việc 6. Tạo lô thành phẩm (màn 16c, bước nhập kết quả)

| Mã | File:dòng | Vấn đề | Đề xuất | Trước→sau | Căn cứ |
|---|---|---|---|---|---|
| B2-50 | `b/16c-cure-detail.html:56-65` | Nhập kết quả chung màn với ngửi kiểm tra; 4 ô (2 số bắt buộc, 2 ngày), nút «Hoàn thành lệnh» ở cuối | Màn riêng «Nhập kết quả» sau «Đạt»: 2 ô số to (đã có `.big-number`, `inputmode` đúng) «Cân được bao nhiêu kg», «Bán được bao nhiêu chai»; nút to «Hoàn thành, tạo lô» | 1 màn 2 nút chính → 2 màn, mỗi màn 1 nút; 1c+2g | BR-09 |
| B2-51 | `b/16c-cure-detail.html:61-62` | Hai ô ngày điền sẵn nhưng vẫn là ô chọn ngày của trình duyệt | Hiện chữ «Ngày xong: hôm nay 20/11/2026 · Hạn dùng: 20/05/2028 (18 tháng)» kèm «Sửa» (bấm mới mở ô ngày). **Túi thơm, sáp, viên: hạn dùng chưa có mặc định, nên ô hạn hiện to và nút khóa tới khi có hạn** | 0c / 0g mặc định | BR-11 (hạn tự tính, sửa được; NULL thì bắt nhập tay) |
| B2-52 | `b/16c-cure-detail.html:62` | Nhãn «Hạn dùng (tự tính 18 tháng, sửa được)» | «Hạn dùng (tự tính 18 tháng)» | chữ | BR-11 |
| B2-53 | `b/16c-cure-detail.html:60` | Chữ «(chai)» cố định, mà túi thơm là «túi» | Nhãn lấy theo đơn vị đếm của sản phẩm (`23-products.html:57`) | — | đơn vị đếm sản phẩm |

### Việc 7. Lưu mẫu (màn 17, 26b, 26c)

| Mã | File:dòng | Vấn đề | Đề xuất | Trước→sau | Căn cứ |
|---|---|---|---|---|---|
| B2-60 | `b/17-prod-done.html:44-52` | Hỏi «Đã lấy chưa?» nhưng chỉ có «Lưu mẫu» và «Sang bước gán tem», hai nút ngang nhau, không có đáp «Chưa» | Hai nút: **«Đã lấy chai lưu mẫu»** (chính; lưu rồi tự sang gán tem của lô này) và **«Để sau»** (phụ; vẫn sang gán tem, lô nằm ở «Lô chưa lưu mẫu»). Vị trí (tủ, kệ) là ô nhỏ điền sẵn lần trước | 2c → 1c | BR-29; TK 7.5 (không chặn gán tem) |
| B2-61 | `b/17-prod-done.html:50` | Banner «Chưa lưu mẫu. Lô hiện ở «Lô chưa lưu mẫu»…» là chữ nội bộ | Bỏ banner; chọn «Để sau» thì toast «Nhớ lưu mẫu sau, việc này nằm ở trang chủ» | chữ | TK 7.5 |
| B2-62 | `b/17-prod-done.html:41` | Đoạn chữ dày: ngày pha, ngày xong, hạn, ngửi, ghi chú chai | Ngày và hạn đưa vào ô KPI sẵn có (`:35-40`); còn một dòng «90 chai bán được, chưa gồm chai lưu mẫu» | chữ | #461 |
| B2-63 | `b/17-prod-done.html:34` | Nhắc mã QC2-261023-01 hai lần trong một câu | «Xong! Lô QC2-261023-01 đã tạo.» | chữ | — |
| B2-64 | `b/26b-lot-detail.html:61-62`, `b/26c-retain-list.html:45` | «Lưu mẫu» không có ô vị trí (17 có) | Bấm mở hộp «Để chai ở đâu?», ô vị trí điền sẵn lần trước + nút «Lưu mẫu» | 1c, 0g | TK 7.5 (`location?` tuỳ chọn) |
| B2-65 | `b/26c-retain-list.html:36` | «Hủy mẫu» đỏ ngay trên hàng, 44 px | ≥ 48 px, hỏi xác nhận «Hủy mẫu QC2-251105-01?» | — | TK 7.5 (hủy khi hết hạn, chủ DN) |

### Việc 8. Gán tem (màn 15, 17, 18)

| Mã | File:dòng | Vấn đề | Đề xuất | Trước→sau | Căn cứ |
|---|---|---|---|---|---|
| B2-70 | `b/18-labels.html:44-46` | Tiêu đề «Quét TEM CUỐI của đoạn tem» hiện trước; bước «tem đầu» chỉ nằm ở banner nhỏ sau khi quét | Hai bước rõ: «Bước 1/2: quét tem ĐẦU của cuộn», rồi «Bước 2/2: quét tem CUỐI». Quét xong tem cuối tự gán, không cần nút | 2 quét → 2 quét (BR-12 cần 2 tem) | BR-12 |
| B2-71 | `b/18-labels.html:46` | «quét lại» là `button.link` nhỏ | Nút 48 px «Quét lại tem đầu» | — | chuẩn chạm |
| B2-72 | `b/18-labels.html:38` | «Đã gán 150 / 200» chưa nói còn bao nhiêu tem phải dán | Dòng to «Còn 50 tem cần gán» + thanh tiến độ | — | BR-12 |
| B2-73 | `b/18-labels.html:47` | Phản hồi sau khi gán (`#msg`) rỗng | Thông báo to «Đã gán 50 tem, lô này xong» (xanh) hoặc lý do lỗi bằng chữ thường (tem khác cuộn, tem đã dùng) | — | BR-12 (all-or-nothing) |
| B2-74 | `b/15-prod-list.html:41-43`, `b/24-prod-owner.html:62-64` | «Lô cần gán tem» chỉ có Q100-261120-02, **thiếu QC2-261023-01 (0/90)** dù `18:36` ghi lô này còn 0/90 | Thêm thẻ «QC2-261023-01 · đã gán 0/90» | — | thống nhất với #29 |
| B2-75 | `b/18-labels.html:36` | Lưới chọn lô vẫn hiện khi vào từ 15/17 (đã có `?lot=`) | Có `?lot=`: ẩn lưới, chỉ còn «Lô QC2-261023-01 · Đổi lô» | −1c khi vào từ 15 | #461 (điền sẵn) |

---

## 3. Nhất quán và chữ trên màn quản lý

| Mã | File:dòng | Vấn đề | Đề xuất |
|---|---|---|---|
| B2-80 | `b/15:36-37`, `b/24:58-59`, `b/16b:36-39` | Cả 4 mẻ cùng trỏ `/san-xuat/ua/1` (QC2-…-02, DDT, TUI, QC1) | Mỗi mẻ một id: QC2-…-02 = `ua/1`, DDT = `ua/2`, TUI = `ua/3`, QC1 = `ua/4`. Cần @Long xác nhận vỏ `_tools/vo.html` có route theo id |
| B2-81 | `b/26-plots-lots.html:33,35-37` | Cột «Hiệu suất» còn dù sếp đã bỏ 1,92% (#429); bảng 15 cột; «SL», «Ngày SX» viết tắt | Bỏ «Hiệu suất» và «Giá quế / đơn vị» (luôn «—» trong ví dụ); «SL» → «Số lượng», «Ngày SX» → «Ngày làm xong». Còn: Lô · Sản phẩm · Hạn dùng · Số lượng · Đã gán tem · Mẫu lưu · Trạng thái |
| B2-82 | `b/26-plots-lots.html:35-37` | Nút «Thu hồi» đỏ trên từng hàng, 44 px, không xác nhận | Chuyển vào chi tiết lô (`26b:65` đã có «Thu hồi lô»); danh sách chỉ giữ nhãn trạng thái |
| B2-83 | `b/16b-cure-list.html:34-41` | Bảng 7 cột, nút `.btn.small` 44 px, «QC2 · ủ 28 ngày» chữ nhỏ | Mỗi mẻ một thẻ như ở 15: tên sản phẩm to, «Còn 3 ngày», nút 64 px «Ngửi kiểm tra» hoặc «Đã lắc chai hôm nay» |
| B2-84 | `b/23b:38` | «Đầu ra», «Bán thành phẩm TT1»: chữ kỹ thuật | Giữ màn (không dùng hằng ngày); đổi «Đầu ra» → «Làm ra», «Bán thành phẩm TT1» → «Hương nền TT1» |
| B2-85 | `b/23c:39,41` | «Nhãn mẻ», «Ủ tối đa (ngày, tham khảo)» để trống, không bắt buộc | Thu vào «Thêm tuỳ chọn» (mặc định đóng) |
| B2-86 | `b/23:39-48` | Cột «Lưu mẫu», «Dán tem» dùng ✔ và «—» | Đổi thành «Có» / «Không» |
| B2-87 | `b/26d:55-59` | «FAIL», «PASS», «cường độ / dễ chịu», «TB» | «Đạt» / «Không đạt», «Mùi mạnh / Dễ chịu», «Trung bình» |

---

## 4. CSS chung cần sửa (ghi lại, không sửa trong task này)

| Vị trí | Hiện tại | Cần |
|---|---|---|
| `app.css:79` | `button.small, .btn.small` `min-height:44px` | ≥ 48 px |
| `app.css:80` | `button.link` `min-height:auto` | vùng chạm ≥ 48 px |
| `app.css:100` | checkbox 28 px | nhãn bọc quanh ≥ 48 px |
| `app.css:119` | `.tag` `.78rem` ≈ 14 px | ≥ `.9rem` |
| `app.css:64,87,146,162` | `.tile .badge`, `.choice .sub`, `.totalbar .lbl`, `.kpi .l` `.85rem` ≈ 15,3 px | ≥ `.9rem` |
| `b/15:16` (style nội tuyến) | `td input,td select{min-height:44px}` | 48 px |
| `b/15:14` `.chip` | khung ≈ 40 px | `min-height:48px` |

---

## 5. Ngoài phạm vi, chuyển Lead

- `b/14b-ingr-stock.html:54` còn nhắc QC2-261023-01 (review #448); thuộc cụm A.
- Chưa kiểm trên trình duyệt thật; chưa đối chiếu sổ tay PDF (số mốc ngửi và lắc chai lấy theo TK).
- **Giữ nguyên trạng thái lô QC2 chốt ở #29**: -01 đã ngửi đạt, đang dùng, 0/90 đã gán tem; -02 (LSX-2610-003) đang chờ ngửi. Không đề xuất nào đổi hai mã này (B2-74 chỉ thêm thẻ -01 vào danh sách cần gán tem).

## 6. Tóm tắt CẦN SẾP QUYẾT (mặc định in đậm)

| Mã | Câu hỏi | Mặc định |
|---|---|---|
| B2-07 | Cho xưởng tự bắt đầu mẻ (hiện chỉ chủ DN)? | **Giữ chỉ chủ DN** |
| B2-17 | Bỏ quét tem khi chỉ còn một lô tồn? | **Không bỏ** (có nút lùi khi tem hỏng) |
| B2-18 | Nút điền sẵn số cân = gợi ý? | **Không làm** |
| B2-31 | Lưu «đã lắc chai» vào dữ liệu? | **Chỉ nhắc, không lưu** |
| B2-44 | Bỏ 4 ô chọn ngửi khỏi form? | **Bỏ**, giữ «Đạt / Chưa đạt» + ghi chú tuỳ chọn |
