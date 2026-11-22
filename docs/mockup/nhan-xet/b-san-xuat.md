# Nhận xét mockup – cụm B: sản xuất

Người soát: Lan2 (BA) · task #21 · ngày 21/11/2026. Chỉ đọc; không sửa HTML hay `thiet-ke-chi-tiet.md`.

## Phạm vi và căn cứ

Bảy màn trong `docs/mockup/de-xuat/man/b-san-xuat/` (viết tắt đường dẫn là `b/`):

| STT | Màn | File |
| --- | --- | --- |
| 15 | Sản xuất / đóng gói (xưởng) | `b/15-prod-list.html` |
| 16 | Lệnh sản xuất – nháp | `b/16-prod-order.html` |
| 17 | Lệnh sản xuất – hoàn thành | `b/17-prod-done.html` |
| 18 | Gán tem / hủy tem | `b/18-labels.html` |
| 23 | Sản phẩm (chủ DN) | `b/23-products.html` |
| 24 | Tạo lệnh sản xuất (chủ DN) | `b/24-prod-owner.html` |
| 26 | Lô thành phẩm · thu hồi | `b/26-plots-lots.html` |

Căn cứ, theo thứ tự ưu tiên khi mâu thuẫn:

1. **Sổ tay** `D:\Sản phẩm quế\Công thức sản xuất Tinh dầu & Túi thơm Quế Văn Yên.pdf` (bản 2, 17/11/2026, 15 trang), viết tắt "sổ tay tr.N".
2. `docs/thiet-ke-chi-tiet.md` (viết tắt TK) mục 4 (bảng recipe, ingredient, production_order, product_lot, retained_sample, scent_trial), mục 7.2–7.5, BR-08..12, BR-20, AC-08..11.
3. `docs/lo-trinh-chuyen-doi-so.md` (viết tắt LT).

**Lưu ý nguồn.** Topic #2 đã sửa TK (công thức, phụ liệu, ủ, mã lô, lưu mẫu) khi mình soát. Mình chỉ đọc TK, không chắc nó đã chốt hẳn. Chỗ nào TK khớp sổ tay thì mình dẫn cả hai; chỗ nào chỉ dựa sổ tay thì ghi "căn cứ sổ tay". Giữa lúc soát, LT cũng được cập nhật: LT:13 và LT:108 đưa công thức, kho phụ liệu theo gram, ủ, lưu mẫu, thử lưu hương vào GĐ2; LT:171-175 bỏ mẫu mã lô cũ `TP-…`. Các dẫn LT dưới đây theo bản mới. Mockup chưa theo kịp LT.

Điều sổ tay thay đổi lớn nhất so với mockup: **sản phẩm là hỗn hợp tinh dầu pha theo gram rồi ủ 21–28 ngày** (sổ tay tr.1, tr.6), không phải quế khô đem sàng rồi đóng gói.

Mức: `critical` sai hẳn nghiệp vụ; `high` thiếu hoặc sai ở luồng chính; `medium` lệch hoặc thiếu ở luồng phụ; `low` dữ liệu mẫu, chữ.

## Tóm tắt

| Mã | Màn | Mức | Việc |
| --- | --- | --- | --- |
| B-01 | 16 | critical | Lệnh vẫn là "quét lô quế đem sàng", không có công thức và phụ liệu |
| B-02 | 24 | high | Tạo lệnh thiếu công thức, phương án TT1/TT2, cỡ mẻ |
| B-03 | 16 | high | Thiếu bước đưa phụ liệu vào theo gram thực tế |
| B-04 | 15, 16, 17 | high | Thiếu giai đoạn ủ (CURING) |
| B-05 | 15, 16, 17, 18, 24, 26 | high | Mã lô sai mẫu; mã sinh sai lúc |
| B-06 | 17 | high | Ví dụ "chưng cất" và hiệu suất 1,92% sai bản chất tinh dầu pha |
| B-07 | 23 | high | Sản phẩm không gắn công thức; danh sách và hạn dùng lệch sổ tay |
| B-08 | 17, 26 | high | Thiếu lưu mẫu |
| B-09 | (thiếu) | high | Màn thiếu: khai công thức |
| B-10 | (thiếu) | high | Màn thiếu: kho phụ liệu (danh mục, phiếu nhập, tồn theo lô) |
| B-11 | (thiếu) | high | Màn thiếu: theo dõi ủ và ngửi kiểm tra |
| B-12 | 26 | medium | Giá vốn chỉ tính quế, hiệu suất không hợp tinh dầu pha |
| B-13 | 26 | medium | Thiếu chi tiết mẻ (sổ ghi lô) |
| B-14 | (thiếu) | high | Màn thiếu: thử lưu hương 28 ngày (LT đã xếp vào GĐ2) |
| B-15 | 16, 23 | medium | Số liệu túi thơm lệch sổ tay; quy cách 50 g |
| B-16 | 24, 23 | medium | Trà có trong luồng sản xuất ở GĐ2, trái lộ trình |
| B-17 | 15, 24 | low | Cùng một lệnh, số lô đã quét khác nhau |
| B-18 | 18 | low | Màn gán tem đúng; chỉ thêm ghi chú |

