# Rà soát UX cụm A (nhập/xuất kho, màn 02–14) + chuẩn chung

Task #32, theo ý sếp (#460): người dùng rất kém công nghệ, cần ít bước nhất, nhanh nhất.
Màn nguồn: `docs/mockup/de-xuat/man/a-nhap-xuat-kho/` (viết tắt `A/`). Căn cứ nghiệp vụ: `docs/thiet-ke-chi-tiet.md` (viết tắt TK) mục 6.2–6.5 và BR-01..25.
Chưa sửa file màn nào (ngoài vùng của task); chỉ sửa `app.css`. Các đề xuất bên dưới là việc để Long (Dev) dựng.

## 0. Chuẩn UX chung (áp cho cả 3 cụm A, B, C)

| # | Chuẩn | Cách kiểm |
|---|---|---|
| 0.1 | **Vùng chạm ≥ 48×48 px** cho mọi nút, link, ô nhập, dòng bảng bấm được, ô tick (kể cả vùng chữ cạnh ô tick). Nút thao tác chính ≥ 64 px, nút chính cuối màn 72 px. | Đo bằng script (xem mục 5) |
| 0.2 | **Chữ thân ≥ 18 px, chữ phụ (nhãn nhỏ, ghi chú, cột bảng) ≥ 16 px.** Không có chữ dưới 16 px trên màn thao tác. Số tiền, số cân ở ô nhập 32 px. (Tem, phiếu in ra giấy theo khổ giấy nên không áp.) | Đo font tính toán |
| 0.3 | **Mỗi màn một nút chính, một màu duy nhất (xanh lá `--cta`), nằm ở cuối màn** (thanh dưới cùng, cao 72 px). Nút khác viền nâu nền trắng. Nút nguy hiểm (Hủy) viền đỏ, không bao giờ là nút chính. Một màn không có hai nút xanh lá. | Nhìn màn |
| 0.4 | **Chữ không viết tắt, chữ đời thường.** «Số điện thoại» không «SĐT»; «Số lượng» không «SL»; «Hạn dùng» không «HSD»; «Doanh nghiệp» không «DN/XNK»; «Giai đoạn 2» không «GĐ2» (nhãn này chỉ có trong bản xem trước, bản chạy thật không hiện nút chưa có). Không «Enter», «serial», «API». Một việc một tên gọi: dùng «Loại» (không lúc «Hạng» lúc «Loại»), «Đơn hàng» cho thành phẩm. | Đọc lại chữ |
| 0.5 | **Chọn bằng nút, không gõ, nếu danh sách ≤ 8 lựa chọn.** Quét tem ưu tiên hơn gõ mã. Ô số bật bàn phím số (`inputmode`). | |
| 0.6 | **Điền sẵn**: hôm nay, người đang đăng nhập, lựa chọn của lần trước, giá hôm nay, lô cũ nhất. Chỉ hỏi khi không đoán được. | |
| 0.7 | **Không bỏ trường bắt buộc của BR**; chỉ điền sẵn hoặc cất vào mục «Thêm» khi BR không bắt buộc. | |
| 0.8 | **Việc nguy hiểm** (hủy phiếu, làm lại kiểm kê, xóa dòng) có 1 bước xác nhận bằng hộp thoại hai nút to, nút «Giữ lại» là nút mặc định. Việc thường làm thì không hỏi xác nhận. | |
| 0.9 | Trạng thái mỗi màn có đủ: rỗng («Chưa có dòng nào» + chỉ dẫn việc đầu tiên), lỗi (khung đỏ, nói rõ làm gì tiếp), quá dài (bảng cuộn ngang trong `.table-wrap`, không tràn trang). Có viền focus 3 px khi dùng bàn phím. | |
| 0.10 | Màn hẹp (điện thoại ~390 px): một cột, thanh dưới xếp dọc, nút chính tràn ngang. Chưa có giao diện tối (dự án chưa đòi hỏi), không làm. | |

## 1. Việc hằng ngày của cụm A: hiện trạng → đề xuất

Cách đếm: **chạm** = một lần bấm nút hoặc một lần quét tem; **gõ** = một ô phải gõ bằng bàn phím; **trang** = trang web riêng (các bước hiện dần trong cùng trang chỉ tính 1 trang). Đếm theo màn `A/` đang có; «in» là 1 chạm vào nút In ở hộp thoại in.

### V1. Cân và thu mua một lần bán (02 → 03/04 → 05)

Tình huống mẫu: người bán đã có trong danh sách, 3 dòng hàng (như 05:56 «3 lô»).

