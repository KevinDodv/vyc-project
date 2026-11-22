# Thay đổi cụm A (nhập, xuất, kho): task #24

Người làm: Khoa (dev) · 21/11/2026. Sửa 12 màn cũ và thêm 7 màn mới trong `de-xuat/man/a-nhap-xuat-kho/`. Không đụng `app.css`, `goc/`, `nhan-xet*`, `_tools/`, cụm B và C. CSS: dùng `app.css`; chỗ cần kiểu riêng (nhãn GĐ2, tab dạng link, tem 40 × 30) thì đặt `style` ngay trong màn.

Mã vấn đề A-nn theo `docs/mockup/nhan-xet.md`. Ghép thử: copy `docs/mockup` ra thư mục tạm ngoài repo, chạy `_tools/mockup.mjs ghep` ở đó: 63 màn, không trùng key. Chụp trước/sau do #27.

## 1. Màn đã sửa (mỗi màn một dòng)

| Key | Mã | Đã đổi gì |
|---|---|---|
| `home-shop` | A-04 | Giữ 4 nút lớn + nút nhỏ. Gắn `data-gd` và nhãn «GĐ2» cho Sản xuất, Gán tem; thêm nút nhỏ «Mẫu lưu» (GĐ2, `/mau-luu`); thêm dòng chú thích bản GĐ1 chỉ có 5 nút nào |
| `receipt-1` | A-02, A-11 | Thêm tab «Quế / Phụ liệu» (link `/nhap-hang/phu-lieu`); «+ Người bán mới» thành link `/nhap-hang/nguoi-ban-moi`; «Thương lái Bình» có nhãn «Hàng chung» |
| `receipt-2` | A-02, A-11 | Thêm tab «Quế / Phụ liệu»; «+ Người bán mới» thành link |
| `receipt-3` | A-02, A-12 | Thêm tab; «In lại phiếu» và «In lại tem lô» thành link tới hộp thoại in (`/nhap-hang/in-phieu`) |
| `receipt-list` | A-05, A-02 | Bỏ cột «Tổng tiền» (xưởng không xem tiền phiếu cũ), thêm câu giải thích; thêm tab «Phiếu nhập quế / Phiếu nhập phụ liệu (GĐ2)» (tab phụ liệu dùng lại khuôn này, chưa vẽ riêng) |
| `issue-dry` | A-09, A-10 | Ô số cân trống (hết `1.180`); đã chọn lô `NL-2611-0008`, dòng mẫu 42,5 kg × 50.000 đ = 2.125.000 đ, tổng và nút Lưu bật; lô `NL-2611-0007` có nhãn «mua là loại 1» |
| `issue-product` | A-07, A-08 | Xóa banner người mua lặp lần hai; thêm khung «Các lỗi quét và lỗi lưu khác»: mã không tồn tại, tem chưa gán lô, đã xuất ngày, tem đã hủy, lô thu hồi, và lỗi BR-25 khi lưu |
| `issue-list` | A-05, A-06, A-17 | Bỏ cột «Tổng tiền»; thêm cột «Người lập»; thêm dòng «Đã hủy» (PX-002); bỏ option Trà khỏi bộ lọc sản phẩm |
| `issue-detail` | A-05, A-06, A-14, A-17 | Cùng bảng nền như `issue-list`. Hộp thoại đổi sang đơn PX-001: có người lập, 2 chai + 1 tinh dầu quà + thiệp quà, mỗi serial kèm lô và hạn dùng, có nhãn «Quà tặng», không có cột giá; chân hộp thoại nói rõ ai được hủy. Bỏ option Trà |
| `inv-nl` | A-01, A-15, A-16, A-02 | Tab Thành phẩm: lô `Q100-261120-02`, thêm lô cam `Q100-250105-01` còn 46 ngày, chú thích «số tem không gồm chai lưu mẫu»; banner kiểm kê thêm câu lô đang trong lệnh sản xuất không tính; thêm tab «Phụ liệu (GĐ2)» (`/ton-kho/phu-lieu`) |
| `inv-tp` | A-01, A-15, A-16, A-02 | Như `inv-nl` (cùng ba tab trong một khuôn) |
| `inv-kk` | A-01, A-15, A-16, A-02 | Như `inv-nl` |

## 2. Màn mới (có trường `sau` trong `_ds.json`)