Điểm cần sếp quyết đã gắn **[SẾP QUYẾT]**: B-06, B-07, B-12, B-15 (B-10 chỉ còn câu hỏi giá vốn ở B-12).

---

## Lỗi trên màn hiện có

### B-01 · Màn 16 Lệnh sản xuất · critical
**Sai gì.** Lệnh Túi thơm quế 50 g chỉ có 3 bước: (1) quét tem lô quế "đem sàng", (2) chọn Loại 1/2/3 sau sàng, (3) nhập số cân kg và số lượng. Không có công thức, phụ liệu, ủ. Tức vẫn là mô hình sàng/đóng gói quế khô. Sản phẩm thật là tinh dầu và túi thơm pha từ gram: túi vỏ quế 25 g = vỏ quế cắt hạt 12 g + dăm gỗ 8 g + hạt thạch cao 5 g + dung dịch tẩm 2,5 g (sổ tay tr.12); tinh dầu = 3–4 loại tinh dầu pha theo % khối lượng (tr.6–8).

**Căn cứ.** `b/16-prod-order.html:20` ("Quét tem các lô nguyên liệu đem sàng"), `:29` ("Chọn loại sau sàng lọc"), `:33-39` (kg, số lượng, ngày, hạn). Sổ tay tr.1, tr.6–8, tr.12. TK 7.2: "Một lệnh có 4 bước: chọn công thức và cỡ mẻ → đưa nguyên liệu vào (cân từng gram) → ủ → nhập đầu ra"; bước chọn loại chỉ hiện cho lệnh PRODUCT có lô quế đưa thẳng vào.
**Đề xuất.** Dựng lại màn theo 4 bước của TK 7.2:
1. Công thức và cỡ mẻ (xem B-02).
2. Nguyên liệu: bảng thành phần công thức với gram gợi ý và ô gram thực tế (xem B-03); lô quế chỉ có khi công thức cần quế thô (sơ chế vỏ quế, chưng dầu).
3. Ủ (xem B-04).
4. Đầu ra.

Bước "Chọn loại sau sàng lọc" chỉ hiện với lệnh có lô quế đưa thẳng vào. Túi thơm lấy vỏ quế từ bán thành phẩm VQH nên **không hiện** bước này (TK mục 4, công thức `TUI` và `SC-VQH`).

### B-02 · Màn 24 Tạo lệnh sản xuất (chủ DN) · high
**Sai gì.** Form chỉ có Sản phẩm, Ngày, Ghi chú. Thiếu công thức và cỡ mẻ:
- Công thức: tinh dầu có 6 công thức (QC1, QC2, RQ1, RQ2, TQ1, TQ2) cho cùng một sản phẩm "tinh dầu 10 ml" (sổ tay tr.6–8). Hương nền chọn TT1 hoặc TT2 (tr.9). Sáp, viên, dung dịch tẩm cũng chọn một trong hai (tr.9–10).
- Cỡ mẻ: sổ tay cho gram theo mẻ 100 ml và 1 lít (tr.6).
- Không chọn được bán thành phẩm cần làm (hương nền TT1/TT2, dung dịch tẩm, dầu quế ủ, vỏ quế sơ chế).

**Căn cứ.** `b/24-prod-owner.html:20-25`. Sổ tay tr.6–10. TK 7.2 "Tạo lệnh (OWNER)": chọn sản phẩm hoặc bán thành phẩm, công thức (phiên bản ACTIVE), nhóm lựa chọn, `target_batch_g`.

**Đề xuất.** Thêm vào form:
- Ô "Làm gì": Sản phẩm / Bán thành phẩm.
- Công thức: chọn từ danh sách, mặc định phiên bản ACTIVE khớp `recipe_code`.
- Nếu công thức có nhóm lựa chọn: nút chọn TT1 hoặc TT2.
- Cỡ mẻ (gram), mặc định bằng mẻ chuẩn, kèm dòng xem trước lượng cân từng thành phần. Ví dụ QC1 cỡ 897,2 g cho 314,0 / 89,7 / 493,5 g (sổ tay tr.6).

