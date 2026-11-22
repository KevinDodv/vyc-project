# Thay đổi cụm C (task #26)

Bản đề xuất cho cụm C (đăng nhập, quản lý chủ DN, mẫu in, trang QR khách), làm theo `docs/mockup/nhan-xet.md` (mã C-01..C-22) và các mặc định ở mục 1.3–1.4 của file đó. Mọi file nằm trong `docs/mockup/de-xuat/man/c-quan-ly-in-qr/`. Bản gốc `docs/mockup/goc/` không đụng.

Mặc định đã áp dụng (sếp chưa trả lời): C-01/C-02 bỏ người mua khỏi trang QR; C-07 tem mẻ 40 × 30 mm; C-18 chỉ ghi chú, không vẽ «Tài khoản», «Chứng nhận»; mã lô mẫu `Q100-261120-01/-02`.

## 1. Kết quả theo từng vấn đề

| Mã | Xử lý | Chỗ sửa |
|---|---|---|
| C-01 | Xong | 36, 38: xoá cả khối «Tình trạng bán» (ngày bán, kênh, người mua, SĐT che, khu vực). 38 còn khung đỏ + sản phẩm + lô |
| C-02 | Xong | 32: bỏ ô tích «hiện người mua». Màn 37 «Chưa bán» bỏ; file 37 đổi thành `37-q-many-scans` (khung vàng quét quá ngưỡng, xem C-05); 36 đại diện cho IN_STOCK và ISSUED |
| C-03 | Xong phần cụm C | `TP-TD10-2611-0x` → `Q100-261120-0x` ở 27, 29 (hai serial), 36, 37, 38. Placeholder ô tra cứu 27 thêm Q100-, QC1-, Q-, PNP-. Cụm B (15, 17, 18, 24, 26) và A do người làm cụm đó đổi |
| C-04 | Xong, **cần route** | Màn mới `41-vung-nguyen-lieu` (bản đồ giữ chỗ Leaflet + OSM có 2 ghim, 4 thẻ số, lọc xã, bảng 4 đồi, nhãn cam «thiếu tọa độ» / «thiếu ảnh»). 19 thêm tile «Vùng nguyên liệu» |
| C-05 | Xong | `37-q-many-scans` (36 + dòng vàng «Mã này đã được quét 27 lần, lần đầu ngày 20/11/2026…»), `43-q-notfound`, `44-q-void`; câu chữ nguyên văn TK §8.4 |
| C-06 | Xong | 36, 37 (và 38 phần sản phẩm): khung ảnh sản phẩm 96 px; 36, 37: dải 3 ô «Ảnh đồi» trong khối Vùng nguyên liệu. Ô giữ chỗ, chưa có ảnh thật |
| C-07 | Xong theo mặc định, **chờ sếp** | Màn mới `42-print-batch`: tem 40 × 30 mm gồm QR, mã lô `Q100-261120-02`, tên sản phẩm, NSX, HSD; ghi chú trên màn «tem serial không in mã lô». «Cách dùng, cảnh báo» không in trên tem này. QR trong tem là hình mẫu của màn 33, chưa chứa mã lô thật |
| C-08 | Xong | 27: cột ô tích ở bảng lô thành phẩm, nút đỏ «Thu hồi các lô đã chọn», nút «Xem mẫu lưu» ở từng dòng lô |
| C-09 | Xong một phần | 27: khối «Lô phụ liệu» (Q-2611-01 ← PNP-261105-001, nơi bán: gia đình) và dòng vàng «nguồn ngoài, chưa nối về lô quế (BR-31)». Không vẽ chuỗi lệnh ủ ← lệnh chưng ← NL vì B-06 mặc định chưa chốt xưởng tự chưng; ngày của các lô NL trong màn đều là 20/11 nên chuỗi chưng + ủ 4–6 tuần cũng không khớp ngày |
| C-10 | Xong ở 27; **30 và 26 chờ cụm B** | 27: bỏ NL-2611-0007/0008/0009 khỏi nhánh NCC-CQ-001 (theo 30 thuộc NCC-CQ-002), còn NL-2611-0004 (85 kg) khớp 30 (85 kg → 1,63 kg). Phần lô -01 (120,5 kg → 20 chai) nằm ở 26: nếu cụm B đổi số lô -01 thì phải sửa dòng NCC-CQ-002 ở 30 (hiện 1,2 kg, 1%) cho khớp. Mình không đổi 30 khi chưa biết số mới |
| C-11 | Xong | 25: CT-2611-02 «đã in 1–300», CT-2611-01 «đã in 1–50»; thêm cuộn mới CT-2611-03 (100 tem, chưa gán, chưa in) |
| C-12 | Xong | 35: mã serial trên một dòng, 6 pt, không `<br>`, bỏ letter-spacing âm (12 ký tự ≈ 15 mm trong chỗ rộng ≈ 17,8 mm). **Chưa in thử**, vẫn cần thử máy in tem thật (TK §11) |
| C-13 | Xong | 21: nút «✔ Duyệt» ở dòng NCC-CQ-003. 22: dòng «Thêm đồi mới» mở rộng (thôn, diện tích, năm trồng, tọa độ, ảnh, đồi mặc định). Màn mới `22b-supplier-approve`: hộp sửa NCC-CQ-003 chưa có đồi, banner BR-03, nút Duyệt cạnh Lưu |
| C-14 | Xong, **cần route** | 31: thêm tile Công thức, Phụ liệu & phiếu nhập phụ liệu, Mẫu lưu, Thử lưu hương 28 ngày. 19: banner cam «1 lô chưa lưu mẫu» và banner xanh «1 mẻ đang ủ: QC1-261117-01, còn 6 ngày». Chưa làm thẻ «Mẫu sắp hết hạn lưu» vì chưa có số liệu hạn giữ |
| C-15 | Xong | 28 và 29: ô «Tỉnh / xã»; nút CSV ghi «(SĐT đầy đủ, ghi nhật ký)» |
| C-16 | Xong | 29: bỏ dấu nối thừa, ghi «SĐT: (sàn không cung cấp)»; banner có dòng «Đã ghi nhật ký: Chủ DN, 20/11/2026 19:52» |
| C-17 | Xong | 34: «Kênh: Bán trực tiếp» |
| C-18 | Xong theo mặc định | 31: dòng chú thích «dùng chung khuôn với Người bán, chưa vẽ» và nhãn «chưa vẽ» trên 6 tile. Không vẽ Tài khoản, Chứng nhận. Gợi ý «chưa vẽ» của vỏ khi bấm vào là việc của vỏ (xem mục 3) |
| C-19 | Xong | 19: nhãn «GĐ2» trên 5 tile (Cuộn tem, Lô thành phẩm, Tra cứu, Vùng nguyên liệu, Khách hàng). Tile «Sản xuất / đóng gói» thuộc cụm B, chưa gắn nhãn |
| C-20 | Xong | 01: bỏ link «← Về trang chủ». Màn mới `01b-login-err` (khung đỏ, còn 2 lần thử), `01c-login-locked` (khoá 15 phút, nút Đăng nhập tắt) |
| C-21 | Xong | 36, 37: «[ví dụ minh hoạ, chưa có thật]» sau dòng OCOP |
| C-22 | Xong | 32: ô tên miền chỉ đọc + «Đã in cuộn đầu tiên (CT-2611-01) ngày 20/11/2026, không đổi được» |

