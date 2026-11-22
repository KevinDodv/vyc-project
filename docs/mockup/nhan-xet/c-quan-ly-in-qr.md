# Nhận xét cụm C – Đăng nhập, quản lý chủ DN, mẫu in, trang QR khách

Soát 20 màn trong `docs/mockup/de-xuat/man/c-quan-ly-in-qr/` (01, 19–22, 25, 27–40). Chưa sửa HTML.

**Viết tắt căn cứ.** `36:61` là `36-q-ok.html` dòng 61 (thư mục cụm C). `TK §x` là `docs/thiet-ke-chi-tiet.md` mục x; dẫn theo mục/mã BR vì số dòng đang đổi do topic #2. `goc:87` là `docs/mockup/goc/mockup-goc.html` dòng 87.

**Mức:** high = sai thiết kế hoặc thiếu màn cốt lõi; medium = lệch/thiếu nhưng không chặn; low = chỉnh cho đúng/gọn. Không có critical.

## Tóm tắt

- 4 high: trang QR công khai lộ người mua (C-01, C-02), mã lô theo mẫu cũ (C-03), thiếu màn Vùng nguyên liệu (C-04).
- 10 medium (C-05..C-14), 8 low (C-15..C-22).
- 3 điểm gắn [SẾP QUYẾT]: người mua trên trang QR (C-01/C-02), nhãn lô thành phẩm (C-07), phạm vi danh mục (C-18).
- Đã khớp, không cần sửa: che tên/SĐT ở 27, 28, 29, 34 (BR-24, AC-24); ghi chú nhật ký «Xem đầy đủ» ở `29:38`; tem NL (33) đúng TK §6.2; QR tem 18,8 mm ≥ 18 mm (TK §11); số liệu cuộn tem ở 25 cộng đúng (145+5+150 = 300; 20+29+1 = 50); `/truy-xuat` (40) không noindex, đúng TK §8.1; BR-22 ở dòng NM-000003 (Shopee, không SĐT).

---

## High