### B-03 · Màn 16 · Thiếu đưa phụ liệu vào theo gram · high
**Sai gì.** Không có chỗ quét tem lô phụ liệu và gõ gram thực tế. Sổ tay bắt buộc: cân điện tử 0,01 g, TARE trước mỗi nguyên liệu, sai số cho phép ±0,05 g, lỡ tay thì ghi số thật, không múc bớt (tr.5 quy tắc 1–3), ghi ngay vào sổ lô mã lô, ngày, gram thực tế từng nguyên liệu (tr.5 quy tắc 5, tr.14 C.3). Mockup chỉ có lô quế tính kg "không cân lại".

**Căn cứ.** `b/16-prod-order.html:20-27`. TK 7.2 "Đưa nguyên liệu vào": lô phụ liệu theo gram, cảnh báo vàng lệch quá ±0,05 g, từ chối khi sai phụ liệu, hết tồn, quá hạn; cảnh báo khi tinh dầu mua ngoài chưa có COA (sổ tay tr.4).

**Đề xuất.** Mỗi dòng công thức hiện: tên phụ liệu, gợi ý (g), ô quét tem lô, ô gram thực tế, trạng thái (đủ / thiếu / lệch). Gợi ý lô có hạn gần nhất. Banner vàng khi lệch quá 0,05 g, banner cam khi lô chưa có COA. Dòng bột màu có nhãn "tùy chọn". Nút "+ Thêm dòng ngoài công thức" cho đồ trang trí sáp 3–5 g (tr.10). Đổi tiêu đề bước 1 thành "Quét tem lô quế (cả lô, không cân lại)" để phân biệt với phụ liệu cân từng gram.

### B-04 · Màn 15, 16, 17 · Thiếu giai đoạn ủ · high
**Sai gì.** Vòng đời lệnh trong mockup chỉ Nháp → Hoàn thành. Sổ tay: pha xong phải ủ nhiều ngày rồi lọc, ngửi kiểm tra, đóng chai.

| Đối tượng | Ủ | Sổ tay |
| --- | --- | --- |
| Tinh dầu dầu nhẹ / đậm đà | 21 / 28 ngày, lắc chai 3 ngày một lần | tr.6 A.1 bước 4 |
| Hương nền TT1/TT2 | tối thiểu 14 ngày | tr.9 |
| Dung dịch tẩm | 48 giờ | tr.9–10 |
| Sáp thơm | 14 ngày | tr.10 |
| Viên thạch cao | 7 ngày sau tẩm | tr.12 |
| Túi vỏ quế | 5–7 ngày | tr.13 |
| Dầu quế | 4–6 tuần | tr.8 A.5 |

**Căn cứ.** `b/16-prod-order.html:17` (tag "Nháp"), `b/17-prod-done.html:17` (tag "Hoàn thành"), `b/15-prod-list.html:19` (thẻ lệnh chỉ có mã, ngày, số lô). TK 7.2: trạng thái CURING, nút "Đã pha xong, bắt đầu ủ", "Còn N ngày", "Ủ thêm" (7 ngày), `cure_check_note`.

**Đề xuất.**
- Màn 16: nút "Đã pha xong, bắt đầu ủ"; sau khi bấm hiện "Ngày bắt đầu ủ / Ngày sớm nhất xong ủ", tem mẻ để dán lọ ủ, dòng nguyên liệu khoá.
- Tag trạng thái thêm "Đang ủ".
- Màn 15 và 24: thẻ lệnh CURING hiện mã công thức, ngày dự kiến xong, chữ xám "Còn N ngày".
- Màn 17: nút "Hoàn thành" chỉ sáng khi đủ ngày; chưa đủ thì hiện "Mẻ QC1-261117-01 còn 6 ngày mới đủ ủ".

Màn theo dõi chi tiết xem B-11.

### B-05 · Màn 15, 16, 17, 18, 24, 26 · Mã lô sai mẫu · high
**Sai gì.** Lô thành phẩm trên mockup là `TP-TD10-2611-02`, `TP-TD10-2611-01` (SKU + tháng + số thứ tự). Sổ tay quy định mã lô `[Mã công thức]-[Năm tháng ngày]-[Số mẻ]`, ví dụ `QC1-261117-01` (tr.14 C.3). `TD10` là SKU, không cho biết công thức nào (một SKU tinh dầu 10 ml có 6 công thức), mất đúng điều sổ tay muốn: tra mã lô là biết mẻ dùng công thức nào và ai làm (tr.14). Hai lô -01 và -02 cùng ngày 20/11 nên mã phải có phần ngày.

