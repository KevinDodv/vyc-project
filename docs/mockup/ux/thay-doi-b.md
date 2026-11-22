# Thay đổi cụm B theo rà soát UX (task #36)

Người sửa: Phuong · 21/11/2026. Làm theo `ux/ra-soat-b.md`; sửa các màn trong `de-xuat/man/b-san-xuat/`. Không đụng `app.css`, `goc/`, `ban-chinh.html`, `ban-xem-truoc.html`, `_tools/vo.html`. Chưa ghép lại `ban-xem-truoc.html` (việc của @Long, #38).

**Cập nhật 21/11/2026 (trả lại ở #36, theo sếp chốt #494):** ý 3, 4, 5 sếp đổi so với mặc định đã vào màn: nút «Điền sẵn số cân theo gợi ý» (B2-18), lưu việc lắc chai gồm ai và lúc nào (B2-30/31), form ngửi chỉ còn Đạt / Chưa đạt, người kiểm tự lấy theo người đăng nhập (B2-44). Ý 1 và 2 giữ như mặc định (B2-07, B2-17). Ý 7 (in tem theo lô, gán luôn) đã áp ở 17 và 18 theo @Dat (#498, #499). Các dòng bên dưới đã sửa lại; dòng nào còn chữ «mặc định» là do sếp chọn đúng mặc định.

Giữ nguyên trạng thái lô đã chốt ở #29: **QC2-261023-01** đã ngửi đạt, đang dùng, đã gán tem 0/90 (màn 17, 26, 26b, 26c, thẻ «cần gán tem» ở 15 và 24); **QC2-261023-02** (LSX-2610-003) chờ ngửi (màn 15, 16b, 16c, 16d, 24).

## 1. Màn mới và điều Long cần làm khi ghép

| STT | Key | Màn | Chèn sau |
|---|---|---|---|
| 16d | `cure-smell` | Ngửi kiểm tra: «Đạt» hoặc «Chưa đạt, ủ thêm 7 ngày» | `cure-detail` |
| 16e | `cure-result` | Nhập kết quả: số kg, số chai, tạo lô | `cure-smell` |

Đã thêm vào `b-san-xuat/_ds.json` (18 mục, parse được; 68 key của cả 3 cụm, không trùng).

**@Long:** `_tools/vo.html` chỉ có route `/san-xuat/ua/<số>` → `cure_detail`. Hai link mới cần thêm 2 dòng route **đặt trước** dòng đó, nếu không bấm sẽ rơi vào 16c:
`/san-xuat/ua/<số>/ngui` → `cure_smell`, `/san-xuat/ua/<số>/ket-qua` → `cure_result`.
B2-80 (mỗi mẻ một id `ua/1..4`) **không cần sửa vỏ**: route `/san-xuat/ua/\d+` nhận mọi id (đã thử).

## 2. Số bước trước → sau (mỗi việc hằng ngày)

Chạm = một lần bấm hoặc quét; gõ = ô phải gõ. Không tính chạm mở màn.

| # | Việc | Màn | Trước | Sau |
|---|---|---|---|---|
| 1 | Bắt đầu mẻ | 24 | 4 chạm + 1 gõ (cỡ mẻ gram) | 4 chạm + 0 gõ: mở form, chọn sản phẩm, chọn cỡ mẻ, Tạo lệnh (3 chạm nếu cùng sản phẩm lần trước, vì đã chọn sẵn) |
| 2 | Ghi 4 nguyên liệu | 16 | 8 chạm (4 quét + 4 chuyển ô) + 4 gõ | **Cách A (gõ số cân thật):** 4 quét + 4 gõ; quét xong tự nhảy vào ô số cân, Enter sang thứ kế (hành vi của app, màn tĩnh chỉ ghi bằng chữ). **Cách B (nút «Điền sẵn số cân theo gợi ý», sếp chốt):** mỗi thứ 1 quét + 1 điền sẵn + 1 «Xác nhận số cân» = 12 chạm + 0 gõ cho 4 thứ. Số điền sẵn mờ, nhãn «gợi ý», chưa lưu cho tới khi xác nhận |
| 3 | Đưa vào ủ | 16 | 1 chạm | 1 chạm; bỏ khối «Nhập kết quả» mờ |
| 4 | Lắc chai | 15, 16b, 24 | không có chỗ bấm | 1 chạm «Đã lắc chai hôm nay» ngay trên thẻ; **ghi người đăng nhập và giờ lắc**, lịch sử hiện ở 16c và 26b (sếp chốt, B2-31) |
| 5 | Ngửi kiểm tra | 16d | 9 chạm (4 ô chọn × 2 + Đạt) | 1 chạm «Đạt»; chưa đạt 2 chạm (mở, chọn lý do). Người kiểm và giờ tự ghi, chỉ hiện chữ nhỏ «Người kiểm: … lúc …», không có ô chọn |
| 6 | Tạo lô | 16e | 1 chạm + 2 gõ + 2 ô ngày | 1 chạm + 2 gõ; ngày hiện thành chữ, «Sửa ngày» mới mở ô |
| 7 | Lưu mẫu | 17 | 2 chạm | 1 chạm «Đã lấy chai lưu mẫu» (tự sang màn in tem) |
| 8 | Dán tem cho lô | 17, 18 | 2 quét | **In tem theo lô, gán luôn** (sếp chốt #494 ý 7, @Dat): 17 có nút «In tem cho 90 chai» trỏ `/quan-ly/cuon-tem` (A1), 2 chạm ở màn in (@Dat đếm 9 → 2 ở `thay-doi-c.md`). Không còn quét tem đầu/cuối. 18 chỉ còn **gán bù** tem in rời (vẫn 2 quét, BR-12) và hủy tem lỗi, có banner ghi rõ |

Cộng các việc trên (một mẻ tinh dầu 4 thành phần, không tính lắc chai, +1 chạm mỗi lần lắc): **27 chạm + 7 gõ → 14 chạm + 6 gõ** nếu cân bằng cách A (gõ số cân thật); **22 chạm + 2 gõ** nếu cân bằng cách B (nút điền sẵn, thêm 8 chạm điền sẵn và xác nhận, bớt 4 gõ). Hai cách cùng bắt cân thật 0,01 g; khác nhau ở chỗ có gõ lại số hay chỉ xác nhận số gợi ý. Tôi cộng lại từng việc; số «25 → 17» ở `ra-soat-b.md` §1 không cộng lại được từ bảng, nên dùng số ở đây (nói «khoảng», vì đếm tay). Bản trước ghi «7 gõ giữ nguyên»; cộng lại là 6 (cỡ mẻ đã thành nút bấm, ghi 0 gõ ở dòng 1), nên đã sửa.

## 3. Từng đề xuất

Cột «Kết quả»: **làm** = đúng đề xuất; **làm theo sếp** = điểm CẦN SẾP QUYẾT đã được sếp chốt ở #494 (ghi rõ chọn đúng mặc định hay đổi); ghi chú nét đứt trên màn nay ghi «Sếp đã chốt»; **một phần** kèm lý do.

| Mã | Màn | Đã sửa gì | Kết quả |
|---|---|---|---|
| B2-01 | 24 | Hàng nút «Làm bao nhiêu?»: 100 ml · 500 ml · 1 lít · Số khác; gram tự tính, ô gõ chỉ mở ở «Số khác» | làm |
| B2-02 | 24 | Sản phẩm là nút to, không còn mã SKU; sản phẩm lần trước làm đứng đầu, chọn sẵn; Trà vẫn xám | làm |
| B2-03 | 24 | «Làm thành phẩm» / «Làm hương nền, dầu quế ủ…»; công thức chỉ còn một dòng chữ | làm |
| B2-04 | 24 | Đầu màn là nút xanh «+ Bắt đầu mẻ mới», bấm mới mở form (đóng sẵn); ba danh sách đi sau | làm |
| B2-05 | 24 | Ghi chú nét đứt mô tả 2 nút TT1/TT2 bắt chọn, «Tạo lệnh» xám tới khi chọn (QC2 không có nhóm này nên không vẽ nút khóa) | làm |
| B2-06 | 24 | «Ngày làm: hôm nay» + «Đổi ngày»; «+ Thêm ghi chú» | làm |
| B2-07 | 15 | Giữ chỉ chủ DN tạo lệnh; thêm dòng «Chưa thấy lệnh mới? Nhờ chủ doanh nghiệp tạo lệnh» + ghi chú «Sếp đã chốt» (#494 ý 1) | làm theo sếp (chọn đúng mặc định) |
| B2-10 | 16 | Mỗi thành phần một thẻ lớn theo thứ tự công thức: tên đầy đủ, «Cân 480,00 g» cỡ 32 px, lô gợi ý, ô quét, ô số cân. Bỏ bảng 6 cột và mã viết tắt | làm |
| B2-11 | 16 | Dòng hướng dẫn «quét xong tự nhảy xuống ô số cân, Enter sang thứ kế». `inputmode="decimal"` đã có | một phần: hành vi là việc của app, màn tĩnh chỉ ghi bằng chữ |
| B2-12 | 16 | «Quét tem lô, rồi gõ số cân. Cân sai thì ghi số thật…»; «TARE» thành «bấm TARE (trừ bì)» | làm |
| B2-13 | 16 | Trong thẻ vàng: «Nhiều hơn 0,09 g so với cần cân (cho phép 0,05 g). Vẫn lưu được.»; bỏ banner riêng | làm |
| B2-14 | 16 | «Bỏ dòng này», cao ≥ 48 px (ghi đè trong màn) | làm |
| B2-15 | 16 | «+ Thêm phụ liệu ngoài công thức» là nút thường 64 px | làm |
| B2-16 | 16 | Dưới ô quét: «Tem không quét được? Chọn lô» mở 2 nút lô | làm |
| B2-17 | 16 | Vẫn quét tem; chỉ có đường lùi B2-16 | làm theo sếp (#494 ý 2, chọn đúng mặc định) |
| B2-18 | 16 | Mỗi thẻ thành phần chưa cân có nút «Điền sẵn số cân theo gợi ý (200,00 g)». Số điền sẵn hiện mờ, nghiêng, nhãn «gợi ý»; phải bấm «Xác nhận số cân» mới lưu, sửa được nếu cân thật khác. Màn tĩnh vẽ trạng thái sau khi bấm trong khối thu gọn «Xem ô sau khi bấm». Bỏ annot «CẦN SẾP QUYẾT» | làm theo sếp (#494 ý 3, đổi so với mặc định «không có nút»). Máy chủ chỉ coi số điền sẵn là gợi ý, vẫn lưu số đã xác nhận |
| B2-20 | 16 | Bỏ khối «4 Nhập kết quả» mờ khỏi màn pha | làm |
| B2-21 | 16 | Một khối «Pha xong thì đưa vào ủ»: dòng «Còn thiếu: Hạt thạch cao ↑», nút 72 px xám; ghi chú toast «Đã đưa vào ủ. Dán tem TUI-261120-01 lên lọ.» | một phần: «bấm nhảy tới thẻ» là hành vi app, màn tĩnh chỉ có mũi tên ↑ |
| B2-30 | 15, 16b, 24, 16c | Thẻ mẻ có nút to «Đã lắc chai hôm nay» khi đến lượt (QC1), kèm dòng «Bấm là ghi người đăng nhập và giờ lắc». 16c bỏ 10 ô tick khóa, thêm «Lịch sử lắc chai» (ngày giờ · người, ví dụ «19/11 08:10 · Thủ kho (mẫu)») | làm theo sếp (#494 ý 4) |
| B2-31 | 15, 16b, 16c, 26b | Lưu việc lắc chai: ai lắc, lúc nào (người và giờ lấy từ phiên đăng nhập và giờ máy chủ). 26b bỏ chữ «máy nhắc, không ghi từng lần», hiện «đã lắc 9 lần» và 3 lần gần nhất. Cần thêm bản ghi «lắc chai» vào thiết kế (đã chuyển sang topic #2, #496) | làm theo sếp (#494 ý 4, đổi so với mặc định «chỉ nhắc») |
| B2-40 | 16d (mới) | Màn riêng: «Đạt» (xanh, 72 px) và «Chưa đạt, ủ thêm 7 ngày». 4 mốc ngửi nằm ở «Xem hướng dẫn ngửi»; «+ Ghi chú thêm» thu gọn. Dòng chữ nhỏ «Người kiểm: Thủ kho (mẫu) lúc 20/11 08:30» (theo @Tri #472: giữ truy vết; đúng chữ sếp chốt) | làm |
| B2-41 | 16d | Lý do ủ thêm: 2 nút («Còn mùi gắt», «Khác mẫu chuẩn») + «Lý do khác (gõ)» | làm |
| B2-42 | 16c, 16d | 16c chỉ còn nút «Ngửi kiểm tra»; «Đạt» chuyển sang 16e. Mỗi màn một nút chính | làm |
| B2-43 | 16c | Khối «Chỉ chủ doanh nghiệp thấy»: nút thật «Bỏ qua kiểm tra ngày ủ», lý do bắt buộc (2 nút nhanh + gõ), ghi tên, giờ, lý do (BR-28) | làm |
| B2-44 | 16d | Bỏ 4 ô chọn, chỉ Đạt / Chưa đạt + ghi chú tuỳ chọn. Người ngửi và giờ tự lấy theo người đăng nhập, không có ô chọn. Bỏ annot «CẦN SẾP QUYẾT» | làm theo sếp (#494 ý 5, chọn đúng mặc định «bỏ 4 ô», thêm chữ «Người kiểm … lúc …») |
| B2-50 | 16e (mới) | 2 ô số to «Cân được bao nhiêu kg?», «Bán được bao nhiêu chai?»; nút «Hoàn thành, tạo lô» | làm |
| B2-51 | 16e | «Ngày xong: hôm nay · Hạn dùng: 20/05/2028 (tự tính 18 tháng)» + «Sửa ngày». Túi thơm, sáp, viên (chưa có hạn mặc định): ô hạn hiện to, nút khóa tới khi nhập | một phần: trường hợp túi thơm chỉ ghi bằng chữ, không vẽ thêm màn |
| B2-52 | 16e | Nhãn «(tự tính 18 tháng)», bỏ «sửa được» (nút «Sửa ngày» đã nói thay) | làm |
| B2-53 | 16e | Nhãn theo đơn vị đếm (túi thơm: «túi»); màn mẫu là tinh dầu nên hiện «chai» | một phần: ghi bằng chữ |
| B2-60 | 17 | «Đã lấy chai lưu mẫu» (chính, tự sang gán tem) và «Để sau» (vẫn sang gán tem); vị trí là ô điền sẵn | làm |
| B2-61 | 17 | Bỏ banner «Chưa lưu mẫu…»; ghi chú toast «Nhớ lưu mẫu sau, việc này nằm ở trang chủ» | làm |
| B2-62 | 17 | Ngày xong và hạn dùng vào ô KPI; còn một dòng «90 chai chưa gồm chai lưu mẫu…» | làm |
| B2-63 | 17 | «Xong! Lô QC2-261023-01 đã tạo.» | làm |
| B2-64 | 26b, 26c | «Lưu mẫu» mở «Để chai ở đâu?», ô vị trí điền sẵn + nút «Lưu mẫu». 26c: «Lô chưa lưu mẫu» đổi từ bảng sang thẻ | làm |
| B2-65 | 26c | «Hủy mẫu» ≥ 48 px, mở hỏi «Hủy mẫu QC2-251105-01?» rồi mới có nút xác nhận | làm |
| B2-70 | 18 | Giữ «Bước 1/2 … tem ĐẦU», «Bước 2/2 … tem CUỐI» và tự gán sau khi quét tem cuối, nhưng nay chỉ cho **gán bù** tem in rời: tab đổi «Gán bù tem rời vào lô», tên màn «Gán bù / hủy tem», có banner «Tem in theo lô đã gán luôn, không cần quét ở đây» (ý 7 của sếp, thống nhất với @Dat) | làm (trạng thái «mới vào chỉ có bước 1/2» ghi bằng chữ) |
| B2-71 | 18 | «Quét lại tem đầu» là nút 48 px | làm |
| B2-72 | 18 | Dòng to «Còn 50 tem cần gán» + thanh tiến độ + «Đã gán 150 / 200» | làm |
| B2-73 | 18 | Ô thông báo `#msg` có chú thích kèm 3 ví dụ: xanh «Đã gán 50 tem, lô này xong», 2 lỗi bằng chữ thường | làm |
| B2-74 | 15, 24 | Thêm thẻ «QC2-261023-01 · đã gán 0/90 · Còn 90 tem cần gán» | làm |
| B2-75 | 18 | Lưới chọn lô ẩn, còn «Lô Q100-261120-02» + «Đổi lô» | làm |
| B2-80 | 15, 16b, 24 | QC2-…-02 = `ua/1`, DDT = `ua/2`, TUI = `ua/3`, QC1 = `ua/4` | làm; vỏ không cần sửa (xem §1) |
| B2-81 | 26 | Bỏ «Hiệu suất» và «Giá quế / đơn vị»; «SL» → «Số lượng»; «Ngày SX» → «Ngày làm xong». «Công thức» và «Ngày pha» do sếp đã duyệt (#429) nên **giữ**, chuyển thành chữ nhỏ dưới «Sản phẩm» và «Ngày làm xong». 15 cột → 11 | một phần: ra-soat-b đề xuất bỏ cả hai cột này, tôi giữ vì ngại lệch với bản đã duyệt; sếp muốn gọn hơn thì bỏ tiếp |
| B2-82 | 26 | Bỏ nút «Thu hồi» đỏ từng hàng; thay bằng «Xem lô» (nút thu hồi nằm trong trang lô, 26b:65) | một phần: xem §5 (lô Q100) |
| B2-83 | 16b | Bảng 7 cột → thẻ mỗi mẻ: tên to, «Còn 3 ngày», nút 64 px «Ngửi kiểm tra» hoặc «Đã lắc chai hôm nay» | làm |
| B2-84 | 23b, 23c | «Đầu ra» → «Làm ra»; «Bán thành phẩm TT1/TT2/DDT/Q/VQH» → «Hương nền TT1/TT2», «Dung dịch tẩm», «Dầu quế ủ», «Vỏ quế sơ chế» | làm |
| B2-85 | 23c | «Nhãn mẻ» và «Ủ tối đa» vào «Thêm tuỳ chọn» (đóng sẵn) | làm |
| B2-86 | 23 | ✔ và — thành «Có» / «Không» ở cột «Lưu mẫu» và «Dán tem» | làm |
| B2-87 | 26d | FAIL/PASS → «Không đạt»/«Đạt»; «cường độ / dễ chịu» → «Mùi mạnh / dễ chịu»; «TB» → «trung bình» | làm |

CSS (mục 4 của ra-soat-b): `app.css` không sửa (ngoài vùng). Trong từng màn đã ghi đè: `td input,td select` 44 → 48 px, `.chip` `min-height:48px`, `button.small` 48 px. **Còn để cho người giữ `app.css`:** `button.small` (`:79`), `button.link` (`:80`), `.tag` `.78rem`, `.tile .badge`, `.choice .sub`, `.totalbar .lbl`, `.kpi .l` `.85rem` (nhỏ hơn 16 px), checkbox 28 px.

## 4. Sửa thêm ngoài danh sách

- `26c`: tab «Mẫu đang giữ (4)» chỉ có 3 dòng, sửa thành «(3)».
- `26b`: dòng «Lắc chai 10/10 lần» sửa theo B2-31: «đã lắc 9 lần» + 3 lần gần nhất (ai, lúc nào).
- `16c`: thay 10 ô tick khóa bằng «Lịch sử lắc chai» (theo B2-31, sếp chốt lưu).
- `17`: thêm khối «Tem cho lô này» với nút «In tem cho 90 chai» → `/quan-ly/cuon-tem`; hai nút lưu mẫu cũng trỏ về đó (trước trỏ `/dong-goi?lot=3`).
- `18`: bỏ chữ «Gán tem», thành «Gán bù / hủy tem» (cả `_ds.json` mục 18), thêm banner. Bước 1/2, 2/2 giữ cho việc gán bù.
- `16e`: ghi chú rõ màn này chỉ hiện sau khi bấm «Đạt»; mẻ -02 đang chờ ngửi, số 0,83 kg và 90 chai là số mẫu.

## 5. Việc còn lại và cần quyết

- **Lô Q100 và thu hồi** (B2-82): đã chốt ở #509: nút «Thu hồi lô» đặt ở màn tra cứu 27 cho mọi lô, không làm 26b cho từng lô; @Dat làm (chỉ sửa 27-trace.html, ngoài vùng của task này). Chữ ở 26:52 giữ nguyên.
- Cần thêm vào tài liệu thiết kế (đã chuyển topic #2, #496): bản ghi «lắc chai» (ai, lúc nào) ở giai đoạn ủ.
- `14b-ingr-stock.html:54` còn nhắc QC2-261023-01 (cụm A, như `ra-soat-b.md` §5).
- Ghi chú cho @Thao: bảng §1 dòng 5–6 của `ra-soat-b.md` đếm «1 màn» nhưng B2-42 và B2-50 tách thành 2 màn; bản sửa đã tách (16d, 16e).

## 6. Đã mở thử trên trình duyệt


**Lượt sửa theo #494 (21/11/2026):** mở bằng Chrome không cửa sổ, ở 1280 px, trên bản ghép CSS tạm ngoài repo (chép `app.css` vào từng màn):
- 15, 16, 16b, 16c, 17: không tràn ngang, không nút hay ô nào cao dưới 48 px. Đã xem ảnh: 16 (nút «Điền sẵn số cân theo gợi ý», ô gợi ý mờ kèm nhãn «gợi ý»), 16c (lịch sử lắc 3 dòng + «Xem cả 9 lần»), 17 (khối «Tem cho lô này», chỉ một nút xanh).
- **Chưa mở được trình duyệt** cho 16d, 18, 24, 26b (Chrome tắt giữa chừng khi chuyển trang); các màn này chỉ sửa chữ/khối nhỏ, mới kiểm bằng grep: không còn «không ghi», «máy nhắc», «CẦN SẾP QUYẾT», «Hệ thống tự ghi người ngửi». Cần ai mở lại khi ghép (#38).
- Ảnh mới: `.proteam/evidence/b36-16-prod-order-gopy.png`, `b36-16c-cure-detail-sau2.png`, `b36-17-prod-done-sau2.png`.
Chrome không cửa sổ (điều khiển bằng CDP), trên bản ghép tạm nằm ngoài repo (có thêm 2 dòng route nói ở §1), 21/11/2026:

- Mở từng màn của cụm (15, 16, 16b–16e, 17, 18, 23, 23b, 23c, 24, 26, 26b–26d) ở 1280 px: không tràn ngang. Ở 390 px (15, 16, 16b–16e, 17, 18, 24, 26b, 26c): không tràn ngang, không còn nút hay ô nào cao dưới 48 px.
- Bấm thử: 15 → «Ngửi kiểm tra» → 16d → «Đạt» → 16e → «← Ngửi kiểm tra» → 16d; 16b → «Xem chi tiết» (`ua/4`) → 16c; 17 → gán tem → 18; 26 → bấm mã lô QC2-261023-01 (cùng đích với nút «Xem lô») → 26b. «Chưa đạt, ủ thêm 7 ngày» mở ra đúng. Menu có 68 mục.
- Chưa thử: bản ghép thật `ban-xem-truoc.html` (chưa có 2 route trong vỏ); điện thoại thật.
- Ảnh chụp trước/sau: `.proteam/evidence/b36-<màn>-truoc.png` và `-sau.png` (thêm `b36-24-prod-owner-mo.png`, `b36-16d-cure-smell-mo.png`, và `-dt` là bản 390 px). Màn mới 16d, 16e chỉ có ảnh sau.

## 7. File đã sửa

Trong `de-xuat/man/b-san-xuat/`: `15`, `16`, `16b`, `16c`, `16d`, `17`, `18`, `23`, `23b`, `23c`, `24`, `26`, `26b`, `26c`, `26d` (.html); **mới** `16d-cure-smell.html`, `16e-cure-result.html`; `_ds.json`. Không đụng `06b`, `14b` (cụm A).
