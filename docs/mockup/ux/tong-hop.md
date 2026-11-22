# Tổng hợp bản đề xuất UX cho sếp duyệt (task #38)

Ghép ngày 21/11/2026 · Long (dev). Bản xem trước: `docs/mockup/de-xuat/ban-xem-truoc.html` (**80 màn**: 68 màn ghép ở #45 + 12 màn danh mục ghép ở #49, xem 5.6; các số 68 ở mục 0 và 5.1 là lúc kiểm trước khi thêm). Bản chính `docs/mockup/ban-chinh.html` (trước 63 màn) **đã chép đè** bằng bản 80 màn ngày 21/11/2026 (Lead duyệt theo uỷ quyền của sếp #804). Nguồn số liệu: `ux/thay-doi-a.md`, `ux/thay-doi-b.md`, `ux/thay-doi-c.md` và `ux/ra-soat-a/b/c.md`.

Cách đếm: **chạm** = một lần bấm hoặc quét tem; **gõ** = số ô phải gõ bàn phím. Là số **đếm tay theo mockup tĩnh**, chưa thử với người dùng thật (nên thử 2–3 nhân viên khi có bản dựng).

## 0. Kết quả kiểm bản ghép (Chrome không cửa sổ, 1440 px)

| Việc kiểm | Kết quả |
|---|---|
| Bấm lần lượt **mọi mục menu trái** | **68 / 68 màn mở được**: nội dung không rỗng, tiêu đề và «n / 68» khớp, không có lỗi JavaScript |
| Bấm thử **mọi link** `<a href>` trên 68 màn (236 link, tính duy nhất theo từng màn) | 226 dẫn đúng sang màn trong vỏ; 10 là link cố ý không mở trong bản xem trước (1 dấu `#`, 3 tải CSV, 4 số điện thoại, 2 trang web ngoài); **0 link báo «không có trong bản xem trước»** (sau khi vá route, xem dưới) |
| 19 trang chủ chủ: ô «Bán quế khô» / «Bán thành phẩm» (Thao #539) | → `/xuat-hang/que-kho` → màn 08 `issue-dry` / `/xuat-hang/don-hang` → màn 09 `issue-product`. Ở 02 trang chủ thủ kho cũng đúng như vậy |
| «Kiểm kê kho» (12, 13) | → 14 `inv-kk`; trước khi vá rơi về `inv-nl` |
| «Ngửi kiểm tra», «Đạt» (15, 16b, 16c, 16d, 24) | → 16d `cure-smell` và 16e `cure-result`; trước khi vá cả hai rơi vào 16c |
| «+ Thêm người bán» (21, 22b) | → 21b `supplier-add`; trước khi vá rơi về 21 |
| «In bổ sung 50 tem» (25) | → 35 `print-roll`; trước khi vá báo «không có trong bản xem trước» |

**Vá route.** 4 route Long đã vá tay vào `ban-xem-truoc.html` (`/ton-kho/kiem-ke`, `/in/tem-bo-sung`, `/san-xuat/ua/N/ngui`, `/san-xuat/ua/N/ket-qua`, và `moi=1` của người bán) nay đã nằm trong `_tools/vo.html` (hàm `route`, task #45), nên `mockup.mjs ghep` không làm mất nữa. Đã ghép lại và bấm thử: các link trên vẫn dẫn đúng màn.

Màn không có link dẫn vào, chỉ mở bằng menu: `receipt-cancel` (06c, hộp hủy phiếu), `inv-kk-reset` (14c, hộp xóa các bao đã quét), `receipt-warn`, `receipt-chung`, `issue-product-san/-moi/-loi` (biến thể trạng thái). Hộp thoại thì nút mở nằm ở bản chạy thật, vỏ tĩnh không bật được.

**Đo ở 492 px** (Thao #531): 08, 09, 09b, 09c, 09d, trang chủ thủ kho (02) và chủ (19). Không màn nào tràn ngang trang (`scrollWidth` = 492). Chữ nhỏ nhất 16,2 px. Mỗi màn đúng 1 nút xanh chính (19 có thêm nút «Duyệt», «Lưu mẫu» của khối «Việc cần xử lý»). Ngoài chữ «Đăng xuất» ở thanh trên (xem mục 4) và ô tick 32 px nằm trong nhãn cao 48 px, không có nút, link, ô nhập nào dưới 48 px. Bảng dòng hàng ở 09–09d rộng hơn màn nên **cuộn ngang bên trong khung bảng** (cột «Thành tiền» bị cắt, kéo ngang mới thấy); trang không bị kéo. Ảnh: `anh/issue-dry-sau-492.png`, `anh/issue-product-sau-492.png`, `anh/issue-product-san-sau-492.png`, `anh/issue-product-moi-sau-492.png`, `anh/issue-product-loi-sau-492.png`.

**Chưa kiểm:** điện thoại thật; hộp thoại in của trình duyệt (khổ 50 × 30 phải in thử một tem thật); giao diện tối (dự án chưa hỗ trợ).

## 1. Số bước mỗi việc hằng ngày: trước → sau

«Trước» là hiện trạng của `ban-chinh.html`; «Sau» là bản đề xuất đã dựng ở `de-xuat/`. Số cụm A đã tính cả lô 2 sếp chốt ở #524 (bao tự quét, kênh bán hai ô riêng).

### Cụm A: nhập, xuất, kho (nguồn `ux/ra-soat-a.md` §2 và `ux/thay-doi-a.md` §6)

| Việc | Chạm trước → sau | Ô gõ trước → sau | Ghi chú |
|---|---|---|---|
| Cân thu mua, 3 dòng hàng | 14 → 10 | 3 → 3 | một hàng 6 nút loại quế; dòng gõ dở tự thêm khi «Lưu và in» |
| Cân thu mua, 1 dòng hàng | 8 → 5 | 1 → 1 | |
| Thêm người bán mới | 6 → 3–4 | 1 → 1 | |
| Hủy phiếu nhập hôm nay | 2 → 3 | 0 → 0 | **tăng cố ý**: thêm hộp xác nhận «Giữ lại / Hủy phiếu» (06c) |
| Bán quế khô | 9 → **6** | 1 → 1 | 5 chạm nếu tự chọn sẵn bao; sếp chọn nhân viên **tự quét tem bao** (Q-A1) nên +1 |
| Bán thành phẩm, khách lẻ cũ | 7 → **6** | 1 → 1 | 5 chạm theo bản gộp ô; +1 chạm chọn kênh vì giữ hai ô riêng (Q-A3) |
| Bán thành phẩm, khách lẻ mới | 10 → **6** | 3 → 2 | như trên; địa chỉ không bắt (Q-A2) |
| Bán thành phẩm, Shopee | 10 → 7 | 2 → 2 | kênh Shopee tự điền theo khách, +0 chạm (`thay-doi-a.md` §6). **Chưa đếm lại sau lô 2** |
| Xem tồn kho | 1–2 → 1–2 | 0 → 0 | |
| Kiểm kê | 3 + N → 3 + N | 0 → 0 | N = số bao quét; thêm hộp xác nhận chỉ khi «Làm lại» |
| Tìm đơn theo số điện thoại | 4 + gõ → 3 + gõ | 1 → 1 | |

### Cụm B: sản xuất (nguồn `ux/thay-doi-b.md` §2; tôi đã cộng lại từng dòng, khớp)

| Việc | Chạm trước → sau | Ô gõ trước → sau | Ghi chú |
|---|---|---|---|
| Bắt đầu mẻ (màn 24) | 4 → 4 (3 nếu cùng sản phẩm lần trước) | 1 → 0 | cỡ mẻ chọn bằng nút 100 ml / 500 ml / 1 lít |
| Ghi 4 nguyên liệu (16), cách A: gõ số cân thật | 8 → 4 | 4 → 4 | quét xong tự nhảy vào ô số cân |
| — cùng việc, cách B: nút «Điền sẵn số cân theo gợi ý» (sếp chốt) | 8 → 12 | 4 → 0 | mỗi thứ: 1 quét + 1 điền sẵn + 1 «Xác nhận số cân» |
| Đưa vào ủ | 1 → 1 | 0 → 0 | bỏ khối «Nhập kết quả» mờ |
| Lắc chai (15, 16b, 24) | không có chỗ bấm → 1 mỗi lần | 0 → 0 | ghi người đăng nhập và giờ (sếp chốt); lịch sử ở 16c, 26b |
| Ngửi kiểm tra (16d) | 9 → 1 (chưa đạt: 2) | 0 → 0 | bỏ 4 ô chọn; người ngửi tự ghi theo người đăng nhập |
| Tạo lô (16e) | 1 → 1 | 2 → 2 | ngày hiện thành chữ, «Sửa ngày» mới mở ô |
| Lưu mẫu (17) | 2 → 1 | 0 → 0 | |
| Dán tem cho lô | 2 quét → **2 chạm** | 0 → 0 | in tem theo lô, gán luôn (sếp chốt #494 ý 7); gán bù vẫn quét 2 tem (BR-12) |
| **Cả một mẻ tinh dầu 4 thành phần**, cách A | **27 → 14** | **7 → 6** | không tính lắc chai (+1 mỗi lần) |
| — cách B | 27 → 22 | 7 → 2 | = 14 + 8 chạm điền sẵn và xác nhận, bớt 4 gõ |

### Cụm C: quản lý, in, QR (nguồn `ux/thay-doi-c.md` §0, §3)

| Việc | Chạm trước → sau | Ô gõ trước → sau | Ghi chú |
|---|---|---|---|
| In tem cho lô vừa làm xong | 9 (5 màn) → **2** | 1 → 0 | nút «In 90 tem cho lô này» + «In» trong hộp thoại; thủ kho làm được, ghi người in |
| In bổ sung tem (lô thiếu tem) | chưa có → 3 | — → 0 | chọn lý do, «In bổ sung», «In» |
| Duyệt người bán chờ duyệt | 3 → 2 | 0 → 0 | |
| Thêm người bán nhanh | ≈ 16 → ≈ 6 | 5 → 1 | 3 ô: tên, loại, thôn |
| Đổi khoảng thời gian báo cáo | 4 → 1 | 2 → 0 | |

Lưu ý khi đọc: (1) mọi số đều là đếm tay, chưa thử với người dùng thật; (2) dòng «Bán thành phẩm, Shopee» chưa ai đếm lại sau lô 2; (3) hộp thoại in tự mở khi vào trang là hành vi của bản chạy thật, mockup không tự gọi `window.print()`.

## 2. Các mục «CẦN SẾP QUYẾT» và phương án đã làm

«Mặc định» là phương án các bản rà soát đề xuất. Cột «Đã làm» cho biết bản `ban-xem-truoc.html` đang theo cái nào. Sếp chọn khác thì sửa theo cột cuối.

### Sếp đã chốt (#494 lô 1, #524 lô 2): đã áp vào màn

| Mã | Câu hỏi | Mặc định đề xuất | **Sếp chốt / đã làm** | Ảnh trước → sau | Nếu sếp đổi ý |
|---|---|---|---|---|---|
| Q-A1 | Bán quế khô: tự chọn sẵn bao cũ nhất? | Có, quét tem để đổi | **Không, nhân viên tự quét tem bao** (đổi so mặc định) | 08 `issue-dry`: [trước](anh/issue-dry-truoc.png) → [sau](anh/issue-dry-sau.png), [492 px](anh/issue-dry-sau-492.png) | `08`: thêm lại khung chọn sẵn bao cũ nhất |
| Q-A2 | Bán trực tiếp / Website: bắt tỉnh/xã, địa chỉ? | Không bắt, để trong «Thêm» | **Giữ mặc định** | 09c `issue-product-moi`: [trước](anh/issue-product-moi-truoc.png) → [sau](anh/issue-product-moi-sau.png) (khối «＋ Thêm thông tin người mua») | `09`, `09c`, `09d`: đưa «Tỉnh / xã», «Số nhà» ra ngoài «Thêm» |
| Q-A3 | Gộp ô «khách» và «kênh bán»? | Gộp | **Giữ hai ô riêng** (đổi so mặc định): hàng «Kênh bán» 10 kênh; sàn, đại lý, doanh nghiệp tự điền kênh theo khách; khách lẻ chưa chọn sẵn | 09 [trước](anh/issue-product-truoc.png) → [sau](anh/issue-product-sau.png) · 09b [trước](anh/issue-product-san-truoc.png) → [sau](anh/issue-product-san-sau.png) · 09c [trước](anh/issue-product-moi-truoc.png) → [sau](anh/issue-product-moi-sau.png) · 09d [trước](anh/issue-product-loi-truoc.png) → [sau](anh/issue-product-loi-sau.png) · 492 px: [09](anh/issue-product-sau-492.png), [09b](anh/issue-product-san-sau-492.png), [09c](anh/issue-product-moi-sau-492.png), [09d](anh/issue-product-loi-sau-492.png) | `09`…`09d`: bỏ hàng «Kênh bán»; thêm cột kênh mặc định cho khách (phần thiết kế ở topic #2) |
| B2-07 | Cho xưởng tự bắt đầu mẻ? | Giữ chỉ chủ | **Chỉ chủ bắt đầu mẻ** (đúng mặc định) | 15 `prod-list`: [trước](anh/prod-list-truoc.png) → [sau](anh/prod-list-sau.png) | `15`: thêm nút «+ Bắt đầu mẻ mới» |
| B2-17 | Bỏ quét tem lô khi chỉ còn một lô? | Không bỏ | **Quét tem lô nguyên liệu** (đúng mặc định) | 16 `prod-order`: [trước](anh/prod-order-truoc.png) → [sau](anh/prod-order-sau.png) | `16`: thêm nút «Đúng lô này» |
| B2-18 | Nút điền sẵn số cân = gợi ý? | Không làm | **Làm**: «Điền sẵn số cân theo gợi ý», số hiện mờ nhãn «gợi ý», vẫn phải «Xác nhận số cân» (đổi so mặc định) | 16 `prod-order`: [trước](anh/prod-order-truoc.png) → [sau](anh/prod-order-sau.png) | `16`: bỏ nút điền sẵn |
| B2-31 | Lưu «đã lắc chai»? | Chỉ nhắc, không lưu | **Lưu ai lắc và lúc nào** (đổi so mặc định) | 15 [trước](anh/prod-list-truoc.png) → [sau](anh/prod-list-sau.png) · 16b `cure-list` [trước](anh/cure-list-truoc.png) → [sau](anh/cure-list-sau.png) · 16c `cure-detail` [trước](anh/cure-detail-truoc.png) → [sau](anh/cure-detail-sau.png) · 24 `prod-owner` [trước](anh/prod-owner-truoc.png) → [sau](anh/prod-owner-sau.png) · 26b `lot-detail` [trước](anh/lot-detail-truoc.png) → [sau](anh/lot-detail-sau.png) | bỏ «Lịch sử lắc chai», nút thành lời nhắc. Bản ghi «lắc chai» cần vào `thiet-ke-chi-tiet.md` (topic #2) |
| B2-44 | Bỏ 4 ô chọn ngửi khỏi form? | Bỏ | **Bỏ**, chỉ «Đạt / Chưa đạt»; **người ngửi và giờ tự ghi theo người đăng nhập** | 16d `cure-smell`: màn mới, chỉ có ảnh [sau](anh/cure-smell-sau.png); phần ngửi cũ nằm trong [16c trước](anh/cure-detail-truoc.png) | thêm lại 4 ô chọn mốc ngửi ở 16d |
| Q-C1 | Thủ kho tạo và in tem cho lô mình làm? | Có, ghi người in | **Có** | 25 `rolls`: [trước](anh/rolls-truoc.png) → [sau](anh/rolls-sau.png); 02 `home-shop`, ô «In tem lô»: [trước](anh/home-shop-truoc.png) → [sau](anh/home-shop-sau.png) | `02`: bỏ ô «In tem lô»; `25`: đưa lại `data-role="OWNER"` |
| Q-C2 | In theo lô, gán luôn, bỏ quét tem đầu/cuối? | Giữ quét tem đầu/cuối (nhưng khuyến nghị in theo lô) | **In theo lô, gán luôn**; gán bù vẫn có (đổi so mặc định) | 17 `prod-done` [trước](anh/prod-done-truoc.png) → [sau](anh/prod-done-sau.png) · 18 `labels` [trước](anh/labels-truoc.png) → [sau](anh/labels-sau.png) · 25 [trước](anh/rolls-truoc.png) → [sau](anh/rolls-sau.png) · 42 `print-batch` [trước](anh/print-batch-truoc.png) → [sau](anh/print-batch-sau.png) · 35 `print-roll` [trước](anh/print-roll-truoc.png) → [sau](anh/print-roll-sau.png) | đổi BR-12 và mục 7.3 về quét tem đầu/cuối (topic #2) |
| Q-C3 | Khổ tem 40 × 30 hay lớn hơn? | 40 × 30 | **50 × 30** (đổi so mặc định) | 33 `print-receipt` [trước](anh/print-receipt-truoc.png) → [sau](anh/print-receipt-sau.png) · 05b `receipt-print` [trước](anh/receipt-print-truoc.png) → [sau](anh/receipt-print-sau.png) · 32 `settings` [trước](anh/settings-truoc.png) → [sau](anh/settings-sau.png) · 42, 35 như trên | đổi 50 → 40 ở `@page tem`, `.tem`, QR 22 → 18,8 mm. **Vẫn phải in thử một tem thật** |

### Chưa hỏi sếp, đội tự làm theo mặc định (sếp xem lại nếu không đồng ý)

| Mã | Câu hỏi | **Đã làm** | Ảnh trước → sau |
|---|---|---|---|
| Q-C4 | Số tem dự phòng khi in theo số chai | **Không còn +5**: in đúng số chai chưa có tem (90); thiếu thì «In bổ sung» có lý do (hệ quả của Q-C2) | 25: [trước](anh/rolls-truoc.png) → [sau](anh/rolls-sau.png) |
| Q-C5 | Trang chủ chủ: dời ô ít dùng vào «Quản lý khác»? | **Có**: ô lớn Nhập hàng, **Bán quế khô**, **Bán thành phẩm**, Sản xuất, Xem tồn kho; khối «Việc cần xử lý»; 4 ô «Hay dùng» | 19 `home-owner`: [trước](anh/home-owner-truoc.png) → [sau](anh/home-owner-sau.png); 31 `admin`: [trước](anh/admin-truoc.png) → [sau](anh/admin-sau.png) |
| B2-81 | Bỏ cột «Công thức» và «Ngày pha» ở màn 26? | **Giữ** hai cột (chuyển thành chữ nhỏ dưới cột khác), vì sếp đã duyệt ở #429 | 26 `plots-lots`: [trước](anh/plots-lots-truoc.png) → [sau](anh/plots-lots-sau.png) |
| B2-82 | Lô Q100 mất đường thu hồi khi bỏ nút ở 26 | Nút «Thu hồi lô» đặt ở màn tra cứu 27 (chốt #509). Lô -02 có nút, lô -01 đã RECALLED thì ẩn nút | 27 `trace`: [trước](anh/trace-truoc.png) → [sau](anh/trace-sau.png) |
| Túi thơm 50 g → 25 g | Đã chốt ở #429 (câu 4) | đã áp ở 10, 11, 28, 29 | 21 `issue-list`: [trước](anh/issue-list-truoc.png) → [sau](anh/issue-list-sau.png) · 22 `issue-detail`: [trước](anh/issue-detail-truoc.png) → [sau](anh/issue-detail-sau.png) |
| 33:56 | «Đông Cuông › Đồng Vối» ở tem lô nguyên liệu | còn nguyên, đang chờ Lead quyết (`thay-doi-c.md` §2) | 33 `print-receipt`: [sau](anh/print-receipt-sau.png) |

**Ghi chú cố ý (Diep #530):** ở `09c` kênh «Trực tiếp» và ở `09d` kênh «Website» được **chọn sẵn** trong khi khách là «Khách lẻ». Đây là kênh nhân viên đã bấm trong ca thử, để vẽ đúng trạng thái màn; ở `09` (khách lẻ vừa mở màn) **chưa chọn sẵn kênh nào**. Bản chạy thật: chỉ khách có kênh mặc định (sàn, đại lý, doanh nghiệp, như `09b` chọn sẵn Shopee) mới điền sẵn.

Ảnh `trace-sau` (27) chụp lại **có CSS** theo nhắc của reviewer ở #39: lô -02 có nút «Thu hồi lô».

## 3. Ảnh trước / sau

Ảnh ở `docs/mockup/ux/anh/<key>-truoc.png` (từ `ban-chinh.html`) và `<key>-sau.png` (từ `ban-xem-truoc.html`). Chụp từng màn riêng, **có CSS**, kéo dài hết chiều cao màn: rộng 1140 px cho màn máy tính và mẫu in, 390 px cho 7 màn khách quét QR. Tổng 131 ảnh trước/sau (63 trước + 68 sau) và 5 ảnh 492 px (`*-sau-492.png`). Màn mới chỉ có ảnh sau.

Cột «Tình trạng»: **đổi** = nội dung màn khác bản chính (58 màn); **mới** (5 màn: `receipt-cancel`, `inv-kk-reset`, `cure-smell`, `cure-result`, `supplier-add`); **chỉ đổi CSS chung** (5 màn: `login`, `login-err`, `login-locked`, `ingr-receipt`, `ingr-stock`): nội dung giữ nguyên nhưng nút chính nay màu xanh lá, chữ phụ ≥ 16 px, vùng chạm ≥ 48 px (`app.css` đổi chung cho mọi màn).

| Vỏ | Mã | Màn | Tình trạng | Trước | Sau |
|---|---|---|---|---|---|
| 01 | 01 | `login` Đăng nhập | chỉ đổi CSS chung | [ảnh](anh/login-truoc.png) | [ảnh](anh/login-sau.png) |
| 02 | 01b | `login-err` Đăng nhập — sai tên hoặc mật khẩu | chỉ đổi CSS chung | [ảnh](anh/login-err-truoc.png) | [ảnh](anh/login-err-sau.png) |
| 03 | 01c | `login-locked` Đăng nhập — tài khoản bị khóa 15 phút | chỉ đổi CSS chung | [ảnh](anh/login-locked-truoc.png) | [ảnh](anh/login-locked-sau.png) |
| 04 | 02 | `home-shop` Trang chủ xưởng (5 ô lớn, việc cần làm) | đổi | [ảnh](anh/home-shop-truoc.png) | [ảnh](anh/home-shop-sau.png) |
| 05 | 03 | `receipt-1` Phiếu cân — bước 1: chọn người bán | đổi | [ảnh](anh/receipt-1-truoc.png) | [ảnh](anh/receipt-1-sau.png) |
| 06 | 03b | `receipt-newsup` Phiếu cân — người bán mới (mặc định hàng chung) | đổi | [ảnh](anh/receipt-newsup-truoc.png) | [ảnh](anh/receipt-newsup-sau.png) |
| 07 | 04 | `receipt-2` Phiếu cân — đang thêm dòng (đồi, hạng, số cân) | đổi | [ảnh](anh/receipt-2-truoc.png) | [ảnh](anh/receipt-2-sau.png) |
| 08 | 04b | `receipt-warn` Phiếu cân — giá lệch hơn 20%, chưa có giá hôm nay | đổi | [ảnh](anh/receipt-warn-truoc.png) | [ảnh](anh/receipt-warn-sau.png) |
| 09 | 04c | `receipt-chung` Phiếu cân — người bán hàng chung (thương lái) | đổi | [ảnh](anh/receipt-chung-truoc.png) | [ảnh](anh/receipt-chung-sau.png) |
| 10 | 05 | `receipt-3` Phiếu cân — đã lưu, tự in phiếu + tem lô | đổi | [ảnh](anh/receipt-3-truoc.png) | [ảnh](anh/receipt-3-sau.png) |
| 11 | 05b | `receipt-print` Phiếu cân — hộp thoại in phiếu nhập + tem lô | đổi | [ảnh](anh/receipt-print-truoc.png) | [ảnh](anh/receipt-print-sau.png) |
| 12 | 06 | `receipt-list` Phiếu nhập hôm nay (sửa / hủy trong ngày) | đổi | [ảnh](anh/receipt-list-truoc.png) | [ảnh](anh/receipt-list-sau.png) |
| 13 | 06b | `ingr-receipt` Nhập phụ liệu (gram, số lô, COA) | chỉ đổi CSS chung | [ảnh](anh/ingr-receipt-truoc.png) | [ảnh](anh/ingr-receipt-sau.png) |
| 14 | 06c | `receipt-cancel` Hủy phiếu nhập — hộp xác nhận «Giữ lại / Hủy phiếu» | mới | — | [ảnh](anh/receipt-cancel-sau.png) |
| 17 | 07 | `issue-menu` Xuất hàng — lối dự phòng (trang chủ đã có Bán quế khô, Bán thành phẩm) | đổi | [ảnh](anh/issue-menu-truoc.png) | [ảnh](anh/issue-menu-sau.png) |
| 16 | 08 | `issue-dry` Bán quế khô — quét tem lô, gõ số cân lúc bán | đổi | [ảnh](anh/issue-dry-truoc.png) | [ảnh](anh/issue-dry-sau.png) |
| 17 | 09 | `issue-product` Đơn hàng — quét tem, người mua cũ tự nhận, quà tặng, báo quét trùng | đổi | [ảnh](anh/issue-product-truoc.png) | [ảnh](anh/issue-product-sau.png) |
| 18 | 09b | `issue-product-san` Đơn hàng — kênh sàn (bắt buộc tên + tỉnh) | đổi | [ảnh](anh/issue-product-san-truoc.png) | [ảnh](anh/issue-product-san-sau.png) |
| 19 | 09c | `issue-product-moi` Đơn hàng — người mua mới (SĐT chưa có) | đổi | [ảnh](anh/issue-product-moi-truoc.png) | [ảnh](anh/issue-product-moi-sau.png) |
| 20 | 09d | `issue-product-loi` Đơn hàng — lỗi thiếu tên / SĐT kênh Website | đổi | [ảnh](anh/issue-product-loi-truoc.png) | [ảnh](anh/issue-product-loi-sau.png) |
| 21 | 10 | `issue-list` Danh sách đơn hàng (tên, SĐT đã che) | đổi | [ảnh](anh/issue-list-truoc.png) | [ảnh](anh/issue-list-sau.png) |
| 22 | 11 | `issue-detail` Chi tiết đơn hàng | đổi | [ảnh](anh/issue-detail-truoc.png) | [ảnh](anh/issue-detail-sau.png) |
| 23 | 12 | `inv-nl` Tồn kho nguyên liệu (xưởng không thấy giá) | đổi | [ảnh](anh/inv-nl-truoc.png) | [ảnh](anh/inv-nl-sau.png) |
| 24 | 13 | `inv-tp` Tồn kho thành phẩm | đổi | [ảnh](anh/inv-tp-truoc.png) | [ảnh](anh/inv-tp-sau.png) |
| 25 | 14 | `inv-kk` Kiểm kê kho (quét tem, bấm Kiểm tra) | đổi | [ảnh](anh/inv-kk-truoc.png) | [ảnh](anh/inv-kk-sau.png) |
| 26 | 14b | `ingr-stock` Tồn kho phụ liệu | chỉ đổi CSS chung | [ảnh](anh/ingr-stock-truoc.png) | [ảnh](anh/ingr-stock-sau.png) |
| 27 | 14c | `inv-kk-reset` Kiểm kê — hộp xác nhận «Làm lại» | mới | — | [ảnh](anh/inv-kk-reset-sau.png) |
| 28 | 15 | `prod-list` Sản xuất / đóng gói | đổi | [ảnh](anh/prod-list-truoc.png) | [ảnh](anh/prod-list-sau.png) |
| 29 | 16 | `prod-order` Lệnh sản xuất: công thức, nguyên liệu theo gram, ủ | đổi | [ảnh](anh/prod-order-truoc.png) | [ảnh](anh/prod-order-sau.png) |
| 30 | 16b | `cure-list` Mẻ đang ủ | đổi | [ảnh](anh/cure-list-truoc.png) | [ảnh](anh/cure-list-sau.png) |
| 31 | 16c | `cure-detail` Mẻ đang ủ: lắc chai, ngửi kiểm tra, hoàn thành | đổi | [ảnh](anh/cure-detail-truoc.png) | [ảnh](anh/cure-detail-sau.png) |
| 32 | 16d | `cure-smell` Ngửi kiểm tra: Đạt hoặc ủ thêm | mới | — | [ảnh](anh/cure-smell-sau.png) |
| 33 | 16e | `cure-result` Nhập kết quả: số kg, số chai, tạo lô | mới | — | [ảnh](anh/cure-result-sau.png) |
| 34 | 17 | `prod-done` Lệnh hoàn thành: lô thành phẩm, chai lưu mẫu | đổi | [ảnh](anh/prod-done-truoc.png) | [ảnh](anh/prod-done-sau.png) |
| 35 | 18 | `labels` Gán bù / hủy tem: quét tem đầu, tem cuối của đoạn tem rời | đổi | [ảnh](anh/labels-truoc.png) | [ảnh](anh/labels-sau.png) |
| 36 | 19 | `home-owner` Trang chủ chủ DN (người bán chờ duyệt) | đổi | [ảnh](anh/home-owner-truoc.png) | [ảnh](anh/home-owner-sau.png) |
| 37 | 20 | `prices` Bảng giá theo hạng (6 ô giá mua, 6 ô giá bán) | đổi | [ảnh](anh/prices-truoc.png) | [ảnh](anh/prices-sau.png) |
| 38 | 21 | `suppliers` Người bán & đồi quế | đổi | [ảnh](anh/suppliers-truoc.png) | [ảnh](anh/suppliers-sau.png) |
| 39 | 21b | `supplier-add` Thêm người bán nhanh (3 bước: tên, loại, thôn) | mới | — | [ảnh](anh/supplier-add-sau.png) |
| 40 | 22 | `supplier-edit` Sửa người bán — bảng đồi quế | đổi | [ảnh](anh/supplier-edit-truoc.png) | [ảnh](anh/supplier-edit-sau.png) |
| 41 | 22b | `supplier-approve` Duyệt người bán chờ duyệt (hộp sửa) | đổi | [ảnh](anh/supplier-approve-truoc.png) | [ảnh](anh/supplier-approve-sau.png) |
| 42 | 23 | `products` Sản phẩm: công thức, hạn dùng, cách dùng | đổi | [ảnh](anh/products-truoc.png) | [ảnh](anh/products-sau.png) |
| 43 | 23b | `recipe-list` Công thức | đổi | [ảnh](anh/recipe-list-truoc.png) | [ảnh](anh/recipe-list-sau.png) |
| 44 | 23c | `recipe-edit` Khai công thức (thành phần theo gram) | đổi | [ảnh](anh/recipe-edit-truoc.png) | [ảnh](anh/recipe-edit-sau.png) |
| 45 | 24 | `prod-owner` Tạo lệnh sản xuất: công thức, cỡ mẻ | đổi | [ảnh](anh/prod-owner-truoc.png) | [ảnh](anh/prod-owner-sau.png) |
| 46 | 25 | `rolls` In tem theo lô (gán luôn, in bổ sung); cuộn tự do chỉ chủ | đổi | [ảnh](anh/rolls-truoc.png) | [ảnh](anh/rolls-sau.png) |
| 47 | 26 | `plots-lots` Lô thành phẩm · mẫu lưu · thu hồi | đổi | [ảnh](anh/plots-lots-truoc.png) | [ảnh](anh/plots-lots-sau.png) |
| 48 | 26b | `lot-detail` Chi tiết mẻ (sổ ghi lô) | đổi | [ảnh](anh/lot-detail-truoc.png) | [ảnh](anh/lot-detail-sau.png) |
| 49 | 26c | `retain-list` Mẫu lưu · lô chưa lưu mẫu | đổi | [ảnh](anh/retain-list-truoc.png) | [ảnh](anh/retain-list-sau.png) |
| 50 | 26d | `scent-trial` Thử lưu hương 28 ngày | đổi | [ảnh](anh/scent-trial-truoc.png) | [ảnh](anh/scent-trial-sau.png) |
| 51 | 27 | `trace` Tra cứu hai chiều (từ người bán → khách) | đổi | [ảnh](anh/trace-truoc.png) | [ảnh](anh/trace-sau.png) |
| 52 | 41 | `vung-nguyen-lieu` Vùng nguyên liệu (bản đồ, bảng đồi) | đổi | [ảnh](anh/vung-nguyen-lieu-truoc.png) | [ảnh](anh/vung-nguyen-lieu-sau.png) |
| 53 | 28 | `buyers` Khách hàng đã mua | đổi | [ảnh](anh/buyers-truoc.png) | [ảnh](anh/buyers-sau.png) |
| 54 | 29 | `buyer-detail` Chi tiết khách — “Xem đầy đủ” có ghi nhật ký | đổi | [ảnh](anh/buyer-detail-truoc.png) | [ảnh](anh/buyer-detail-sau.png) |
| 55 | 30 | `reports` Báo cáo hiệu suất theo người bán | đổi | [ảnh](anh/reports-truoc.png) | [ảnh](anh/reports-sau.png) |
| 56 | 31 | `admin` Menu quản lý | đổi | [ảnh](anh/admin-truoc.png) | [ảnh](anh/admin-sau.png) |
| 57 | 32 | `settings` Cài đặt (tên miền QR, khổ tem…) | đổi | [ảnh](anh/settings-truoc.png) | [ảnh](anh/settings-sau.png) |
| 58 | 33 | `print-receipt` Phiếu nhập A5 + tem lô nguyên liệu 50×30 | đổi | [ảnh](anh/print-receipt-truoc.png) | [ảnh](anh/print-receipt-sau.png) |
| 59 | 34 | `print-issue` Phiếu xuất / đơn hàng (có quà tặng) | đổi | [ảnh](anh/print-issue-truoc.png) | [ảnh](anh/print-issue-sau.png) |
| 60 | 35 | `print-roll` In bổ sung tem cho lô (nối tiếp serial, 50×30) | đổi | [ảnh](anh/print-roll-truoc.png) | [ảnh](anh/print-roll-sau.png) |
| 61 | 42 | `print-batch` Tem theo lô 50×30 (QR serial + mã lô + NSX + HSD, gán luôn) | đổi | [ảnh](anh/print-batch-truoc.png) | [ảnh](anh/print-batch-sau.png) |
| 62 | 36 | `q-ok` Chính hãng — hợp lệ (trong kho hoặc đã xuất; không hiện người mua) | đổi | [ảnh](anh/q-ok-truoc.png) | [ảnh](anh/q-ok-sau.png) |
| 63 | 37 | `q-many-scans` Chính hãng — quét quá ngưỡng (khung vàng) | đổi | [ảnh](anh/q-many-scans-truoc.png) | [ảnh](anh/q-many-scans-sau.png) |
| 64 | 38 | `q-recall` Lô bị thu hồi (khung đỏ) | đổi | [ảnh](anh/q-recall-truoc.png) | [ảnh](anh/q-recall-sau.png) |
| 65 | 39 | `q-unassigned` Mã chưa kích hoạt (nghi giả) | đổi | [ảnh](anh/q-unassigned-truoc.png) | [ảnh](anh/q-unassigned-sau.png) |
| 66 | 43 | `q-notfound` Mã không có trong hệ thống | đổi | [ảnh](anh/q-notfound-truoc.png) | [ảnh](anh/q-notfound-sau.png) |
| 67 | 44 | `q-void` Mã đã bị hủy | đổi | [ảnh](anh/q-void-truoc.png) | [ảnh](anh/q-void-sau.png) |
| 68 | 40 | `q-form` Nhập mã tay | đổi | [ảnh](anh/q-form-truoc.png) | [ảnh](anh/q-form-sau.png) |

## 4. Việc còn lại, ngoài vùng của task này

- **`ux/thay-doi-a.md` dòng 1–66** (mục 1–4) vẫn là bản cũ của #24: ghi «tem 40 × 30», nhãn «GĐ2», «50 g», mâu thuẫn với mục 5–6 và bản hiện tại (Thao #522). Cũng nên thêm số bước trước → sau vào đó (bảng mục 1 ở trên dùng lại được).
- **`de-xuat/thay-doi-a.md`** nhảy mục từ 4 sang 6 (thiếu mục 5 «Bổ sung sau ý 7–9» mà `ux/thay-doi-a.md` có); hai file lệch nhau (Thao #531). `de-xuat/thay-doi-b.md` và `thay-doi-c.md` là bản cũ hơn `ux/thay-doi-b.md`, `ux/thay-doi-c.md`.
- **Chữ «Đăng xuất»** ở thanh trên mọi màn đã đo cao 21 px ở 1140 px và 44 px ở 492 px, dưới chuẩn 48 px của `ra-soat-a.md` mục 0.1. Có từ trước, không thuộc bản sửa nào; cần người giữ `app.css` hoặc khung chung.
- **Tên «Dán tem lên chai»** ở 02 dẫn `/dong-goi` → màn 18 mang tên «Gán bù / hủy tem». Vì tem in theo lô đã gán luôn (ý 7), nút trang chủ nên đổi chữ cho khớp (chỉ gán bù/hủy tem lỗi) hoặc ẩn khi không có tem rời. Lead/Dat cân nhắc.
- **Màn in** `print-receipt` (33) và `print-batch` (42) có tiêu đề menu mới «…50×30»; `ban-chinh.html` còn «40×30».
- Số chạm của cụm A dòng Shopee chưa đếm lại sau lô 2; các số khác là đếm tay.

## 5. Luồng nút (task #45: nút thao tác đi tiếp theo luồng, nút chọn sáng tại chỗ)

Vỏ `_tools/vo.html` xử lý 3 loại: `<a href>` và `<button data-go>` đi qua `route()` hoặc `#khoá-màn` (chỉ nhận khoá có trong bảng màn, giá trị lạ báo «Màn hình này không có trong bản xem trước»); `<button data-pick>` đặt `aria-pressed=true`, bỏ ở nút anh em cùng cha, bật/tắt tab `tab-<data-tab>`, ô chọn không phải `.choice` thì đổ nền nâu để nhìn thấy; nút không gắn gì giữ hint «không chạy thật». Nút in (`onclick="window.print()"`) vẫn chạy thật. Ghép bằng `node docs/mockup/_tools/mockup.mjs ghep` → `de-xuat/ban-xem-truoc.html` (68 màn); `ban-chinh.html` và `goc/` chưa đụng.

### 5.1 Quét tự động toàn bộ nút (Chrome không cửa sổ, 1440 px)

Bấm từng `<button>` trên 68 màn rồi đọc kết quả (script cũ `_tools/quet-nut.js`, nay không dùng). **Quét lại trên 80 màn sau #50–#53** (chạy bằng `node docs/mockup/_tools/bam-thu.mjs quet`, 21/11/2026): **193** nút `data-act` (xử lý tại chỗ, đếm riêng), **127** nút `data-go` đi sang đúng màn đích, **295** nút `data-pick` sáng tại chỗ, 10 nút `disabled`, **0** nút báo «không có trong bản xem trước» (`badTarget` rỗng). Còn **13** nút báo «không chạy thật» (trước là **173**) và **0** lỗi (sau khi sửa `vo.html`, xem 5.3). Luồng danh mục chạy lại: `bam-thu.mjs danh-muc` TẤT CẢ ĐẠT. Bảng dưới là số của lần quét cũ trên 68 màn, giữ để so:

| Loại | Số nút | Kết quả |
|---|---|---|
| `data-go` | 88 | 87 đi sang đúng màn đích; 1 là nút trỏ về chính màn đang mở (`receipt-cancel` (06c) «Hủy», nền của hộp hủy phiếu là danh sách 06, đứng yên là đúng) |
| `data-pick` | 264 | 264 sáng lên tại chỗ, không hint |
| Có `data-go` nhưng báo «không có trong bản xem trước» | 0 | |
| Lỗi (nút không gắn mà lại đổi màn) | 0 | |
| Còn hint «không chạy thật» | 87 | danh sách ở 5.3 |
| Bị `disabled` | 5 | 5.4 |

### 5.2 Luồng đã bấm thử (ảnh `ux/anh/luong-*.png`)

| Luồng | Các bước đã bấm | Ảnh |
|---|---|---|
| **Nhập hàng 02→06** | Trang chủ 02 → «Nhập hàng» 03 → bấm thẻ người bán → 04 phiếu cân → «+ Thêm dòng» → «💾 Lưu và in» → 05 đã lưu → 05b in phiếu → «Xong» → 06 phiếu nhập hôm nay | `luong-nhap-hang-1-trang-chu`, `-2-chon-nguoi-ban`, `-3-them-dong`, `-4-da-luu`, `-5-in-phieu`, `-6-phieu-hom-nay` |
| **Bán quế khô** | Trang chủ → «Bán quế khô» 08 → «💾 Lưu và in» → 10 danh sách đơn | `luong-ban-que-kho-1-nhap`, `-2-danh-sach-don` |
| **Bán thành phẩm** | 09 quét tem → bấm kênh Shopee → 09b (kênh sàn) → «💾 Lưu đơn và in» → 10 danh sách đơn. Nhánh: 09 «Không phải người này» → 09c (người mua mới) → kênh Website → 09d (báo lỗi) | `luong-ban-thanh-pham-1-quet-tem`, `-2-kenh-san`, `-3-danh-sach-don`, `-4-nguoi-mua-moi`, `-5-loi-website` |
| **Mẻ sản xuất 15→17** | 15 danh sách mẻ → 16 lệnh sản xuất → «Điền sẵn số cân theo gợi ý» (sáng nền nâu) → «Xác nhận số cân» → 16b đang ủ → 16c chi tiết mẻ → «Hoàn thành sớm» → 16e kết quả → «Hoàn thành, tạo lô» → 17 lệnh hoàn thành → in tem theo lô (25) → 42 tem theo lô | `luong-me-san-xuat-1-danh-sach` … `-10-tem-theo-lo` |
| **Ủ và ngửi** | 16b đang ủ (lắc chai) → 16d ngửi kiểm tra → «Chưa đạt, ủ thêm 7 ngày» (mở khối) → chọn lý do «Còn mùi gắt» → «Ủ thêm 7 ngày» → quay về 16b | `luong-u-va-ngui-1-lac-chai`, `-2-ngui`, `-3-chon-ly-do`, `-4-u-them` |
| **Đăng nhập** | 01 form → «Đăng nhập» → 19 trang chủ chủ doanh nghiệp → «Đăng xuất» → 01 | `luong-dang-nhap-1-form`, `-2-trang-chu-chu`, `-3-dang-xuat` |
| **Truy xuất QR** | 27 tra cứu → «Thu hồi lô» → 38 lô thu hồi; 40 nhập mã tay → «Kiểm tra» → 36 mã hợp lệ | `luong-truy-xuat-qr-1-tra-cuu`, `-2-lo-thu-hoi`, `-3-nhap-ma`, `-4-hop-le` |
| **Nút chọn** | Chọn một ô hạng quế; bấm tab ở màn hủy tem (sáng tại chỗ, tab đổi nội dung) | `luong-chon-o-hang-que`, `luong-chon-o-tab-huy-tem` |

Ghi chú khi bấm: ô lý do «Còn mùi gắt» nằm trong khối «Chưa đạt» gập sẵn, ảnh `luong-u-va-ngui-3-chon-ly-do` đã mở khối ra và cuộn tới ô đang sáng; ảnh `luong-me-san-xuat-3-dien-san` cuộn tới nút «Điền sẵn» đang sáng. Lúc đầu nút «Điền sẵn» chỉ thêm class `active` mà CSS chỉ tô `active` trong `.tabs`, nên bấm mà không thấy gì; đã sửa trong vỏ (nền nâu cho mọi `data-pick` không phải `.choice`).

**Hai chỗ luồng không có nút dẫn** (Quang ghi ở #43): 23 → 23b và 17 → 18. Vẫn mở được bằng menu trái.

### 5.3 Nút còn hint «không chạy thật» (13 nút, trước là 173) (đã sửa 2 lỗi vỏ)

Sau #50–#53, nút thêm/bỏ dòng, Ngừng dùng/Dùng lại, Lưu, In, Chọn file đã có phản hồi tại chỗ (mục 5.7). Còn lại 13 nút giữ hint, mỗi nút có lý do:

| Màn | Nút | Lý do giữ hint |
|---|---|---|
| 06b `ingr-receipt` | «Sửa» ×2 | sửa một dòng phiếu phụ liệu đã nhập cần form sửa dòng; mockup không có màn đó |
| 06c `receipt-cancel` | «Hủy» | đây là nền của hộp hủy phiếu, nút trỏ về chính màn đang mở; không có trạng thái «sau khi hủy» |
| 18 `labels` | «Quét lại tem đầu» | cần máy quét thật; bản xem trước không mô phỏng thiết bị |
| 22b `supplier-approve` | «+ Thêm đồi» | chưa có màn thêm đồi ở luồng duyệt; 22 đã có «+ Thêm đồi» thêm dòng |
| 26d `scent-trial` | «+ Nhập kết quả ngày 28» | chưa có màn nhập điểm ngày 28 |
| 29 `buyer-detail` | «👁 Xem đầy đủ», «Xóa thông tin cá nhân» | cần hộp xác nhận kèm ghi nhật ký truy cập dữ liệu cá nhân; chưa có màn |
| 32 `settings` | «+ Thêm mới» | chưa rõ thêm cài đặt gì, chưa có màn đích |
| 45b `area-edit`, 46b `goods-type-edit` | «+ Thêm» (mỗi màn 1) | nền của hộp sửa, trỏ về chính màn |
| 49b `cert-edit` | «+ Thêm chứng nhận» | nền của hộp sửa; chưa gắn `data-go` sang 49 như 45b/46b |
| 50b `account-edit` | «+ Thêm tài khoản» | nền của hộp sửa; chưa gắn `data-go` sang 50 như 45b/46b |

Quét bằng `bam-thu.mjs quet` cho ra đúng 13 dòng này (gồm 06b «Sửa» ×2, trong bảng trên gộp một dòng).

**Hai lỗi đã gặp ở lần quét đầu, đã sửa ở `_tools/vo.html` (#54) rồi ghép và quét lại:**

1. `row-add` ở 23 `products` «+ Thêm mới» và 26d `scent-trial` «+ Đợt thử mới»: nút nằm trên bảng nên `pickList` không thấy danh sách; nay không có danh sách nào đứng trước thì lấy danh sách đầu tiên đứng sau nút.
2. `row-del` ở 16 `prod-order` «Bỏ dòng này»: nút nằm trong `div.ing`, không phải tr/li/.row; nay xoá con trực tiếp của vùng `data-rows` chứa nút.
3. Kèm theo: `toggle` nhớ class `danger` gốc của nút (`data-dg`), không ép theo chữ nút nữa (medium của reviewer #640).

Quét lại: 0 lỗi. `danh-muc` TẤT CẢ ĐẠT. `ux/tai-cho.mjs` đạt cả 7 nút.

### 5.4 Nút `disabled` (không bấm được, đúng thiết kế)

| Màn | Nút | Lý do |
|---|---|---|
| 01c `login-locked` | «Đăng nhập» | tài khoản bị khóa 15 phút |
| 03 `receipt-1` | «💾 Lưu và in» | chưa chọn người bán |
| 16 `prod-order` | «▶ Đã pha xong, đưa vào ủ» | bật khi cân đủ; luồng đi qua «Xác nhận số cân» (đã nối sang danh sách ủ) |
| 24 `prod-owner` | thẻ mẻ giai đoạn 4 | chỉ để xem |
| 26d `scent-trial` | «Đóng đợt thử» | chưa đủ kết quả |
| 47b `material-edit` | «Ngừng dùng» ×2 (Loại 1, Loại 2) | hạng đang có lô trong kho |
| 50 `account`, 50b `account-edit` | «Ngừng dùng» (1 nút ở 50, 2 nút ở 50b) | «Không tự ngừng dùng chính mình» |

### 5.6 Danh mục (task #49): 6 danh mục, 12 màn

Ghép 12 màn của #46, #47, #48 vào `_ds.json` (nhóm «Chủ doanh nghiệp», đặt sau 32 `settings`, màn sửa đứng ngay sau danh sách), bỏ ghi chú ở 31, đổi nhãn thành «Địa bàn (tỉnh, xã, thôn)». Bấm thử bằng `node _tools/bam-thu.mjs danh-muc` (Chrome không cửa sổ, 1440 px); mọi bước đạt:

| Danh mục | Ô ở 31 → danh sách | Dòng → form | Lưu → danh sách | «+ Thêm» → form | ✕ → danh sách | Ảnh (`ux/anh/`) |
|---|---|---|---|---|---|---|
| Địa bàn | 45 `area` | 45b `area-edit` | đạt | đạt | đạt | `danh-muc-dia-ban-1-ds`, `-2-form` |
| Loại hàng hóa | 46 `goods-type` | 46b `goods-type-edit` | đạt | đạt | đạt | `danh-muc-loai-hang-1-ds`, `-2-form` |
| Nguyên liệu & hạng | 47 `material` | 47b `material-edit` | đạt | đạt | đạt | `danh-muc-nguyen-lieu-1-ds`, `-2-form` |
| Khách & kênh bán | 48 `customer-dm` | 48b `customer-dm-edit` | đạt | đạt | đạt | `danh-muc-khach-hang-1-ds`, `-2-form` |
| Chứng nhận | 49 `cert` | 49b `cert-edit` | đạt | đạt | đạt | `danh-muc-chung-nhan-1-ds`, `-2-form` |
| Tài khoản | 50 `account` | 50b `account-edit` | đạt | đạt | đạt | `danh-muc-tai-khoan-1-ds`, `-2-form` |

Ảnh menu: `danh-muc-0-menu-quan-ly`. Cả 6 ô không báo hint nào khi bấm. Bấm một dòng của bảng cũng mở form (`<tr data-go>`), việc Ha ghi ở #584 (`vo.html` trước chỉ bắt `<button>` và `<a>`).

Thay đổi ở vỏ (`_tools/vo.html`): 6 route mới `/quan-ly/danh-muc/{dia-ban, loai-hang, nguyen-lieu, khach-hang, chung-nhan, tai-khoan}` (nguyên liệu và khách thêm `?moi=1` thì ra form), vẫn chỉ nhận khoá có trong bảng (`hasOwn`); click bắt thêm phần tử `[data-go]` bất kỳ (dòng bảng), bỏ qua ô nhập; nút `data-go` trỏ về chính màn thì báo hint. `_tools/mockup.mjs` đọc thêm trường `file` của `_ds.json` (tên file màn danh mục không theo khoá).

**Chưa làm / ghi lại**
- Nội dung chữ trong 12 màn (Quận/Yên Bái ở 48b, 49; Loại hàng mẫu; «7 sản phẩm» ở 46) là việc các reviewer đã ghi ở #46–#48; `#49` không sửa nội dung màn.
- Hộp sửa chưa có trạng thái «sau khi bấm Lưu» (không báo «Đã lưu»): Lưu chỉ về danh sách.

### 5.7 Sáu loại `data-act` (task #50–#54: xử lý tại chỗ, không hint)

Nút gắn `data-act="<loại>"` được vỏ `_tools/vo.html` xử lý ngay trong màn, ưu tiên hơn `data-go` của dòng chứa nó (không nhảy màn). Nút không gắn hoặc `disabled` giữ hành vi cũ.

| `data-act` | Việc vỏ làm | Số nút (quét 21/11) |
|---|---|---|
| `row-add` | nhân đôi dòng cuối của danh sách `[data-rows]` (hoặc tbody/ul/ol gần nút), bỏ `id`, xoá ô nhập | 15 |
| `row-del` | xoá dòng `tr/li/.row` chứa nút  | 13 |
| `toggle` | đổi chữ nút «Ngừng dùng» ⇄ «Dùng lại» và chữ trạng thái ở `[data-status]`/`.tag`/`.badge`, làm mờ dòng | 149 |
| `save` | báo xanh «Đã lưu» 2 giây ở vỏ; có `data-go` thì đi tiếp sau 0,45 giây | 5 |
| `print` | gọi `window.print()` | 5 |
| `file` | mở hộp chọn file của trình duyệt, hiện tên file đã chọn | 4 |

Bấm tay 7 nút trên Chrome không cửa sổ (script `ux/tai-cho.mjs`; ảnh `ux/anh/tai-cho-*.png`): 04 «+ Thêm dòng» thêm dòng (3 → 4) đạt; 45 «Ngừng dùng» đổi sang «Dùng lại» và trạng thái đổi đạt; 20 «Lưu bảng giá» hiện «Đã lưu» đạt; 47b «Chọn ảnh» mở hộp chọn file (`Page.fileChooserOpened`) đạt; 16 «Bỏ dòng này» xoá khối (4 → 3 khối) đạt sau khi sửa `row-del`.

### 5.5 Medium của reviewer, đã xử lý hay ghi lại

- 25 `rolls`: «In lại» và «In 100 tem» đang trỏ `#print-batch`; Ha gợi ý `#print-roll` (in bổ sung). Chưa đổi (file cụm C ngoài vùng); ghi để Thu/Lead quyết.
- 40 `q-form`: «Kiểm tra» chỉ trỏ `#q-ok`; nhánh «không có mã» nằm ở màn 43, vào bằng nhập mã khác.
- 16 `prod-order`: «Đã pha xong, đưa vào ủ» vẫn disabled, cố ý (xem 5.4).
- Vỏ vá route `ket-qua`/`ngui` (Nga, Ha nhắc): đã có trong `vo.html`.