| Key | Sau | Mã | Nội dung |
|---|---|---|---|
| `receipt-newsup` | `receipt-1` | A-11 | Form người bán mới: tên, kiểu (gia đình / hộ dân / thương lái), xã, thôn bằng nút; dòng «mặc định hàng chung, chủ DN duyệt sau» |
| `receipt-warn` | `receipt-2` | A-13 | Banner xám «Chưa có giá hôm nay, đang dùng giá ngày 19/11»; dòng 2 giá 52.000 đ/kg lệch hơn 20% so với 38.000 → cảnh báo vàng; tổng 8.090.100 đ. Trường hợp «chưa từng có giá» ghi bằng chữ dưới bảng |
| `receipt-chung` | `receipt-warn` | A-11 | Người bán Thương lái Bình: nhãn «Hàng chung» thay «Vùng kiểm soát», không có bước chọn đồi; dòng Vỏ quế Loại 2, 500 kg, 19.000.000 đ |
| `receipt-print` | `receipt-3` | A-12 | Hộp thoại in sau khi lưu: phiếu nhập A5 (có tiền, vì là phiếu đang lập) và tem lô 40 × 30 mm (QR, không có giá), có một tem hàng chung với dải «CHUNG» |
| `issue-product-san` | `issue-product` | A-07 | Kênh Shopee: nhãn «(bắt buộc tên + tỉnh; SĐT không bắt buộc)», ô tên và tỉnh, SĐT để trống |
| `issue-product-moi` | `issue-product-san` | A-07 | Kênh bán trực tiếp, SĐT 0912345678 chưa có: banner «chưa có trong hệ thống», hiện khối họ tên, tỉnh/xã, số nhà, tích đồng ý Zalo/SMS |
| `issue-product-loi` | `issue-product-moi` | A-07 | Kênh Website thiếu tên và SĐT: banner đỏ «Cần tên và số điện thoại người mua» (BR-22, AC-21), ô lỗi viền đỏ |

## 3. Vấn đề không sửa trong cụm A, hoặc sửa một phần

