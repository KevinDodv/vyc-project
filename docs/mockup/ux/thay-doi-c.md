# Thay đổi UX cụm C (task #37)

Làm theo `docs/mockup/ux/ra-soat-c.md`. Lượt đầu theo phương án mặc định mục 6; lượt sau áp các ý sếp chốt ở #494 (ý 6–9: thủ kho in tem, in theo lô gán luôn, khổ 50×30), xem mục 0. Mọi file nằm trong `docs/mockup/de-xuat/man/c-quan-ly-in-qr/`. Không sửa `app.css`, không sửa file cụm A/B. Chưa chạy ghép; ảnh tạm ở `docs/mockup/ux/anh-c/` (chụp bằng Edge không cửa sổ, chỉ để tự kiểm, #38 chụp chính thức).

## 0. Lượt 2: áp ý sếp chốt ở #494 (ý 6–9)

Mọi file trong `docs/mockup/de-xuat/man/c-quan-ly-in-qr/`. Mục này **thay** các dòng cũ về màn 25, 35, 42 ở mục 1 (đã gạch bỏ) và Q-C1, Q-C2, Q-C3 ở mục 2 (đã bỏ).

| Ý sếp | Màn | Sửa | Số bước trước → sau |
|---|---|---|---|
| 6. Thủ kho tạo và in tem cho lô mình làm, ghi người in | 25 | Bỏ `data-role="OWNER"` ở `<body>`; khối «Lô cần in tem» dùng được cho thủ kho (thanh trên ghi «Thủ kho (mẫu)»). Thêm bảng «Lịch sử in tem theo lô»: lô, dải tem, người in, lúc in, lý do. Chỉ khối «In cuộn tem tự do» (và bảng cuộn, «In lại một phần») còn `data-role="OWNER"`, kèm nhãn «🔒 Chỉ chủ». | Thủ kho: không làm được → 2 chạm |
| 7. In theo lô, gán luôn, bộ toàn trình | 25 | «Lô cần in tem»: mỗi lô một thẻ có chuỗi **Lô nguyên liệu → Mẻ → Lô thành phẩm → Dải serial** và một nút «🖨 In 90 tem cho lô này». Bỏ ô «Số tem», bỏ khối «Nhãn lô chưa in». Máy tự tính số tem theo số chai chưa có tem; không còn 95 (bỏ +5 dự phòng vì đã có in bổ sung). | chủ: 9 chạm, 5 màn, 1 ô gõ (cũ) → **2 chạm** (nút in + «In» trong hộp thoại), 0 ô gõ; thủ kho thêm bước quét tem đầu/tem cuối: bỏ hẳn |
| 7. In bổ sung | 25 | Lô Q100-261120-02 (200 chai, đã có tem 1–150): khối «+ In bổ sung tem cho lô này (thiếu 50 tem)»: số tem (điền sẵn 50), **lý do bắt buộc** (4 nút), nút «🖨 In bổ sung 50 tem»; ghi người in và lúc in. Tem nối tiếp serial của đúng lô, không tạo lô mới. | mới: 3 chạm (chọn lý do, in bổ sung, «In») |
| 7. Bộ toàn trình trên trang truy xuất | 27 | Thêm thẻ «Bộ toàn trình của lô Q100-261120-02» (cùng chuỗi, kèm dải tem đã in, ai in) và dòng «Thiếu 50 tem so với 200 chai» + nút «In bổ sung 50 tem» (trỏ `/quan-ly/cuon-tem`). | |
| 7. Tem gộp theo lô | 42 | Đổi thành «Tem theo lô · QC2-261023-01»: 3 tem xem trước (1/90, 2/90, 3/90), mỗi tem một QR serial + mã lô + tên + NSX + HSD + mã tem. Đầu trang có chuỗi bộ toàn trình và dòng «tự gắn vào lô, không cần quét tem đầu và tem cuối; máy ghi người in». | |
| 7. Tem bổ sung | 35 | Đổi từ «Tem QR serial theo cuộn» thành «In bổ sung tem · Q100-261120-02»: tem 151/200…, chuỗi toàn trình, dòng ghi người in và lý do. Link từ 25: `/in/tem-bo-sung?lo=…&n=50`. | |
| 8. Khổ 50 × 30 | 25, 32, 33, 34, 35, 42, `_ds.json` | `@page tem` và `.tem` 50 × 30 mm, QR 22 mm (trước 18,8 mm), chữ 7,5–8 pt; 32 «Khổ tem: rộng» 40 → 50; ghi chú «50 × 30» ở 25, 33, 42; tên mục 33 trong `_ds.json`. | |
| 9. Như ý 7 (tem nguyên liệu, in thiếu) | 33 | Tem lô nguyên liệu chuyển 50 × 30; vẫn in cùng phiếu nhập một lần. Chuỗi toàn trình bắt đầu từ chính lô NL này. | |
| (hệ thống) | `_ds.json` | Đổi tên mục 25, 33, 35, 42. Không thêm key mới; vẫn 28 mục, parse được, không trùng key và stt. | |