| | Hiện trạng | Đề xuất |
|---|---|---|
| Trang | 3 (02, 03, hộp in) | 2 (02, 03+hộp in) |
| Chạm, 3 dòng | **14**: Nhập hàng 1, người bán 1, đồi 1, mỗi dòng (nguyên liệu 1 + loại 1 + «Thêm dòng» 1) × 3, Lưu 1, in 1 | **10**: Nhập hàng 1, người bán 1, đồi 0 (tự chọn), mỗi dòng (nút hàng 1 + «Thêm dòng» 1, dòng cuối tự thêm khi Lưu) = 5, Lưu 1, in 1 |
| Chạm, 1 dòng | **8** | **5** |
| Gõ | 3 (số cân mỗi dòng) | 3 (giữ nguyên: cân thật phải gõ) |
| Chỗ khó hiểu | «Hạng» đổi thành «Loại» giữa chừng (04:38 nhãn «Hạng», bảng «Loại»); «Vùng kiểm soát» không nói nghĩa là gì (04:22); mã «NCC-CQ-001» (04:22); «(Enter)» trên nút (03:44); 3 bước đánh số nhưng bước 2 «đồi» có người bán chỉ có 1 đồi vẫn phải bấm; nút «Phiếu hôm nay» nhỏ nằm sát nút Lưu (03:62) dễ bấm nhầm; sau khi lưu, thanh dưới vẫn hiện «Lưu và in» mờ (05:63) trong khi việc tiếp theo là «Phiếu mới» (05:56) |  |

Đề xuất (mỗi đề xuất ghi màn, sửa gì, trước → sau, căn cứ):

- **A1. Gộp «nguyên liệu» + «loại» thành một dãy nút hàng.** 03:38–39 (và 03b:40–41, 04:38–39, 04b, 04c, 05, 05b cùng khối): bỏ hai hàng nút, thay bằng một hàng 6 nút lớn «Vỏ quế loại 1 · 45.000 đ/kg», «Vỏ quế loại 2», «Vỏ quế loại 3», «Quế vụn loại 1», … mỗi nút có giá hôm nay. Mỗi dòng 3 chạm → 2 chạm; bỏ chữ «Chọn nguyên liệu trước» (03:39). Căn cứ: TK 6.2 (bấm nguyên liệu, bấm hạng, giá dưới nút) và BR-04 (giá mặc định theo bảng giá), dữ liệu vẫn đủ nguyên liệu + hạng.
- **A2. «Lưu và in» tự thêm dòng đang gõ dở.** 03:44 + 03:63 (và các bản 03b, 04*, 05*): nếu đã chọn hàng và gõ số cân mà chưa bấm «Thêm dòng», bấm «Lưu và in» vẫn tính dòng đó. Bỏ chữ «(Enter)» ở 03:44. −1 chạm mỗi phiếu. Căn cứ: BR-01 (mỗi dòng một lô) không đổi.
- **A3. Đồi tự chọn.** 03:30–33, 04:30–33: người bán chỉ có 1 đồi (hoặc là hàng chung) → bỏ bước 2 (đã ẩn ở 04c:30, giữ). Người bán có ≥2 đồi → hiện nút đồi, chọn sẵn đồi của lần trước (04:32 đang chọn sẵn D-CQ-001-01, nhưng thiếu quy tắc «nhớ lần trước»). −1 chạm với người bán 1 đồi. Căn cứ: TK 6.2 (`plot_id?` không bắt buộc ở body POST, TK 943).
- **A4. Giải thích thuật ngữ ngay tại chỗ.** 04:22, 12:21: «Vùng kiểm soát» → «Vùng kiểm soát (làm được tinh dầu có QR)», «Hàng chung» → «Hàng chung (chỉ bán quế khô)». Ẩn mã «NCC-CQ-001» khỏi màn thao tác (chỉ để cho chủ). Căn cứ: BR-03, BR-08 (nghĩa của hai luồng). Chỉ đổi chữ, **không đổi nghiệp vụ**.
- **A5. Sau khi lưu chỉ còn một việc: «Phiếu mới».** 05:56–63, 05b:56–63: banner xanh «Đã lưu…» + 3 nút («In lại phiếu», «In lại tem lô», «+ Phiếu mới») giữ, nhưng thanh dưới đổi thành nút chính xanh «Phiếu mới» (thay nút «Lưu và in» đang mờ ở 05:63), tổng tiền giữ để người bán đối chiếu. Trước → sau: 2 nút hơi trùng → 1 nút chính. Căn cứ: TK 6.2 «Lưu và in».
- **A6. Bỏ link «Phiếu hôm nay» khỏi thanh dưới.** 03:62 (và 03b:64, 04*:62, 05*:62): nút phụ nằm cạnh nút chính dễ bấm nhầm, màn Trang chủ đã có (02:25). Chuyển thành link nhỏ ở đầu màn.