### C-01 · Trang QR (36, 38) hiện người mua và kênh bán, trái thiết kế
- **Màn:** 36-q-ok, 38-q-recall.
- **Sai gì:** khối «Tình trạng bán» hiện Ngày bán, Kênh mua, Người mua `T T H`, SĐT `*******222`, Khu vực. TK §6.6 «Dữ liệu cá nhân»: thông tin người mua không bao giờ xuất hiện trên website hay trang truy xuất. TK §8.4: danh sách «Nội dung truy xuất đầy đủ» không có khối này, và «Tuyệt đối không hiện… tên khách hàng, mã phiếu». BR-24: không bao giờ trả qua API công khai, kể cả bản che. Rủi ro thực: tem in sẵn cả cuộn, ai quét cũng thấy chữ cái đầu, 3 số cuối và tỉnh của người đã mua.
- **Căn cứ:** `36:60-77`, `38:60-77` (ghi chú che ở `36:74`).
- **Mức:** high.
- **Đề xuất:** xoá cả khối «Tình trạng bán» ở 36 và 38. Giữ thứ tự TK §8.4: chính hãng → ảnh/tên → mã lô, NSX, HSD → vùng nguyên liệu → hộ trồng (nếu đồng ý) → chứng nhận → câu chuyện → mua lại → số lần quét. Trang 38 giữ khung đỏ thu hồi + thông tin sản phẩm + lô, bỏ phần người mua.
- **[SẾP QUYẾT]** Nếu sếp chủ ý cho khách thấy «đã bán cho ai», phải sửa TK §6.6, §8.4, BR-17, BR-24, AC-13 (topic #2 đang giữ file). Khuyến nghị: bỏ, vì người quét tem của người khác sẽ thấy dữ liệu cá nhân.

### C-02 · Cài đặt (32) có công tắc bật sẵn cho việc ở C-01; 37 có trạng thái «Chưa bán» ngoài thiết kế
- **Màn:** 32-settings, 37-q-unsold.
- **Sai gì:** (a) ô tích «Trang truy xuất hiện người mua khi sản phẩm đã bán (tên viết tắt, 3 số cuối SĐT, khu vực)» đang `checked`; không có trong danh sách setting của TK và mâu thuẫn BR-24. (b) 37 hiện «● Chưa bán — Sản phẩm chưa được ghi nhận bán ra từ cơ sở» cho serial IN_STOCK. TK §8.4 xếp IN_STOCK và ISSUED chung một nội dung; không có biến thể «chưa bán». Khách mua qua kênh chưa quét xuất kho sẽ đọc thông báo này như tem lạ.
- **Căn cứ:** `32:23` (checkbox), `37:61-66`.
- **Mức:** high (đi cùng C-01).
- **Đề xuất:** bỏ ô tích ở 32. Ở 37 bỏ khối «Tình trạng bán»; khi đó 37 trùng 36 (chỉ khác mã), nên cho 36 đại diện IN_STOCK và ISSUED, và dùng slot của 37 cho màn «quét N lần quá ngưỡng» (C-05).
- **[SẾP QUYẾT]** cùng quyết định với C-01.

### C-03 · Mã lô thành phẩm dùng mẫu cũ `TP-TD10-2611-02`
- **Màn:** 36, 37, 38 (trang QR); 27 (tra cứu); 29 (chi tiết người mua). Cụm B (15, 17, 18, 24, 26) cũng dùng, báo ở notes.
- **Sai gì:** TK §10 «Chốt mẫu mã lô» (topic #2): lô thành phẩm = `<mã công thức>-YYMMDD-NN` (ví dụ QC1-261117-01); mẫu `TP-<SKU>-YYMM-NN` đã bị bỏ. Sổ tay C.3 cũng ghi `[Mã công thức]-[Năm tháng ngày]-[Số mẻ]`. Mockup còn tiền tố `TP-`, SKU và chỉ 4 chữ số tháng.
- **Căn cứ:** `36:55`, `37:55`, `38:55`, `27:19` (cột lô thành phẩm), `29:38` (hai serial của lô). Ô tra cứu `27:17` chỉ liệt kê `TP-…`.
- **Mức:** high (hiện ở màn khách và nhiều màn chủ DN).
- **Đề xuất:** đổi `TP-TD10-2611-02` thành `QC1-261120-02` và `TP-TD10-2611-01` thành `QC1-261120-01` (cùng công thức QC1, cùng ngày pha 20/11/2026; QC1 lấy theo ví dụ của TK, đổi nếu mẻ mẫu là công thức khác). Placeholder ô tra cứu: «Mã tem, QC1-…, Q-…, NL-…, PN-…, PNP-…, PX-…, LSX-…, NCC-… hoặc NM-…» (TK §7.4).

### C-04 · Thiếu màn «Vùng nguyên liệu»
- **Màn:** cần thêm màn mới (đề xuất `41-vung-nguyen-lieu`, nhóm Chủ DN, sau `trace`); sửa 19 và vỏ xem trước.
- **Sai gì:** TK §7.1 yêu cầu màn riêng cho OWNER: bản đồ đồi có tọa độ (Leaflet + OpenStreetMap), bảng đồi (xã, thôn, diện tích, năm trồng, tổng kg mua 12 tháng, hiệu suất trung bình), đồi thiếu tọa độ/ảnh gắn «thiếu thông tin truy xuất». Menu ở 31 có link `/quan-ly/vung-nguyen-lieu` nhưng route trỏ `null` nên bấm không đổi màn; trang chủ chủ DN (19) không có ô vào màn này. Dữ liệu mẫu đã có: hai đồi của NCC-CQ-001 đều «thiếu tọa độ / ảnh» (`22:32`).
- **Căn cứ:** `goc:87` (`[/^\/quan-ly\/vung-nguyen-lieu/, null]`); `31-admin.html:36`; `19:26-35` không có tile; TK §7.1; lộ trình GĐ2 («khai báo vùng»).
- **Mức:** high (màn cốt lõi của phân hệ truy xuất bị thiếu).
- **Đề xuất:** thêm `41-vung-nguyen-lieu.html`: khung bản đồ (ô giữ chỗ có ghim, ghi «Leaflet + OpenStreetMap»), bảng đồi dùng dữ liệu mẫu sẵn có (D-CQ-001-01 Thôn 3, 2,5 ha, 2012; D-CQ-001-02 Khe Hùm, 1,2 ha, 2016; đồi của NCC-DC-001 và NCC-CQ-002), nhãn cam «thiếu thông tin truy xuất», lọc theo xã. Thêm tile «Vùng nguyên liệu» vào 19. Gắn route `vung-nguyen-lieu` vào khoá mới trong vỏ và `_ds.json` (ngoài vùng của task #22, nhờ Lead giao).

---

## Medium

### C-05 · Trang QR thiếu các trạng thái ngoài «hợp lệ»
- **Màn:** 36–40.
- **Sai gì:** TK §8.4 có 6 trường hợp: không tồn tại, UNASSIGNED, VOID, RECALLED, IN_STOCK/ISSUED, và dòng vàng khi `scan_count` vượt ngưỡng. Mockup có UNASSIGNED (39), RECALLED (38), hợp lệ (36), nhập tay (40). Thiếu «Mã không có trong hệ thống», «Mã đã bị hủy» và cảnh báo «quét N lần, lần đầu dd/mm/yyyy». Ngưỡng 20 đã có ở 32 nhưng không màn nào dùng nó (BR-18; lộ trình «nghi giả»).
- **Căn cứ:** TK §8.4 (bảng trạng thái), BR-18; `32:23`; danh sách `_ds.json`.
- **Mức:** medium.
- **Đề xuất:** thêm 3 màn cùng khuôn 39: `q-notfound`, `q-void`, `q-many-scans` (bản 36 có thêm khung vàng). Thông điệp lấy nguyên văn bảng TK §8.4.

### C-06 · Trang QR không có ảnh sản phẩm, ảnh đồi
- **Màn:** 36, 37, 38.
- **Sai gì:** TK §8.4 thứ tự «ảnh, tên sản phẩm» và «tối đa 3 ảnh đồi». HTML không có thẻ `<img>` hay khung giữ chỗ; khối sản phẩm chỉ có tên và «10 ml».
- **Căn cứ:** `36:49-52`, `36:82-93`.
- **Mức:** medium.
- **Đề xuất:** thêm khung ảnh sản phẩm 1:1 và dải 3 ô «ảnh đồi» (hộp xám có chữ); không dùng ảnh thật vì chưa có tệp.

### C-07 · Tem serial không (và không thể) có mã lô, NSX, HSD; chưa có mẫu in nhãn lô thành phẩm
- **Màn:** 35-print-roll; thiếu mẫu in cho nhãn/tem mẻ.
- **Sai gì:** tem ở 35 chỉ có QR, «Quế Văn Yên», «Quét xem nguồn gốc», mã serial, `CT-2611-02 · n`, đúng TK §7.3. Mã lô không thể in lên tem này vì cuộn in trước, gán lô sau. Nhưng sổ tay (cuối mục C, trang 15) ghi «trên mỗi nhãn ghi: mã lô, ngày sản xuất, hạn dùng, cách dùng, cảnh báo không bôi lên da, không uống, để xa trẻ em và thú cưng»; TK §7.2 «in tem mẻ để dán lên lọ ủ»; TK §13 «khổ tem serial và tem lô». Nhóm Mẫu in hiện chỉ có phiếu nhập (33), phiếu xuất (34), tem serial (35); `18-labels` (cụm B) chỉ gán/hủy tem. Vậy «mã lô in trên tem» chưa có chỗ ở.
- **Căn cứ:** `35:51-56`; TK §7.2, §7.3, §13; sổ tay C.3 và đoạn nhãn.
- **Mức:** medium.
- **Đề xuất:** thêm mẫu in «Tem mẻ / nhãn lô» (`42-print-batch.html`, dùng lại CSS `.tem`): mã lô `QC1-261120-02` (chữ lớn + QR chứa mã lô như tem NL), tên sản phẩm, NSX, HSD. Ghi chú trên màn: tem serial không in mã lô; mã lô in trên nhãn này. «Cách dùng, cảnh báo» dài nên để cho nhãn hộp, tem 40 × 30 chỉ giữ mã lô, NSX, HSD.
- **[SẾP QUYẾT]** Nhãn chai cuối cùng gồm những gì, khổ nào (tem 40 × 30 hay nhãn lớn hơn). Không có trả lời thì tôi vẽ bản 40 × 30 như trên.

### C-08 · Tra cứu hai chiều (27) thiếu thu hồi và «Xem mẫu lưu»
- **Màn:** 27-trace.
- **Sai gì:** TK §7.4: từ tra cứu xuôi chọn một hay nhiều lô thành phẩm rồi bấm «Thu hồi các lô đã chọn» (mỗi lô lý do và audit riêng); khi khiếu nại, tra cứu lô có nút «Xem mẫu lưu» (TK §7.5). Mockup chỉ có bảng lô, không ô chọn, không nút nào. AC-23 (thu hồi rồi tra cứu xuôi, thấy đủ người mua) cần luồng này.
- **Căn cứ:** `27:19` (bảng «Lô thành phẩm»); TK §7.4, §7.5; AC-15, AC-23.
- **Mức:** medium.
- **Đề xuất:** thêm cột ô tích ở bảng lô thành phẩm, nút đỏ «Thu hồi các lô đã chọn» dưới bảng, nút nhỏ «Xem mẫu lưu» ở dòng lô (vị trí, hạn giữ). Tên màn «Mẫu lưu» phụ thuộc topic #2.

### C-09 · Cây truy xuất (27) mới có nhánh quế, chưa có nhánh phụ liệu
- **Màn:** 27-trace.
- **Sai gì:** TK §7 và §7.4 (topic #2): truy xuất gồm (a) lô NL đưa thẳng vào lệnh và (b) lô phụ liệu qua `production_ingredient`, nguồn là phiếu nhập phụ liệu (PNP-) hoặc lệnh làm ra nó; dầu quế mua ngoài hiện «nguồn ngoài, chưa nối về lô quế». Mockup chỉ có Lô NL → Người bán → Lệnh → Lô TP → Phiếu xuất → Người mua cuối.
- **Căn cứ:** `27:19`; TK §7 đầu mục, §7.4 mục «Ngược» và «Dầu quế nối về lô quế».
- **Mức:** medium.
- **Đề xuất:** thêm khối «Lô phụ liệu» ở chiều ngược (Q-2611-01 ← lệnh ủ U-Q ← QM-2610-02 ← lệnh chưng ← NL-…; CAM-2609-01 ← PNP-… ← nơi bán) và dòng vàng «nguồn ngoài, chưa nối về lô quế». Đổi nhãn theo kết quả topic #2.

### C-10 · Dữ liệu mẫu giữa 27, 30 và 26 mâu thuẫn
- **Màn:** 27, 30 (đối chiếu 26, cụm B).
- **Sai gì:** ở 27, lô NL-2611-0007 (120,5 kg, PN-261120-005) thuộc NCC-CQ-001. Ở 30 (theo người bán), 120,5 kg là của Nguyễn Văn Hùng (NCC-CQ-002), còn NCC-CQ-001 chỉ 85 kg; ở 26 lô -01 có giá vốn 271.125 đ = 5.422.500 đ / 20 chai, tức 120,5 kg đi vào lô -01. Một lô NL không thể thuộc hai người bán. Thêm nữa, lô -01 cho 1,2 kg thành phẩm ra 20 chai 10 ml (60 g/chai) trong khi lô -02 là 1,63 kg ra 200 chai (khoảng 8 g/chai).
- **Căn cứ:** `27:19` (NL-2611-0007/0008/0009 cùng PN-261120-005, cùng NCC-CQ-001), `30:24` (dòng Nguyễn Văn Hùng), `b-san-xuat/26-plots-lots.html:19` (lô -01: SL 20, giá vốn 271.125 đ).
- **Mức:** medium (số sai làm sếp ngờ logic báo cáo).
- **Đề xuất:** ở 27 chuyển NL-0007/0008/0009 sang NCC-CQ-002 (hoặc sửa 30), sửa thành phẩm lô -01 khoảng 0,18 kg hoặc tăng SL lên khoảng 130 chai. Chốt cùng cụm B để 26 khớp.

### C-11 · Cuộn tem (25): «Đã in: chưa in» nhưng đã có tem xuất, thu hồi
- **Màn:** 25-rolls.
- **Sai gì:** CT-2611-02 có «Đã xuất: 5», «Trong kho: 145» (tem đã gán lô, đã dán lên chai) nhưng cột «Đã in» là «chưa in». CT-2611-01 có «Thu hồi: 20» cũng «chưa in». Tem chưa in thì không thể thu hồi. Nhãn `warn` còn làm người xem tưởng cuộn thiếu việc.
- **Căn cứ:** `25:25` (hai hàng cuộn, ô «Đã in»).
- **Mức:** medium.
- **Đề xuất:** ghi «đã in 1–300» cho CT-2611-02 và «đã in 1–50» cho CT-2611-01; giữ «chưa in» cho một cuộn mới tạo (thêm hàng mẫu CT-2611-03, 100 tem, toàn «Chưa gán»).

### C-12 · Tem serial (35) ngắt mã thành «MKWX-142J / RH»
- **Màn:** 35-print-roll.
- **Sai gì:** TK §7.3 mã chữ dạng `K7Q2-MX9P-AT` một cụm. Ở 35 mã bị `<br>` tách thành «MKWX-142J» và «RH» (2 ký tự một dòng), khó đọc khi gõ tay và không khớp chuỗi mã in ở 25/29/36. QR ≥ 18 mm (TK §11) nên chữ chỉ còn khoảng 17,8 mm bề rộng.
- **Căn cứ:** `35:54` (`MKWX-142J<br>RH`, `letter-spacing:-.2pt`, font 6,6pt).
- **Mức:** medium.
- **Đề xuất:** để mã trên một dòng, font 5,6pt, bỏ `<br>`; hoặc ngắt có chủ ý «MKWX-» / «142J-RH». Nhờ Dev kiểm bằng in thử trên máy in tem thật (TK §11).

### C-13 · Người bán (21, 22): chưa có thao tác «Duyệt», form đồi thiếu trường
- **Màn:** 21-suppliers, 22-supplier-edit, 19-home-owner.
- **Sai gì:** TK §5 «Duyệt người bán mới»: chủ DN bổ sung đồi, đổi luồng rồi duyệt; API `POST /suppliers/{id}/approve`. Banner ở 19 «1 người bán chờ duyệt — bấm để duyệt» dẫn tới 21; ở 21 dòng NCC-CQ-003 có tag «Chờ duyệt» nhưng không có nút duyệt, và hộp sửa (22) mở cho NCC-CQ-001 đã duyệt nên không thấy luồng. Form đồi chỉ có bảng; «+ Thêm đồi» không có trường tọa độ (dán từ Google Maps), ảnh, đồi mặc định.
- **Căn cứ:** `19:24`, `21:23` (hàng NCC-CQ-003), `22:32` (dialog chỉ có Đóng/Lưu); TK §5 (hàng «Nhà cung cấp», «Đồi quế»), BR-03.
- **Mức:** medium.
- **Đề xuất:** thêm biến thể 22b: hộp sửa NCC-CQ-003 có nút «✔ Duyệt» cạnh Lưu và dòng «Đến khi duyệt, lô của người bán này luôn là hàng chung (BR-03)»; thêm dòng mở rộng của «+ Thêm đồi» có ô tọa độ, nút ảnh, ô tích «Đồi mặc định».

### C-14 · Menu quản lý (31) và trang chủ chủ DN (19) chưa có màn của topic #2
- **Màn:** 31-admin, 19-home-owner.
- **Sai gì:** TK §7.5: «Lô chưa lưu mẫu» hiện ở trang chủ OWNER và có màn «Mẫu lưu»; TK §7.2/§3 có công thức, lô phụ liệu, phiếu nhập phụ liệu; TK §7.5 có đợt thử lưu hương. Hai màn không có lối vào nào cho các việc này; nhóm «Danh mục» của 31 cũng thiếu «Công thức», «Phụ liệu».
- **Căn cứ:** `31-admin.html` (các link `/quan-ly/…`), `19:24-35`; TK §7.5.
- **Mức:** medium (phụ thuộc topic #2, tên route chưa chốt).
- **Đề xuất:** sau khi topic #2 chốt tên: thêm vào 31 «Công thức», «Phụ liệu & phiếu nhập phụ liệu», «Mẫu lưu», «Thử lưu hương»; thêm vào 19 khối «Lô chưa lưu mẫu: N» (banner cam kiểu `.banner.warn`).

---

## Low

### C-15 · Khách hàng đã mua (28): thiếu lọc theo tỉnh; CSV không báo dữ liệu đầy đủ
- **Màn:** 28-buyers.
- **Sai gì:** TK §6.6 «Lọc: theo sản phẩm, kênh, khoảng ngày, tỉnh» và API có `area_id`; mockup không có tỉnh. Nút «⬇ CSV khách đồng ý nhận tin» không cho biết file chứa tên và SĐT đầy đủ (BR-24: CSV của OWNER trả bản đầy đủ, ghi audit_log).
- **Căn cứ:** `28:17-26`.
- **Đề xuất:** thêm ô chọn «Tỉnh / xã» cùng khuôn `select` «Kênh»; đổi nhãn nút «⬇ CSV (SĐT đầy đủ, ghi nhật ký)».

### C-16 · Chi tiết người mua (29): dấu nối thừa khi không có SĐT; không báo đã ghi nhật ký
- **Màn:** 29-buyer-detail.
- **Sai gì:** dòng tóm tắt in `L M T ·  · Lào Cai` (hai dấu nối với khoảng trống) vì NM-000003 không có SĐT (đúng BR-22 kênh Shopee). Banner sau «Xem đầy đủ» còn dấu nối thừa và không có dòng xác nhận «đã ghi nhật ký». Ghi chú «Mỗi lần bấm… ghi vào nhật ký» có, nhưng sau khi bấm không thấy bằng chứng.
- **Căn cứ:** `29:38`.
- **Đề xuất:** bỏ dấu nối khi trường trống, ghi «SĐT: (sàn không cung cấp)»; thêm dòng nhỏ trong banner «Đã ghi nhật ký: Chủ DN, 20/11/2026 19:52». Phần che dữ liệu và nhật ký đúng thiết kế, chỉ hoàn thiện hiển thị.

### C-17 · Phiếu xuất (34) hiện «Kênh: DIRECT»
- **Màn:** 34-print-issue.
- **Sai gì:** phiếu in giao khách hiện mã kênh thô `DIRECT` trong khi 28 dùng «Bán trực tiếp».
- **Căn cứ:** `34:53`.
- **Đề xuất:** đổi thành «Bán trực tiếp». Nhãn «Quà tặng», tổng 300.000 đ (AC-22) và che tên/SĐT (AC-24) đã đúng.

### C-18 · Mới có 3 màn danh mục, sáu mục còn lại dẫn về trang menu
- **Màn:** 31-admin («Tài khoản», «Địa bàn», «Khách hàng», «Nguyên liệu & hạng», «Loại hàng hóa», «Chứng nhận»).
- **Sai gì:** TK §5 có 9 danh mục dùng chung một khuôn; TK §2 có «Quản lý tài khoản» chỉ OWNER. Bản xem trước có người bán, sản phẩm (23, cụm B), cài đặt. Sáu mục còn lại rơi về nhánh dự phòng `/quan-ly → admin` (`goc:88`), người xem bấm mà không đổi màn và tưởng lỗi.
- **Căn cứ:** `31-admin.html` (9 link danh mục), `goc:88`.
- **Đề xuất:** thêm gợi ý của vỏ «màn này dùng chung khuôn danh mục, chưa vẽ».
- **[SẾP QUYẾT]** có cần vẽ «Tài khoản» (phân quyền, khóa 15 phút sau 5 lần sai) và «Chứng nhận» (liên quan BR-14, OCOP) không? Khuyến nghị: chỉ ghi chú, danh mục cùng khuôn.

### C-19 · Trang chủ chủ DN (19) gộp GĐ1 và GĐ2, không đánh dấu giai đoạn
- **Màn:** 19-home-owner và cả cụm.
- **Sai gì:** theo lộ trình, GĐ1 là danh mục + nhập hàng, tồn kho, xuất quế khô (01, 20, 21, 22, 32, 33, phần nhập/xuất của 19); GĐ2 là sản xuất, truy xuất, QR (25, 27, 34, 35, 36–40) cùng người mua cuối (BR-22..25, AC-20..24 xếp GĐ2 trong thiết kế, lộ trình không nhắc). 19 hiện cả «Cuộn tem QR», «Lô thành phẩm · thu hồi», «Khách hàng đã mua» ngay từ đầu. Không sai nhưng sếp khó thấy phần nào giao ở giai đoạn nào.
- **Căn cứ:** `19:26-35`; lộ trình (GĐ1 dòng 106, GĐ2 dòng 108); `tom-tat.md` («Quản lý người mua cuối… lộ trình không nhắc»).
- **Đề xuất:** thêm nhãn nhỏ «GĐ2» trên các tile cuộn tem, lô thành phẩm, tra cứu, khách hàng. Không đổi cấu trúc.

### C-20 · Đăng nhập (01): link «← Về trang chủ» lặp vòng, chưa có trạng thái lỗi/khóa
- **Màn:** 01-login.
- **Sai gì:** thanh trên có «← Về trang chủ» dẫn tới `/`, mà trang chủ lại đòi đăng nhập. TK §6.1: nút này của các màn con sau đăng nhập. TK §9: khóa 15 phút sau 5 lần sai; vùng `#err` đang `hidden`, không có mẫu cho «Sai tên đăng nhập hoặc mật khẩu» hay «Tài khoản bị khóa 15 phút».
- **Căn cứ:** `01:12`, `01:24`; TK §9 (Xác thực), §11 (Bảo mật).
- **Đề xuất:** bỏ link «← Về trang chủ» ở màn đăng nhập; thêm 01b (khung đỏ «Sai tên đăng nhập hoặc mật khẩu. Còn 2 lần thử.») và 01c («Tài khoản bị khóa 15 phút»).

### C-21 · Chứng nhận mẫu trên trang QR (36, 37) là dữ liệu chưa có thật
- **Màn:** 36, 37.
- **Sai gì:** «OCOP 4 sao — số OCOP-LC-2027-015 (hiệu lực đến 01/10/2029)» cho tinh dầu khi ngày mẫu là 20/11/2026; lộ trình xếp OCOP vào GĐ4 (1–6/2028), chưa nộp hồ sơ. Sếp xem dễ hiểu là đã có chứng nhận.
- **Căn cứ:** `36:99`, khối «Chứng nhận» của 37; lộ trình GĐ4.
- **Đề xuất:** ghi rõ «(ví dụ)» hoặc đổi thành chứng nhận có thể có sớm hơn (phiếu công bố sản phẩm).

### C-22 · Cài đặt (32): tên miền QR không khoá sau khi in cuộn đầu tiên
- **Màn:** 32-settings (đối chiếu 25).
- **Sai gì:** nhãn «CHỐT TRƯỚC KHI IN CUỘN ĐẦU» và banner ở 25 nói đã in thì không đổi được, nhưng ô tên miền vẫn sửa tự do dù mẫu đã có cuộn có tem xuất. Đổi tên miền làm hỏng mọi QR đã in (TK §13).
- **Căn cứ:** `32:23` (input không `disabled`), `25:19`, TK §13.
- **Đề xuất:** ô tên miền chỉ đọc kèm «Đã in cuộn đầu tiên ngày 20/11/2026, không đổi được» (bản xem trước đặt luôn trạng thái này).

---

## Phần chưa xem / giới hạn

- PDF sổ tay không đọc được trên máy này (thiếu poppler). Tôi dùng `docs/_tools/tmp/so-tay.txt` (mất dấu tiếng Việt, chỉ đọc được mục C.3 và đoạn nhãn) và các chỗ thiết kế trích sổ tay. Chưa đối chiếu thành phần, công thức, hạn dùng với sổ tay; hạn 24 tháng ở 36–38 chưa kiểm (TK §13 còn mở).
- Chưa mở màn trên trình duyệt: đã đọc HTML/CSS, chưa xem hộp thoại in và khung điện thoại.
- Cụm B (26, 18, 15, 17, 24) chỉ đọc để đối chiếu mã lô và số liệu.
- Không sửa HTML, không đụng `docs/thiet-ke-chi-tiet.md`.
