# Nhận xét mockup giao diện: bản gộp (task #23)

Gộp từ ba file soát: `nhan-xet/a-nhap-xuat-kho.md` (Minh, màn 02–14), `nhan-xet/b-san-xuat.md` (Lan2, màn 15–18, 23, 24, 26 và màn thiếu theo sổ tay), `nhan-xet/c-quan-ly-in-qr.md` (Huy3, 20 màn còn lại). Ba file gốc giữ nguyên làm nơi xem chi tiết (trường dữ liệu từng màn thiếu, phân tích dài); bản này là bảng để sếp duyệt và để bản đề xuất / ảnh trước-sau dẫn lại bằng mã **A-nn / B-nn / C-nn**.

Chỉ nhận xét, chưa sửa HTML. Bản gốc mockup ở `docs/mockup/goc/`, màn tách ở `docs/mockup/de-xuat/man/`.

---

## 1. Tóm tắt cho sếp

### 1.1 Số vấn đề

57 vấn đề trong ba file → **53 sau khi gộp** (A-01 = B-05 = C-03 mã lô; A-02 = B-10 kho phụ liệu; A-17 = B-16 trà). Không bỏ vấn đề nào vì thiếu căn cứ; mọi dòng đều có dẫn `file:dòng` hoặc mã BR/AC/mục thiết kế.

| Mức | Số | Mã |
|---|---|---|
| critical | 1 | B-01 |
| high | 15 | A-01, A-02, A-05, B-02, B-03, B-04, B-06, B-07, B-08, B-09, B-11, B-14, C-01, C-02, C-04 |
| medium | 21 | A-03, A-04, A-06, A-07, A-09, A-11, A-12, B-12, B-13, B-15, A-17/B-16, C-05..C-14 |
| low | 16 | A-08, A-10, A-13, A-14, A-15, A-16, B-17, B-18, C-15..C-22 |

Điểm nặng nhất: (1) màn Sản xuất vẫn là «quét lô quế đem sàng», chưa có công thức, phụ liệu theo gram, giai đoạn ủ, lưu mẫu (B-01..B-11); (2) mã lô thành phẩm còn mẫu cũ `TP-TD10-2611-02` ở 13 màn (A-01); (3) trang QR công khai đang hiện người mua và có công tắc bật sẵn (C-01, C-02); (4) cụm A chưa có chỗ nào cho kho phụ liệu (A-02).

### 1.2 Màn còn thiếu (cần thêm file màn + `_ds.json` + route vỏ)

Tên key là đề xuất, chưa chốt. Giai đoạn theo `lo-trinh-chuyen-doi-so.md` (LT).

| Màn | Cụm | GĐ | Mã |
|---|---|---|---|
| Nhập phụ liệu (`ingr-receipt`), Tồn phụ liệu (`ingr-stock`) | A/B | 2 | A-02 |
| Khai công thức (OWNER) | B | 2 | B-09 |
| Theo dõi ủ và ngửi kiểm tra | B | 2 | B-11 |
| Chi tiết mẻ (sổ ghi lô) | B | 2 | B-13 |
| Mẫu lưu, Lô chưa lưu mẫu | B/C | 2 | B-08, C-08, C-14 |
| Thử lưu hương 28 ngày | B | 2 | B-14 |
| Vùng nguyên liệu (`41-vung-nguyen-lieu`) | C | 2 | C-04 |
| Tem mẻ / nhãn lô (`42-print-batch`) | C | 2 | C-07 |
| Trang QR: không có mã, mã đã hủy, quét quá ngưỡng | C | 2 | C-05 |
| Phụ: `03b` người bán mới, `04b` giá lệch 20%, `05b` in phiếu và tem lô, `09b` kênh sàn, `09c` người mua mới | A | 1–2 | A-11, A-13, A-12, A-07 |
| Phụ: `01b`/`01c` đăng nhập sai/khóa, `22b` duyệt người bán | C | 1 | C-20, C-13 |

Màn mới phải thêm route vào vỏ (`vo.html`) và `_ds.json`; việc này ngoài vùng soát, giao cho #24–#26.

### 1.3 Điểm [SẾP QUYẾT] và phương án mặc định