Người bán mới (03b):

| | Hiện trạng | Đề xuất |
|---|---|---|
| Chạm | **6**: Nhập hàng 1, «+ Người bán mới» 1, kiểu 1, xã 1, thôn 1, Lưu 1 | **3–4**: nhập hàng 1, «+ Người bán mới» 1, (kiểu/xã/thôn chọn sẵn theo lần thêm trước, chỉ đổi khi khác) , Lưu 1 |
| Gõ | 1 (tên) | 1 (tên) |
| Chỗ khó | Banner dài 2 câu (03b:22); «Kiểu», «Luồng» là thuật ngữ; hai nút «Lưu và chọn người bán này» + «Hủy» ngang hàng (03b:29) | |

- **A7. Điền sẵn kiểu, xã, thôn; bỏ dòng «Luồng».** 03b:25–28: «Kiểu» chọn sẵn «Hộ dân» (đang là mặc định, 03b:25), xã và thôn nhớ lần trước. Dòng «Luồng: Hàng chung (chưa duyệt)» (03b:28) gộp vào banner một câu: «Người bán mới tính là hàng chung (chỉ bán quế khô) cho tới khi chủ duyệt.» Nút chính «Lưu», «Hủy» thành link. Căn cứ: BR-03 (người bán mới luôn GENERAL), TK 640.

### V2. Xem, in lại, sửa, hủy phiếu nhập hôm nay (02 → 06)

| | Hiện trạng | Đề xuất |
|---|---|---|
| Trang | 2 | 2 |
| Chạm, xem phiếu hôm nay | 1 (ô ngày đã điền hôm nay, nhưng có thêm nút «Xem» 06:21 gây hiểu phải bấm) | 1 (tự hiện hôm nay) |
| Chạm, in lại | 2 (tile + «In») | 2 |
| Chạm, hủy | 2 + hộp xác nhận chưa vẽ (06:27 nút «Hủy» nhỏ ngay cạnh «Sửa», «In») | 3 (tile, Hủy, xác nhận «Hủy phiếu» / «Giữ lại») |
| Chỗ khó | «Từ ngày»/«Đến ngày»/«Xem» chiếm cả hàng; đoạn ghi chú 3 câu (06:24); nút nhỏ 44 px sát nhau; trạng thái «có lô đã dùng» nói gì thì không biết (06:27) | |

- **A8. Mặc định «Hôm nay», ngày khác cất vào «Xem ngày khác».** 06:19–22: thay hai ô ngày + nút «Xem» bằng dòng chữ «Hôm nay 20/11/2026» và link «Xem ngày khác» mở ô ngày. Bảng tự tải. Căn cứ: TK 6.1 (xưởng xem phiếu hôm nay).
- **A9. Thêm hộp xác nhận hủy, và ghi lý do không sửa được ngay trên dòng.** 06:27: nút «Hủy» mở hộp «Hủy phiếu PN-261120-005? [Hủy phiếu] [Giữ lại]». Dòng đã có lô dùng (06:27 `có lô đã dùng`) hiện «Không sửa được: lô đã dùng» thay vì chỉ bỏ nút. Rút ghi chú 06:24 còn 1 câu: «Chỉ sửa, hủy được phiếu của mình trong ngày.» Căn cứ: BR-05, BR-19. Nút Sửa/In/Hủy đã ≥48 px nhờ `app.css`.

### V3. Bán quế khô theo cân (02 → 07 → 08)

| | Hiện trạng | Đề xuất |
|---|---|---|
| Trang | 4 (02, 07, 08, hộp in) | 3 (02, 08, hộp in) |
| Chạm | **9**: Xuất hàng 1, Bán quế khô 1, người mua 1, nguyên liệu 1, loại bán 1, lô 1, Thêm dòng 1, Lưu 1, in 1 | **5**: Bán quế khô 1, người mua 1, nút hàng 1, lô (chọn sẵn lô cũ nhất) 0–1, Lưu 1, in 1 |
| Gõ | 1 (số cân lúc bán) | 1 |
| Chỗ khó | màn 07 chỉ có 3 nút (đi vòng); tiêu đề bước 2 dài 1 câu 4 mũi tên (08:27); ô quét tem + danh sách lô + 2 ô nhập cùng lúc (08:32–40); nhãn «DN xuất khẩu» (08:22) | |

