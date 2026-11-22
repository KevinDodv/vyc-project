# So sánh trước / sau (task #27)

Ảnh chụp bằng Edge không cửa sổ, rộng 1440 px, cắt đúng vùng màn hình (không gồm menu của vỏ). «Trước» là `goc/mockup-goc.html#<key>`, «Sau» là `de-xuat/ban-xem-truoc.html#<key>`. Màn mới chỉ có ảnh «Sau». Màn điện thoại được kéo dài hết nội dung để thấy đủ.

Mã vấn đề lấy từ `nhan-xet.md` và `de-xuat/thay-doi-a|b|c.md`. Bản đề xuất làm theo các mặc định chưa được sếp chốt (xem mục 1.3 của nhan-xet.md).

Tổng: 35 màn sửa (trước + sau), 23 màn mới (chỉ sau), 5 giữ nguyên (không chụp): issue-menu, prices, print-receipt, q-unassigned, q-form. Bản đề xuất 63 màn (40 màn gốc + 23 màn mới). Ảnh chụp lại ngày 21/11/2026 sau khi sếp duyệt mặc định (#429) và các màn cụm A/B/C sửa xong; so-sanh.md đếm đủ 35 ảnh `-truoc` ứng với 35 mục «sửa» (số 33 ở bản trước là đếm thiếu; 34 ảnh trước cộng thêm `reports-truoc.png`). Mỗi key chỉ có một ảnh `-truoc` và một `-sau`; riêng `issue-product` gốc một màn nay tách thành 4 màn (`issue-product`, `-san`, `-moi`, `-loi`): ảnh `issue-product-truoc.png` là màn gốc chung, ba màn tách chỉ có ảnh «sau». Đã chụp lại «sau»: issue-list, issue-detail, receipt-warn, prod-list, prod-owner, cure-list, cure-detail, recipe-list, plots-lots, retain-list, trace, reports, admin, vung-nguyen-lieu, rolls, print-batch, q-ok, q-many-scans.

## 1. Đăng nhập (`login`)

- Mã vấn đề: C-20
- Bỏ link «← Về trang chủ» ở màn đăng nhập.

| Trước | Sau |
|---|---|
| ![login trước](anh/login-truoc.png) | ![login sau](anh/login-sau.png) |

## 2. Đăng nhập — sai tên hoặc mật khẩu (`login-err`)

- Mã vấn đề: C-20
- Màn mới. Mới: khung đỏ sai tên/mật khẩu, còn 2 lần thử.

Sau (màn mới):

![login-err sau](anh/login-err-sau.png)

## 3. Đăng nhập — tài khoản bị khóa 15 phút (`login-locked`)

- Mã vấn đề: C-20
- Màn mới. Mới: khoá 15 phút, nút Đăng nhập tắt.

Sau (màn mới):

![login-locked sau](anh/login-locked-sau.png)

## 4. Trang chủ xưởng (4 nút lớn) (`home-shop`)

- Mã vấn đề: A-04
- Nhãn GĐ2 cho Sản xuất và Gán tem, thêm nút nhỏ «Mẫu lưu», chú thích bản GĐ1 chỉ có 5 nút.

| Trước | Sau |
|---|---|
| ![home-shop trước](anh/home-shop-truoc.png) | ![home-shop sau](anh/home-shop-sau.png) |

## 5. Phiếu cân — bước 1: chọn người bán (`receipt-1`)

- Mã vấn đề: A-02, A-11
- Thêm tab Quế/Phụ liệu, «+ Người bán mới» thành link, nhãn «Hàng chung» cho thương lái.

| Trước | Sau |
|---|---|
| ![receipt-1 trước](anh/receipt-1-truoc.png) | ![receipt-1 sau](anh/receipt-1-sau.png) |

## 6. Phiếu cân — người bán mới (mặc định hàng chung) (`receipt-newsup`)

- Mã vấn đề: A-11
- Màn mới. Mới: form người bán mới, mặc định hàng chung, chủ DN duyệt sau.

Sau (màn mới):

![receipt-newsup sau](anh/receipt-newsup-sau.png)

## 7. Phiếu cân — đang thêm dòng (đồi, hạng, số cân) (`receipt-2`)

- Mã vấn đề: A-02, A-11
- Thêm tab Quế/Phụ liệu; «+ Người bán mới» thành link.

| Trước | Sau |
|---|---|
| ![receipt-2 trước](anh/receipt-2-truoc.png) | ![receipt-2 sau](anh/receipt-2-sau.png) |

## 8. Phiếu cân — giá lệch hơn 20%, chưa có giá hôm nay (`receipt-warn`)

- Mã vấn đề: A-13
- Màn mới. Mới: chưa có giá hôm nay, dòng giá lệch hơn 20% có cảnh báo vàng.

Sau (màn mới):

![receipt-warn sau](anh/receipt-warn-sau.png)

## 9. Phiếu cân — người bán hàng chung (thương lái) (`receipt-chung`)

- Mã vấn đề: A-11
- Màn mới. Mới: người bán hàng chung, nhãn «Hàng chung», không chọn đồi.

Sau (màn mới):

![receipt-chung sau](anh/receipt-chung-sau.png)

## 10. Phiếu cân — đã lưu, tự in phiếu + tem lô (`receipt-3`)

- Mã vấn đề: A-02, A-12
- Thêm tab; «In lại phiếu/tem lô» thành link tới hộp thoại in.

| Trước | Sau |
|---|---|
| ![receipt-3 trước](anh/receipt-3-truoc.png) | ![receipt-3 sau](anh/receipt-3-sau.png) |

## 11. Phiếu cân — hộp thoại in phiếu nhập + tem lô (`receipt-print`)

- Mã vấn đề: A-12
- Màn mới. Mới: hộp thoại in phiếu nhập A5 và tem lô 40×30 (có tem hàng chung).

Sau (màn mới):

![receipt-print sau](anh/receipt-print-sau.png)

## 12. Phiếu nhập hôm nay (sửa / hủy trong ngày) (`receipt-list`)

- Mã vấn đề: A-02, A-05
- Bỏ cột «Tổng tiền» (xưởng không xem tiền phiếu cũ), thêm tab phiếu phụ liệu.

| Trước | Sau |
|---|---|
| ![receipt-list trước](anh/receipt-list-truoc.png) | ![receipt-list sau](anh/receipt-list-sau.png) |

## 13. Nhập phụ liệu (gram, số lô, COA) (`ingr-receipt`)

- Mã vấn đề: B-03, B-10
- Màn mới. Mới: nhập phụ liệu theo gram, số lô NCC, hạn, COA, không có cột giá.

Sau (màn mới):

![ingr-receipt sau](anh/ingr-receipt-sau.png)

## 14. Bán quế khô — quét tem lô, gõ số cân lúc bán (`issue-dry`)

- Mã vấn đề: A-09, A-10
- Ô số cân trống (hết «1.180»), dòng mẫu 42,5 kg × 50.000 đ, nhãn «mua là loại 1».

| Trước | Sau |
|---|---|
| ![issue-dry trước](anh/issue-dry-truoc.png) | ![issue-dry sau](anh/issue-dry-sau.png) |

## 15. Đơn hàng — quét tem, người mua cũ tự nhận, quà tặng, báo quét trùng (`issue-product`)

- Mã vấn đề: A-07, A-08
- Bỏ banner người mua lặp; thêm khung các lỗi quét và lỗi lưu.

| Trước | Sau |
|---|---|
| ![issue-product trước](anh/issue-product-truoc.png) | ![issue-product sau](anh/issue-product-sau.png) |

## 16. Đơn hàng — kênh sàn (bắt buộc tên + tỉnh) (`issue-product-san`)

- Mã vấn đề: A-07
- Màn mới. Mới: kênh sàn, bắt buộc tên + tỉnh, SĐT không bắt buộc.

Sau (màn mới):

![issue-product-san sau](anh/issue-product-san-sau.png)

## 17. Đơn hàng — người mua mới (SĐT chưa có) (`issue-product-moi`)

- Mã vấn đề: A-07
- Màn mới. Mới: người mua mới (SĐT chưa có), hiện khối họ tên, địa chỉ, đồng ý Zalo/SMS.

Sau (màn mới):

![issue-product-moi sau](anh/issue-product-moi-sau.png)

## 18. Đơn hàng — lỗi thiếu tên / SĐT kênh Website (`issue-product-loi`)

- Mã vấn đề: A-07
- Màn mới. Mới: kênh Website thiếu tên/SĐT, banner đỏ và ô lỗi viền đỏ (BR-22).

Sau (màn mới):

![issue-product-loi sau](anh/issue-product-loi-sau.png)

## 19. Danh sách đơn hàng (tên, SĐT đã che) (`issue-list`)

- Mã vấn đề: A-05, A-06, A-17
- Bỏ cột «Tổng tiền», thêm cột «Người lập» và dòng «Đã hủy», bỏ Trà khỏi bộ lọc.

| Trước | Sau |
|---|---|
| ![issue-list trước](anh/issue-list-truoc.png) | ![issue-list sau](anh/issue-list-sau.png) |

## 20. Chi tiết đơn hàng (`issue-detail`)

- Mã vấn đề: A-05, A-06, A-14, A-17
- Hộp thoại đơn PX-001: có người lập, quà tặng, serial kèm lô/hạn, không có cột giá.

| Trước | Sau |
|---|---|
| ![issue-detail trước](anh/issue-detail-truoc.png) | ![issue-detail sau](anh/issue-detail-sau.png) |

## 21. Tồn kho nguyên liệu (xưởng không thấy giá) (`inv-nl`)

- Mã vấn đề: A-01, A-02, A-15, A-16
- Lô Q100-261120-02, lô cam còn 46 ngày, ghi chú số tem không gồm chai lưu mẫu, tab Phụ liệu.

| Trước | Sau |
|---|---|
| ![inv-nl trước](anh/inv-nl-truoc.png) | ![inv-nl sau](anh/inv-nl-sau.png) |

## 22. Tồn kho thành phẩm (`inv-tp`)

- Mã vấn đề: A-01, A-02, A-15, A-16
- Như tồn kho nguyên liệu (cùng khuôn ba tab).

| Trước | Sau |
|---|---|
| ![inv-tp trước](anh/inv-tp-truoc.png) | ![inv-tp sau](anh/inv-tp-sau.png) |

## 23. Kiểm kê bằng máy quét (báo thiếu / thừa) (`inv-kk`)

- Mã vấn đề: A-01, A-02, A-15, A-16
- Như trên; banner kiểm kê thêm câu lô đang trong lệnh sản xuất không tính.

| Trước | Sau |
|---|---|
| ![inv-kk trước](anh/inv-kk-truoc.png) | ![inv-kk sau](anh/inv-kk-sau.png) |

## 24. Tồn kho phụ liệu (`ingr-stock`)

- Mã vấn đề: B-03, B-10
- Màn mới. Mới: tồn phụ liệu theo lô, hạn cam/đỏ, chấm vàng chưa COA.

Sau (màn mới):

![ingr-stock sau](anh/ingr-stock-sau.png)

## 25. Sản xuất / đóng gói (`prod-list`)

- Mã vấn đề: B-04, B-05, B-17
- Thẻ «Mẻ đang ủ», mã lô mới, lệnh LSX-2611-003 «đã nhập 3/4 thành phần».

| Trước | Sau |
|---|---|
| ![prod-list trước](anh/prod-list-truoc.png) | ![prod-list sau](anh/prod-list-sau.png) |

## 26. Lệnh sản xuất: công thức, nguyên liệu theo gram, ủ (`prod-order`)

- Mã vấn đề: B-01, B-03, B-05, B-15, B-17
- Dựng lại theo 4 bước: công thức/cỡ mẻ, nguyên liệu theo gram, ủ, kết quả. Ví dụ túi thơm TUI 25 g.

| Trước | Sau |
|---|---|
| ![prod-order trước](anh/prod-order-truoc.png) | ![prod-order sau](anh/prod-order-sau.png) |

## 27. Mẻ đang ủ (`cure-list`)

- Mã vấn đề: B-04, B-11
- Màn mới. Mới: danh sách mẻ đang ủ, còn N ngày, nhắc lắc chai.

Sau (màn mới):

![cure-list sau](anh/cure-list-sau.png)

## 28. Mẻ đang ủ: lắc chai, ngửi kiểm tra, hoàn thành (`cure-detail`)

- Mã vấn đề: B-04, B-11
- Màn mới. Mới: chi tiết ủ, tick lắc chai, ngửi kiểm tra 4 bước, Đạt / Ủ thêm 7 ngày.

Sau (màn mới):

![cure-detail sau](anh/cure-detail-sau.png)

## 29. Lệnh hoàn thành: lô thành phẩm, chai lưu mẫu (`prod-done`)

- Mã vấn đề: B-05, B-06, B-08
- Bỏ «mẻ chưng cất» và hiệu suất 1,92%; hiện gram phụ liệu, số chai, chai lưu mẫu.

| Trước | Sau |
|---|---|
| ![prod-done trước](anh/prod-done-truoc.png) | ![prod-done sau](anh/prod-done-sau.png) |

## 30. Gán tem: quét tem đầu, tem cuối của đoạn (`labels`)

- Mã vấn đề: B-05, B-18
- Thêm 2 lô, dòng «Chai lưu mẫu không dán tem», mã lô mới.

| Trước | Sau |
|---|---|
| ![labels trước](anh/labels-truoc.png) | ![labels sau](anh/labels-sau.png) |

## 31. Trang chủ chủ DN (người bán chờ duyệt) (`home-owner`)

- Mã vấn đề: C-14, C-04, C-19
- Banner «1 lô chưa lưu mẫu» và «1 mẻ đang ủ», tile Vùng nguyên liệu, nhãn GĐ2.

| Trước | Sau |
|---|---|
| ![home-owner trước](anh/home-owner-truoc.png) | ![home-owner sau](anh/home-owner-sau.png) |

## 32. Người bán & đồi quế (`suppliers`)

- Mã vấn đề: C-13
- Nút «✔ Duyệt» ở dòng NCC-CQ-003.

| Trước | Sau |
|---|---|
| ![suppliers trước](anh/suppliers-truoc.png) | ![suppliers sau](anh/suppliers-sau.png) |

## 33. Sửa người bán — bảng đồi quế (`supplier-edit`)

- Mã vấn đề: C-13
- Dòng «Thêm đồi mới» mở rộng (thôn, diện tích, năm trồng, tọa độ, ảnh).

| Trước | Sau |
|---|---|
| ![supplier-edit trước](anh/supplier-edit-truoc.png) | ![supplier-edit sau](anh/supplier-edit-sau.png) |

## 34. Duyệt người bán chờ duyệt (hộp sửa) (`supplier-approve`)

- Mã vấn đề: C-13
- Màn mới. Mới: hộp sửa/duyệt người bán chờ duyệt NCC-CQ-003.

Sau (màn mới):

![supplier-approve sau](anh/supplier-approve-sau.png)

## 35. Sản phẩm: công thức, hạn dùng, cách dùng (`products`)

- Mã vấn đề: B-07, B-15, B-16
- Thêm cột công thức, lưu mẫu, hạn dùng theo sổ tay; Trà mờ ghi giai đoạn; túi thơm 25 g.

| Trước | Sau |
|---|---|
| ![products trước](anh/products-truoc.png) | ![products sau](anh/products-sau.png) |

## 36. Công thức (`recipe-list`)

- Mã vấn đề: B-09
- Màn mới. Mới: danh sách công thức, kể cả QC1 v2 nháp.

Sau (màn mới):

![recipe-list sau](anh/recipe-list-sau.png)

## 37. Khai công thức (thành phần theo gram) (`recipe-edit`)

- Mã vấn đề: B-09
- Màn mới. Mới: form khai công thức (gram, % tự tính, nhóm lựa chọn).

Sau (màn mới):

![recipe-edit sau](anh/recipe-edit-sau.png)

## 38. Tạo lệnh sản xuất: công thức, cỡ mẻ (`prod-owner`)

- Mã vấn đề: B-02, B-04, B-05, B-07, B-16, B-17
- Form tạo lệnh theo công thức và cỡ mẻ gram; TRA100 bị khoá giai đoạn 4.

| Trước | Sau |
|---|---|
| ![prod-owner trước](anh/prod-owner-truoc.png) | ![prod-owner sau](anh/prod-owner-sau.png) |

## 39. Cuộn tem QR (`rolls`)

- Mã vấn đề: C-11
- CT-2611-02 «đã in 1–300», CT-2611-01 «đã in 1–50», thêm cuộn CT-2611-03.

| Trước | Sau |
|---|---|
| ![rolls trước](anh/rolls-truoc.png) | ![rolls sau](anh/rolls-sau.png) |

## 40. Lô thành phẩm · mẫu lưu · thu hồi (`plots-lots`)

- Mã vấn đề: B-05, B-08, B-12, C-08
- Cột Công thức và Mẫu lưu, chọn lô để thu hồi, «Giá quế / đơn vị».

| Trước | Sau |
|---|---|
| ![plots-lots trước](anh/plots-lots-truoc.png) | ![plots-lots sau](anh/plots-lots-sau.png) |

## 41. Chi tiết mẻ (sổ ghi lô) (`lot-detail`)

- Mã vấn đề: B-13
- Màn mới. Mới: chi tiết mẻ QC2, gram thực tế so với gợi ý theo lô phụ liệu.

Sau (màn mới):

![lot-detail sau](anh/lot-detail-sau.png)

## 42. Mẫu lưu · lô chưa lưu mẫu (`retain-list`)

- Mã vấn đề: B-08
- Màn mới. Mới: mẫu lưu và tab «Lô chưa lưu mẫu».

Sau (màn mới):

![retain-list sau](anh/retain-list-sau.png)

## 43. Thử lưu hương 28 ngày (`scent-trial`)

- Mã vấn đề: B-14
- Màn mới. Mới: thử lưu hương 28 ngày, lưới ngày 0–28, PASS/FAIL tự tính.

Sau (màn mới):

![scent-trial sau](anh/scent-trial-sau.png)

## 44. Tra cứu hai chiều (từ người bán → khách) (`trace`)

- Mã vấn đề: C-03, C-09, C-10
- Mã lô mới, khối lô phụ liệu, bỏ lô NL lệch khỏi nhánh NCC-CQ-001.

| Trước | Sau |
|---|---|
| ![trace trước](anh/trace-truoc.png) | ![trace sau](anh/trace-sau.png) |

## 45. Vùng nguyên liệu (bản đồ, bảng đồi) (`vung-nguyen-lieu`)

- Mã vấn đề: C-04
- Màn mới. Mới: bản đồ giữ chỗ Leaflet + OSM, thẻ số, bảng đồi, nhãn thiếu tọa độ/ảnh.

Sau (màn mới):

![vung-nguyen-lieu sau](anh/vung-nguyen-lieu-sau.png)

## 46. Khách hàng đã mua (`buyers`)

- Mã vấn đề: C-15
- Thêm ô «Tỉnh / xã», nút CSV ghi rõ SĐT đầy đủ có ghi nhật ký.

| Trước | Sau |
|---|---|
| ![buyers trước](anh/buyers-truoc.png) | ![buyers sau](anh/buyers-sau.png) |

## 47. Chi tiết khách — “Xem đầy đủ” có ghi nhật ký (`buyer-detail`)

- Mã vấn đề: C-15, C-16
- Ô tỉnh/xã, «SĐT: (sàn không cung cấp)», dòng «Đã ghi nhật ký».

| Trước | Sau |
|---|---|
| ![buyer-detail trước](anh/buyer-detail-truoc.png) | ![buyer-detail sau](anh/buyer-detail-sau.png) |

## 48. Menu quản lý (`admin`)

- Mã vấn đề: C-14, C-18
- Thêm tile Công thức, Phụ liệu, Mẫu lưu, Thử lưu hương; nhãn «chưa vẽ» cho 6 tile.

| Trước | Sau |
|---|---|
| ![admin trước](anh/admin-truoc.png) | ![admin sau](anh/admin-sau.png) |

## 49. Cài đặt (tên miền QR, khổ tem…) (`settings`)

- Mã vấn đề: C-02, C-22
- Bỏ ô tích «hiện người mua»; tên miền QR chỉ đọc sau khi đã in cuộn đầu.

| Trước | Sau |
|---|---|
| ![settings trước](anh/settings-truoc.png) | ![settings sau](anh/settings-sau.png) |

## 50. Phiếu xuất / đơn hàng (có quà tặng) (`print-issue`)

- Mã vấn đề: C-17
- Ghi «Kênh: Bán trực tiếp».

| Trước | Sau |
|---|---|
| ![print-issue trước](anh/print-issue-truoc.png) | ![print-issue sau](anh/print-issue-sau.png) |

## 51. Tem QR serial theo cuộn (`print-roll`)

- Mã vấn đề: C-12
- Mã serial trên một dòng, cỡ 6 pt (chưa in thử máy in thật).

| Trước | Sau |
|---|---|
| ![print-roll trước](anh/print-roll-truoc.png) | ![print-roll sau](anh/print-roll-sau.png) |

## 52. Tem mẻ / nhãn lô 40×30 (có mã lô, NSX, HSD) (`print-batch`)

- Mã vấn đề: C-07
- Màn mới. Mới: tem mẻ 40×30 mm có QR, mã lô, NSX, HSD (chờ sếp chốt khổ nhãn).

Sau (màn mới):

![print-batch sau](anh/print-batch-sau.png)

## 53. Chính hãng — hợp lệ (trong kho hoặc đã xuất; không hiện người mua) (`q-ok`)

- Mã vấn đề: C-01, C-06, C-21
- Bỏ khối người mua; thêm khung ảnh sản phẩm, ảnh đồi; ghi chú OCOP là ví dụ.

| Trước | Sau |
|---|---|
| ![q-ok trước](anh/q-ok-truoc.png) | ![q-ok sau](anh/q-ok-sau.png) |

## 54. Chính hãng — quét quá ngưỡng (khung vàng) (`q-many-scans`)

- Mã vấn đề: C-02, C-05
- Thay màn «Chưa bán» bằng màn quét quá ngưỡng (khung vàng, TK §8.4). Ảnh «trước» là màn q-unsold.

| Trước | Sau |
|---|---|
| ![q-many-scans trước](anh/q-many-scans-truoc.png) | ![q-many-scans sau](anh/q-many-scans-sau.png) |

## 55. Lô bị thu hồi (khung đỏ) (`q-recall`)

- Mã vấn đề: C-01
- Bỏ khối tình trạng bán, còn khung đỏ + sản phẩm + lô.

| Trước | Sau |
|---|---|
| ![q-recall trước](anh/q-recall-truoc.png) | ![q-recall sau](anh/q-recall-sau.png) |

## 56. Mã không có trong hệ thống (`q-notfound`)

- Mã vấn đề: C-05
- Màn mới. Mới: mã không có trong hệ thống.

Sau (màn mới):

![q-notfound sau](anh/q-notfound-sau.png)

## 57. Mã đã bị hủy (`q-void`)

- Mã vấn đề: C-05
- Màn mới. Mới: mã đã bị hủy.

Sau (màn mới):

![q-void sau](anh/q-void-sau.png)


## 58. Báo cáo — bỏ hiệu suất (`reports`)

- Mã vấn đề: B-06 (mặc định #1, không chưng tại xưởng)
- Bỏ cột «Hiệu suất» và giá trị 1,92% / 1%; tab «Hiệu suất» thành «Sản lượng»; «Tiền NL» thành «Tiền mua NL»; chú thích mới. Mục này trước đây ghi là «giữ nguyên», nay có sửa nên có thêm ảnh trước.

| Trước | Sau |
|---|---|
| ![reports trước](anh/reports-truoc.png) | ![reports sau](anh/reports-sau.png) |