| Mã | Tình trạng |
|---|---|
| A-02 | **Không tạo hai màn phụ liệu ở cụm A.** Nhung (#25) đã tạo `ingr-receipt` và `ingr-stock` trong `b-san-xuat/` (B-10 = A-02). Mình có dựng bản riêng rồi xóa để khỏi trùng key. Cụm A chỉ thêm tab trỏ sang hai màn đó (03–05, 06, 12–14). Màn 06 chưa có biến thể «phiếu phụ liệu» riêng, theo mặc định của nhận xét |
| A-03 | Đã có ở `ingr-stock` của Nhung (dòng xám «Bao bì: chưa quản lý»). Cụm A không thêm gì |
| A-06 | Hộp thoại ở `issue-detail` chỉ vẽ phiếu của chính thủ kho (có nút Hủy). Trường hợp phiếu người khác (PX-004 do chủ DN lập) mô tả bằng chữ ở chân hộp thoại, chưa vẽ màn riêng |
| A-10 | Chưa thêm lô «hàng chung» có nhãn «CHUNG» vào `issue-dry`: màn tồn kho `inv-nl` đang ghi cột Hàng chung là «—» (không có tồn), thêm lô sẽ lệch số. Chỉ thêm nhãn «mua là loại 1» |
| A-15 | Lô cũ lấy là `Q100-250105-01` (SX 05/01/2025, hạn 24 tháng → 05/01/2027, còn 46 ngày) thay vì `QC1-261117-01` như đề xuất, vì lô QC1 làm 17/11/2026 không thể còn 45 ngày hạn; Q100 giữ đúng cùng sản phẩm «Tinh dầu quế Văn Yên 10 ml» |
| A-08 | Làm bằng khung có thể mở trong `issue-product`, không tách màn |
| A-09 | Quy tắc đọc số chấm/phẩy chưa ghi vào TK §6.2 (việc của topic #2); màn không còn số `1.180` gây hiểu nhầm |
| 50 g | `issue-list` và `issue-detail` vẫn có «Túi thơm quế Văn Yên 50 g» trong bộ lọc sản phẩm. B-15 đề xuất 25 g nhưng không nêu hai màn này; đổi cùng lúc với cụm B nếu sếp chốt 25 g |

## 4. Route cần thêm vào vỏ (`_tools/vo.html`, hàm `route`)

Đặt **trước** mẫu `^/nhap-hang`, `^/ton-kho` đã có (vỏ dò theo thứ tự). Key trong vỏ viết gạch dưới, vỏ tự đổi sang gạch ngang.

| Mẫu | Key màn | Ở màn nào |
|---|---|---|
| `^/nhap-hang/phu-lieu` | `ingr_receipt` | tab «Phụ liệu» ở `receipt-1`, `receipt-2`, `receipt-3` |
| `^/nhap-hang/nguoi-ban-moi` | `receipt_newsup` | nút «+ Người bán mới» ở `receipt-1`, `receipt-2` |
| `^/nhap-hang/in-phieu` | `receipt_print` | «In lại phiếu / tem lô» ở `receipt-3` |
| `^/ton-kho/phu-lieu` | `ingr_stock` | tab «Phụ liệu» ở `inv-nl`, `inv-tp`, `inv-kk` |
| `^/mau-luu` | màn Mẫu lưu của cụm B (key `retain-list`?) | nút «Mẫu lưu» ở `home-shop` |

Chưa thêm route thì bấm các link trên nhảy về màn cũ gần nhất (`/nhap-hang/...` về `receipt_1`) hoặc báo «không có trong bản xem trước» (`/mau-luu`). Các màn biến thể `receipt-warn`, `receipt-chung`, `issue-product-san/-moi/-loi` chỉ vào qua menu trái hoặc nút Trước/Sau, không có link.

## Sau khi sếp duyệt (#429)

- `10-issue-list.html:23`, `11-issue-detail.html:23`: «Túi thơm 50 g» → «Túi thơm 25 g» (câu 4 chốt 25 g). Cụm A không còn «50 g».
- `04b-receipt-warn.html:39`: câu cảnh báo ghi rõ «Dòng 2 (Vỏ quế Loại 2) … bảng giá Vỏ quế Loại 2 (38.000 đ/kg)». Số 38.000 khớp 04c và bảng dòng 2 (52.000 đ, lệch >20%). Dropdown 18.000/14.000/10.000 ở dòng 46 là bảng giá của **Quế vụn** (đang chọn để nhập dòng 3), không phải Vỏ quế, nên không đổi; chỉ làm rõ chữ cảnh báo.

---

# Rà soát UX cụm A: task #35 (Long)

Làm theo `docs/mockup/ux/ra-soat-a.md` (A1–A29) và các điểm chồng của Hoa (`ux/ra-soat-c.md` mục 3, P1, P3). Chỉ sửa trong `de-xuat/man/a-nhap-xuat-kho/`; không đụng `app.css`, `_tools/`, cụm B, C. Lô 2 sếp đã chốt ở #524: Q-A1 không chọn sẵn bao, Q-A2 giữ mặc định, Q-A3 giữ hai ô riêng (đã áp, xem mục 4). Q-C1 vẫn theo **phương án mặc định**; sếp chọn khác thì sửa lại theo cột «Nếu sếp chọn khác».

## 1. Màn đã sửa

| Màn | Việc đã làm (mã đề xuất) |
|---|---|
| `02-home-shop` | 5 ô lớn: Nhập hàng, **Bán quế khô**, **Bán thành phẩm**, Xem tồn kho, Sản xuất (A10; bỏ ô «Xuất hàng»). Thêm khối **«Việc cần làm»** (lô còn chai chưa dán tem; mẻ đủ ngày ủ chờ ngửi, Hoa). Ô «Gán tem / hủy tem» đổi chữ **«Dán tem lên chai»**; thêm ô **«In tem lô»** (Q-C1 = có). Bỏ nhãn «GĐ2» và dòng chú giải (giữ `data-gd`) |
| `03`, `04`, `04b`, `04c`, `05`, `05b` | A1: một hàng 6 nút «Vỏ quế loại 1 · 45.000 đ/kg»…; A2: bỏ «(Enter)», nút «+ Thêm dòng» thành nút phụ, có dòng nhắc «Lưu và in» tự thêm dòng gõ dở, ô số cân để trống; A3: đồi chọn sẵn có chữ «lần trước»; A4: «Vùng kiểm soát (làm được tinh dầu có QR)», «Hàng chung (chỉ bán quế khô)», ẩn mã NCC; A6: bỏ «Phiếu hôm nay» khỏi thanh dưới, thành link «Xem phiếu nhập hôm nay ›» ở đầu màn; bỏ nhãn «GĐ2» |
| `05`, `05b` | A5 + P1: sau khi lưu, thanh dưới là nút chính xanh **«+ Phiếu mới»**, giữ tổng cân và tiền; hai nút in gộp một «🖨 In lại phiếu và tem lô» |
| `03b` | A7: bỏ dòng «Luồng», banner một câu, «Lưu» (nút chính 72 px) + «Hủy» thành link, ghi chú «chọn sẵn như lần thêm trước»; bỏ thanh dưới (không có việc gì ở đó) |
| `06` | A8: «Hôm nay 20/11/2026» + «＋ Xem ngày khác», bỏ nút «Xem»; A9: ghi chú một câu, dòng có lô đã dùng ghi «Không sửa, không hủy được: lô đã dùng»; nút chính «+ Phiếu nhập mới» xuống thanh dưới |
| `07` | Chỉ còn là lối dự phòng (có ghi chú), «Đơn hàng thành phẩm» → «Bán thành phẩm» |
| `08` | A11–A14: 6 nút «Vỏ quế loại 2 · bán 50.000 đ/kg»…; **không chọn sẵn bao** (lô 2, Q-A1): ô quét tem bao là lối chính, quét xong mới hiện bao đã chọn; «＋ Không quét được? Chọn lô trong danh sách» là lối phụ; «Lưu và in» tự thêm dòng dở; một nút chính; «Doanh nghiệp xuất khẩu» |
| `09`, `09b`, `09c`, `09d` | A15–A22: **một cột**, 3 bước «Bán cho ai» → «Quét tem» → «Người mua». «Bán cho ai» là một hàng nút (dưới đó là hàng «Kênh bán» đủ 10 kênh, lô 2 Q-A3: sàn, đại lý, doanh nghiệp được chọn sẵn kênh mặc định nhưng đổi được; khách lẻ chưa chọn sẵn); mã đơn chỉ hiện với Website và sàn; người mua chỉ hiện ô BR-22 bắt buộc (trực tiếp/website: họ tên + số điện thoại; sàn: họ tên + tỉnh), phần còn lại trong «＋ Thêm thông tin người mua (không bắt buộc)», ô «Đồng ý nhận tin» **không tích sẵn**; đơn giá là chữ + nút «Đổi giá»; «Số lượng» thay «SL»; lỗi quét một dòng việc phải làm |
| `10`, `11` | A27–A29: «Hôm nay / 7 ngày / Tháng này» + ô số điện thoại, các bộ lọc còn lại vào «＋ Lọc thêm»; bảng 5 cột (Số phiếu, Giờ, Khách, Số lượng, Trạng thái; người lập, kênh, người mua ở hộp chi tiết). Hộp 11: nút chính «🖨 In phiếu» (P3 của Hoa), «Hủy đơn» viền đỏ, «Đóng»; «hạn dùng» thay «HSD» |
| `12`, `13` | A23–A25: tab «Quế / Thành phẩm / Phụ liệu» + nút «📋 Kiểm kê kho» ở cuối; cột «Vùng kiểm soát», «Hàng chung» có chú thích; ô số lô có «›»; một câu hướng dẫn mỗi tab; «không tính chai lưu mẫu» chuyển lên tiêu đề cột |
| `14` | A26: thành trang riêng «Kiểm kê kho»: «Quét tem từng bao trong kho, rồi bấm **Kiểm tra**» (nút chính ở thanh dưới); dòng lỗi (thiếu, thừa) đứng trước các ô số |

## 2. Màn mới (2)

| Key | Sau | Nội dung |
|---|---|---|
| `receipt-cancel` (06c) | `receipt-list` | Hộp «Hủy phiếu PN-261120-005?» nút mặc định xanh **«Giữ lại»**, «Hủy phiếu» viền đỏ (A9). Hộp «Hủy đơn» ở `11` dùng cùng kiểu |
| `inv-kk-reset` (14c) | `inv-kk` | Hộp «Xóa 4 bao đã quét?» «Giữ lại» / «Xóa» (A26) |

Tổng số màn của bản ghép tăng 2 (cụm A: 20 → 22).

## 3. Chỗ lệch so với `ra-soat-a.md` và việc còn lại

- **A22:** nhãn nút chính giữ «Lưu đơn và in».
- **A3:** chỉ `04c` (người bán hàng chung) không có bước đồi; các màn khác người bán có 2 đồi nên giữ bước, chỉ thêm «lần trước».
- **A14:** bản tĩnh không vẽ được danh sách «gần đây»; chỉ đổi chữ và ghi chú «đã chọn sẵn người mua lần trước».
- **Hoa P1/P3** áp vào `05`, `05b`, `11` (một nút in ở `05`, nút chính «In phiếu» ở `11`). Hộp in tự mở ngay sau khi lưu là việc của C/33 và luồng thật, mockup tĩnh giữ như cũ.
- **«GĐ2»:** đã bỏ nhãn ở mọi màn cụm A (theo ra-soat-a 0.4 và ra-soat-c mục 3); dấu giai đoạn còn ở `data-gd` của trang chủ. Bản gốc `goc/` không đổi.
- Số cân và đơn giá ở `04`, `04b`, `04c`, `05`, `05b` để trống (bản cũ gõ sẵn 12 hoặc 500 trùng với dòng đã thêm, nay không khớp với quy tắc «dòng dở tự thêm»).
- **Route cần thêm vào vỏ** (`_tools/vo.html`, đặt trước `^/ton-kho`): `^/ton-kho/kiem-ke` → `inv_kk`. Chưa thêm thì nút «Kiểm kê kho» ở `12`, `13` nhảy về `inv-nl`. Tôi không sửa `_tools/` nên để lại cho người ghép (#38).
- `c-quan-ly-in-qr/19-home-owner.html:30` vẫn có ô «Xuất hàng» dẫn `/xuat-hang` (màn 07, còn là lối dự phòng). Nếu trang chủ chủ cũng tách «Bán quế khô» và «Bán thành phẩm» thì Hoa/Dat đổi ở C.
- Giờ ở cột «Giờ» của `10`, `11` (16:42, 15:10, 11:25, 09:05) là số mẫu.

## 4. Nếu sếp chọn khác

| Câu | Làm lại |
|---|---|
| Q-A1 «không chọn sẵn lô» | **Đã áp (lô 2, #524).** `08`: bỏ khung xanh «Lô NL-2611-0002 …», ô quét tem là lối chính |
| Q-A2 «bắt tỉnh/xã, địa chỉ» | **Sếp giữ mặc định (#524), không đổi.**  `09`, `09c`, `09d`: đưa «Tỉnh / xã», «Số nhà – đường» ra khỏi «＋ Thêm thông tin…» |
| Q-A3 «giữ hai ô riêng» | **Đã áp (lô 2, #524).** `09`…`09d`: thêm lại hàng «Kênh bán» đủ 10 kênh dưới «Bán cho ai» |
| Q-C1 «chỉ chủ in tem» | `02`: bỏ ô «In tem lô» |

## 5. Bổ sung sau ý 7–9 của sếp (#494)

- `05b`: tem lô đổi khổ **40 × 30 → 50 × 30 mm** (khung xem trước 250×150 px), cả tem thường và tem «CHUNG».
- Nút «Gán tem» ở `02` đã thành «Dán tem lên chai» và ô «In tem lô» (Q-C1 = có); không còn chữ «Gán tem» trong cụm A.

## 6. Lô 2 của sếp (#524), đã áp

| Câu | Sếp chọn | Đã sửa |
|---|---|---|
| Q-A1 | Không chọn sẵn bao cũ nhất, nhân viên tự quét | `08`: bỏ khung xanh chọn sẵn; ô «Quét tem bao lấy hàng» là lối chính, quét xong mới hiện bao đã chọn; danh sách lô chỉ là lối phụ, không bao nào chọn sẵn |
| Q-A2 | Giữ mặc định: không bắt tỉnh/xã, để trong «Thêm» | Không đổi |
| Q-A3 | Giữ hai ô riêng (khách và kênh bán) | `09`, `09b`, `09c`, `09d`: hàng «Kênh bán» đủ 10 kênh (Trực tiếp, Website, Facebook / Zalo, Shopee, TikTok Shop, Lazada, Đại lý, Doanh nghiệp, Xuất khẩu, Khác) dưới «Bán cho ai». Chọn Shopee thì kênh Shopee chọn sẵn (`09b`), khách lẻ chưa chọn sẵn (`09`); `09c`, `09d` hiển thị trạng thái đã chọn Trực tiếp / Website; đổi được |

**Số chạm so với bản trước lô 2:**

- Bán quế khô: +1 chạm (quét tem bao); mất khoản −1 chạm của «chọn sẵn bao cũ nhất». Đổi lại không có rủi ro bán nhầm bao.
- Bán thành phẩm: khách sàn/đại lý/doanh nghiệp +0 chạm (kênh chọn sẵn, chỉ đổi khi cần); khách lẻ +1 chạm (chọn 1 trong 10 kênh). Mất khoản −2 chạm của phương án gộp.
- Giữ một nút xanh chốt mỗi màn; nút kênh cao 56 px; hàng kênh tự xuống dòng, không tràn ngang ở 492 px.
- Chưa đo lại bằng trình duyệt ở 492 px ngoài các màn 08 và 09 đã chụp (xem thẻ #40).