**Căn cứ.** `b/15-prod-list.html:21`; `b/17-prod-done.html:46`; `b/18-labels.html:21`; `b/24-prod-owner.html:31`; `b/26-plots-lots.html:19`. TK BR-20 và `product_lot.code` (`QC1-261117-01`, ngày pha = ngày bắt đầu ủ).

**Đề xuất.**
- Đổi mọi mã lô mẫu sang `QC1-261120-01`, `QC1-261120-02`. Tem lô phụ liệu theo mẫu `Q-2611-01`.
- Màn 26: thêm cột "Công thức" (hoặc gộp vào tên) và "Ngày pha" bên cạnh "Ngày SX" (TK `blend_date` khác `mfg_date`).
- Màn 16/17: nói rõ mã lô sinh khi **bắt đầu ủ**, không phải lúc hoàn thành; màn 17 chỉ hiện lại mã đã có.
- `b/17-prod-done.html:46` "Đã tạo lô thành phẩm" đổi thành "Mẻ … đã ủ xong, đã tạo lô thành phẩm".

### B-06 · Màn 17 · Ví dụ mẻ "chưng cất" và hiệu suất 1,92% · high · [SẾP QUYẾT]
**Sai gì.** Màn 17 là lệnh "Tinh dầu quế Văn Yên 10 ml", ghi chú "Mẻ chưng cất số 2": 125 kg nguyên liệu → 2,4 kg thành phẩm → 200 chai, hiệu suất 1,92%, hoàn thành ngay trong ngày lệnh (20/11/2026). Ba chỗ lệch sổ tay:
1. Sổ tay **không** có bước chưng cất. Dầu quế là nguyên liệu nhận từ nguồn gia đình, đem lắng, thoát khí, ủ kín 4–6 tuần, lọc (tr.8 A.5). Sản phẩm 10 ml là hỗn hợp pha rồi ủ 21–28 ngày (tr.6), không xong trong một ngày.
2. 1,92% là hiệu suất chưng dầu từ quế, chỉ có nghĩa với bán thành phẩm dầu quế (TK 7.4: tính trên lệnh làm ra nó). Gắn vào chai tinh dầu pha là sai nghĩa; TK để `yield_pct` NULL khi lô không có quế.
3. Số lệch nhẹ: 100 ml pha ≈ 89,7–92,2 g và ra khoảng 9 chai 10 ml (tr.5, tr.6 A.2), nên 200 chai ≈ 2,0 kg, không phải 2,4 kg.

**Căn cứ.** `b/17-prod-done.html:17` ("Mẻ chưng cất số 2"), `:46` (125 kg, 2,4 kg, 1,92%, 200 chai, ngày SX = ngày lệnh). Sổ tay tr.5, 6, 8. TK mục 4 (cuối phần recipe): công thức chưng "không seed" cho đến khi chủ DN chốt.

**Đề xuất.**
- Đổi ghi chú thành "Mẻ QC1 dầu nhẹ" hoặc tương tự. Với lệnh PRODUCT dùng phụ liệu, bỏ ô "hiệu suất", thay bằng: tổng gram phụ liệu đưa vào, số chai, ngày pha, ngày xong ủ.
- Giữ KPI hiệu suất chỉ cho lệnh làm bán thành phẩm từ quế.
- Ngày SX mẫu cách ngày pha 21 ngày (ví dụ pha 30/10, xong 20/11).

**[SẾP QUYẾT]** Xưởng tự chưng dầu quế từ vỏ quế, hay chỉ nhận dầu từ gia đình? Nếu chưng: thêm lệnh INTERMEDIATE "chưng" (lô quế → dầu mới chưng) và sổ tay phải bổ sung quy trình. Nếu không: cây truy xuất dừng ở "nguồn gia đình" và mockup bỏ chữ "chưng cất". Mình đề xuất theo sổ tay (không chưng) cho đến khi sếp nói khác.

