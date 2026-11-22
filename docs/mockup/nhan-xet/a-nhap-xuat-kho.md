# Nhận xét cụm A: nhập / xuất / kho (màn 02–14)

Người soát: Minh (BA), task #20. Chỉ đọc; không sửa HTML.

Màn nằm ở `docs/mockup/de-xuat/man/a-nhap-xuat-kho/<STT>-<key>.html` (viết tắt `<STT>:<dòng>` bên dưới, ví dụ `04:49`). Thiết kế = `docs/thiet-ke-chi-tiet.md` (viết tắt TK; số dòng TK thay đổi vì topic #2 đang sửa, nên căn cứ ghi theo mã BR/AC hoặc tên mục). Lộ trình = `docs/lo-trinh-chuyen-doi-so.md` (LT). Sổ tay = PDF «Công thức sản xuất…» (ST, số trang trong PDF, đối chiếu qua TK vì bản PDF ở máy này lỗi font).

Mức: **cao** = sai so với thiết kế đã chốt hoặc lộ dữ liệu; **vừa** = thiếu hoặc lệch, nên sửa trước khi sếp duyệt; **thấp** = chỉnh cho sạch.

## 0. Màn thuộc giai đoạn nào

| STT | Key | GĐ | Ghi chú |
|---|---|---|---|
| 02 | home-shop | 1 (+2) | 4 nút lớn theo TK 6.1, nhưng LT nói GĐ1 chỉ 3 nút. Nút «Sản xuất», «Gán tem» là GĐ2 |
| 03–06 | receipt-1/2/3, receipt-list | 1 | AC-01..05 |
| 07 | issue-menu | 1 (+2) | Ô «Quế khô» GĐ1; ô «Đơn hàng thành phẩm» GĐ2 |
| 08 | issue-dry | 1 | AC-06 |
| 09 | issue-product | 2 | Serial, quà, người mua cuối: BR-22..25, AC-12, AC-20..24 |
| 10, 11 | issue-list, issue-detail | 1 (quế khô) + 2 (đơn thành phẩm) | |
| 12 | inv-nl | 1 | AC-06, AC-07 |
| 13 | inv-tp | 2 | Cần lô thành phẩm và serial |
| 14 | inv-kk | 1 | AC-07 |

Không màn nào trong cụm A thuộc GĐ3–4. Cụm A **không có** màn nào về kho phụ liệu (xem A-02).

## 1. Danh sách vấn đề

### A-01 · Mã lô thành phẩm còn theo mẫu cũ · mức **cao**
- **Màn:** 12 / 13 / 14 (`inv-nl`, `inv-tp`, `inv-kk`), tab «Thành phẩm».
- **Sai gì:** cột «Lô» ghi `TP-TD10-2611-02`. Mẫu này đã bị bỏ. Lô thành phẩm nay là `<mã công thức>-YYMMDD-NN`.
- **Căn cứ:** `12:29`, `13:29`, `14:29` (cùng một dòng `<td class="mono">TP-TD10-2611-02</td>`). TK (bảng mẫu mã BR-20, dòng «Lô thành phẩm (= mã mẻ)») và TK (mục «Chốt mẫu mã lô»: «Mẫu lô thành phẩm cũ `TP-<SKU>-YYMM-NN` và ví dụ TP-TD10-2611-03 bị bỏ»). Sổ tay tr.14 mục C.3: `QC1-261117-01`.
- **Đề xuất sửa:** trong 3 file, đổi `TP-TD10-2611-02` thành `Q100-261120-01`. Lý do chọn Q100: sản phẩm là «Tinh dầu quế Văn Yên 10 ml», hạn dùng trên màn là 24 tháng (20/11/2026 → 20/11/2028), khớp công thức Q100 (dầu quế 100% đóng chai 10 ml, hạn 24 tháng, TK mục seed công thức và `shelf_life_months` ở TK). Giữ nguyên ngày SX 20/11/2026 để phần `261120` khớp ngày. Số 145 tem, ngày SX, hạn dùng giữ nguyên.

### A-02 · Thiếu hẳn kho phụ liệu: nhập phụ liệu và tồn phụ liệu · mức **cao**
- **Màn:** thiếu. Menu «Nhập hàng» 03 và «Xem tồn kho» 12–14 không có chỗ nào cho phụ liệu.
- **Sai gì:** TK nay đã mô tả đủ: mục 6.5a «Phiếu nhập phụ liệu» (vào từ «Nhập hàng» → tab «Phụ liệu») và mục 6.5 gạch đầu dòng «Phụ liệu» (tab tồn kho). Bảng `ingredient_receipt` (mã `PNP-YYMMDD-NNN`), `ingredient_lot` (mã `<mã phụ liệu>-YYMM-NN`, tồn gram `remaining_g`). Sổ tay cân từng gram, một lô dùng cho nhiều lệnh. Mockup chỉ có kho quế (kg) và thành phẩm: xưởng không nhập được phụ liệu, không xem được tồn gram.
- **Căn cứ:** TK mục 6.5a; TK mục 6.5 (gạch «Phụ liệu»); TK mục 2 (dòng «Lập phiếu nhập phụ liệu»: WORKSHOP **Có**); TK mục 9 (API `/ingredient-receipts`, `/ingredient-lots`); BR-10 (phiếu nhập phụ liệu **không có đơn giá**); BR-20 (mẫu PNP, lô phụ liệu).
- **Đề xuất sửa (thêm màn, tạo file mới, ghi vào `_ds.json` cụm A với `"sau"`):**
  1. Key `ingr-receipt`, `sau: receipt-list`. «Nhập hàng — tab Phụ liệu», dùng khuôn 03–05: Bước 1 nơi bán (tên, SĐT; gợi ý «Nguồn gia đình»); Bước 2 chọn phụ liệu bằng nút (Q, QM, CAM, TTV, HH, HOI, DPG, SD, SO, TC… theo seed phụ liệu của TK mục 4; **bỏ NUOC** vì `track_stock=false`); gõ **gram**; số lô trên nhãn NCC; hạn dùng theo nhãn; nút đính ảnh COA. Phụ liệu `requires_coa` (Q, CAM, TTV, HH, HOI) mà chưa có COA: **cảnh báo vàng**, vẫn lưu được (không phải chặn đỏ). Bảng dòng hàng và chân màn chỉ có gram, **không có cột đơn giá, thành tiền, tổng tiền**. «Lưu và in» in phiếu PNP + 1 tem lô phụ liệu mỗi dòng (QR chứa mã, ví dụ `CAM-2611-01`).
  2. Key `ingr-stock`, `sau: inv-kk`. Thêm tab thứ 4 «Phụ liệu» cho bộ tab của 12–14 (`12:17`) và dựng một màn với tab này đang chọn: bảng phụ liệu → số lô, **tổng gram còn**, hạn dùng gần nhất; lô dưới 60 ngày tô cam, quá hạn tô đỏ, tinh dầu mua ngoài chưa có COA có chấm vàng; gồm cả bán thành phẩm (dầu quế đã ủ, hương nền, dung dịch tẩm). Bấm ô xem từng lô và các lệnh đã lấy gram. Không có cột giá. Số liệu mẫu: `Q-2611-01` (dầu quế đã ủ, hạn 24 tháng), `CAM-2611-01`, `DPG-2611-01`, `TT1-2611-01` (tự làm).
  3. Màn 03 (và 02 nếu cần): thêm hai tab «Quế» / «Phụ liệu» ở đầu màn nhập hàng. Trang chủ 02 vẫn 4 nút lớn, không thêm nút.
- **[SẾP QUYẾT]** Không còn là câu hỏi có/không (TK đã chốt WORKSHOP được nhập). Chỉ cần sếp xác nhận mockup vẽ cả hai màn phụ liệu ở GĐ2 (phụ liệu phục vụ công thức và lệnh sản xuất, GĐ2). **Mặc định:** vẽ cả hai, đánh dấu GĐ2.
- Ghi cho Lead: TK mục 6.5a chưa nói rõ phiếu nhập phụ liệu có màn «danh sách phiếu / sửa / hủy trong ngày» như 06 không (API có `PATCH` và `cancel`). Mặc định: tái dùng màn 06 với tab «Phụ liệu» ở đầu; chưa vẽ riêng.

### A-03 · Bao bì (chai, nắp, túi, nhãn, hộp) không có trong thiết kế lẫn mockup · mức **vừa** · [SẾP QUYẾT]
- **Màn:** thiếu (cùng chỗ với A-02).
- **Sai gì:** sổ tay liệt kê chai thủy tinh hổ phách 100/500 ml, chai thành phẩm 10/30 ml nút nhỏ giọt, nhãn ghi mã lô, ngày SX, hạn dùng, cảnh báo (ST tr.3, tr.14), nhưng TK chỉ quản lý phụ liệu **theo gram**; bao bì bị loại khỏi giá vốn (BR-10; câu hỏi mở cuối TK mục 13: «Giá vốn có cần tính thêm bao bì và phụ liệu không (mặc định: không)»). Kho đếm cái (chai, túi, nhãn) không có bảng nào. Nếu xưởng hết chai/nhãn thì phần mềm không báo.
- **Căn cứ:** TK (BR-10), TK, TK (định nghĩa phụ liệu «quản lý theo gram»), ST tr.3, tr.14 (qua TK).
- **Đề xuất:** **không vẽ** kho bao bì ở mockup này. Để bù lại, trong màn tồn kho mới (A-02 mục 2) ghi dòng xám «Bao bì (chai, túi, nhãn): chưa quản lý trong phần mềm GĐ1–2».
- **Phương án mặc định:** không làm kho bao bì ở GĐ1–2. Phương án thay: coi chai/túi/nhãn là phụ liệu đếm theo cái (`unit='cái'`), cần sửa TK (`ingredient` hiện tính gram) và BR-10, không thuộc việc sửa mockup.

### A-04 · Trang chủ xưởng: số nút, nút thuộc GĐ2, thiếu nút mới · mức **vừa** · [SẾP QUYẾT]
- **Màn:** 02 (`home-shop`).
- **Sai gì:** (a) Có 4 nút lớn + 3 nút nhỏ (`02:17-27`). TK 6.1 nói «Bốn nút lớn … Không có menu bên»; LT nói «trang đầu chỉ có 3 nút lớn». Hai tài liệu đã lệch nhau, mockup thêm 3 nút nhỏ thứ ba. (b) «Gán tem / hủy tem» (`02:27`, href `/dong-goi`) và «Sản xuất / đóng gói» (`02:20`) là GĐ2; bản GĐ1 không có. (c) Chưa có chỗ cho «Mẫu lưu» (TK má»¥c 7.5 dòng «Màn hình "Mẫu lưu" (OWNER, xưởng xem)»).
- **Căn cứ:** TK (mục 6.1); LT; TK (mục 7.5).
- **Đề xuất sửa:** giữ 4 nút lớn như TK 6.1. Ba nút nhỏ giữ cho GĐ2 nhưng thêm chú thích dưới màn (hoặc `data-gd="2"`) để biết nút nào bản GĐ1 bỏ. Thêm nút nhỏ «Mẫu lưu». Nhập phụ liệu vào từ tab trong «Nhập hàng» (A-02), không thêm nút. Không thêm menu bên.
- **Mặc định cho [SẾP QUYẾT]:** mockup trình bày bản **đầy đủ GĐ2**; bản GĐ1 tự động chỉ còn Nhập hàng / Xuất hàng / Xem tồn kho (đúng LT).

### A-05 · Phân quyền xem giá: danh sách phiếu lộ tiền không nhất quán · mức **cao** · [SẾP QUYẾT]
- **Màn:** 06 (`receipt-list`), 10/11 (`issue-list`, `issue-detail`).
- **Sai gì:** TK: với WORKSHOP, mọi trường giá bị loại khỏi response báo cáo, «trừ chính phiếu người đó đang lập». Trên màn: 06 hiện tiền cho PN-005, PN-002, PN-001 (người lập «Thủ kho (mẫu)»: `7.460.100 đ`, `19.000.000 đ`, `6.562.500 đ`), nhưng **ẩn «—»** cho PN-004, PN-003 (người lập «Chủ doanh nghiệp (mẫu)»). Cột «Tổng tiền» ở 10 hiện `300.000 đ` cho PX-001 và «—» cho PX-004, PX-003. Tức mockup cho thủ kho xem giá các phiếu cũ mình đã lập, vượt mức TK; còn ở 10 không rõ vì sao PX-001 hiện mà hai phiếu kia thì không (cột «Người lập» không có, xem A-06).
- **Căn cứ:** TK (bảng phân quyền dòng «Báo cáo tồn kho: Có (không thấy giá)») và TK (câu «mọi trường giá … bị loại khỏi response của báo cáo, trừ chính phiếu người đó đang lập»); AC-06 («WORKSHOP không thấy giá trên báo cáo tồn kho»); TK (API `/material-lots`: «WORKSHOP: bỏ trường giá»). Hiện giá trên danh sách là chuyện của API, không chỉ ẩn nút (TK).
- **Đề xuất sửa:** (1) ở 06 và 10 bỏ cột «Tổng tiền» cho WORKSHOP (`06:26` cột thứ 6, `10:29` cột thứ 7); hoặc nếu giữ cột thì mọi dòng phải là «—». (2) Màn sau khi **lưu** (05, hộp thoại in) vẫn hiện tiền vì là phiếu đang lập. (3) 11: dialog đã không có tiền, giữ; xóa ô `<td class="num"></td>` trống ở cột cuối bảng dòng hàng (xem A-14).
- **[SẾP QUYẾT]** Thủ kho có được xem lại tiền các phiếu **mình đã lập** trong ngày không? **Mặc định:** không (đúng chữ TK). Phương án thay: cho xem tiền phiếu của chính mình trong ngày lập, mọi phiếu khác «—» (cần sửa TK theo topic #2).
- Lưu ý cho thiết kế: TK mục 2 (bảng giá theo hạng, WORKSHOP «Không») mâu thuẫn mục 6.2 (giá mua hôm nay hiện dưới mỗi nút hạng ở màn nhập). Mockup 04 theo mục 6.2 (hiện giá). Ghi cho topic #2, không phải lỗi mockup.

### A-06 · Danh sách phiếu thiếu cột «Người lập» và nút Hủy luôn hiện · mức **vừa**
- **Màn:** 10 (`issue-list`), 11 (`issue-detail`).
- **Sai gì:** BR-06 (cùng quyền như BR-05): WORKSHOP chỉ hủy được phiếu **của mình, trong ngày lập**. Màn 06 đã làm đúng (cột «Người lập», nút Sửa/Hủy chỉ ở PN-005). Màn 10 không có cột «Người lập»; dialog chi tiết ở 11 luôn có nút «Hủy phiếu» (`11:38`) cho PX-004 mà không nói phiếu của ai.
- **Căn cứ:** TK (BR-05, BR-06); TK (bảng phân quyền: sửa/hủy phiếu, «Có, chỉ phiếu của mình»; sau ngày lập «Không»); AC-05; `06:26` (đã đúng).
- **Đề xuất sửa:** (1) 10: thêm cột «Người lập» sau «Khách» (copy kiểu cột ở `06:26`). (2) 11: nút «Hủy phiếu» chỉ hiện nếu phiếu của chính mình và trong ngày; phiếu khác thì thay bằng chữ xám «Chỉ chủ DN hủy được» (cùng chữ với AC-05: «Chỉ chủ doanh nghiệp được sửa phiếu ngày trước»). (3) Thêm trạng thái «Đã hủy» làm một dòng mẫu trong danh sách (BR-19: không xóa cứng); hiện số phiếu bị nhảy: 10 có PX-004, 003, 001, không có 002.

### A-07 · Màn nhập người mua: nhãn bắt buộc cố định, dòng báo trùng, thiếu trạng thái theo kênh · mức **vừa**
- **Màn:** 09 (`issue-product`).
- **Sai gì:** (a) Banner tìm thấy người mua bị lặp hai lần giống hệt (`09:31`: hai khối `<div class="banner ok">T T H · *******222 …</div>`). (b) Nhãn `Người mua cuối <small id="buyer-req">(bắt buộc tên + SĐT)</small>` (`09:28`) đúng với kênh Bán trực tiếp đang chọn, nhưng BR-22 khác theo kênh: sàn (Shopee, TikTok, Lazada) bắt buộc **tên + tỉnh**, không bắt SĐT; đại lý / quà tặng DN / xuất khẩu không bắt buộc. Mockup chỉ có một trạng thái; 11 có đơn Shopee (người mua «L M T», không SĐT) nhưng màn nhập tương ứng không có. (c) Chưa có màn mẫu cho trường hợp chưa có SĐT trong hệ thống (khối `#b-new` hiện, `09:32-41`, đang bị `hidden`).
- **Căn cứ:** TK (mục 6.6 «Mức bắt buộc phụ thuộc kênh bán»), BR-22 (TK), AC-20, AC-21; chuẩn hóa số BR-23 (+84 → 0).
- **Đề xuất sửa:** (a) xóa khối banner thứ hai ở `09:31`. (b) Tạo 2 màn phụ: `09b-issue-product-san` (kênh Shopee đang chọn, nhãn «(bắt buộc tên + tỉnh)», ô SĐT ghi «không bắt buộc»); và `09c-issue-product-moi` (SĐT chưa có → hiện `#b-new` với họ tên, lưới Tỉnh/xã, số nhà, ô đồng ý Zalo/SMS). (c) Thêm màn lỗi AC-21: bấm Lưu ở kênh Website khi thiếu SĐT → banner đỏ «Cần tên và số điện thoại người mua».
- **Ghi chú:** ô SĐT đang gõ hiện rõ `0987111222` (`09:30`) đúng TK 6.6 («Lúc đang nhập: trường gõ hiện rõ»). Tên đã che «T T H» đúng BR-24. Không cần sửa.

### A-08 · Màn quét thành phẩm: thiếu các thông báo lỗi và BR-25 · mức **thấp**
- **Màn:** 09.
- **Sai gì:** chỉ có một lỗi mẫu («Đã quét trong phiếu này», `09:53`). TK 6.4 liệt kê 6 lý do quét sai (mã không tồn tại, tem chưa gán lô, đã xuất ngày dd/mm, đã hủy, lô bị thu hồi, đã quét trong phiếu này), bíp dài + thông báo đỏ.
- **Căn cứ:** TK (mục 6.4), AC-12, BR-13, BR-25 (đơn phải có ít nhất 1 dòng không phải quà).
- **Đề xuất sửa:** thêm một màn phụ hoặc khung chú thích liệt kê chữ cho 5 lỗi còn lại, và lỗi BR-25 «Đơn phải có ít nhất một sản phẩm không phải quà». Không bắt buộc cho bản duyệt đầu.

### A-09 · Xuất quế khô: số liệu mẫu mâu thuẫn, nhập số thập phân chưa rõ · mức **vừa** · [SẾP QUYẾT]
- **Màn:** 08 (`issue-dry`).
- **Sai gì:** ô số cân đang có `value="1.180"` (`08:37`) khi **chưa quét lô nào** (`#picked` rỗng, nút «Lưu và in» đang `disabled`, bảng «Chưa có dòng nào»). Các lô trong danh sách chỉ nặng 30 / 120,5 / 45 kg (`08:35`), nên 1.180 kg không thể là cân của lô nào trong màn này. Đồng thời «1.180» là dấu chấm của phần nghìn (AC-06 ghi 1.180 kg), nhưng TK 6.2 nói ô số nhận **cả dấu phẩy và dấu chấm thập phân**, vậy «1.180» có thể bị hiểu là 1,18 kg. Không xác định được cách xử lý.
- **Căn cứ:** AC-06 (TK: L1 1.250 kg, bán 1.180 kg, OWNER thấy 94,4%); TK mục 6.2 (dấu phẩy và chấm thập phân); TK (OWNER thấy dòng phụ «Cân lúc mua → cân lúc bán (94,4%)»).
- **Đề xuất sửa:** (1) 08: chọn lô **NL-2611-0008** (Vỏ quế Loại 2, 45 kg), đưa vào `#picked` và bảng dòng một dòng mẫu: «Vỏ quế Loại 2 · NL-2611-0008 · 42,5 kg · 50.000 đ · 2.125.000 đ», tổng khớp, nút Lưu bật. 42,5/45 = 94,4% đúng ví dụ AC-06. (2) Đổi `value="1.180"` thành `value="42,5"`. (3) Màn xưởng **không** hiện dòng phụ «94,4%» (chỉ OWNER); nếu muốn minh họa thì đặt ở màn của chủ DN (cụm C, báo cho BA cụm C).
- **[SẾP QUYẾT]** Quy tắc đọc số: **Mặc định:** dấu phẩy hoặc chấm đứng một mình luôn là thập phân; số từ 1000 gõ liền không dấu («1180»); khi hiển thị dùng «1.180,5 kg» (chấm nghìn, phẩy thập phân, như 03–05 đang dùng «120,5»). Cần ghi vào TK 6.2 (báo Lead cho topic #2).

### A-10 · Danh sách lô tồn để chọn không có nhãn «mua là loại N» và không có luồng CHUNG · mức **thấp**
- **Màn:** 08.
- **Sai gì:** Loại bán đang chọn là Loại 2 (`08:34`), nhưng danh sách (`08:35`) lẫn cả lô «Loại 1 · 120,5 kg» mà chỉ ghi chữ «Loại 1» trong dòng phụ như mọi lô khác. TK: lô có loại lần 1 khác loại bán vẫn chọn được, nhưng hiện **nhãn xám «mua là loại 2»** để biết là phân loại lại bằng tay. Danh sách cũng không cho biết lô nào là hàng chung (GENERAL); TK 6.2 yêu cầu xưởng phân biệt hàng chung khi xếp kho (tem in chữ «CHUNG»).
- **Căn cứ:** TK (mục 6.3 cuối), TK (tem GENERAL in «CHUNG»), AC-03.
- **Đề xuất sửa:** trong `08:35` mỗi nút lô thêm `<span class="tag">` xám: với NL-2611-0007 «mua là loại 1»; thêm một lô mẫu hàng chung (ví dụ lô của Thương lái Bình) kèm nhãn «CHUNG» đậm. Lô trùng loại bán thì không cần nhãn.

### A-11 · Nhập hàng: thiếu màn «Người bán mới» và nhãn luồng hàng · mức **vừa**
- **Màn:** 03 (`receipt-1`), thiếu thêm màn.
- **Sai gì:** nút «+ Người bán mới» (`03:25`) có nhưng không có màn form nhỏ. TK: tên*, kiểu*, thôn* (chọn Xã → Thôn bằng nút), luồng mặc định GENERAL, chủ DN duyệt sau. AC-04 cần thấy hệ quả (lô GENERAL, OWNER thấy «1 người bán chờ duyệt»). Lưới người bán (`03:24`) không hiện luồng; luồng chỉ hiện sau khi chọn (`04:21`, tag «Vùng kiểm soát»). Xưởng không biết trước Thương lái Bình là hàng chung (AC-03).
- **Căn cứ:** TK, TK (duyệt người bán mới), BR-03, AC-03, AC-04.
- **Đề xuất sửa:** (1) thêm màn `03b-receipt-newsup` (`sau: receipt-1`): form nhỏ như trên; dòng xám «Người bán mới mặc định là hàng chung, chủ DN duyệt sau». (2) `03:24`: nút «Thương lái Bình» thêm tag «Hàng chung». (3) Ở 04, khi chọn người bán GENERAL: tag «Hàng chung» thay «Vùng kiểm soát» (thêm một biến thể, có thể là màn phụ).

### A-12 · Màn lưu phiếu nhập: thiếu hộp thoại in phiếu và tem lô · mức **vừa**
- **Màn:** 05 (`receipt-3`).
- **Sai gì:** TK: Lưu xong mở hộp thoại in gồm **1 phiếu nhập + 1 tem lô mỗi dòng** (QR chứa mã NL-…, chữ: mã lô, nguyên liệu, loại, kg, ngày, tên người bán); lô GENERAL in thêm chữ **«CHUNG»** đậm. 05 chỉ hiện banner «Đã lưu … 3 lô» (`05:55`) và hai nút in lại. Không thấy tem trông thế nào. Bộ phận làm tem cần mẫu này; AC-01, AC-03 kiểm đúng nội dung tem.
- **Căn cứ:** TK (mục 6.2, «Lưu và in»), TK (in ấn: khổ tem trong setting, QR ≥ 18 mm; câu hỏi mở: mặc định 40 × 30 mm), AC-01, AC-03.
- **Đề xuất sửa:** thêm màn `05b-receipt-print` (`sau: receipt-3`): khung xem trước 2 tem 40 × 30 mm: «NL-2611-0007 · Vỏ quế · Loại 1 · 120,5 kg · 20/11/2026 · Gia đình (đồi nhà)» có ô QR; tem thứ hai mẫu hàng chung có dải đậm «CHUNG». Kèm khung phiếu nhập (khổ A5). Phiếu nhập này là phiếu đang lập, nên **có hiện tiền**; tem **không có giá**.

### A-13 · Màn nhập: thiếu cảnh báo giá lệch 20% và banner «chưa có giá hôm nay» · mức **thấp**
- **Màn:** 04 (`receipt-2`), và biến thể.
- **Sai gì:** các phần tử có trong HTML nhưng không hiện trạng thái nào: `#line-warn` (`04:45`), `#price-banner` (`04:17`), `#manual-price-box` (`04:40`). Thiết kế cần ba trường hợp: giá lệch > 20% bảng giá → cảnh báo vàng, vẫn cho lưu; không có giá hôm nay → «Chưa có giá hôm nay, đang dùng giá ngày dd/mm»; chưa từng có giá → bắt gõ đơn giá tay.
- **Căn cứ:** TK, BR-04, câu hỏi mở «Ngưỡng cảnh báo giá mua lệch bảng giá (mặc định 20%)».
- **Đề xuất sửa:** thêm 1 màn phụ `04b-receipt-warn`: sửa giá dòng 2 thành 52.000 đ/kg (so bảng giá 38.000 → lệch > 20%), hiện `#line-warn` vàng «Giá lệch hơn 20% so với bảng giá, vẫn lưu được». Thêm banner xám `#price-banner` ở `04:17`: «Chưa có giá hôm nay, đang dùng giá ngày 19/11». Hai trạng thái còn lại để ghi chú, không cần vẽ.

### A-14 · Chi tiết đơn (11): thiếu quà, lô và hạn của serial; có ô trống · mức **thấp**
- **Màn:** 11 (`issue-detail`).
- **Sai gì:** TK: mở một đơn thấy người mua, dòng hàng, **dòng quà**, và **từng serial**; BR-25 gắn nhãn «Quà tặng». Dialog ví dụ là đơn Shopee không có quà, nên chưa thấy nhãn quà; bảng dòng hàng không có tiêu đề cột, có một ô `<td class="num"></td>` trống (cột giá của WORKSHOP, `11:38`).
- **Căn cứ:** TK (6.4, «Mở một đơn thấy…»).
- **Đề xuất sửa:** làm dialog cho đơn **PX-261120-001 (có quà)** làm màn chính: dòng hàng 2 chai 150.000, dòng quà tinh dầu (nhãn «Quà tặng», 0 đ) và thiệp; mỗi serial kèm mã lô thành phẩm và hạn dùng. Đổi ô trống thành xóa hẳn cột giá cho WORKSHOP (A-05).

### A-15 · Tồn kho thành phẩm: chưa hiện cảnh báo hạn dùng và lô đang ủ · mức **thấp** · [SẾP QUYẾT]
- **Màn:** 13 (`inv-tp`).
- **Sai gì:** TK 6.5: lô còn dưới 60 ngày đến hạn tô cam; mockup chỉ có một lô còn 24 tháng nên không thấy màu cam. Về giai đoạn ủ: lô có ủ 2–6 tuần có mã mẻ ngay từ ngày pha (TK mục 3), nhưng chỉ thành lô thành phẩm khi nhập đầu ra. Tồn kho thành phẩm không có chỗ cho các mẻ đang ủ; đồng thời con số «Số tem trong kho» không gồm chai lưu mẫu (TK: chai lưu mẫu không dán tem, không tính vào `quantity`).
- **Căn cứ:** TK (6.5), TK (7.2, lệnh CURING), TK (7.5).
- **Đề xuất sửa:** thêm dòng mẫu thứ hai ở `13:29`, ví dụ `QC1-261117-01`, hạn còn 45 ngày, tô cam. Chú thích dưới bảng: «Số tem không gồm chai lưu mẫu».
- **[SẾP QUYẾT]** Có hiện mẻ đang ủ ngay ở «Xem tồn kho» không? **Mặc định:** không; mẻ đang ủ chỉ xuất hiện ở màn «Sản xuất» (TK: danh sách lệnh DRAFT và CURING, «Còn N ngày»), thuộc cụm B. Tồn kho chỉ có lô đã nhập đầu ra.

### A-16 · Kiểm kê (14): chỉ kiểm quế, không kiểm phụ liệu · mức **thấp**
- **Màn:** 14 (`inv-kk`).
- **Sai gì:** kiểm kê của TK 6.5 chỉ so với lô `IN_STOCK`: đúng với màn hiện có (4 lô, 3 khớp, 1 thiếu NL-2611-0009, 1 lạ NL-2611-9999; số khớp, tính lại được: 3 + 1 = 4 lô). Nhưng phụ liệu tính gram, kiểm bằng cách quét tem lô thì chỉ biết có lô, không biết còn bao nhiêu gram (TK «cân điện tử»). Màn cũng không nói lô đang nằm trong lệnh sản xuất (RESERVED, đã nêu ở 12: «1 lô, 22,5 kg») không tính vào danh sách chờ quét.
- **Căn cứ:** TK (mục 6.5), AC-07, TK (vòng đời lô).
- **Đề xuất sửa:** thêm dòng xám trong banner `14:32`: «Lô đang nằm trong lệnh sản xuất không tính vào kiểm kê». Kiểm kê phụ liệu để sau khi sếp quyết A-02 (mặc định: kiểm kê chỉ quét lô quế và thành phẩm, phụ liệu cân lại khi cần).

### A-17 · Danh sách sản phẩm trong bộ lọc có Trà quế · mức **thấp**
- **Màn:** 10, 11 (`#product`, `10:23`, `11:23`).
- **Sai gì:** lọc «Sản phẩm» liệt kê «Trà quế Văn Yên 100 g». Trà là thực phẩm (`is_food`) cần giấy ATTP mới được lập phiếu xuất (BR-14), và LT xếp trà vào GĐ4. Năm đầu chỉ có tinh dầu, túi thơm, hộp quà (`docs/tom-tat.md`: chiến lược năm 1).
- **Căn cứ:** BR-14 (TK), LT GĐ4 (LT), `docs/tom-tat.md` mục «Bối cảnh».
- **Đề xuất sửa:** bỏ option Trà khỏi `<select id="product">` ở hai file, hoặc thay bằng «Hộp quà 290.000 đ». Danh sách sản phẩm đợt 1 còn là câu hỏi mở (TK); ghi chú để chủ DN chốt.

## 2. Màn còn thiếu (tổng hợp)

| Đề xuất key (`sau`) | Nội dung | Mức | Căn cứ |
|---|---|---|---|
| `ingr-receipt` (`receipt-list`) | Nhập phụ liệu (PNP): nơi bán, phụ liệu, gram, số lô NCC, hạn, COA | cao | A-02, TK |
| `ingr-stock` (`inv-kk`) | Tồn kho phụ liệu theo gram, tab thứ 4 | cao | A-02, TK |
| `03b-receipt-newsup` (`receipt-1`) | Form «Người bán mới», luồng GENERAL, chờ duyệt | vừa | A-11, AC-04 |
| `05b-receipt-print` (`receipt-3`) | Xem trước phiếu + tem lô (có «CHUNG») | vừa | A-12, AC-01/03 |
| `04b-receipt-warn` (`receipt-2`) | Giá lệch 20%, banner giá cũ | thấp | A-13, BR-04 |
| `09b`, `09c` (`issue-product`) | Kênh sàn (tên + tỉnh), người mua mới, lỗi AC-21 | vừa | A-07, BR-22 |
| Màn «Mẫu lưu» (xưởng xem) | Danh sách theo hạn lưu, vị trí | thấp (cụm B) | TK má»¥c 7.5 |

Các màn «Mẫu lưu», «Lô chưa lưu mẫu» thuộc cụm B (sản xuất) hoặc C (chủ DN) chứ không phải kho; ghi lại để BA hai cụm này gom.

## 3. Việc cụm A không có và chuyển cho Lead/BA khác

- **Công nợ nhà cung cấp:** LT liệt kê trong đầu ra GĐ1. TK chỉ nhắc ở bảng phân quyền (TK), không có bảng dữ liệu hay màn nào. Mockup cụm A không có; nếu có thì thuộc màn chủ DN (cụm C). Báo Lead: thiết kế thiếu, hỏi sếp có làm ở GĐ1 không.
- **Chênh LT/TK về trang chủ xưởng:** 3 nút (LT) và 4 nút (TK). Đã nêu ở A-04.
- **Quyền xem giá:** TK mục 2 mâu thuẫn mục 6.2 (A-05).
- **Dữ liệu mẫu có ngày 20/11/2026** (06, 10, 12…) trong khi hôm nay là 21/11/2026. Không phải lỗi, chỉ nhớ là dữ liệu đóng băng.

## 4. Đã soát và đúng (không cần sửa)

- 04: tính tiền đúng: 120,5 × 45.000 = 5.422.500; 45 × 38.000 = 1.710.000; 18,2 × 18.000 = 327.600; tổng 7.460.100 đ, 183,7 kg. Khớp AC-01 và BR-04 (làm tròn).
- 05: mã phiếu `PN-261120-005`, lô `NL-2611-0007..0009` đúng mẫu BR-20; 3 lô khớp với 12 (0007: 120,5 kg Vỏ L1; 0008: 45 kg Vỏ L2; 0009: 18,2 kg Quế vụn L1; Vỏ L2 tổng 75 kg gồm cả NL-2611-0002).
- 06: chỉ phiếu của mình, trong ngày, chưa dùng lô mới có Sửa/Hủy (BR-05); phiếu đã có lô dùng bị khóa.
- 09/10/11: tên che «T T H», «N V A», «L M T», SĐT che `*******222`, `*******678` đúng BR-24, AC-24. Serial 10 ký tự Base32 (không chứa I, L, O, U). Đơn mẫu 2 chai × 150.000 + 1 quà + thiệp = 300.000 đ, 4 món, khớp AC-22 và BR-25.
- 12–14: không hiện giá cho WORKSHOP; 2 cột «Vùng kiểm soát» / «Hàng chung» đúng TK; kiểm kê báo thiếu/thừa, không tự sửa dữ liệu (AC-07).
- Kênh bán trong 09/10 có đủ 10 giá trị, khớp BR-22.

## 5. Chưa kiểm

- Không chạy trình duyệt: các nhận xét dựa trên HTML tĩnh trong `de-xuat/man/a-nhap-xuat-kho/`. JS của vỏ (`vo.html`) và hành vi bấm không xem; nhãn `#buyer-req` ở A-07 có thể đổi theo kênh khi bấm thật, chưa kiểm.
- Sổ tay PDF: bản `pdftotext` lỗi font tiếng Việt; đối chiếu số trang và nội dung qua TK (đã trích dẫn sổ tay) và qua phần chữ đọc được (danh sách dụng cụ tr.3, mã lô tr.14).