Bản đề xuất (#24–#26) làm theo mặc định cho tới khi sếp trả lời.

| # | Mã | Câu hỏi | Mặc định |
|---|---|---|---|
| 1 | B-06 | Xưởng có tự chưng dầu quế từ vỏ quế không? | Thiết kế hiện hỗ trợ cả hai (dầu từ gia đình qua phiếu «Nguồn gia đình», hoặc chưng tại xưởng); sổ tay chỉ mô tả từ lúc đã có dầu. Mockup bỏ chữ «chưng cất» và hiệu suất 1,92% khỏi ví dụ chai tinh dầu pha; chỉ vẽ lệnh chưng khi sếp chốt chưng tại xưởng |
| 2 | B-07 | Danh sách sản phẩm đợt 1 (cả 6 mùi hay chọn vài mùi) và hạn dùng sáp, viên, túi | Hai tinh dầu mẫu (QC1 18 tháng, Q100 24 tháng, đúng sổ tay) và một túi vỏ quế hạn «chưa có» |
| 3 | B-12 (+ B-10) | Có tính giá phụ liệu vào giá vốn không? Nếu có, phiếu nhập phụ liệu cần cột đơn giá | Không (theo BR-10); đổi cột thành «Giá quế / đơn vị», phiếu nhập phụ liệu không có cột giá |
| 4 | B-15 | Túi thơm 25 g (sổ tay) hay 50 g (mockup)? | 25 g theo sổ tay |
| 5 | C-01, C-02 | Trang QR công khai có hiện người mua (tên viết tắt, 3 số cuối SĐT, khu vực, kênh) không? | Bỏ (đúng TK §6.6, §8.4, BR-24); bỏ luôn ô tích ở màn Cài đặt |
| 6 | C-07 | Nhãn chai cuối gồm gì, khổ nào? | Tem mẻ 40 × 30 mm: mã lô, NSX, HSD; cách dùng và cảnh báo để cho nhãn hộp |
| 7 | C-18 | Có vẽ thêm danh mục «Tài khoản», «Chứng nhận» không? | Không, chỉ ghi chú «dùng chung khuôn danh mục» |
| 8 | A-05 | Thủ kho có xem lại tiền các phiếu mình đã lập trong ngày không? | Không (đúng chữ TK); bỏ cột «Tổng tiền» ở 06 và 10 |
| 9 | A-09 | Quy tắc đọc số: «1.180» là 1,18 hay 1180? | Dấu phẩy hoặc chấm đứng một mình luôn là thập phân; số từ 1000 gõ liền; hiển thị «1.180,5 kg» |
| 10 | A-03 | Quản lý bao bì (chai, nhãn, túi) trong phần mềm? | Không ở GĐ1–2; màn tồn kho có dòng xám «Bao bì: chưa quản lý» |
| 11 | A-04 | Trang chủ xưởng vẽ bản GĐ1 (3 nút) hay đầy đủ GĐ2 (4 nút + 3 nút nhỏ)? | Đầy đủ GĐ2, đánh dấu nút nào của GĐ2 |
| 12 | A-15 | Hiện mẻ đang ủ ngay ở «Xem tồn kho»? | Không; mẻ đang ủ chỉ ở màn Sản xuất |
| 13 | A-02 | (xác nhận) vẽ cả hai màn phụ liệu ở GĐ2? | Vẽ, đánh dấu GĐ2 |
Sếp duyệt toàn bộ mặc định (#429).

**Chuyển Lead / topic #2** (lỗi ở tài liệu thiết kế, không phải ở mockup): (a) công nợ nhà cung cấp có trong LT (đầu ra GĐ1) nhưng TK không có bảng hay màn; (b) TK mục 2 (WORKSHOP không xem bảng giá) mâu thuẫn mục 6.2 (giá hôm nay hiện dưới nút hạng ở màn nhập); (c) TK §6.1 nói 4 nút lớn, LT nói 3; (d) quy tắc đọc số chấm/phẩy cần ghi vào TK §6.2.

### 1.4 Quyết định khi gộp (mình tự chốt, không hỏi sếp)

- **Mã lô mẫu.** A-01 đề xuất `Q100-261120-01`, B-05 và C-03 đề xuất `QC1-261120-0x`. Chốt **Q100**: sản phẩm trên màn là «Tinh dầu quế Văn Yên 10 ml», hạn 24 tháng, khớp công thức Q100 (TK mục 4 seed: Q 100 g, ủ 0 ngày, hạn 24 tháng) nên ngày pha = ngày SX = 20/11/2026. Giữ đuôi số mẻ cũ để các màn nhất quán: `TP-TD10-2611-01` → `Q100-261120-01`, `TP-TD10-2611-02` → `Q100-261120-02`. Màn minh hoạ ủ (B-04, B-11) dùng ví dụ của sổ tay `QC1-261117-01` (mẻ pha 17/11, ủ 21 ngày), vì Q100 không ủ.
- **Giữ nguyên mã vấn đề** (không đánh số lại). Bảng sắp theo màn nên không bị nhảy mã; mã B-12 → B-15 → B-13 chỉ là thứ tự viết trong file gốc.
- **B-10 chỉ ở một chỗ**: gộp vào A-02, B-10 ghi nhận là cùng dòng. Câu hỏi giá vốn chỉ hỏi một lần (#3).
- **Trà** (A-17 và B-16): một dòng, mức medium.
- Sửa lỗi font «má»¥c» → «mục» ở nguồn A; bổ sung mã BR/AC/mục vào các chỗ nguồn A chỉ ghi «TK».

---

## 2. Quy ước đọc bảng

- Đường dẫn màn: `a/` = `de-xuat/man/a-nhap-xuat-kho/`, `b/` = `.../b-san-xuat/`, `c/` = `.../c-quan-ly-in-qr/`. `a/12:29` là file màn 12 dòng 29. `goc:87` là `goc/mockup-goc.html` dòng 87.
- `TK` = `docs/thiet-ke-chi-tiet.md` (số mục, mã BR/AC; không dùng số dòng vì topic #2 đang sửa). `LT` = `docs/lo-trinh-chuyen-doi-so.md`. `ST` = sổ tay «Công thức sản xuất Tinh dầu & Túi thơm Quế Văn Yên» (bản 2, 17/11/2026), «tr.N» là số trang.
- Mức: critical = sai hẳn nghiệp vụ; high = sai thiết kế đã chốt, lộ dữ liệu hoặc thiếu ở luồng chính; medium = lệch hoặc thiếu ở luồng phụ; low = dữ liệu mẫu, chữ.
- Cột «Đề xuất» là hướng sửa; chi tiết từng trường, từng câu chữ nằm trong file gốc cùng mã.

---

## 3. Bảng vấn đề theo thứ tự màn

### 3.0 Xuyên nhiều màn

| Mã | Màn | Mức | Sai gì | Căn cứ | Đề xuất |
|---|---|---|---|---|---|
| **A-01** = B-05 = C-03 | 12, 13, 14, 15, 17, 18, 24, 26 (cụm B); 27, 29, 36, 37, 38 (cụm C) | high | Mã lô thành phẩm theo mẫu cũ `TP-TD10-2611-02`. Mẫu đã bỏ; lô nay là `<mã công thức>-YYMMDD-NN` và TD10 là SKU, không cho biết công thức nào. Cũng sai chỗ ở B-05: mã sinh lúc **bắt đầu ủ**, không phải lúc hoàn thành. Ô tra cứu `c/27:17` còn placeholder `TP-…` | `a/12:29`, `a/13:29`, `a/14:29`; `b/15:21`, `b/17:46`, `b/18:21`, `b/24:31`, `b/26:19`; `c/27:19`, `c/29:38`, `c/36:55`, `c/37:55`, `c/38:55`. TK BR-20 (bảng mẫu mã, dòng «Lô thành phẩm (= mã mẻ)») và mục «Chốt mẫu mã lô thành phẩm»; ST tr.14 mục C.3 (`QC1-261117-01`) | Đổi theo quyết định ở 1.4: `-01` → `Q100-261120-01`, `-02` → `Q100-261120-02` ở mọi màn (giữ 145 tem, ngày SX, hạn). Màn 26 thêm cột «Công thức» và «Ngày pha» (TK `blend_date` khác `mfg_date`). Màn 16/17 nói rõ mã sinh khi bắt đầu ủ; `b/17:46` đổi «Đã tạo lô thành phẩm» thành «Mẻ … đã ủ xong, đã tạo lô thành phẩm». Placeholder `c/27:17`: «Mã tem, QC1-…, Q-…, NL-…, PN-…, PNP-…, PX-…, LSX-…, NCC-… hoặc NM-…» (TK §7.4). Tem lô phụ liệu theo mẫu `Q-2611-01` |
| **A-02** = B-10 | Thiếu; chỗ vào ở 03, 12–14, 02 | high | Không có chỗ nào cho kho phụ liệu: không nhập được phụ liệu, không xem tồn theo gram, không có danh mục phụ liệu. TK đã mô tả đủ (phiếu `PNP-YYMMDD-NNN`, lô `<mã phụ liệu>-YYMM-NN`, tồn `remaining_g`). Mockup chỉ có kho quế (kg) và thành phẩm | TK mục 6.5a, 6.5 (gạch «Phụ liệu»), mục 2 (dòng «Lập phiếu nhập phụ liệu»: WORKSHOP Có), mục 9 (API `/ingredient-receipts`, `/ingredient-lots`), BR-10 (phiếu nhập phụ liệu không có đơn giá), BR-20; ST tr.4. LT GĐ2 | Thêm `ingr-receipt` (`sau: receipt-list`): nơi bán, nút chọn phụ liệu (Q, QM, CAM, TTV, HH, HOI, DPG, SD, SO, TC…; **bỏ NUOC** vì không theo dõi tồn), gram, số lô NCC, hạn, đính COA; phụ liệu cần COA mà chưa có thì cảnh báo vàng, không chặn; không có cột giá. Thêm `ingr-stock` (`sau: inv-kk`) và tab «Phụ liệu» ở bộ tab 12–14 (`a/12:17`): lô, tổng gram còn, hạn gần nhất; lô dưới 60 ngày cam, quá hạn đỏ, chưa COA có chấm vàng. Màn 03 thêm hai tab «Quế» / «Phụ liệu». Màn 06 tái dùng cho phiếu phụ liệu. Danh mục phụ liệu và trường cần có: xem B-10 trong `b-san-xuat.md`. Mặc định #13 |
| **A-17** = B-16 | 10, 11 (bộ lọc); 23, 24 | medium | Trà quế (thực phẩm, cần giấy ATTP) xuất hiện trong bộ lọc sản phẩm (xưởng) và trong danh sách tạo lệnh sản xuất (chủ DN) ở GĐ1–2. LT xếp trà và bột vào GĐ4 (1–6/2028); sổ tay không có công thức trà; năm đầu chỉ tinh dầu, túi thơm, hộp quà | `a/10:23`, `a/11:23` (`#product`); `b/24:21` (option TRA100); `b/23:22` (ghi chú trà, bột), `b/23:23` (dòng TRA100 Nháp). BR-14, AC-17; LT GĐ4, GĐ2 (5–9/2027); `tom-tat.md` | Bỏ option Trà khỏi `#product` ở 10 và 11 (hoặc thay «Hộp quà 290.000 đ»). Màn 24 chỉ liệt kê sản phẩm có công thức đang dùng; TRA100 mờ kèm nhãn «GĐ4, chờ giấy tờ ATTP». Màn 23 giữ dòng Trà để minh hoạ BR-14, ghi chú giai đoạn sau |

### 3.1 Màn 01 – 02: Đăng nhập, trang chủ xưởng

| Mã | Màn | Mức | Sai gì | Căn cứ | Đề xuất |
|---|---|---|---|---|---|
| C-20 | 01 | low | Link «← Về trang chủ» dẫn về `/`, mà trang chủ lại đòi đăng nhập (vòng lặp). Không có mẫu «Sai tên đăng nhập hoặc mật khẩu» và «Tài khoản bị khóa 15 phút» (`#err` đang `hidden`) | `c/01:12`, `c/01:24`. TK §6.1 (nút này của màn con sau đăng nhập); TK §9 (Xác thực: khóa 15 phút sau 5 lần sai), §11 | Bỏ link ở màn đăng nhập. Thêm `01b` (khung đỏ «Sai tên đăng nhập hoặc mật khẩu. Còn 2 lần thử.») và `01c` («Tài khoản bị khóa 15 phút») |
| A-04 | 02 | medium | (a) Có 4 nút lớn + 3 nút nhỏ (`02:17-27`); TK §6.1 nói 4 nút lớn, LT nói 3, hai tài liệu đã lệch, mockup thêm 3 nút nhỏ. (b) «Sản xuất / đóng gói» (`02:20`) và «Gán tem / hủy tem» (`02:27`, href `/dong-goi`) là GĐ2 nhưng không đánh dấu. (c) Chưa có chỗ cho «Mẫu lưu» | `a/02:17-27`. TK §6.1; LT (trang đầu 3 nút lớn); TK §7.5 (dòng «Màn hình "Mẫu lưu" (OWNER, xưởng xem)») | Giữ 4 nút lớn theo TK §6.1. Ba nút nhỏ giữ nhưng gắn `data-gd="2"` hoặc chú thích để bản GĐ1 bỏ. Thêm nút nhỏ «Mẫu lưu». Nhập phụ liệu vào bằng tab trong «Nhập hàng» (A-02), không thêm nút, không thêm menu bên. Mặc định #11 |

### 3.2 Màn 03 – 06: Nhập hàng

| Mã | Màn | Mức | Sai gì | Căn cứ | Đề xuất |
|---|---|---|---|---|---|
| A-11 | 03 (+ 04) | medium | Nút «+ Người bán mới» (`03:25`) không có màn. Lưới người bán (`03:24`) không báo luồng hàng; luồng chỉ hiện sau khi chọn (`04:21`, tag «Vùng kiểm soát»). Xưởng không biết trước Thương lái Bình là hàng chung | `a/03:24-25`, `a/04:21`. TK §5 và §6.2 (người bán mới: tên*, kiểu*, thôn*, luồng mặc định GENERAL, chủ DN duyệt sau), BR-03, AC-03, AC-04 | Thêm `03b-receipt-newsup` (`sau: receipt-1`) kèm dòng «Người bán mới mặc định là hàng chung, chủ DN duyệt sau». Nút «Thương lái Bình» thêm tag «Hàng chung». Ở 04, khi chọn người bán GENERAL: tag «Hàng chung» thay «Vùng kiểm soát» (biến thể) |
| A-13 | 04 | low | Có sẵn `#line-warn` (`04:45`), `#price-banner` (`04:17`), `#manual-price-box` (`04:40`) nhưng không hiện trạng thái nào: giá lệch > 20%, chưa có giá hôm nay, chưa từng có giá | `a/04:17`, `:40`, `:45`. BR-04; TK mục 13 (ngưỡng 20% mặc định) | Thêm `04b-receipt-warn`: dòng 2 giá 52.000 đ/kg (bảng giá 38.000), `#line-warn` vàng «Giá lệch hơn 20% so với bảng giá, vẫn lưu được»; banner xám `#price-banner` ở `04:17` «Chưa có giá hôm nay, đang dùng giá ngày 19/11». Hai trạng thái còn lại để ghi chú |
| A-12 | 05 | medium | Lưu xong chỉ có banner «Đã lưu … 3 lô» (`05:55`), không có hộp thoại in: 1 phiếu nhập + 1 tem lô mỗi dòng (QR chứa mã NL-…; lô GENERAL thêm chữ «CHUNG» đậm). Bộ phận làm tem không thấy mẫu | `a/05:55`. TK §6.2 («Lưu và in»), §11 (QR ≥ 18 mm), §13 (khổ tem, mặc định 40 × 30); AC-01, AC-03 | Thêm `05b-receipt-print` (`sau: receipt-3`): xem trước 2 tem 40 × 30 («NL-2611-0007 · Vỏ quế · Loại 1 · 120,5 kg · 20/11/2026 · Gia đình (đồi nhà)» + QR; tem thứ hai có dải «CHUNG») và phiếu nhập A5. Phiếu có tiền (là phiếu đang lập), tem **không có giá** |
| A-05 | 06, 10, 11 | high | Quyền xem giá: TK loại mọi trường giá khỏi báo cáo của WORKSHOP, trừ chính phiếu đang lập. Màn 06 hiện tiền PN-005, PN-002, PN-001 (`7.460.100 đ`, `19.000.000 đ`, `6.562.500 đ`) nhưng «—» cho PN-004, PN-003; màn 10 hiện `300.000 đ` cho PX-001 mà «—» cho PX-004, PX-003, không rõ vì sao. Thủ kho xem lại được tiền phiếu cũ, vượt mức TK | `a/06:26` (cột 6), `a/10:28-29` (cột «Tổng tiền»). TK mục 2 (bảng phân quyền: báo cáo tồn kho «Có, không thấy giá», câu «trừ chính phiếu người đó đang lập»), mục 9 (API `/material-lots`: WORKSHOP bỏ trường giá), AC-06 | Bỏ cột «Tổng tiền» ở 06 và 10 cho WORKSHOP (hoặc mọi dòng «—»). Màn sau khi lưu (05) vẫn hiện tiền. Ở 11, dialog không có tiền, giữ; xoá ô trống `<td class="num"></td>` (`a/11:38`). Mặc định #8. Lưu ý thiết kế: TK mục 2 mâu thuẫn mục 6.2 (xem 1.3) |

### 3.3 Màn 07 – 11: Xuất hàng

| Mã | Màn | Mức | Sai gì | Căn cứ | Đề xuất |
|---|---|---|---|---|---|
| A-09 | 08 | medium | Ô số cân đang `value="1.180"` (`08:37`) khi chưa quét lô nào (`#picked` rỗng, «Lưu và in» `disabled`); các lô chỉ nặng 30 / 120,5 / 45 kg nên 1.180 kg không thuộc lô nào. «1.180» còn không rõ là 1,18 hay 1180 vì TK cho nhận cả phẩy và chấm thập phân | `a/08:35`, `a/08:37`. AC-06 (1.250 kg mua, 1.180 kg bán, OWNER thấy 94,4%); TK §6.2 | Chọn lô `NL-2611-0008` (Vỏ quế Loại 2, 45 kg) vào `#picked`, dòng mẫu «Vỏ quế Loại 2 · NL-2611-0008 · 42,5 kg · 50.000 đ · 2.125.000 đ», nút Lưu bật; `value="42,5"` (42,5/45 = 94,4%). Dòng phụ «94,4%» chỉ OWNER, không đặt ở màn xưởng. Quy tắc đọc số: mặc định #9; ghi vào TK §6.2 |
| A-10 | 08 | low | Loại bán đang chọn là Loại 2 (`08:34`) nhưng danh sách lô (`08:35`) lẫn lô «Loại 1» không có nhãn «mua là loại N»; không có lô hàng chung (tem in «CHUNG») để phân biệt | `a/08:34-35`. TK §6.3 cuối (nhãn xám «mua là loại 2»), §6.2 (tem GENERAL in «CHUNG»), AC-03 | Mỗi nút lô thêm `<span class="tag">` xám: NL-2611-0007 «mua là loại 1»; thêm lô mẫu hàng chung (Thương lái Bình) nhãn «CHUNG» đậm. Lô trùng loại bán không cần nhãn |
| A-07 | 09 | medium | (a) Banner tìm thấy người mua lặp hai lần giống hệt (`09:31`). (b) Nhãn `buyer-req` cố định «(bắt buộc tên + SĐT)» (`09:28`) chỉ đúng kênh Bán trực tiếp; sàn bắt buộc tên + tỉnh, không SĐT; đại lý, quà DN, xuất khẩu không bắt buộc. (c) Không có màn SĐT chưa có trong hệ thống (`#b-new` đang `hidden`, `09:32-41`) | `a/09:28`, `:31`, `:32-41`. TK §6.6 (mức bắt buộc theo kênh), BR-22, BR-23, AC-20, AC-21 | Xoá banner thứ hai `09:31`. Thêm `09b-issue-product-san` (Shopee, «(bắt buộc tên + tỉnh)», SĐT «không bắt buộc») và `09c-issue-product-moi` (hiện `#b-new`: họ tên, tỉnh/xã, số nhà, đồng ý Zalo/SMS). Thêm màn lỗi AC-21 (Website thiếu SĐT → banner đỏ «Cần tên và số điện thoại người mua»). Tên che «T T H» và SĐT hiện rõ lúc gõ là đúng, không sửa |
| A-08 | 09 | low | Chỉ có một lỗi quét mẫu («Đã quét trong phiếu này», `09:53`); TK liệt kê 6 lý do quét sai và lỗi BR-25 (đơn không có dòng nào không phải quà) | `a/09:53`. TK §6.4, BR-13, BR-25, AC-12 | Khung chú thích (hoặc màn phụ) với chữ 5 lỗi còn lại và lỗi BR-25. Không bắt buộc cho bản duyệt đầu |
| A-06 | 10, 11 | medium | Màn 10 không có cột «Người lập»; dialog 11 luôn có nút «Hủy phiếu» (`11:38`) cho PX-004 mà không nói phiếu của ai. BR-06: WORKSHOP chỉ hủy phiếu của mình trong ngày. Không có dòng «Đã hủy» mẫu (số phiếu nhảy: có 004, 003, 001, không có 002) | `a/10:28-29`, `a/11:38`; `a/06:26` (đã đúng). BR-05, BR-06, BR-19, AC-05; TK mục 2 (sửa/hủy phiếu «Có, chỉ phiếu của mình») | 10: thêm cột «Người lập» sau «Khách» (như `06:26`). 11: nút Hủy chỉ khi phiếu của mình và trong ngày; phiếu khác thay bằng chữ xám «Chỉ chủ DN hủy được». Thêm một dòng «Đã hủy» |
| A-14 | 11 | low | Dialog là đơn Shopee không có quà nên không thấy nhãn «Quà tặng» (BR-25); bảng dòng hàng không có tiêu đề cột và có ô `<td class="num"></td>` trống | `a/11:38`. TK §6.4 («Mở một đơn thấy…» dòng quà, từng serial), BR-25, AC-22 | Dialog chính cho đơn `PX-261120-001` (2 chai 150.000, quà tinh dầu «Quà tặng» 0 đ, thiệp); mỗi serial kèm mã lô và hạn dùng. Xoá hẳn cột giá cho WORKSHOP (A-05) |

### 3.4 Màn 12 – 14: Tồn kho

| Mã | Màn | Mức | Sai gì | Căn cứ | Đề xuất |
|---|---|---|---|---|---|
| A-15 | 13 | low | Chưa thấy cảnh báo cam (còn dưới 60 ngày) vì chỉ có một lô còn 24 tháng; «Số tem trong kho» không nói không gồm chai lưu mẫu; mẻ đang ủ không có chỗ trong tồn kho | `a/13:29`. TK §6.5 (cam dưới 60 ngày), §7.2 (CURING), §7.5 (chai lưu mẫu không dán tem, không tính `quantity`) | Thêm dòng mẫu thứ hai ở `13:29` (ví dụ `QC1-261117-01`, hạn còn 45 ngày, tô cam); chú thích dưới bảng «Số tem không gồm chai lưu mẫu». Mẻ đang ủ không hiện ở tồn kho (mặc định #12) |
| A-16 | 14 | low | Kiểm kê chỉ quét lô quế và thành phẩm; không nói lô nằm trong lệnh sản xuất (RESERVED, đã nêu ở 12: «1 lô, 22,5 kg») không tính vào danh sách chờ quét. Phụ liệu theo gram không kiểm được bằng quét tem | `a/14:32`. TK §6.5, AC-07, TK (vòng đời lô) | Thêm dòng xám ở banner `14:32` «Lô đang nằm trong lệnh sản xuất không tính vào kiểm kê». Kiểm kê phụ liệu để sau A-02 (mặc định: chỉ quế và thành phẩm) |
| A-03 | 12, 13, 14 (+ 03; thiếu) | medium | Bao bì (chai, nắp, túi, nhãn, hộp) không có trong thiết kế lẫn mockup. Sổ tay liệt kê chai hổ phách 100/500 ml, chai thành phẩm 10/30 ml nút nhỏ giọt, nhãn; TK chỉ quản lý phụ liệu theo gram và loại bao bì khỏi giá vốn. Kho đếm cái không có bảng nào, hết chai/nhãn phần mềm không báo | TK BR-10 (giá vốn chỉ quế), TK mục 4 (định nghĩa phụ liệu «quản lý theo gram»), TK mục 13 (câu hỏi «giá vốn có tính bao bì và phụ liệu không», mặc định không); ST tr.3, tr.14 | Không vẽ kho bao bì ở GĐ1–2. Màn tồn kho phụ liệu mới (A-02) có dòng xám «Bao bì (chai, túi, nhãn): chưa quản lý trong phần mềm GĐ1–2». Phương án thay: coi bao bì là phụ liệu đếm theo cái (`unit='cái'`), cần sửa TK và BR-10. **[SẾP QUYẾT]** #10 |

### 3.5 Màn 15 – 18: Sản xuất (xưởng)

| Mã | Màn | Mức | Sai gì | Căn cứ | Đề xuất |
|---|---|---|---|---|---|
| B-04 | 15, 16, 17 | high | Vòng đời lệnh chỉ Nháp → Hoàn thành; không có giai đoạn ủ: tinh dầu 21/28 ngày, hương nền ≥ 14, dung dịch tẩm 48 giờ, sáp 14, viên 7, túi 5–7, dầu quế 4–6 tuần | `b/16:17` (tag «Nháp»), `b/17:17` (tag «Hoàn thành»), `b/15:19`. ST tr.6 (A.1 bước 4), tr.8 (A.5), tr.9–10, 12–13; TK §7.2 (CURING, «Đã pha xong, bắt đầu ủ», «Còn N ngày», «Ủ thêm», `cure_check_note`), BR-28 | Màn 16: nút «Đã pha xong, bắt đầu ủ» → hiện ngày bắt đầu và ngày sớm nhất xong, tem mẻ cho lọ ủ, khoá dòng nguyên liệu. Tag «Đang ủ». Màn 15 và 24: thẻ CURING có mã công thức, ngày dự kiến, «Còn N ngày». Màn 17: «Hoàn thành» chỉ sáng khi đủ ngày; chưa đủ thì «Mẻ QC1-261117-01 còn 6 ngày mới đủ ủ». Chi tiết theo dõi: B-11 |
| B-17 | 15, 24 (+ 16) | low | Cùng lệnh LSX-2611-003: màn 15 «1 lô đã quét», màn 24 «2 lô đã quét», màn 16 liệt kê 2 lô | `b/15:19`, `b/24:29`, `b/16:25` | Thống nhất dữ liệu mẫu; nếu làm theo B-01 thì thẻ đổi thành «đã nhập 3/4 thành phần» hoặc «ngày xong ủ dự kiến …» |
| B-01 | 16 | **critical** | Lệnh Túi thơm 50 g chỉ có 3 bước: quét tem lô quế «đem sàng», chọn Loại sau sàng, nhập kg và số lượng. Vẫn là mô hình sàng quế khô, không có công thức, phụ liệu, ủ. Sản phẩm thật là hỗn hợp pha theo gram (túi 25 g = vỏ quế cắt hạt 12 g + dăm gỗ 8 g + thạch cao 5 g + dung dịch tẩm 2,5 g; tinh dầu = 3–4 loại pha theo %) | `b/16:20` («Quét tem các lô nguyên liệu đem sàng»), `:29` («Chọn loại sau sàng lọc»), `:33-39`. ST tr.1, tr.6–8, tr.12. TK §7.2: 4 bước «chọn công thức và cỡ mẻ → đưa nguyên liệu vào (cân từng gram) → ủ → nhập đầu ra»; công thức `TUI` và `SC-VQH` (TK mục 4) | Dựng lại theo 4 bước TK §7.2: (1) công thức và cỡ mẻ (B-02); (2) nguyên liệu theo gram (B-03), lô quế chỉ khi công thức cần quế thô; (3) ủ (B-04); (4) đầu ra. Bước «Chọn loại sau sàng lọc» chỉ cho lệnh có lô quế đưa thẳng vào; túi thơm lấy vỏ quế từ bán thành phẩm VQH nên không hiện bước này |
| B-03 | 16 | high | Không có chỗ quét tem lô phụ liệu và gõ gram thực tế. Sổ tay: cân 0,01 g, TARE từng nguyên liệu, sai số ±0,05 g, lỡ tay ghi số thật, ghi ngay vào sổ lô. Mockup chỉ có lô quế tính kg «không cân lại» | `b/16:20-27`. ST tr.4–5 (quy tắc 1–3, 5), tr.14 C.3; TK §7.2 «Đưa nguyên liệu vào» (cảnh báo vàng lệch > ±0,05 g, từ chối sai phụ liệu, hết tồn, quá hạn; cảnh báo chưa COA), BR-26, BR-27, AC-25, AC-26 | Mỗi dòng công thức: tên phụ liệu, gợi ý (g), ô quét tem lô, ô gram thực tế, trạng thái (đủ / thiếu / lệch). Banner vàng lệch > 0,05 g, cam chưa COA; bột màu «tùy chọn»; «+ Thêm dòng ngoài công thức» (đồ trang trí sáp 3–5 g). Đổi tiêu đề bước 1 thành «Quét tem lô quế (cả lô, không cân lại)» |
| B-06 | 17 | high | Ví dụ «Mẻ chưng cất số 2»: 125 kg → 2,4 kg → 200 chai, hiệu suất 1,92%, hoàn thành ngay ngày lệnh. Sai ba chỗ: sổ tay không có bước chưng (dầu nhận từ gia đình rồi lắng, ủ 4–6 tuần, tr.8); 1,92% là hiệu suất chưng dầu, gắn vào chai pha là sai nghĩa (TK để `yield_pct` NULL khi không có quế); số lệch (100 ml pha ≈ 89,7–92,2 g ra khoảng 9 chai 10 ml, nên 200 chai ≈ 2,0 kg) | `b/17:17`, `b/17:46`. ST tr.5, 6 (A.2), 8; TK §7.4 (hiệu suất tính trên lệnh làm ra bán thành phẩm), TK mục 4 (công thức chưng «không seed» đến khi chủ DN chốt) | Đổi ghi chú thành «Mẻ Q100» (hoặc mẻ khác theo công thức). Với lệnh dùng phụ liệu bỏ ô «hiệu suất», thay bằng tổng gram phụ liệu, số chai, ngày pha, ngày xong ủ. Giữ KPI hiệu suất cho lệnh bán thành phẩm từ quế. Ngày SX mẫu cách ngày pha theo thời gian ủ của công thức (Q100 không ủ). **[SẾP QUYẾT]** #1 |
| B-08 | 17, 26 | high | Sau hoàn thành đi thẳng sang gán tem; không có bước lưu mẫu. Sổ tay: lưu 1 chai 10 ml mỗi lô trong 12 tháng. Màn 26 không có cột «Mẫu lưu» | `b/17:46` (chỉ nút «Sang bước gán tem»), `b/26:18`. ST tr.6 (A.1 bước 8); TK §7.5 (hỏi «Đã lấy chai lưu mẫu chưa?» + vị trí; chai lưu mẫu không dán tem, không tính `quantity`; «Lô chưa lưu mẫu»; «Xem mẫu lưu»), BR-29, AC-34, AC-35 | Màn 17: khối «Chai lưu mẫu» (vị trí tủ/kệ, nút Lưu); chưa lưu hiện «Chưa lưu mẫu», **không chặn** gán tem; ghi «200 chai là số bán được, chưa gồm chai lưu mẫu». Màn 26: cột «Mẫu lưu» (Giữ đến dd/mm/yyyy / Chưa lưu / Đã hủy); lô RECALLED không cho hủy mẫu. Màn mới «Mẫu lưu» (OWNER, xưởng xem): lô, vị trí, ngày lưu, giữ đến; dưới 30 ngày cam; «Hủy mẫu» khi hết hạn. Chỉ cho sản phẩm có cờ lưu mẫu (6 công thức tinh dầu khuếch tán) |
| B-18 | 18 | low | Màn khớp TK §7.3 và BR-12 (quét tem đầu và cuối, «Đã gán 150 / 200», 4 lý do hủy; 145 trong kho + 5 đã xuất = 150 khớp màn 26). Chỉ thiếu dòng nhắc chai lưu mẫu không dán tem, và chưa có nhãn thành phẩm in ra (mã lô, NSX, HSD, cách dùng, cảnh báo) | `b/18:28-37`. TK §7.3, BR-12; ST tr.15 (nhãn) | Thêm dòng «Chai lưu mẫu không dán tem» (B-08); đổi mã lô theo A-01; nhãn thành phẩm xem C-07 |

### 3.6 Màn 19 – 22: Trang chủ chủ DN, người bán

| Mã | Màn | Mức | Sai gì | Căn cứ | Đề xuất |
|---|---|---|---|---|---|
| C-14 | 19, 31 | medium | Không có lối vào cho việc của topic #2: «Lô chưa lưu mẫu» ở trang chủ OWNER, màn «Mẫu lưu», công thức, phụ liệu, phiếu nhập phụ liệu, thử lưu hương. Nhóm «Danh mục» của 31 thiếu «Công thức», «Phụ liệu». Cũng thiếu thẻ «Đang ủ», «Mẫu sắp hết hạn lưu» (B-04, B-08) | `c/19:24-35`, `c/31-admin.html` (các link `/quan-ly/…`). TK §7.5, §7.2, mục 3 | Sau khi topic #2 chốt tên route: thêm vào 31 «Công thức», «Phụ liệu & phiếu nhập phụ liệu», «Mẫu lưu», «Thử lưu hương»; thêm vào 19 banner cam «Lô chưa lưu mẫu: N», thẻ «Đang ủ» |
| C-19 | 19 | low | Gộp GĐ1 và GĐ2, không đánh dấu giai đoạn: tile Cuộn tem, Lô thành phẩm, Khách hàng đã mua có ngay từ đầu. Sếp khó thấy phần nào giao ở giai đoạn nào | `c/19:26-35`. LT (GĐ1 dòng 106, GĐ2 dòng 108); `tom-tat.md` (người mua cuối lộ trình không nhắc) | Nhãn nhỏ «GĐ2» trên các tile thuộc GĐ2; không đổi cấu trúc |
| C-04 | 19, 31, (thiếu) | high | Thiếu màn «Vùng nguyên liệu» (OWNER): bản đồ đồi (Leaflet + OpenStreetMap), bảng đồi (xã, thôn, diện tích, năm trồng, kg mua 12 tháng, hiệu suất TB), đồi thiếu tọa độ/ảnh gắn «thiếu thông tin truy xuất». Menu 31 có link nhưng route trỏ `null`; 19 không có ô vào. Dữ liệu mẫu đã có: hai đồi của NCC-CQ-001 «thiếu tọa độ / ảnh» | `goc:87` (`[/^\/quan-ly\/vung-nguyen-lieu/, null]`), `c/31-admin.html:36`, `c/19:26-35`, `c/22:32`. TK §7.1; LT GĐ2 («khai báo vùng») | Thêm `41-vung-nguyen-lieu.html` (nhóm Chủ DN): khung bản đồ giữ chỗ có ghim «Leaflet + OpenStreetMap», bảng đồi từ dữ liệu mẫu (D-CQ-001-01 Thôn 3, 2,5 ha, 2012; D-CQ-001-02 Khe Hùm, 1,2 ha, 2016; đồi của NCC-DC-001, NCC-CQ-002), nhãn cam «thiếu thông tin truy xuất», lọc theo xã. Tile «Vùng nguyên liệu» ở 19. Thêm route và `_ds.json` |
| C-13 | 19, 21, 22 | medium | Banner ở 19 «1 người bán chờ duyệt» dẫn tới 21; ở 21 dòng NCC-CQ-003 có tag «Chờ duyệt» nhưng không có nút duyệt; hộp sửa (22) mở cho NCC-CQ-001 đã duyệt nên không thấy luồng. «+ Thêm đồi» không có tọa độ, ảnh, đồi mặc định | `c/19:24`, `c/21:23`, `c/22:32` (dialog chỉ Đóng/Lưu). TK §5 (hàng «Nhà cung cấp», «Đồi quế», duyệt người bán mới), API `POST /suppliers/{id}/approve`, BR-03 | Thêm `22b`: hộp sửa NCC-CQ-003 có nút «✔ Duyệt» cạnh Lưu và dòng «Đến khi duyệt, lô của người bán này luôn là hàng chung (BR-03)»; dòng mở rộng của «+ Thêm đồi» có ô tọa độ, nút ảnh, ô tích «Đồi mặc định» |

### 3.7 Màn 23 – 26: Sản phẩm, lệnh (chủ DN), cuộn tem, lô

| Mã | Màn | Mức | Sai gì | Căn cứ | Đề xuất |
|---|---|---|---|---|---|
| B-07 | 23 | high | (1) Không có cột công thức mặc định. (2) Danh sách không khớp sổ tay (khuếch tán 6 công thức × chai 10/30 ml, quế 100% 10 ml, sáp, viên + refill, túi vỏ quế): mockup có TD10, TT50, TRA100, THIEP; không rõ TD10 là loại nào. (3) Hạn dùng: TT50 12 tháng không có căn cứ; sổ tay khuếch tán 18 tháng, quế 100% 24 tháng, sáp/viên/túi không ghi. (4) Thiếu «cách dùng và cảnh báo» in nhãn (4–5 giọt/100 ml nước; không bôi da, không uống, xa trẻ em và thú cưng) | `b/23:23`. ST tr.5–15 (tr.6, 8, 14–15); TK `product` (`recipe_code`, `shelf_life_months`, `usage_md`); TK mục 13 (danh sách sản phẩm đợt 1 còn mở) | Thêm cột «Công thức» và ô chọn trong form sửa. Dữ liệu mẫu: `TD-QC1-10` «Tinh dầu Quế Cam dịu nhẹ 10 ml» (18 tháng), `Q100-10` «Tinh dầu Quế Văn Yên 100% 10 ml» (24 tháng), một túi vỏ quế hạn «chưa có». Hạn sáp/viên/túi hiện «chưa có». Thêm «Cách dùng và cảnh báo». **[SẾP QUYẾT]** #2 |
| B-02 | 24 | high | Form chỉ có Sản phẩm, Ngày, Ghi chú. Thiếu công thức (6 công thức tinh dầu; hương nền chọn TT1 hoặc TT2; sáp, viên, dung dịch tẩm chọn một trong hai), cỡ mẻ (gram) và lựa chọn làm bán thành phẩm | `b/24:20-25`. ST tr.6–10; TK §7.2 «Tạo lệnh (OWNER)» (sản phẩm hoặc bán thành phẩm, công thức ACTIVE, nhóm lựa chọn, `target_batch_g`) | Thêm: «Làm gì» (Sản phẩm / Bán thành phẩm); công thức (mặc định phiên bản ACTIVE); nút TT1/TT2 nếu có nhóm lựa chọn; cỡ mẻ (g) mặc định mẻ chuẩn kèm xem trước lượng cân (QC1 cỡ 897,2 g → 314,0 / 89,7 / 493,5 g, ST tr.6) |
| C-11 | 25 | medium | CT-2611-02 có «Đã xuất: 5», «Trong kho: 145» (đã gán lô, đã dán) nhưng ô «Đã in» là «chưa in»; CT-2611-01 «Thu hồi: 20» cũng «chưa in». Tem chưa in thì không thể xuất hay thu hồi | `c/25:25` | Ghi «đã in 1–300» (CT-2611-02), «đã in 1–50» (CT-2611-01); giữ «chưa in» cho một cuộn mới (thêm CT-2611-03, 100 tem, toàn «Chưa gán»). Số cộng đã đúng (145+5+150 = 300; 20+29+1 = 50) |
| B-12 | 26 | medium | Cột «Giá vốn NL» 28.125 đ/chai chỉ là tiền quế chia số chai (125 kg × 45.000 ÷ 200) cho tinh dầu pha từ 3–4 loại tinh dầu; dễ bị hiểu là giá vốn thật. Cột «Hiệu suất» vô nghĩa với lô chỉ dùng phụ liệu | `b/26:18-19`. BR-10 (giá vốn chỉ gồm quế); TK mục 13 (có tính phụ liệu, bao bì không); `yield_pct` NULL khi không có quế | Đổi tên cột «Giá quế / đơn vị»; «—» ở lô chỉ dùng phụ liệu; Hiệu suất «—» khi không có quế. **[SẾP QUYẾT]** #3 (kéo theo cột đơn giá ở phiếu nhập phụ liệu, A-02) |
| B-13 | 26 | medium | Chỉ một dòng mỗi lô; không có chỗ xem lại mẻ. Sổ ghi lô sổ tay gồm: mã lô, ngày pha, công thức, lô tinh dầu quế dùng, gram thực tế (đính phiếu cân), ngày xong, số lượng, người làm, ghi chú | `b/26:19`. ST tr.14 C.3; TK §7.4 (tra cứu ngược) | Màn «Chi tiết mẻ» mở từ 26: công thức, ngày pha, ngày xong ủ, người làm; bảng gram thực tế so với gợi ý theo từng lô phụ liệu; kết quả ngửi kiểm tra; số lượng; mẫu lưu; nút Thu hồi. Dùng chung dữ liệu với tra cứu 27 |
| B-15 | 16, 23, 26 | medium | Số liệu túi thơm lệch sổ tay: lệnh mẫu 52,5 kg vỏ quế → 9,8 kg → 180 túi, quy cách 50 g. Sổ tay: túi 25 g, 40 túi dùng 480 g vỏ quế (12 g/túi) + dăm gỗ, thạch cao, dung dịch tẩm; 52,5 kg ra khoảng 4.000 túi. Chưa có đơn vị «viên», «tấm» | `b/16:25-26` (30 + 22,5 kg), `:35` (9,8), `:36` (180); `b/23:23` (TT50, 50 g). ST tr.12 | Số mẫu theo công thức TUI (mẻ 40 túi: VQH 480 g, DG 320 g, HT 200 g, DDT 100 g, tổng 1.100 g). `unit` theo sản phẩm (chai / túi / viên / tấm). **[SẾP QUYẾT]** #4 |

### 3.8 Màn 27 – 32: Tra cứu, khách, quản lý, cài đặt

| Mã | Màn | Mức | Sai gì | Căn cứ | Đề xuất |
|---|---|---|---|---|---|
| C-08 | 27 | medium | Tra cứu xuôi không có ô chọn lô, nút «Thu hồi các lô đã chọn» và nút «Xem mẫu lưu»; AC-23 (thu hồi rồi tra cứu xuôi thấy đủ người mua) cần luồng này | `c/27:19` (bảng «Lô thành phẩm»). TK §7.4, §7.5; AC-15, AC-23 | Thêm cột ô tích, nút đỏ «Thu hồi các lô đã chọn» dưới bảng, nút nhỏ «Xem mẫu lưu» ở dòng lô (vị trí, hạn giữ). Tên màn «Mẫu lưu» theo topic #2 |
| C-09 | 27 | medium | Cây truy xuất chỉ có nhánh quế (Lô NL → Người bán → Lệnh → Lô TP → Phiếu xuất → Người mua cuối); thiếu nhánh lô phụ liệu (qua `production_ingredient`; nguồn là PNP- hoặc lệnh làm ra) và dòng «nguồn ngoài, chưa nối về lô quế» cho dầu quế mua ngoài | `c/27:19`. TK §7 đầu mục, §7.4 mục «Ngược» và «Dầu quế nối về lô quế», BR-31, AC-30..32 | Thêm khối «Lô phụ liệu» ở chiều ngược (Q-2611-01 ← lệnh ủ U-Q ← QM-2610-02 ← lệnh chưng ← NL-…; CAM-2609-01 ← PNP-… ← nơi bán) và dòng vàng «nguồn ngoài, chưa nối về lô quế». Đổi nhãn theo kết quả topic #2 |
| C-10 | 27, 30 (đối chiếu 26) | medium | Dữ liệu mẫu mâu thuẫn: ở 27, NL-2611-0007 (120,5 kg, PN-261120-005) thuộc NCC-CQ-001; ở 30, 120,5 kg là của Nguyễn Văn Hùng (NCC-CQ-002), NCC-CQ-001 chỉ 85 kg. Ở 26, lô -01 giá vốn 271.125 đ = 5.422.500 đ / 20 chai (120,5 kg vào lô -01) nhưng 1,2 kg ra 20 chai (60 g/chai) trong khi lô -02 là 1,63 kg ra 200 chai (≈ 8 g/chai) | `c/27:19`, `c/30:24`, `b/26:19` | Ở 27 chuyển NL-0007/0008/0009 sang NCC-CQ-002 (hoặc sửa 30); sửa lô -01 còn khoảng 0,18 kg hoặc tăng lên khoảng 130 chai. Chốt cùng #24 để 26 khớp |
| C-15 | 28 | low | Thiếu lọc theo tỉnh/xã; nút «⬇ CSV khách đồng ý nhận tin» không báo file có tên và SĐT đầy đủ | `c/28:17-26`. TK §6.6 (lọc sản phẩm, kênh, ngày, tỉnh), API `area_id`, BR-24 | Ô «Tỉnh / xã» cùng khuôn `select` «Kênh»; đổi nhãn «⬇ CSV (SĐT đầy đủ, ghi nhật ký)» |
| C-16 | 29 | low | Dòng tóm tắt in `L M T ·  · Lào Cai` (dấu nối thừa) khi NM-000003 không có SĐT (đúng BR-22, Shopee); sau «Xem đầy đủ» không thấy dòng xác nhận đã ghi nhật ký | `c/29:38`. BR-22, BR-24 | Bỏ dấu nối khi trường trống, ghi «SĐT: (sàn không cung cấp)»; thêm «Đã ghi nhật ký: Chủ DN, 20/11/2026 19:52» |
| C-18 | 31 | low | Mới có 3 màn danh mục (người bán, sản phẩm, cài đặt); sáu mục («Tài khoản», «Địa bàn», «Khách hàng», «Nguyên liệu & hạng», «Loại hàng hóa», «Chứng nhận») rơi về nhánh dự phòng `/quan-ly → admin`, bấm không đổi màn, tưởng lỗi | `c/31-admin.html` (9 link danh mục), `goc:88`. TK §5 (9 danh mục chung một khuôn), TK mục 2 («Quản lý tài khoản» chỉ OWNER) | Vỏ hiện gợi ý «màn này dùng chung khuôn danh mục, chưa vẽ». **[SẾP QUYẾT]** #7 |
| C-02 | 32, 37 | high | (a) Ô tích «Trang truy xuất hiện người mua khi sản phẩm đã bán» đang `checked`; không có trong danh sách setting và mâu thuẫn BR-24. (b) Màn 37 hiện «● Chưa bán» cho serial IN_STOCK; TK xếp IN_STOCK và ISSUED chung một nội dung, khách mua qua kênh chưa quét xuất kho sẽ đọc nó như tem lạ | `c/32:23`, `c/37:61-66`. TK §8.4, BR-24 | Bỏ ô tích ở 32. Ở 37 bỏ khối «Tình trạng bán»; khi đó 37 trùng 36, nên 36 đại diện IN_STOCK và ISSUED, dùng slot 37 cho màn «quét N lần quá ngưỡng» (C-05). Cùng quyết định C-01 (#5) |
| C-22 | 32 (+ 25) | low | Nhãn «CHỐT TRƯỚC KHI IN CUỘN ĐẦU» và banner ở 25 nói đã in thì không đổi, nhưng ô tên miền vẫn sửa được dù đã có cuộn có tem xuất. Đổi tên miền làm hỏng mọi QR đã in | `c/32:23` (input không `disabled`), `c/25:19`. TK mục 13 | Ô tên miền chỉ đọc kèm «Đã in cuộn đầu tiên ngày 20/11/2026, không đổi được» |

### 3.9 Màn 33 – 35: Mẫu in

| Mã | Màn | Mức | Sai gì | Căn cứ | Đề xuất |
|---|---|---|---|---|---|
| C-17 | 34 | low | Phiếu xuất in giao khách hiện mã kênh thô `DIRECT`; 28 dùng «Bán trực tiếp» | `c/34:53`. (Nhãn «Quà tặng», tổng 300.000 đ (AC-22), che tên/SĐT (AC-24) đã đúng) | Đổi thành «Bán trực tiếp» |
| C-07 | 35 (+ thiếu mẫu in nhãn lô) | medium | Tem serial ở 35 chỉ có QR, tên, «Quét xem nguồn gốc», mã serial, `CT-2611-02 · n` (đúng TK §7.3) và không thể có mã lô vì cuộn in trước, gán lô sau. Nhưng sổ tay yêu cầu nhãn có mã lô, NSX, HSD, cách dùng, cảnh báo; TK §7.2 «in tem mẻ để dán lên lọ ủ». Nhóm Mẫu in chưa có nhãn nào mang mã lô | `c/35:51-56`. TK §7.2, §7.3, mục 13 (khổ tem serial và tem lô); ST mục C.3 và đoạn nhãn (tr.15) | Thêm mẫu in «Tem mẻ / nhãn lô» (`42-print-batch.html`, dùng lại CSS `.tem`): mã lô `Q100-261120-02` (chữ lớn + QR chứa mã lô như tem NL), tên sản phẩm, NSX, HSD. Ghi chú: tem serial không in mã lô. Cách dùng, cảnh báo dài để cho nhãn hộp. **[SẾP QUYẾT]** #6 |
| C-12 | 35 | medium | Mã serial bị `<br>` ngắt thành «MKWX-142J» / «RH» (2 ký tự một dòng), khó đọc, không khớp chuỗi mã ở 25/29/36; QR ≥ 18 mm nên chữ còn khoảng 17,8 mm | `c/35:54` (`MKWX-142J<br>RH`, font 6,6 pt, `letter-spacing:-.2pt`). TK §7.3 (mã dạng `K7Q2-MX9P-AT`), §11 | Mã trên một dòng, font 5,6 pt, bỏ `<br>`; hoặc ngắt có chủ ý «MKWX-» / «142J-RH». Nhờ Dev in thử trên máy in tem thật (TK §11) |

### 3.10 Màn 36 – 40: Trang QR khách

| Mã | Màn | Mức | Sai gì | Căn cứ | Đề xuất |
|---|---|---|---|---|---|
| C-01 | 36, 38 | high | Khối «Tình trạng bán» hiện ngày bán, kênh mua, người mua `T T H`, SĐT `*******222`, khu vực. TK: thông tin người mua không bao giờ xuất hiện trên website hay trang truy xuất, kể cả bản che. Tem in sẵn cả cuộn, ai quét cũng thấy dữ liệu của người đã mua | `c/36:60-77`, `c/38:60-77` (ghi chú che `c/36:74`). TK §6.6 «Dữ liệu cá nhân», §8.4 (danh sách nội dung công khai; «Tuyệt đối không hiện… tên khách hàng, mã phiếu»), BR-24, BR-17, AC-13 | Xoá khối «Tình trạng bán» ở 36 và 38. Giữ thứ tự TK §8.4: chính hãng → ảnh/tên → mã lô, NSX, HSD → vùng nguyên liệu → hộ trồng (nếu đồng ý) → chứng nhận → câu chuyện → mua lại → số lần quét. 38 giữ khung đỏ thu hồi + thông tin sản phẩm + lô. **[SẾP QUYẾT]** #5 (nếu sếp chủ ý giữ phải sửa TK §6.6, §8.4, BR-17, BR-24, AC-13) |
| C-05 | 36–40 | medium | Thiếu các trạng thái ngoài «hợp lệ»: «Mã không có trong hệ thống», «Mã đã bị hủy» và cảnh báo «quét N lần, lần đầu dd/mm/yyyy». Ngưỡng 20 đã có ở 32 nhưng không màn nào dùng. Hiện có hợp lệ (36), thu hồi (38), UNASSIGNED (39), nhập tay (40) | TK §8.4 (bảng trạng thái), BR-18; `c/32:23` | Thêm `q-notfound`, `q-void`, `q-many-scans` (bản 36 có khung vàng), cùng khuôn 39; câu chữ nguyên văn bảng TK §8.4 |
| C-06 | 36, 37, 38 | medium | Không có ảnh sản phẩm và ảnh đồi (TK: «ảnh, tên sản phẩm» và tối đa 3 ảnh đồi); không có thẻ `<img>` hay khung giữ chỗ | `c/36:49-52`, `c/36:82-93`. TK §8.4 | Khung ảnh sản phẩm 1:1 và dải 3 ô «ảnh đồi» (hộp xám có chữ), không dùng ảnh thật |
| C-21 | 36, 37 | low | Chứng nhận mẫu «OCOP 4 sao, OCOP-LC-2027-015 (hiệu lực đến 01/10/2029)» cho tinh dầu khi ngày mẫu là 20/11/2026; OCOP thuộc GĐ4 (1–6/2028), chưa nộp hồ sơ; dễ bị hiểu là đã có | `c/36:99`, khối «Chứng nhận» của 37. LT GĐ4 | Ghi «(ví dụ)» hoặc đổi sang chứng nhận có thể có sớm (phiếu công bố sản phẩm) |

---

### 3.11 Màn thiếu theo sổ tay (cụm B, GĐ2; chưa có file màn)

Cả ba cần thêm file màn, `_ds.json` và route vỏ. Trường chi tiết từng màn xem `nhan-xet/b-san-xuat.md` cùng mã.

| Mã | Màn | Mức | Sai gì | Căn cứ | Đề xuất |
|---|---|---|---|---|---|
| B-09 | Khai công thức (OWNER), thiếu; lối vào từ 31 (C-14) | high | Không có màn nào khai công thức, trong khi lệnh sản xuất (B-01, B-02) và sản phẩm (B-07) đều dựa vào công thức: mã, tên, đầu ra, phiên bản, mẻ chuẩn (g), ngày ủ tối thiểu, thành phần theo gram và % khối lượng | ST tr.6–13 (bảng gram theo mẻ 100 ml và 1 lít); TK mục 4 (bảng `recipe`, `recipe_item`, seed QC1 = TTV 31,40 + Q 8,97 + CAM 49,35 = 89,72 g), BR-26, AC-37 | Danh sách công thức (mã, tên, đầu ra, phiên bản, mẻ chuẩn, ủ tối thiểu, trạng thái nháp / đang dùng / ngừng; mỗi mã một phiên bản đang dùng). Form: mã*, tên*, đầu ra*, bán thành phẩm làm ra*, nhãn mẻ, ủ tối thiểu*, ủ tối đa (tham khảo), lưu mẫu (tháng), ghi chú bước làm. Bảng thành phần: phụ liệu*, gram*, % tự tính, nhóm lựa chọn TT1/TT2, tùy chọn (bột màu). Lưu: thành phần bán thành phẩm phải có công thức riêng; phiên bản đang dùng không sửa tại chỗ mà nhân bản thành phiên bản mới |
| B-11 | Theo dõi ủ và ngửi kiểm tra, thiếu; hiện ở 15, 19, 24 | high | Không có màn theo dõi mẻ đang ủ: ngày bắt đầu, ngày sớm nhất xong, «Còn N ngày», lịch lắc chai (tinh dầu 3 ngày một lần), ngửi kiểm tra cuối ủ, ủ thêm. Chưa có chỗ ghi OWNER bỏ qua kiểm tra ngày ủ | ST tr.6 (A.1 bước 4 và 6), tr.8 (A.5); TK §7.2 (bắt đầu ủ, «Ủ thêm» +7 ngày, `cure_check_note`), BR-28, AC-27 | Danh sách đang ủ (mã mẻ, công thức, ngày, «Còn N ngày», nhắc lắc chai). Chi tiết mẻ: tick từng lần lắc, nút «Ngửi kiểm tra». Ngửi kiểm tra: nhúng que thử, ngửi ngay, sau 1 giờ, sau 4 giờ, so mẫu chuẩn; kết luận «đạt» hoặc «còn gắt, ủ thêm 7 ngày» (nút «Ủ thêm» ghi lý do). OWNER bỏ qua kiểm tra ngày ủ bắt buộc ghi lý do. Liên quan B-04 |
| B-14 | Thử lưu hương 28 ngày, thiếu | high | Không có màn đợt thử lưu hương cho sáp thơm, viên thạch cao, túi vỏ quế. Chỉ khi có số lưu hương đo thật mới được in lên bao bì | ST tr.13 C.1, tr.14 C.2; TK §7.5 và bảng `scent_trial*`, BR-30, AC-36; LT:13 và LT:236 (GĐ2) | Danh sách đợt thử (mã `TL-2611-01`, công thức, mục tiêu, ngày bắt đầu, trạng thái). Mẫu: mỗi biến thể 3 mẫu ở 3 nơi (tủ kín, ô tô, phòng). Lưới ngày 0, 1, 3, 7, 14, 21, 28: khối lượng (g, cân 0,01 g) và điểm từng người ngửi (cường độ 1–5, độ dễ chịu 1–5), người ngửi không thấy điểm người khác, in được phiếu chấm. Đánh giá 4 tiêu chí (ngày 1 cường độ ≤ 4; ngày 28 trong tủ kín ≥ 2,5; dễ chịu TB ≥ 3,5; mất khối lượng 3 ngày đầu ≤ 1/3 tổng 28 ngày), đạt cả 4 là PASS. Tinh dầu khuếch tán thử cách khác (phút 5, 30, 60) mà TK chưa lưu: ghi vào câu hỏi mở |

**Tham chiếu chéo** (các mã đã có dòng đầy đủ ở mục khác, không lặp lại):

- A-01 (mã lô) ở 3.0, ảnh hưởng 12–14, 26, 36–38. A-02 (kho phụ liệu) và A-17 (trà) ở 3.0, ảnh hưởng 03, 10–14, 23, 24.
- B-08 (mẫu lưu) ở 3.5; cột «Mẫu lưu» của 26 là phần của B-08. B-17 (số lô đã quét lệch ở 15, 24) ở 3.5.
- B-05, B-10, B-16, C-03 gộp vào A-01, A-02, A-17.

---

## 4. Đã soát và đúng (không cần sửa)

- 04: tính tiền đúng (120,5 × 45.000 = 5.422.500; 45 × 38.000 = 1.710.000; 18,2 × 18.000 = 327.600; tổng 7.460.100 đ, 183,7 kg), khớp AC-01, BR-04. 05: mã `PN-261120-005`, lô `NL-2611-0007..0009` đúng BR-20 và khớp 12. 06: Sửa/Hủy chỉ ở phiếu của mình, trong ngày, chưa dùng (BR-05).
- 09/10/11: tên che «T T H», «N V A», «L M T», SĐT che `*******222`, `*******678` (BR-24, AC-24); serial 10 ký tự Base32; đơn mẫu 2 × 150.000 + quà + thiệp = 300.000 đ (AC-22, BR-25); 10 kênh bán khớp BR-22. 12–14 không hiện giá cho WORKSHOP, kiểm kê không tự sửa (AC-07).
- 18 Gán tem khớp TK §7.3, BR-12 (xem B-18). 27, 28, 29, 34: che tên/SĐT đúng; ghi chú nhật ký «Xem đầy đủ» ở `c/29:38` đúng. 33: tem NL đúng TK §6.2. 35: QR 18,8 mm ≥ 18 mm. 40 `/truy-xuất` không noindex, đúng TK §8.1.

## 5. Chưa kiểm

- Chưa bấm thử trên trình duyệt: ba người soát đọc HTML tĩnh; hành vi JS của vỏ (`vo.html`), hộp thoại in, khung điện thoại, nhãn `#buyer-req` có đổi theo kênh khi bấm hay không (A-07) đều chưa xem.
- Sổ tay PDF: bản `pdftotext` ở máy này lỗi font; dẫn sổ tay lấy qua TK và các đoạn đọc được (mục C.3, nhãn, dụng cụ). Chưa đối chiếu lại hạn 24 tháng ở 36–38.
- TK đang được topic #2 sửa; các dẫn theo số mục, BR, AC là bản đọc ngày 21/11/2026. Nếu topic #2 đổi tên mục hoặc route, đối chiếu lại các dòng C-14, B-09..B-11, A-02.
- Bản gộp này tự kiểm lại ở mức: đếm mã và mức (53 vấn đề), mã lô, tên file; không mở lại từng dòng HTML (đã được tester xác nhận ở các task #20–#22).