### B-07 · Màn 23 Sản phẩm · high · [SẾP QUYẾT]
**Sai gì.**
1. Không có cột công thức mặc định, trong khi lệnh cần chọn công thức theo sản phẩm (TK `product.recipe_code`).
2. Danh sách không khớp sổ tay. Sổ tay có: tinh dầu khuếch tán (6 công thức × chai 10/30 ml), tinh dầu Quế Văn Yên 100% chai 10 ml, sáp thơm, viên thạch cao + chai refill 10 ml, túi vỏ quế (tr.5–13). Mockup có TD10 "Tinh dầu quế Văn Yên 10 ml", TT50, TRA100, THIEP; không rõ TD10 là khuếch tán hay quế 100%, không có sáp, viên, refill.
3. Hạn dùng: TD10 24 tháng, TT50 12 tháng. Sổ tay: khuếch tán 18 tháng "do có nhiều cam ngọt" (tr.6), quế 100% 24 tháng (tr.8), sáp/viên/túi **không ghi** (TK 7.2 để chủ DN điền). Số 12 tháng của TT50 không có căn cứ.
4. Thiếu trường cách dùng và cảnh báo in nhãn: "không bôi lên da, không uống, để xa trẻ em và thú cưng"; liều 4–5 giọt (dầu nhẹ) hoặc 3–4 giọt (đậm đà) cho 100 ml nước (tr.6, tr.14–15).

**Căn cứ.** `b/23-products.html:23`. Sổ tay tr.5–15. TK `product` (`recipe_code`, `shelf_life_months`, `usage_md`); TK mục 13 "Danh sách sản phẩm đợt 1, SKU và quy cách" còn mở.

**Đề xuất.**
- Thêm cột "Công thức" ở danh sách và ô chọn trong form sửa.
- Đổi dữ liệu mẫu: `TD-QC1-10` "Tinh dầu Quế Cam dịu nhẹ 10 ml" (18 tháng), `Q100-10` "Tinh dầu Quế Văn Yên 100% 10 ml" (24 tháng). Giữ một sản phẩm túi vỏ quế với hạn bỏ trống hoặc "chờ chủ DN".
- Hạn dùng sáp/viên/túi hiện "chưa có" thay vì số tự bịa.
- Thêm "Cách dùng và cảnh báo".

**[SẾP QUYẾT]** (a) Danh sách sản phẩm đợt 1: bán cả 6 mùi hay chọn trước vài mùi? (b) Hạn dùng sáp thơm, viên thạch cao, túi vỏ quế. Cả hai là câu hỏi mở của TK mục 13.

### B-08 · Màn 17, 26 · Thiếu lưu mẫu · high
**Sai gì.** Sau khi hoàn thành lệnh, màn 17 đi thẳng sang gán tem. Sổ tay: "Lưu mẫu 1 chai 10 ml mỗi lô trong 12 tháng" (tr.6 A.1 bước 8). Màn 26 không có cột hay nút nào về mẫu lưu.

**Căn cứ.** `b/17-prod-done.html:46` (chỉ có nút "Sang bước gán tem"), `b/26-plots-lots.html:18` (cột). TK 7.5: hỏi "Đã lấy chai lưu mẫu chưa?" kèm vị trí; chai lưu mẫu không dán tem và không tính vào `quantity`; danh sách "Lô chưa lưu mẫu"; màn "Mẫu lưu"; nút "Xem mẫu lưu" khi tra cứu.

**Đề xuất.**
- Màn 17: thẻ kết quả thêm khối "Chai lưu mẫu": ô vị trí (tủ, kệ), nút Lưu; chưa lưu thì hiện "Chưa lưu mẫu", **không chặn** gán tem.
- Màn 26: cột "Mẫu lưu" (Giữ đến dd/mm/yyyy / Chưa lưu / Đã hủy). Lô RECALLED không cho hủy mẫu.
- Màn mới "Mẫu lưu" (OWNER, xưởng xem): lô, vị trí, ngày lưu, giữ đến, trạng thái; còn dưới 30 ngày tô cam; nút "Hủy mẫu" khi hết hạn.
- Số chai 200 trên màn 17 ghi rõ là số bán được, chưa gồm chai lưu mẫu.
- Chỉ áp cho công thức có `retain_months` (6 công thức tinh dầu khuếch tán). Quế 100%, sáp, viên, túi sổ tay chưa nói, nên không hiện khối này.

### B-12 · Màn 26 · Giá vốn và hiệu suất · medium · [SẾP QUYẾT]
**Sai gì.** Cột "Giá vốn NL" hiện 28.125 đ/chai cho tinh dầu pha từ 3–4 loại tinh dầu. Con số chỉ là tiền quế chia số chai (125 kg × 45.000 đ ÷ 200). Phần lớn giá thành tinh dầu pha là cam, tuyết tùng, hoắc hương, hồi (sổ tay tr.4), nên số này dễ bị hiểu là giá vốn thật. Cột "Hiệu suất" cũng không có nghĩa với lô chỉ dùng phụ liệu.