## 2. Việc làm thêm ngoài danh sách C-nn

- Câu chuyện thương hiệu ở 32 và 36/37 đổi «chưng cất hơi nước / chưng cất tại xưởng» thành «chế biến thành tinh dầu / chế biến tại xưởng», theo mặc định B-06 (chưa chốt xưởng có tự chưng không). Nếu sếp chốt có chưng thì trả lại câu cũ.
- Tên menu: 36 «Chính hãng — hợp lệ (trong kho hoặc đã xuất; không hiện người mua)», 37 «Chính hãng — quét quá ngưỡng (khung vàng)», 38 «Lô bị thu hồi (khung đỏ)».
- `_ds.json`: thêm 7 mục (01b, 01c, 22b, 41, 42, 43, 44, đều có `sau`), đổi key 37 từ `q-unsold` thành `q-many-scans`. Tổng cụm C 27 màn (trước 20); bản ghép 47 màn khi chưa có màn mới của cụm A và B.

## 3. Việc cho người khác (ngoài vùng của #26)

Route vỏ (`docs/mockup/_tools/vo.html`, mảng `map` trong `route()`):

- Thay `[/^\/quan-ly\/vung-nguyen-lieu/, null]` bằng `[/^\/quan-ly\/vung-nguyen-lieu/, "vung_nguyen_lieu"]` (key màn 41 là `vung-nguyen-lieu`). Chưa đổi thì tile mới ở 19 và 31 báo «không có trong bản xem trước».
- Chèn **trước** dòng `/^\/quan-ly/` (đang rơi về `admin`): `/quan-ly/cong-thuc`, `/quan-ly/phu-lieu`, `/quan-ly/mau-luu`, `/quan-ly/thu-luu-huong` trỏ tới màn cụm B tương ứng khi có (B-09, A-02, B-08, B-14). Tên route do mình đặt tạm, topic #2 chưa chốt; chưa đổi thì bấm vào quay về màn Quản lý.
- Màn `42-print-batch` chưa có link dẫn tới: cần nút «In tem mẻ» ở màn Lô thành phẩm (26, cụm B) hoặc cho vỏ một route (đề xuất `/in/tem-me`).
- Màn `01b`, `01c`, `22b`, `43`, `44`, `37-q-many-scans` chỉ vào được từ menu trái, không có link (đúng cách 39, 40 đang làm).
- Gợi ý «màn này dùng chung khuôn danh mục, chưa vẽ» (C-18) ở vỏ khi bấm 6 tile; hiện tile ghi «chưa vẽ» nhưng bấm vẫn rơi về `admin`.
- Mã lô cũ `TP-TD10-2611-0x` còn ở cụm A (12, 13, 14) và B (15, 17, 18, 24, 26), do người làm cụm đó đổi.