- **A10. Bỏ màn trung gian 07; đưa «Bán quế khô» lên Trang chủ.** 02:19 «Xuất hàng» thay bằng hai ô lớn «Bán quế khô» (→ 08) và «Bán thành phẩm» (→ 09) (Trang chủ có 4 ô lớn giai đoạn 1: Nhập hàng, Bán quế khô, Bán thành phẩm, Xem tồn kho; «Sản xuất» giai đoạn 2). 07 chỉ còn là lối dự phòng (danh sách đơn đã có ở 02:26). Trước → sau: −1 chạm, −1 trang cho cả V3 và V4. Căn cứ: TK 6.1 (trang chủ), 6.3, 6.4. **Không đổi nghiệp vụ.**
- **A11. Gộp «nguyên liệu» + «loại bán» thành một hàng nút** (như A1, có giá bán). 08:29–31: 5–6 nút «Vỏ quế loại 2 · 50.000 đ/kg». −1 chạm. Căn cứ: TK 6.3.
- **A12. Lô cũ nhất chọn sẵn, quét tem chỉ để đổi.** 08:32–35: **CẦN SẾP QUYẾT.** Phương án mặc định: sau khi chọn hàng, tự chọn sẵn lô cũ nhất (TK 666 đã sắp cũ nhất lên đầu), hiện chữ lớn «Lô NL-2611-0002 · 30 kg», nút «Đổi lô» (hiện danh sách) và ô quét. Ô quét tem vẫn có để quét bao thực tế. Rủi ro: nhân viên bán bao khác lô mà không quét. Phương án khác: bắt quét một tem rồi mới cho gõ cân (an toàn hơn, không bớt chạm). −1 chạm nếu sếp chọn mặc định. Căn cứ: BR-07 (lô quế thuộc một dòng xuất), TK 6.3 (quét tem hoặc bấm chọn).
- **A13. «Lưu và in» tự thêm dòng đang gõ dở** (như A2). 08:39, 08:51. −1 chạm.
- **A14. Người mua dùng nút «gần đây», giữ ô tìm.** 08:19–23: 5 nút người mua mua nhiều nhất (đã có 08:22), thêm sẵn người mua lần trước. Đổi nhãn «DN xuất khẩu» (08:22) → «Doanh nghiệp xuất khẩu». Tiêu đề bước 2 (08:27) rút: «Hàng bán». Căn cứ: TK 6.3 (kênh mặc định theo kiểu khách).

### V4. Bán thành phẩm, quét tem (02 → 07 → 09)

Ba tình huống: (a) khách lẻ cũ mua trực tiếp, 2 tem; (b) khách lẻ mới, 2 tem; (c) đơn Shopee, 2 tem.

| | (a) Hiện trạng | (a) Đề xuất | (b) Hiện trạng | (b) Đề xuất | (c) Hiện trạng | (c) Đề xuất |
|---|---|---|---|---|---|---|
| Trang | 4 | 3 | 4 | 3 | 4 | 3 |
| Chạm (kể cả quét tem) | **7**: Xuất hàng 1, Đơn hàng thành phẩm 1, quét 2, Lưu 1, in 1 + ô SĐT | **5**: Bán thành phẩm 1, quét 2, Lưu 1, in 1 | **10**: + tỉnh/xã 1–2, đồng ý 1 | **5** | **10**: Xuất hàng 1, ĐH thành phẩm 1, mở danh sách khách 1 + chọn Shopee 1, nút kênh 1, tỉnh 1, quét 2, Lưu 1, in 1 | **7**: Bán thành phẩm 1, nút «Shopee» 1, tỉnh 1, quét 2, Lưu 1, in 1 |
| Gõ | 1 (số điện thoại 10 số) | 1 | 3 (điện thoại, tên, địa chỉ) | 2 (điện thoại, tên) | 2 (mã đơn, tên) | 2 (mã đơn nếu có, tên) |
| Chỗ khó | | | | | | |

Chỗ khó hiện nay (`A/09-issue-product.html`): hai ô trả lời cùng một câu hỏi «Bán cho ai» (09:21 danh sách thả xuống «Khách / kênh trả tiền» và 09:23 nút «Kênh bán»); thuật ngữ «kênh»; «Người mua cuối» (09:28); hai cột (`.flow`) bắt nhân viên nhìn qua lại; ô «Mã đơn (không bắt buộc)» luôn hiện kể cả bán trực tiếp (09:24–25); địa chỉ «Số nhà – đường» và ô tick «Đồng ý nhận tin ưu đãi qua Zalo / SMS» (09:35–36) làm tưởng bắt buộc; ô đơn giá trong bảng là ô nhập cao 44 px (09:57) rất dễ chạm nhầm; viết tắt «SL» (09:56), «SĐT»; tên người mua hiện «T T H» (che theo BR-24, đúng nhưng khách không hiểu); chữ mã tem 12 px (09:57 inline `0.8rem`).