**Căn cứ.** `b/26-plots-lots.html:18-19`. TK BR-10: "Chỉ gồm tiền nguyên liệu quế; chi phí bao bì, phụ liệu, nhân công nằm ngoài phạm vi." TK mục 13: "Giá vốn có cần tính thêm bao bì và phụ liệu không" còn mở.

**Đề xuất.** Ngắn hạn: đổi tên cột thành "Giá quế / đơn vị", hiện "—" ở lô chỉ dùng phụ liệu; cột Hiệu suất hiện "—" khi không có quế (TK `yield_pct` NULL). Dài hạn tuỳ quyết định.

**[SẾP QUYẾT]** Có tính giá phụ liệu vào giá vốn không? Nếu có, phiếu nhập phụ liệu cần cột đơn giá (xem B-10).

### B-13 · Màn 26 · Thiếu chi tiết mẻ (sổ ghi lô) · medium
**Sai gì.** Màn 26 chỉ một dòng mỗi lô, bấm mã lô nhảy sang tra cứu. Sổ ghi lô của sổ tay (tr.14 C.3) mỗi mẻ một dòng gồm: mã lô, ngày pha, công thức, lô tinh dầu quế dùng, số gram thực tế (đính kèm phiếu cân), ngày xong, số lượng thành phẩm, người làm, ghi chú. Mockup chưa có chỗ nào xem lại mẻ.

**Căn cứ.** `b/26-plots-lots.html:19`. Sổ tay tr.14 C.3. TK 7.4 tra cứu ngược (thuộc cụm C, màn 27).

**Đề xuất.** Thêm màn "Chi tiết mẻ" mở từ màn 26: đầu trang công thức, ngày pha, ngày xong ủ, người làm; bảng gram thực tế so với gợi ý theo từng lô phụ liệu; kết quả ngửi kiểm tra; số lượng; trạng thái mẫu lưu; nút Thu hồi. Dùng chung dữ liệu với màn tra cứu 27, cụm C xem lại để khỏi trùng.

### B-15 · Màn 16, 23 · Số liệu túi thơm lệch sổ tay · medium · [SẾP QUYẾT]
**Sai gì.** Lệnh mẫu: 52,5 kg vỏ quế → 9,8 kg thành phẩm → 180 túi, quy cách "50 g". Sổ tay: túi vỏ quế **25 g**; 40 túi dùng 480 g vỏ quế (12 g/túi), phần còn lại là dăm gỗ, hạt thạch cao, dung dịch tẩm (tr.12). Theo sổ tay 52,5 kg vỏ quế ra khoảng 4.000 túi, không phải 180. Mockup cũng chưa có đơn vị "viên" cho viên thạch cao hay "tấm" cho sáp.

**Căn cứ.** `b/16-prod-order.html:25-26` (30 + 22,5 = 52,5 kg), `:35` (9,8), `:36` (180 túi); `b/23-products.html:23` (TT50, 50 g). Sổ tay tr.12.

**Đề xuất.** Đổi số mẫu theo công thức TUI (mẻ 40 túi: VQH 480 g, DG 320 g, HT 200 g, DDT 100 g, tổng 1.100 g). Cho `unit` khác nhau theo sản phẩm (chai / túi / viên / tấm).

**[SẾP QUYẾT]** Quy cách túi thơm: 25 g theo sổ tay hay 50 g như mockup (chưa có căn cứ)? Nếu thêm sản phẩm 50 g thì cần công thức riêng.

### B-16 · Màn 24, 23 · Trà ở luồng sản xuất GĐ2 · medium
**Sai gì.** Màn 24 cho chọn "Trà quế Văn Yên 100 g (TRA100)" để tạo lệnh. LT chốt trà và bột là thực phẩm, chỉ mở bán sau khi có hồ sơ ATTP, nằm ở GĐ4 (1–6/2028). Sổ tay không có công thức trà. Lệnh sản xuất thuộc GĐ2 (5–9/2027), "lô thành phẩm đầu tiên (tinh dầu, túi thơm)".

**Căn cứ.** `b/24-prod-owner.html:21` (option TRA100); `b/23-products.html:22` (ghi chú trà, bột), `:23` (dòng TRA100 Nháp). LT:13, LT:15, LT:68–69. TK BR-14, AC-17.

**Đề xuất.** Màn 24 chỉ liệt kê sản phẩm có `recipe_code` hoặc đang ACTIVE; TRA100 mờ đi kèm nhãn "GĐ4 – chờ giấy tờ ATTP". Màn 23 giữ dòng Trà để minh hoạ BR-14 nhưng ghi chú giai đoạn sau.