## 4. Đã kiểm và chưa kiểm

Đã kiểm:
- Máy không có `node` trong PATH; chạy `node.exe` từ `C:\Program Files\nodejs`. Không chạy `mockup.mjs ghep` vì lệnh ghi đè `de-xuat/ban-xem-truoc.html` ngoài vùng; dùng bản sao logic ghép (chèn theo `sau`, cùng `vo.html`) và xuất ra thư mục tạm: ghép được 47 màn, không trùng key, không thiếu file.
- Cân đối thẻ `<div>`, `<table>` của cả 27 file cụm C.
- Mở bản ghép bằng Edge (headless) chụp 5 màn: 41, 42, 36 xem đúng; 19 và 22b chụp được nhưng chưa xem lại ảnh.

Chưa kiểm:
- Chưa bấm thử bằng tay trên trình duyệt (link, khung điện thoại), chưa in thử tem 35 và 42 trên giấy.
- Số liệu minh hoạ mình đặt cho màn 41 (diện tích 1,8 ha và 0,9 ha, năm trồng 2015 và 2014 của hai đồi NCC-DC-001, NCC-CQ-002; 62,5 kg và 120,5 kg lấy từ 33 và 30) chưa có nguồn thật; đã ghi chú trên màn.
- (Đã xử lý ở mục 5.) Nguồn quế lô -02 đã thống nhất theo 27.

## 5. Sau khi sếp duyệt (#429, task #30)

Mặc định ở `nhan-xet.md` mục 1.3 đã được duyệt; sửa các điểm medium còn tồn:

1. **Bỏ hiệu suất 1,92%** (không chưng cất tại xưởng):
   - `30-reports.html`: bỏ cột «Hiệu suất» và hai giá trị 1,92%, giá trị 1%; đổi nhãn tab «Hiệu suất» thành «Sản lượng», cột «Tiền NL» thành «Tiền mua NL»; sửa câu chú thích dưới bảng.
   - `41-vung-nguyen-lieu.html`: bỏ cột «Hiệu suất TB» ở cả 4 dòng đồi.
2. **Một nguồn quế cho lô Q100-261120-02, theo 27**: chỉ NCC-CQ-001, lô NL-2611-0004, 85 kg, Châu Quế › Thôn 3.
   - `36`, `37`: bỏ dòng «Xã Đông Cuông — Đồng Vối», năm trồng còn «2012».
   - `30`: NCC-CQ-001 giữ 1 lô, 85 kg NL; NCC-DC-001 và NCC-CQ-002 đổi thành 0 lô, 0 kg NL, 0 kg thành phẩm (mới nhập kho, chưa vào lô). Cột tiền mua NL giữ theo phiếu nhập. File cụm B (26) chỉ đọc, không sửa; 26 không có số theo từng người bán nên không mâu thuẫn. Số «1,63 kg thành phẩm» của NCC-CQ-001 là số cũ, chưa có nguồn đối chiếu.
3. **Lối vào màn 42**: `25-rolls.html` thêm thẻ «Tem mẻ / nhãn lô» dưới bảng cuộn tem, nút «In nhãn lô Q100-261120-02» trỏ `/in/tem-me?lo=Q100-261120-02` (route `print_batch` đã có ở `vo.html:82`).
4. **31-admin**: 6 ô chưa vẽ (địa bàn, khách hàng, nguyên liệu, loại hàng, chứng nhận, tài khoản) đổi nhãn «chưa vẽ» thành chữ xám «dùng chung khuôn danh mục, chưa vẽ».
5. `_ds.json` không đổi.

Còn lại: ở 26 (cụm B) vẫn có cột «Hiệu suất» (giá trị «—») và ở 33 còn «Đông Cuông» là phiếu nhập của NCC-DC-001, đúng nghiệp vụ nên giữ.