- **A15. Gộp «khách» và «kênh» thành một hàng nút «Bán cho ai».** 09:20–23 (cùng khối ở 09b, 09c, 09d): các nút lớn «Khách lẻ», «Shopee», «TikTok Shop», «Lazada», «Đại lý», «Doanh nghiệp». Chọn «Khách lẻ» mới hiện thêm 3 nút nhỏ «Trực tiếp / Website / Facebook-Zalo» (chọn sẵn «Trực tiếp»). Kênh của sàn, đại lý, doanh nghiệp tự suy từ khách. Chạm: (c) −2 (bỏ mở danh sách + 1 chọn). Căn cứ: TK 667 (kênh mặc định theo kiểu khách), BR-22 (bắt buộc người mua theo kênh). **Cần Long xác nhận mô hình dữ liệu**: nếu một khách có thể bán qua nhiều kênh thì giữ chọn kênh trong «Thêm».
- **A16. Chỉ hiện đúng các ô BR-22 bắt buộc.** 09:27–38 (09b:27–38, 09c:27–38): kênh trực tiếp, Website, Facebook-Zalo → chỉ hiện «Số điện thoại» + «Họ tên» (nếu số mới). Kênh sàn → «Họ tên» + «Tỉnh» (nút). Đại lý, doanh nghiệp → ẩn cả khối. «Tỉnh/xã», «Số nhà – đường», ô tick Zalo/SMS (09:34–36) vào mục gập «Thêm thông tin người mua (không bắt buộc)». Chữ nhắc «(bắt buộc tên + SĐT)» (09:28) → «Bắt buộc: họ tên, số điện thoại». (b): −2 chạm, −1 gõ. Căn cứ: BR-22, BR-23 (số điện thoại 10 số), TK 711 mục 6.6. **Không bỏ trường BR bắt buộc.** Nếu sếp muốn luôn thu địa chỉ để giao hàng, **CẦN SẾP QUYẾT**; mặc định là không bắt buộc.
- **A17. Mã đơn chỉ hiện với Website và sàn, nhận quét hoặc gõ.** 09:24–25: ẩn ở «Trực tiếp». Thêm nút quét mã vạch đơn sàn nếu có máy quét (cùng ô quét). −1 ô với bán trực tiếp.
- **A18. Quét tem lên đầu màn, một cột.** 09:17–59: bỏ hai cột `.flow` trên điện thoại (CSS đã làm một cột dưới 900 px); thứ tự: «1. Bán cho ai» (nút), «2. Quét tem» (ô quét tự focus, 09:43), «3. Người mua» (chỉ khi cần), thanh dưới: tổng + «Lưu đơn và in». Tên đề mục dùng «Người mua» thay «Người mua cuối» (09:28).
- **A19. Đơn giá hiển thị chữ, sửa bằng nút «Đổi giá».** 09:57 (09b:56, 09c:56, 09d:56): ô nhập 130×44 px → dòng chữ «150.000 đ» + nút «Đổi giá» (≥48 px) mở ô nhập. Tránh sửa nhầm giá. Cột «SL» → «Số lượng». Căn cứ: TK 6.4 (giá mặc định = giá bán lẻ, sửa được).
- **A20. Quà tặng gập vào «Thêm quà tặng», giữ một nút.** 09:45–52: giữ nút «🎁 Thêm quà tặng», bấm mới mở khối (đang là vậy, 09:47 `hidden`). Chữ «Quà không dán tem» (09:48) → «Quà không có tem (ví dụ thiệp)». Căn cứ: BR-25.
- **A21. Lỗi quét hiện to một dòng, đúng việc phải làm.** 09:53 (khung đỏ hiện «✖ TMFQ-EE8Z-KY: Đã quét trong phiếu này») → «Tem này đã quét trong đơn này. Quét tem khác.»; các lỗi mẫu trong mục gập 09:54 giữ làm tham chiếu cho Dev, ghi rõ «chỉ có trong bản xem trước». Căn cứ: TK 6.4 (bíp dài + lý do).
- **A22. Thanh dưới: «Lưu đơn và in» một nút chính xanh.** 09:62–67: số món, tổng tiền, nút 72 px. Chữ «Số món» giữ.

### V5. Xem tồn kho (02 → 12/13)