### B-17 · Màn 15 và 24 · Dữ liệu không nhất quán · low
**Sai gì.** Cùng lệnh LSX-2611-003: màn 15 ghi "1 lô đã quét", màn 24 ghi "2 lô đã quét", màn 16 liệt kê 2 lô (NL-2611-0002 và NL-2611-0006).

**Căn cứ.** `b/15-prod-list.html:19`, `b/24-prod-owner.html:29`, `b/16-prod-order.html:25`.

**Đề xuất.** Thống nhất dữ liệu mẫu. Nếu làm theo B-01 thì thẻ đổi thành "đã nhập 3/4 thành phần" hoặc "ngày xong ủ dự kiến …".

### B-18 · Màn 18 Gán tem · low (ghi nhận)
Màn khớp TK 7.3 và BR-12: quét tem đầu rồi tem cuối, thanh tiến độ "Đã gán 150 / 200", hủy tem có 4 lý do (`b/18-labels.html:28-37`). Số liệu cùng màn 26 khớp (145 trong kho + 5 đã xuất = 150 đã gán). Chỉ cần thêm:
- Dòng nhắc "Chai lưu mẫu không dán tem" (xem B-08).
- Mã lô đổi theo B-05.
- Chưa có nhãn thành phẩm in ra (mã lô, ngày SX, hạn dùng, cách dùng, cảnh báo; sổ tay tr.15). Nếu sếp muốn phần mềm in nhãn này thì thêm vào cụm in (màn 35), nếu không thì bỏ.

---

## Màn còn thiếu theo sổ tay

Chưa có màn nào trong 40 màn mockup nhắc tới phụ liệu, công thức, ủ, lưu mẫu hay thử lưu hương (mình grep "phụ liệu" trong `de-xuat/man/*/*.html`: không có kết quả). Dưới đây là trường cần có. Màn nào thuộc cụm A (kho) thì Lead gộp với kết quả cụm A.

### B-09 · Khai công thức (OWNER) · high
Căn cứ: sổ tay tr.6–13; TK mục 4 bảng `recipe`, `recipe_item` và bảng seed.
- **Danh sách công thức:** mã, tên, đầu ra (sản phẩm / bán thành phẩm), phiên bản, mẻ chuẩn (g), ngày ủ tối thiểu, trạng thái (nháp / đang dùng / ngừng). Mỗi mã chỉ một phiên bản đang dùng.
- **Form:** mã*, tên*, đầu ra*, (nếu bán thành phẩm) phụ liệu làm ra*, mẻ chuẩn (tự cộng từ thành phần), nhãn mẻ ("mẻ 100 ml ≈ 89,72 g"), ủ tối thiểu*, ủ tối đa (chỉ tham khảo), lưu mẫu (tháng), ghi chú bước làm và nhiệt độ (ví dụ sáp đổ khuôn 70–72 °C, tr.10).
- **Bảng thành phần:** phụ liệu*, gram trên mẻ chuẩn*, % khối lượng (tự tính, khớp cột % của sổ tay, không nhập), nhóm lựa chọn (TT1 hoặc TT2), tùy chọn (bột màu).
- **Kiểm tra khi lưu:** thành phần là bán thành phẩm phải có công thức riêng; phiên bản đang dùng không sửa tại chỗ mà nhân bản thành phiên bản mới. Dữ liệu mẫu: QC1 = tuyết tùng 31,40 g + quế 8,97 g + cam ngọt 49,35 g = 89,72 g (tr.6).

### B-10 · Kho phụ liệu (danh mục, phiếu nhập, tồn theo lô) · high
Căn cứ: sổ tay tr.4 (nguyên liệu, COA từng lô, cam ngọt nên mua đủ dùng 3–6 tháng); TK mục 4 `ingredient`, `ingredient_receipt`, `ingredient_lot`, `production_ingredient`.
- **Danh mục phụ liệu:** mã (Q, QM, CAM, TTV, HH, HOI, DPG, SD, SO, TC, DG, HT, VQH…), tên, loại, tỷ trọng (g/ml, chỉ tham khảo), cần COA, hạn mặc định, có theo dõi tồn không (nước sạch thì không).
- **Phiếu nhập phụ liệu:** nơi bán, SĐT, ngày; dòng gồm phụ liệu*, gram*, số lô trên nhãn nhà cung cấp, hạn, đơn giá (nếu sếp chọn tính giá), ảnh COA. In tem lô (QR chứa mã dạng `CAM-2611-01`). Nhập "Nguồn gia đình" cho dầu quế nhận từ gia đình.
- **Tồn kho phụ liệu:** theo lô: mã lô, phụ liệu, gram còn / gram nhập, hạn, nguồn (mua ngoài hay lệnh nào làm ra), trạng thái; tô cam lô sắp hết hạn, đỏ lô quá hạn.
- Hủy lệnh DRAFT hoặc bỏ dòng thì gram cộng lại vào lô (TK 7.2).