**Chưa làm hoặc ngoài vùng**

- Màn B/17 (nút «In tem cho 90 chai», trỏ `/quan-ly/cuon-tem`) và B/18 (bỏ bước quét tem đầu/cuối, giữ «Hủy tem lỗi» hoặc chuyển hẳn sang in bổ sung): cụm B (#36). Ý sếp bỏ `data-role="OWNER"` ở nút in theo lô B/17 cũng nằm ở đó.
- A/05b dòng 80–83 còn «Tem lô 40 × 30 mm» (khung xem trước 240×180 px): cụm A (#35) sửa thành 50 × 30 (tỉ lệ 250×150 px).
- A/02: nút «Gán tem / hủy tem» cần đổi thành «In tem» (trỏ `/quan-ly/cuon-tem`); cụm A.
- `_tools/vo.html`: thêm route `/in/tem-bo-sung` → `print_roll` (hiện chưa có, link ở 25 sẽ không sang 35) và `?moi=1` → 21b. Việc của #38.
- Đã mở thử 25, 27, 35, 42 bằng Edge không cửa sổ (ảnh `.proteam/evidence/c37-*.png`); chưa bấm link trong vỏ `vo.html`.
- Tem 50 × 30 vẫn **phải in thử một tem thật** trước khi in cả lô.
- Về thiết kế (đã báo ở #496): BR-12 và mục 7.3 đổi sang in theo lô, gán luôn; thêm bản ghi «in tem» (lô, dải serial, người in, lúc in, lý do, lần in bổ sung). Thủ kho tạo/in tem phải được cấp quyền ở phía máy chủ, không chỉ giấu nút (nhắc của Tri, #478).

## 1. Đã sửa (lượt 1)

| Mã (ra-soat-c) | Màn | Sửa |
|---|---|---|
| Trang chủ chủ (mục 3), Q-C5 | 19 | Khối «Việc cần xử lý» (3 dòng, mỗi dòng một nút Duyệt / Lưu mẫu / Xem), «Hay dùng» 3 ô, 1 ô «Quản lý khác». Bỏ nhãn «GĐ2». 13 ô còn 8. |
| Mục 2.5 (C/31) | 31 | 22 ô còn 19, chia 4 nhóm; bỏ ô lặp với trang chủ; bỏ chữ «chưa vẽ» khỏi ô (đưa thành ghi chú riêng cuối trang, nói rõ bản chạy thật không có). Thêm nhóm «Tem, lô hàng và truy xuất» chứa 5 ô dời khỏi trang chủ. |
| Mục 2.5 (C/32) | 32 | Hai khối «Thường chỉnh» và «Gắn với tem đã in»; khổ giấy thành 2 nút A5 / 80 mm; nhãn ngắn, chú thích nhỏ riêng; một nút Lưu. |
| «← Về Quản lý» | 21, 22, 22b, 32, 41 | Đổi chữ nút ở các màn về `/quan-ly`. |
| ~~A2, A3, A4, U2~~ (thay bởi mục 0) | 25 | Đổi tên «In tem». Ô «Số tem» điền sẵn 95 (90 chai + 5 dự phòng), một nút «Tạo cuộn tem và in 95 tem». Banner tên miền một dòng + «ⓘ Chi tiết». «Nhãn lô chưa in» là danh sách lô, mỗi lô một nút. Bảng cuộn: bỏ ô «từ/đến», chỉ còn «In lại»; in một phần nằm trong mục thu gọn. |
| A7, P4, P2 (35, 42 đã thay bởi mục 0) | 33, 34, 35, 42 | Nút «In» cao 56 px; dòng báo «hộp thoại in tự mở khi vào trang» (mockup không tự gọi `window.print()` để khỏi bật hộp thoại khi xem/chụp); 35 ghi «Cuộn CT-2611-02 · tem số 1–300»; 33 ghi in cả phiếu và tem lô một lần. |
| Q1–Q4 | 27 | Ô nhập tự lấy focus, gợi ý «Quét tem, hoặc gõ mã lô»; «Các loại mã ▾» thu gọn; dòng kết luận đầu kết quả; chú giải NL/PN/PNP/LSX/NCC/NM; «Dùng cho mẻ»; bỏ chữ BR-15, BR-31 khỏi màn. «Tra cứu» thành nút phụ (Enter/quét là tự tra). |
| R1–R6 | 30 | Hàng nút «Tháng này / Tháng trước / 3 tháng / Năm nay / Chọn ngày…», bỏ nút «Xem», đổi chữ cột, dòng 0-0-0 mờ, chú thích một câu + ⓘ, nút «Tải bảng Excel (.csv)». R6: kg thành phẩm của NCC-CQ-001 từ «1,63» thành «—» (không có nguồn đối chiếu). |
| D1, D3, D4 | 21, 22, 22b, **21b (mới)** | 21b «Thêm người bán nhanh»: gõ tên, bấm 1 trong 3 nút loại, bấm thôn (3 ô, SĐT/đồi/ảnh để sau). 21/22/22b: «Luồng» thành «Loại hàng thu mua» («Quế có đồi, truy xuất tới đồi» / «Quế thương lái, không biết đồi»), «Cho khách thấy tên…», «Thôn *», ảnh «Chụp ảnh đồi». 22b: nút «✔ Duyệt người bán này» to, ngay dưới banner, bỏ khỏi chân hộp. Nút «+ Thêm người bán» ở 21 trỏ `?moi=1`. |
| D5 | 20 | Bỏ ô ngày; nút «Hôm nay / Hôm qua / Chọn ngày khác…» và «↩ Giá giống hôm qua». |
| W1–W4, W5, W7, W9 | 36–40, 43, 44 | SĐT liên hệ thành nút «📞 Gọi 0900 000 000» cao ≥ 52 px (37, 38, 39, 43); tiêu đề thẻ 17 px không viết hoa; chữ phụ/ghi chú/chân trang ≥ 16 px; mã đã quét 18–20 px đậm (39, 43, 44); nhãn ô ảnh 16 px; ô nhập mã 40 thêm `autocapitalize/autocorrect/spellcheck`; liên kết đầu trang cao 48 px. |
| Ngoài phạm vi báo trước | 28, 29 | «Túi thơm 50 g» thành 25 g; nút CSV ghi «Tải bảng Excel (.csv)». |
| U3 | 19, 31 | Bỏ nhãn «GĐ2» trên cụm C (cụm A tự xử lý A/02). |
| 41 | 41 | Chữ ghi công OSM 11 px thành ≥ 14 px. |

`_ds.json` thêm 1 mục (21b, `sau: suppliers`), đổi tên mục 25. Tổng cụm C 28 màn.

## 2. Chưa làm, hoặc không thuộc vùng của mình

- **Cụm A/B, cần người giữ vùng đó:** A1 (nút «In tem cho 90 chai» ở B/17 → `/quan-ly/cuon-tem`), A5, A6 (B/18 chỉ quét tem đầu), P1 (A/05b mở thẳng hộp thoại in), P3 (A/11 «In phiếu»), nút «In tem» và «Dán tem lên chai» trên trang chủ thủ kho (A/02, đang thống nhất ở #32).
- **Q-C4:** +5 tem dự phòng đã đặt sẵn ở ô «Số tem».
- **D2** (hộp «Bổ sung thông tin truy xuất» ở 41) chưa vẽ riêng; nhãn «thiếu tọa độ / ảnh» còn như cũ. Ô tọa độ ở 22 đổi nhãn thành «tự lấy khi chụp ảnh bằng điện thoại».
- **W6** (chữ «[ví dụ minh hoạ, chưa có thật]» ở 36, 37) giữ nguyên vì chỉ là chữ mẫu; Dev gỡ khi dựng. 44 không thêm nút gọi (bản gốc không có SĐT ở 44).
- **U1, U4, U5, U6, U8 (CSS chung):** `app.css` hiện đã có phần lớn (nút `small` 48 px, `:focus-visible`, chữ phụ 16 px). Cụm C dùng thêm vài lớp riêng đặt trong `<style>` đầu từng file (`.todo`, `.todo-item`, `.range-btns`, `.cta`, `.sub-note`); nên chuyển vào `app.css` khi người giữ file ghép. 19, 20, 22b, 25, 30 có khối `<style>` này.
- 33:56 vẫn «Đông Cuông › Đồng Vối» (đã nằm trong danh sách chờ Lead quyết).

## 3. Cần người ghép (#38) lưu ý

- `_tools/vo.html` chưa có route cho 21b: `?moi=1` hiện rơi vào màn 21. Thêm `[/^\/quan-ly\/danh-muc\/nguoi-ban/, /moi=1/.test(href) ? "supplier_add" : …]` nếu muốn bấm «+ Thêm người bán» sang 21b.
- Bấm «Duyệt» ở trang chủ chủ (19) đã sang 22b theo route `approved=0`; «Lưu mẫu» sang `retain_list`; «Quản lý khác» sang 31.
- Số chạm (ước, theo mockup tĩnh): chủ hoặc thủ kho in tem từ lô vừa xong 9 → 2 (nút «In 90 tem cho lô này» + «In» trong hộp thoại; phụ thuộc B/17 có nút trỏ về 25); duyệt người bán 3 → 2; thêm người bán ≈ 16 chạm + 5 gõ → ≈ 6 chạm + 1 gõ; đổi khoảng báo cáo 4 chạm + 2 gõ → 1 chạm. Chưa thử với người dùng thật.
- Chưa mở bản ghép; chưa chụp trước/sau chính thức; chưa kiểm bấm link trong vỏ.