| | Hiện trạng | Đề xuất |
|---|---|---|
| Trang | 2 | 2 |
| Chạm | 1 (Xem tồn kho) + 1 cho mỗi tab/ô bấm xem lô | 1 + 1 |
| Gõ | 0 | 0 |
| Chỗ khó | 4 tab ngang bằng nhau (12:17) trong khi «Kiểm kê» làm hiếm; cột «Vùng kiểm soát/Hàng chung» khó hiểu (12:21); ghi chú dài 12:19, 12:30, 12:33; ô bấm xem lô chỉ có `cursor:pointer` không có dấu hiệu bấm được (12:22 `td.clickable`); chữ «còn 46 ngày» (12:29) trên nền cam dễ đọc nhầm là cảnh báo hỏng | |

- **A23. Tab «Kiểm kê» tách thành nút phụ «Kiểm kê kho» ở cuối trang tồn kho.** 12:17, 13:17, 14:17: tab còn «Quế», «Thành phẩm», «Phụ liệu»; «Kiểm kê» là nút viền thường ở cuối (làm hiếm, theo task: tách sang mục «Thêm»). Trước → sau: 4 tab → 3 tab + 1 nút. Căn cứ: TK 6.5 (Kiểm kê là nút riêng).
- **A24. Tên tab đời thường.** 12:17 «Nguyên liệu» → «Quế» (nguyên liệu là vỏ quế, quế vụn, TK 6.5 vẫn dùng «Nguyên liệu» ở tài liệu, màn chỉ đổi nhãn). Cột «Vùng kiểm soát/Hàng chung» → hai nút cột kèm chú thích như A4. Ô số lô: thêm mũi tên «›» để thấy bấm được (12:22).
- **A25. Một câu hướng dẫn mỗi tab.** 12:19 «Bấm số kg để xem từng lô.»; 12:30 bỏ phần giải thích «chai lưu mẫu», chỉ còn «Hạn dưới 60 ngày tô cam.» (đã có chữ «còn 46 ngày»). Căn cứ: TK 6.5.

### V6. Kiểm kê kho (02 → 12 → 14)

| | Hiện trạng | Đề xuất |
|---|---|---|
| Trang | 2 | 2 |
| Chạm | 2 + quét N bao + «So với hệ thống» 1 = **3 + N** | **3 + N** (không đổi) |
| Gõ | 0 | 0 |
| Chỗ khó | banner 3 câu (14:33); «So với hệ thống» (14:36); «Làm lại» (14:37) xóa hết số đã quét không hỏi (mất 50 lần quét); kết quả có ô số 4/3/1/1 tách rời khỏi dòng báo lỗi (14:38) | |

- **A26. Đổi chữ và xác nhận «Làm lại».** 14:33 → «Quét tem từng bao trong kho, rồi bấm Kiểm tra.»; 14:36 «So với hệ thống» → «Kiểm tra»; 14:37 «Làm lại» mở hộp «Xóa 4 bao đã quét? [Xóa] [Giữ lại]» (+1 chạm khi làm lại, nhưng tránh mất công). Kết quả: dòng lỗi đứng trước, ô số sau (14:38). Căn cứ: TK 6.5 (kiểm kê chỉ so, không sửa dữ liệu), BR-19.

### V7. Tra, in lại, hủy đơn hàng (02 → 10 → 11)

| | Hiện trạng | Đề xuất |
|---|---|---|
| Trang | 2 (02 → 10) + hộp 11 | 2 + hộp |
| Chạm, in lại đơn hôm nay | 3 (tile, dòng, In lại) | 3 |
| Chạm, tìm theo số điện thoại | 3 + gõ + «Lọc» 1 = 4 | 3 + gõ (tự lọc) |
| Gõ | 0–1 | 0–1 |
| Chỗ khó | **7 bộ lọc ngang hàng** (10:18–25), mặc định lùi 30 ngày (10:19) nên hiện đơn cũ; «Loại» luôn bắt chọn trước (10:18); «SĐT người mua (số cuối)» (10:22) viết tắt; cột «Người lập», «Khách», «Kênh», «Người mua» dày, 8 cột (10:28); trong hộp chi tiết 11 viết tắt «HSD» và mã tem 12 px, câu dài cuối hộp (11) | |