Giai đoạn: GĐ2 (LT:108). Còn mở một câu ở B-12: phiếu nhập phụ liệu có cột đơn giá để tính giá vốn không. Chưa quyết thì mockup không có cột đơn giá.

### B-11 · Theo dõi ủ và ngửi kiểm tra · high
Căn cứ: sổ tay tr.6 A.1 bước 4 và 6, tr.8 A.5; TK 7.2 (bắt đầu ủ, ủ thêm, `cure_check_note`).
- **Danh sách đang ủ** (trang chủ xưởng và chủ DN): mã mẻ, công thức, ngày bắt đầu, ngày sớm nhất xong, "Còn N ngày", nhắc "lắc chai 3 ngày một lần" cho tinh dầu (tr.6).
- **Chi tiết mẻ đang ủ:** lịch lắc chai (tick từng lần); nút "Ngửi kiểm tra".
- **Ngửi kiểm tra** (cuối ủ): nhập kết quả nhúng que thử, ngửi ngay, sau 1 giờ, sau 4 giờ, so với mẫu chuẩn (tr.6); kết luận "đạt" hoặc "còn gắt, ủ thêm 7 ngày" (tr.6). Nút "Ủ thêm" lùi ngày xong và ghi lý do.
- **OWNER bỏ qua kiểm tra ngày ủ:** bắt buộc ghi lý do (TK 7.2).

### B-14 · Thử lưu hương 28 ngày · high
Căn cứ: sổ tay tr.13 C.1, tr.14 C.2; TK 7.5 và bảng `scent_trial*`.
- **Danh sách đợt thử:** mã (TL-2611-01), công thức, mục tiêu ("so dung dịch tẩm 25% / 35% / 45%"), ngày bắt đầu, trạng thái.
- **Mẫu:** mỗi biến thể 3 mẫu giống nhau ở 3 nơi (tủ quần áo đóng kín, ô tô, phòng thường): mã dán mẫu, nhãn biến thể.
- **Ghi kết quả:** lưới ngày 0, 1, 3, 7, 14, 21, 28; mỗi ô gồm khối lượng (g, cân 0,01 g, cùng giờ trong ngày) và điểm từng người ngửi (5–7 người): cường độ 1–5, độ dễ chịu 1–5, ghi chú. Người ngửi chấm riêng, không thấy điểm người khác. In được phiếu chấm điểm (tr.14 C.2).
- **Đánh giá:** 4 tiêu chí (ngày 1 cường độ ≤ 4; ngày 28 trong tủ kín cường độ ≥ 2,5; độ dễ chịu TB ≥ 3,5; khối lượng mất 3 ngày đầu ≤ 1/3 tổng sau 28 ngày). Đạt cả 4 là PASS. Nhập thời gian lưu hương đo thật; **chỉ khi có số này mới được in lên bao bì** (tr.13).

Giai đoạn: GĐ2 (LT:13, LT:236). Chỉ sáp thơm, viên thạch cao, túi vỏ quế dùng đợt thử này. Tinh dầu khuếch tán thử theo cách khác (chạy máy 30 phút, chấm ở phút 5, 30, 60; tr.13) mà TK chưa lưu; nếu cần màn riêng thì ghi vào câu hỏi mở.

---

## Việc cần phối hợp

- **Cụm A:** B-10 (kho phụ liệu) nằm giữa hai cụm; gộp một chỗ khi tổng hợp `nhan-xet.md`.
- **Cụm C:** màn 19 (trang chủ chủ DN) nên có thẻ "Lô chưa lưu mẫu", "Đang ủ", "Mẫu sắp hết hạn lưu" (B-04, B-08). Màn 27 (tra cứu) cần hiện chuỗi phụ liệu và nút "Xem mẫu lưu" (TK 7.4, 7.5). Màn 25 (cuộn tem) và 35 (in tem) chưa có tem mẻ cho lọ ủ.
- **Tài liệu:** LT đã theo sổ tay (LT:108, LT:125). Mình chưa kiểm lại `tom-tat.md` sau cập nhật của topic #2.
- **Nếu TK đổi:** các điểm dẫn TK 7.2, 7.5 và bảng recipe là bản đọc ngày 21/11/2026. Nếu topic #2 đổi, đối chiếu lại; sổ tay vẫn là căn cứ gốc.