- **A27. Mặc định «Hôm nay» và chỉ 2 bộ lọc.** 10:17–26 (11:17–26): hàng nút «Hôm nay | 7 ngày | Tháng này» + ô «Số điện thoại người mua (số cuối)» (tự lọc khi gõ đủ 4 số). Các lọc «Loại», «Kênh», «Sản phẩm», «Đơn có quà», ngày tự chọn gập vào «Lọc thêm». −1 chạm (bỏ «Lọc») và bớt 5 ô. Căn cứ: TK 6.4 (lọc theo ngày, kênh, sản phẩm, SĐT, quà). **Không bỏ bộ lọc**, chỉ cất đi.
- **A28. Rút bảng còn 5 cột: Số phiếu, Giờ, Khách, Số lượng, Trạng thái.** 10:28: «Người lập», «Kênh», «Người mua» vào hộp chi tiết (11). Người mua vẫn che theo BR-24.
- **A29. Hộp chi tiết 11: ba nút «In lại», «Hủy đơn», «Đóng»; nút chính là «In lại».** 11 (dialog cuối): hiện nút chính xanh đang là «Đóng», đổi «In lại» xanh, «Đóng» viền thường; «Hủy phiếu» viền đỏ → mở xác nhận (A9). «HSD» → «Hạn dùng». Câu giải thích quyền hủy (11 `dlg-foot .muted`) rút còn «Chỉ hủy được đơn của mình trong ngày». Căn cứ: BR-06, BR-05.

### Việc ít dùng nên cất sang «Thêm»

- Trang chủ 02: ô nhỏ «Mẫu lưu», «Gán tem / hủy tem» (02:27–28, giai đoạn 2) gom vào ô lớn «Thêm» khi đủ ô; giai đoạn 1 chỉ còn 2 ô nhỏ nên chưa cần.
- Ghi chú phiếu nhập (03:53), mã đơn (A17), thông tin người mua phụ (A16), quà tặng (A20), kiểm kê (A23), bộ lọc đơn (A27).

## 2. Tổng hợp số bước

| Việc hằng ngày | Chạm trước | Chạm sau | Ô gõ trước → sau |
|---|---|---|---|
| V1 cân thu mua, 3 dòng | 14 | 10 | 3 → 3 |
| V1 cân thu mua, 1 dòng | 8 | 5 | 1 → 1 |
| V1b thêm người bán mới | 6 | 3–4 | 1 → 1 |
| V2 hủy phiếu nhập hôm nay | 2 (không xác nhận) | 3 (có xác nhận, an toàn) | 0 → 0 |
| V3 bán quế khô | 9 | 5 | 1 → 1 |
| V4a thành phẩm, khách lẻ cũ | 7 | 5 | 1 → 1 |
| V4b thành phẩm, khách lẻ mới | 10 | 5 | 3 → 2 |
| V4c thành phẩm, Shopee | 10 | 7 | 2 → 2 |
| V5 xem tồn kho | 1–2 | 1–2 | 0 → 0 |
| V6 kiểm kê | 3 + N | 3 + N | 0 → 0 |
| V7 tìm đơn theo số điện thoại | 4 + gõ | 3 + gõ | 1 → 1 |

## 3. Việc CẦN SẾP QUYẾT (gom một lần)

| # | Câu hỏi | Mặc định đề xuất | Tác động |
|---|---|---|---|
| Q-A1 | **A12.** Bán quế khô: có tự chọn sẵn lô cũ nhất không? | Có chọn sẵn, vẫn quét tem để đổi. | −1 chạm; rủi ro bán nhầm bao nếu không quét |
| Q-A2 | **A16.** Bán trực tiếp/Website có bắt nhập tỉnh/xã, địa chỉ để giao hàng? | Không bắt (BR-22 chỉ bắt tên + số điện thoại); cất vào «Thêm». | −2 chạm, −1 gõ |
| Q-A3 | **A15.** Khách và kênh bán là một: mỗi khách đã có kênh cố định (sàn = kênh sàn, đại lý, doanh nghiệp), riêng «Khách lẻ» chọn 1 trong 3 kênh. | Gộp; nếu Dev thấy một khách có nhiều kênh thì giữ chọn kênh trong «Thêm». | −2 chạm (đơn sàn) |

Các đề xuất khác chỉ đổi cách hiển thị, chữ, hoặc thứ tự bước, không đổi BR.

## 4. app.css đã sửa (`docs/mockup/de-xuat/man/app.css`)

Chỉ CSS, không đổi tên class, không đổi thứ tự màn. Thay đổi:

1. Dòng chú thích đầu file: ghi chuẩn mới (chữ ≥18/16, chạm ≥48, nút chính 72).
2. Biến mới: `--cta: #0f6b3a`, `--cta-dark: #0a4f2a`, `--touch: 48px`.
3. `button.primary, .btn.primary` (nút chính): màu xanh lá `--cta` (trước là nâu `--que`, trùng màu nút viền và tab). Hover `--cta-dark`. Trắng trên `--cta` tương phản ≈ 6,6:1. `.tile.primary` (ô lớn Trang chủ) giữ nâu vì là ô điều hướng, không phải nút.
4. `.totalbar button.primary`: min-height 72 px, chữ 1.3rem, min-width 240 px. Thanh dưới cộng khoảng an toàn đáy điện thoại (`env(safe-area-inset-bottom)`).
5. `button.small, .btn.small`: min-height 44 → 48 px, chữ 0,9 → 1rem. `button.link` (ví dụ «Sửa giá»): min-height auto → 48 px.
6. Chữ nhỏ tăng lên 0,9rem (≈16,2 px): `.tag` (trước 0,78rem ≈14 px), `.choice .sub` (0,85 → 0,9), `.tile .badge`, `.totalbar .figure .lbl`, `.kpi .l`, `.topbar .who`, `small`. Thêm `.banner, .muted, p {font-size:1rem}` (18 px) và `.muted.mono {font-size:.9rem !important}` (ghi đè mã tem 0,8rem viết trực tiếp trong màn, 09:57…), `.dlg-foot .muted` 1rem.
7. `input[type=checkbox]` 28 → 32 px; `label:has(> input[type=checkbox])` thành hàng cao ≥ 48 px, bấm cả chữ.
8. `tr.clickable td` padding dọc 0,8rem: dòng bấm được cao ≥ 48 px. `table input:not([type=checkbox])` min-height 48 px (ô đơn giá trong bảng 09:57 từng 44 px, `!important` vì viết trực tiếp trong màn).
9. `summary` cao ≥ 48 px, chữ đậm, có con trỏ bấm.
10. `:focus-visible` viền 3 px nâu (xanh đậm trên nút chính). Trước chỉ ô nhập có viền focus.
11. `@media (max-width: 600px)`: chân màn xếp dọc, nút chính tràn ngang, `main` chừa 11rem đáy, ô lớn Trang chủ 2 cột không `min-width`, nút chọn 2 cột.
12. `.flow > * { min-width: 0 }`: sửa lỗi tràn ngang trang 09 trên màn hẹp (bảng đẩy cột lưới rộng 534 px khi màn 492 px).
13. `button:disabled` độ mờ 0,45 → 0,5.

## 5. Đã kiểm

Ghép `<!--APPCSS-->` với `app.css` mới vào bản tạm (ngoài thư mục dự án) và mở bằng Edge không giao diện, đo bằng script (chiều cao phần tử bấm được, cỡ chữ tính toán, độ tràn ngang) ở cửa sổ 1280 px và ~492 px (Edge không hạ thấp hơn):

- **Đã mở và đo cả 20 màn cụm A** (02, 03, 03b, 04, 04b, 04c, 05, 05b, 06, 07, 08, 09, 09b, 09c, 09d, 10, 11, 12, 13, 14): không còn nút, link, ô nhập, dòng bấm được nào dưới 48 px; nút chính cuối màn 72 px (màn 09*), 64 px ở màn có nút «Xem», «Lọc» (nút chính nằm giữa trang, chưa đủ 72: sẽ về thanh dưới khi Dev làm A8/A27); màu nút chính `rgb(15,107,58)`.
- Không màn nào tràn ngang ở 492 px (09 từng tràn 548 px, đã sửa ở mục 4.12).
- **Chữ dưới 16 px:** chỉ còn trong 05b (phiếu in / tem xem trước, theo khổ giấy, ngoài chuẩn 0.2). Màn 11 từng còn 1 dòng 15,3 px, đã sửa (mục 4.6).
- **Chưa xem bằng mắt:** công cụ đọc ảnh không mở được thư mục ngoài dự án nên không đọc ảnh chụp; kiểm bằng số đo, chưa nhìn tổng thể. Giao diện tối không kiểm (dự án chưa hỗ trợ). Chưa đọc lại các màn cụm B, C với CSS mới, vì cả ba cụm dùng chung `app.css`: @Tuan, @Hoa nên đo lại cụm mình (script ở dưới).

Script đo: nhúng vào cuối màn tạm, duyệt `button, a.btn, a.tile, input, select, summary, tr.clickable, a.back` (cao < 47,5 px) và mọi phần tử có chữ (cỡ chữ < 16 px).

## 6. Việc cho Long, ngoài CSS

Đề xuất A1–A29 cần đổi markup/JS. Thứ tự dựng gợi ý (nhiều lợi nhất trước): A10 (bỏ màn 07), A1/A11 (gộp nút hàng), A2/A13 (tự thêm dòng khi Lưu), A15–A16 (người mua), A8/A27 (mặc định hôm nay), còn lại đổi chữ. Mọi đề xuất giữ nguyên trường BR bắt buộc.
