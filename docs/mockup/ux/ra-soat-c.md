# Soát UX cụm C: quản lý, in, QR, báo cáo, admin (task #34)

Căn cứ: tin #460 của sếp (người dùng kém CNTT, bước ngắn nhất, nhanh) và chuẩn chung #461. Chưa có `ux/ra-soat-a.md` nên dùng chuẩn mặc định: **vùng chạm ≥ 48 px, chữ ≥ 16 px**.

Ký hiệu đường dẫn (đều dưới `docs/mockup/de-xuat/man/`): **C/** = `c-quan-ly-in-qr/`, **A/** = `a-nhap-xuat-kho/`, **B/** = `b-san-xuat/`, **CSS** = `app.css`. Số sau dấu `:` là số dòng thật của file.
Cách đếm: «chạm» gồm bấm, chạm, quét một tem và bấm «In» trong hộp thoại in của trình duyệt. «Ô gõ» là ô người dùng phải gõ chữ hoặc số (ô đã điền sẵn đúng không tính). «Màn» đếm cả màn in và hộp thoại.

---

## 0. Tóm tắt (đọc phần này là đủ)

1. **Hiện nay nhân viên không có đường nào để in tem.** In tem lô (C/42) và in cuộn tem (C/35) chỉ đi qua «Cuộn tem QR» (C/25), mà màn đó là của chủ (`data-role="OWNER"`, C/25:10; thiết kế mục 3 bảng quyền chỉ cho OWNER «Tạo cuộn tem, in tem»). Trang chủ thủ kho (A/02:24-28) chỉ có «Gán tem / hủy tem». Màn «Lệnh sản xuất xong» (B/17:52) chỉ có nút sang gán tem, không có nút in.
2. **Tem lô thì nút cứng một lô:** C/25:26 chỉ có «In nhãn lô Q100-261120-02». Có lô mới là không có nút.
3. **Luồng ngắn nhất cho tem** (từ lô vừa xong): hiện **≈ 9 chạm, 5 màn, 1 ô gõ** → phương án A (giữ nghiệp vụ) **≈ 5 chạm** → phương án B (CẦN SẾP QUYẾT) **2 chạm, 0 ô gõ**.
4. **Trang chủ chủ** (C/19) có 4 ô to + 3 băng báo + 9 ô nhỏ + chữ «GĐ2» (tên nội bộ của dự án, người dùng không hiểu). Gom lại còn 4 ô to + «Việc cần xử lý» + 3 ô hay dùng + 1 ô «Quản lý khác».
5. **Khai người bán** (C/22:32) hiện ≈ 16 thao tác, 13 ô trong một hộp thoại. Tách hai tầng: «Thêm nhanh» 3 ô (≈ 6 thao tác), đồi/ảnh bổ sung sau.
6. **Báo cáo** (C/30): bỏ nút «Xem», thêm nút ngày «Tháng này / Tháng trước / 3 tháng», đổi chữ «NL», «Nhóm».
7. **Vùng chạm dưới 48 px** còn ở: nút `small` 44 px (CSS:79), ô «từ … đến …» trong bảng cuộn tem (C/25:25), nút ✕ đóng hộp thoại (C/22:32). Chữ dưới 16 px: nhãn «GĐ2» 12,6 px (C/19:31-35), chữ phụ trên trang QR công khai 13,5 – 15 px (C/36:28, :33, :34).
8. **Phát hiện ngoài phạm vi, báo để người phụ trách sửa:** C/28:19 và C/29:19 còn «Túi thơm … **50 g**» (đã chốt 25 g). C/36:82 và C/37:83 hiện cả chữ «[ví dụ minh hoạ, chưa có thật]» trên trang công khai.

---

## 1. Việc thường làm: tách nhân viên hằng ngày và quản lý ít dùng

| Nhóm | Việc | Ai làm | Bao lâu một lần | Màn |
|---|---|---|---|---|
| **Hằng ngày** (nhân viên) | Dán tem lên chai (gán đoạn tem vào lô) | Thủ kho | mỗi lô | B/18 |
| | In phiếu nhập sau khi cân | Thủ kho | mỗi phiếu | A/05, A/05b → C/33 |
| | In phiếu xuất / đơn hàng | Thủ kho | mỗi đơn | A/11 → C/34 |
| | In tem lô nguyên liệu (kèm phiếu nhập) | Thủ kho | mỗi phiếu | C/33 |
| | **In tem lô thành phẩm và tem từng chai** | **hiện chỉ chủ, đúng ra là việc của thủ kho** | mỗi lô | C/25, C/42, C/35 |
| **Chủ, hằng ngày – hằng tuần** | Cập nhật bảng giá | Chủ | mỗi ngày | C/20 |
| | Duyệt người bán do xưởng thêm nhanh | Chủ | khi có | C/19:26 → C/21 → C/22b |
| | Lưu mẫu cho lô mới | Chủ / thủ kho | mỗi lô | C/19:24 → B/26c |
| | Tra cứu một mã (QR, lô, phiếu) | Chủ | khi có khiếu nại | C/27 |
| | Xem báo cáo | Chủ | tuần / tháng | C/30 |
| **Ít dùng** (quản lý) | Khai danh mục: địa bàn, sản phẩm, nguyên liệu, loại hàng, chứng nhận, tài khoản | Chủ | vài lần / năm | C/31:20-30 |
| | Tạo cuộn tem mới | Chủ | vài tuần / lần | C/25 |
| | Cài đặt, khách hàng đã mua, vùng nguyên liệu, thu hồi | Chủ | hiếm | C/32, C/28, C/41, B/26 |

Kết luận: trang chủ thủ kho chỉ giữ việc cột «hằng ngày»; trang chủ chủ thêm cột «chủ hằng ngày» ở mặt trước, cột «ít dùng» gom sau một ô «Quản lý khác».

---

## 2. Từng việc: trước / sau

### 2.1 In tem lô thành phẩm (nhãn lô 40 × 30) và tem từng chai, từ lô vừa tạo

**Hiện trạng**

| | Đường đi | Màn | Chạm | Ô gõ | Chỗ khó |
|---|---|---|---|---|---|
| Từ lô vừa xong (chủ) | B/17 → «← Về trang chủ» → C/19 ô «Cuộn tem QR» (C/19:31) → C/25 cuộn xuống → «In nhãn lô …» (C/25:26) → C/42 bấm «In» (C/42:46) → hộp thoại in | 5 (B/17, C/19, C/25, C/42, hộp thoại) | **5** | 0 | Nút «In nhãn lô» chỉ có cho một lô cố định. Lô khác không có nút. |
| Thủ kho | Không có đường | | không làm được | | A/02 không có ô in. B/17:52 chỉ có «Sang bước gán tem». |
| In cuộn serial (chủ) | C/19 → C/25 (1) → sửa «Số tem» (C/25:20, mặc định 500) → «+ Sinh dải serial» (C/25:21) → «In» trên dòng cuộn (C/25:25) → C/35 «In» (C/35:46) → hộp thoại | 5 | **5** (+4 nếu in một phần) | **1** (+2 ô «từ / đến») | «Sinh dải serial» là tiếng lập trình. Số tem không gắn với số chai. Banner tên miền dài 3 câu (C/25:19) hiện mỗi lần. |
| Gán tem vào lô (thủ kho) | A/02 → «Gán tem / hủy tem» (A/02:27) → B/18 chọn lô (B/18:36) → quét tem đầu → quét tem cuối (B/18:45-46) | 2 | **4** (3 nếu đi từ B/17:52 vì lô được chọn sẵn) | 0 | Phải tìm tem cuối cùng ở cuối cuộn. |
| **Cả chuỗi từ lô vừa xong, chưa có cuộn** | B/17 → (về trang chủ) → in cuộn → quay lại → gán | **≈ 5 màn** | **≈ 9** | **1** | Bốn lần đổi màn, hai người khác nhau (chủ rồi thủ kho). |

**Đề xuất A: giữ nguyên nghiệp vụ (BR-12, in trước gán sau). Làm được ngay.**

| # | Sửa | File:dòng | Trước → sau |
|---|---|---|---|
| A1 | B/17: thêm nút lớn «🖨 In tem cho 90 chai» cạnh «Sang bước gán tem». Bấm mở C/25 với ô «Số tem» điền sẵn `số chai chưa có tem + 5 dự phòng` (90 + 5 = 95; tem thừa dùng cho lô sau), con trỏ nằm sẵn ở nút «In». | B/17:52, C/25:20 | chủ: 5 chạm, 1 ô gõ → **3 chạm, 0 ô gõ** (B/17 nút in → «Tạo và in» → «In» trong hộp thoại) |
| A2 | C/25: gộp «+ Sinh dải serial» và «In» thành **một nút «Tạo và in 95 tem»**. Đổi chữ nút thành «Tạo cuộn tem và in». Bỏ cột «từ / đến» khỏi bảng; đưa vào mục «In lại một phần» thu gọn (`<details>`). | C/25:21, C/25:25 | giảm 1 chạm, bỏ 2 ô gõ ở dòng bảng |
| A3 | C/25:19: rút banner thành **một dòng**: «Mã QR dẫn tới quevanyen.vn. In rồi không đổi được.» Chi tiết đường dẫn đưa vào dấu `ⓘ` mở ra. Chỉ hiện đỏ khi **chưa in cuộn nào** (C/32 đã có cuộn đầu tiên thì thôi). | C/25:19 | bớt 3 câu mỗi lần |
| A4 | C/25:26: «Tem mẻ / nhãn lô» thành **danh sách các lô chưa in nhãn** (mỗi lô một nút «In nhãn lô Q100-261120-02 · 200 chai»), không cứng một lô. | C/25:26 | lô nào cũng có nút |
| A5 | B/18: khi vào từ B/17 (`?lot=`), lô **chọn sẵn** và **không hiện lô khác** (để nút «Đổi lô» nhỏ). Hiện ở B/18:36 lô Q100 vẫn chọn sẵn dù vào từ lô QC2. | B/18:36 | gỡ 1 chạm nhầm |
| A6 | B/18: chỉ quét **tem đầu**. Máy tính tem cuối (từ tem đầu, đủ số chai còn thiếu, bỏ tem VOID) và hỏi: «Gán 90 tem, từ MKWX-142J-RH đến 57CE-…? [Đúng, gán] [Không phải]». Thủ kho không phải tìm tem cuối. Nghiệp vụ không đổi: vẫn gán đúng một dải serial, vẫn kiểm cùng cuộn và đang UNASSIGNED (BR-12). Vẫn cho quét tem cuối khi dải không liền. | B/18:45-46 | 2 lần quét + tìm tem cuối → 1 quét + 1 bấm |
| A7 | C/35: in cuộn: tên «tem số 1–95» ở đầu trang xem trước; nút «In» to, mở hộp thoại in tự động khi vào trang (`window.print()` sau khi tải). | C/35:46, C/42:46 | bớt 1 chạm |

**Trước → sau (A):** từ lô vừa xong, chủ **9 chạm / 5 màn / 1 ô gõ → ≈ 5 chạm / 3 màn / 0 ô gõ** (in 3 chạm + gán 2: quét + «Đúng»).

**Đề xuất B: «In theo lô, gán luôn». CẦN SẾP QUYẾT (đổi nghiệp vụ BR-12 và mục 7.3).**

```
Màn B/17 (lô vừa xong)
┌──────────────────────────────────────────────┐
│ ✔ Mẻ QC2-261023-02 đã ủ xong · 90 chai       │
│                                              │
│  [ 🏷  IN 90 TEM DÁN CHAI ]   ← nút to nhất  │
│                                              │
│  ▸ Lưu mẫu (1 chai)…                         │
└──────────────────────────────────────────────┘
  ↓ chạm 1: máy tạo cuộn đúng 90 tem, gắn sẵn với lô này, mở hộp thoại in
  ↓ chạm 2: «In» trong hộp thoại
Màn xác nhận:  «Đã in 90 tem. Dán lên chai.»
  [ Xong ]     [ Tem nào bị hỏng? → quét tem hỏng, in bù 1 tem ]
```

Mỗi tem in: QR serial + mã lô + NSX + HSD (gộp tem serial C/35 và nhãn lô C/42 thành một, vì C/42:46 hiện đang nói «hai tem khác nhau» mà chai 10 ml khó dán hai tem 40 × 30). Tem tự chuyển sang IN_STOCK với lô đó sau khi in; hỏng thì dùng «Hủy tem lỗi» có sẵn (B/18:53).

| Trước → sau (B) | Chạm | Màn | Ô gõ |
|---|---|---|---|
| Từ lô vừa xong tới tem đã in và gán | 9 → **2** | 5 → **2** | 1 → **0** |

- Mất: không còn «in một cuộn dài rồi dùng dần» (cuộn 500 tem in từ trước). Vẫn giữ C/25 cho chủ khi cần in sẵn.
- Cần chốt cùng: (1) tem gộp có đủ chỗ cho QR ≥ 18 mm (mục 11 thiết kế) + mã lô + NSX + HSD trên 40 × 30 không (C/42:50-53 hiện chữ 6,2 pt, quá nhỏ cho mắt người lớn tuổi); (2) thủ kho được in và tạo tem hay vẫn chỉ chủ (mục 3 thiết kế).

**Phương án mặc định khi sếp chưa trả lời: A** (không đổi nghiệp vụ). **Khuyến nghị: B**, vì chỉ B đạt «in tem 1–2 chạm từ lô vừa tạo» như tin #460 muốn.

**CẦN SẾP QUYẾT 1:** cho thủ kho tạo và in tem cho lô mình vừa làm? Mặc định: **có** (ghi nhật ký người in; việc tạo cuộn tự do tới 5.000 tem vẫn chỉ chủ).
**CẦN SẾP QUYẾT 2:** chuyển sang B? Mặc định: giữ A.

### 2.2 In phiếu nhập (có tem lô nguyên liệu) và phiếu xuất

| | Hiện trạng | Màn | Chạm | Ô gõ | Chỗ khó |
|---|---|---|---|---|---|
| Phiếu nhập | A/05b:56 sau khi lưu có «🖨 In lại phiếu» và «🏷 In lại tem lô», **cả hai cùng dẫn `/nhap-hang/in-phieu`**; in xong thì quay về A/05b | 3 (A/05b, C/33, hộp thoại) | **3** | 0 | Chữ «In lại» trong khi chưa in lần nào; hai nút giống nhau làm người dùng bấm cả hai. |
| Phiếu xuất | A/11 → bấm dòng → hộp thoại → «🖨 In lại» (A/11:38) → C/34 «In» (C/34:46) → hộp thoại | 4 | **4** | 0 | Mới lập xong cũng thấy «In lại». |

**Đề xuất**

| # | Sửa | File:dòng | Trước → sau |
|---|---|---|---|
| P1 | A/05b:56: sau khi lưu, hộp thoại in **mở thẳng** (đúng thiết kế mục 6.2 «Sau đó mở hộp thoại in»). Hai nút còn lại thành **một nút «🖨 In lại phiếu và tem»**; chữ «In lại» chỉ hiện sau lần in đầu. | A/05b:56, A/05-receipt-3:56 | 3 chạm → **1 chạm** (chỉ bấm «In» trong hộp thoại in) |
| P2 | C/33 (phiếu + tem lô nguyên liệu): một trang in cho cả hai, không toolbar riêng bắt bấm «In» lần nữa; bấm hộp thoại in là xong. Tem lô luồng chung vẫn có chữ **CHUNG** (BR). | C/33:46 | 2 → 1 |
| P3 | C/34 (phiếu xuất): sau khi lập phiếu ở A/09, mở thẳng trang in; trong A/11 đổi «🖨 In lại» thành «🖨 In phiếu» to ở đầu hộp thoại. | C/34:46, A/11:38 | 4 → **2** |
| P4 | Trang in: nút «In» to hơn: `font-size:16px` (hiện C/33:46, C/34:46 đúng 16 px nhưng `padding:10px 18px` cho ≈ 41 px, dưới 48 px). | CSS in (C/33:40, C/34:40 `.toolbar button`) | đủ 48 px |

Nghiệp vụ không đổi. Chữ in giấy (9,5 pt trong bảng, C/34:18) giữ, vì khổ A5.

### 2.3 Tra cứu QR (nội bộ cho chủ, công khai cho khách)

**Nội bộ (C/27)**

| | Hiện trạng | Chạm | Ô gõ |
|---|---|---|---|
| Chủ tra một mã | C/19:33 ô «Tra cứu hai chiều» → quét hoặc gõ mã vào C/27:17 → «Tra cứu» (C/27:18) | **3** (ô, quét/gõ, nút) | 0–1 |

Chỗ khó: ô nhập có chữ gợi ý 80 ký tự liệt kê 11 loại mã (C/27:17: «Mã tem, Q100-…, QC1-…, Q-…, NL-…, PN-…, PNP-…, PX-…, LSX-…, NCC-… hoặc NM-…»). Người dùng không biết mình cần gõ cái gì. Kết quả là hai cây dài «Ngược về nguồn», «Xuôi tới khách» có chữ `NL`, `PN`, `PNP`, `LSX`, `NCC` không giải thích.

| # | Sửa | File:dòng | Trước → sau |
|---|---|---|---|
| Q1 | Ô nhập tự lấy focus; chữ gợi ý một dòng: **«Quét tem, hoặc gõ mã lô»**. Quét máy quét USB (kết thúc Enter) hoặc bấm Enter **tự tra**, không cần bấm nút. Giữ nút «Tra cứu» làm phương án phụ. | C/27:17-18 | 3 → **2 chạm** (ô, quét); tới 1 khi ô đã sẵn focus |
| Q2 | Trên ô nhập, dưới ô: nút nhỏ «Các loại mã ▾» mở bảng: *Tem trên chai = XXXX-XXXX-XX · Lô thành phẩm = QC2-261023-01 · Lô quế = NL-… · Phiếu nhập = PN-…* (viết đời thường, không viết tắt). Bảng chỉ mở khi người dùng cần. | C/27:17 | gỡ 80 ký tự |
| Q3 | Đầu kết quả: **một dòng kết luận** trước hai cây: ví dụ «Tem này thuộc lô QC2-261023-02, **chưa bán**» hoặc «Đã bán cho N V A ngày 20/11, phiếu PX-261120-001». | C/27 (đầu `#out`, dòng 19) | thấy đáp án không phải đọc cây |
| Q4 | Chú giải ngay đầu cột: `NL` = «Lô quế»; `PN` = «Phiếu nhập»; `PNP` = «Phiếu nhập phụ liệu»; `LSX` = «Lệnh sản xuất»; `NCC` = «Người bán». Cột «Dùng trong lệnh» giữ, đổi thành «Dùng cho mẻ». | C/27 bảng (dòng 19) | |

Thủ kho **không** tra hai chiều (mục 3 thiết kế: chỉ OWNER). Khi quét tem ở B/18, thủ kho đã thấy thông báo tem thuộc lô nào; không cần màn mới.

**Công khai (trang khách quét QR)**: xem mục 5.

### 2.4 Xem báo cáo (C/30)

| | Hiện trạng | Chạm | Ô gõ |
|---|---|---|---|
| Xem báo cáo mặc định | C/19:36 «Báo cáo» → bảng hiện sẵn (90 ngày gần nhất) | 1 | 0 |
| Đổi khoảng thời gian | gõ hai ô ngày (C/30:18-19) → «Xem» (C/30:20) | 3–4 | 2 (ô ngày là ô nhập kiểu `date`, chọn lịch bằng chuột rất lâu) |
| Đổi loại báo cáo | tab (C/30:22) → chọn nhóm → «Xem» | 3 | 0 |
| Xuất bảng | link `/api/v1/reports/yield?…` (C/30:24) | 1 | 0 |

Chỗ khó: tiêu đề cột «NL đưa vào (kg)», «Nhóm» (C/30:24); câu chú thích dài hai câu có chữ «truy xuất», «NL» (C/30:24); nút tải bảng không có chữ nào ngoài đường dẫn.

| # | Sửa | File:dòng | Trước → sau |
|---|---|---|---|
| R1 | Thay hai ô ngày bằng hàng nút: **[Tháng này] [Tháng trước] [3 tháng] [Năm nay] [Chọn ngày…]**. «Chọn ngày…» mới mở hai ô. | C/30:17-20 | 4 chạm + 2 gõ → **1 chạm** |
| R2 | Bỏ nút «Xem»: đổi tab, đổi nhóm, đổi ngày tự tải lại. | C/30:20-22 | 3 → **2** chạm |
| R3 | Đổi chữ: «Nhóm» → tên theo lựa chọn («Người bán» / «Sản phẩm» / «Tháng»); «NL đưa vào (kg)» → «Quế đưa vào (kg)»; «Tiền mua NL» → «Tiền mua quế»; link tải → nút «⬇ Tải bảng Excel (.csv)». | C/30:24 | |
| R4 | Câu chú thích C/30:24 rút còn: «Chỉ tính quế đã đưa vào lô thành phẩm.» Chi tiết (NCC-DC-001, NCC-CQ-002 chưa vào lô) chuyển vào dấu `ⓘ`. | C/30:24 | |
| R5 | Dòng 0 – 0 – 0 (người bán chưa có lô) hiện mờ và dồn cuối bảng. | C/30:24 | |
| R6 | C/30:24 còn «1,63» kg ở NCC-CQ-001 (đội đã biết, báo thêm cho đủ): tính từ lô thật hoặc ghi «—». | C/30:24 | |

Báo cáo giá vốn / công nợ chỉ chủ xem (mục 3 thiết kế); thủ kho chỉ thấy tồn kho (A/12-14), không cần màn báo cáo.

### 2.5 Khai danh mục (người bán, đồi, bảng giá, cài đặt)

**Người bán và đồi (C/21, C/22, C/22b)**

| | Hiện trạng | Chạm | Ô gõ |
|---|---|---|---|
| Thêm người bán hộ dân có 1 đồi | C/19:30 → «+ Thêm mới» (C/21:20) → hộp thoại 7 ô người bán: Tên, Kiểu, SĐT, Địa bàn, Luồng, Đồng ý hiện tên, Trạng thái (C/22:32) → «+ Thêm đồi» → 6 ô đồi: Thôn, Diện tích, Năm trồng, Tọa độ, Ảnh, Đồi mặc định → «Lưu đồi» → «Lưu» | **≈ 16** | **5** (tên, SĐT, ha, năm trồng, tọa độ) + ảnh |
| Duyệt người bán xưởng thêm nhanh | C/19:26 → C/21 (lọc sẵn `approved=0`) → bấm dòng (C/21 hàng) → hộp thoại → «✔ Duyệt người bán» (C/22b:32) | **3** | 0 |
| Cập nhật bảng giá | C/19:29 → sửa 6 ô giá (C/20:21) → «Lưu bảng giá» (C/20:22) | **2 + số giá đổi** | số giá đổi (mỗi ô 24 px, `inputmode=numeric` đã có) |

Chỗ khó: «Kiểu» có chữ «Gia đình / Hộ dân / Thương lái» rồi «Luồng» «Vùng kiểm soát / Chung» đứng riêng, người dùng không hiểu hai cái liên quan (C/21:22 ghi chú riêng); «Đồng ý hiện tên trên trang truy xuất» không giải thích; nhãn «Địa bàn (hộ dân / gia đình: chọn thôn)» (C/22:32) rối. Tọa độ «dán từ Google Maps» người dùng kém CNTT khó làm.

| # | Sửa | File:dòng | Trước → sau |
|---|---|---|---|
| D1 | «Thêm nhanh» **3 phần**: (1) gõ **Tên**; (2) bấm một trong 3 nút to: **[Hộ dân] [Gia đình] [Thương lái]**; (3) bấm **thôn** (danh sách nút theo xã gần nhất đã chọn lần trước). Luồng **tự đặt**: Thương lái = Chung; còn lại = Chung cho tới khi có đồi, có đồi thì chuyển Vùng kiểm soát (đúng ghi chú C/21:22). Đây là các trường bắt buộc (Tên*, Kiểu*, Địa bàn*). SĐT, đồng ý hiện tên, đồi, ảnh để sau. Trạng thái mặc định «Đang dùng». | C/22:32, C/21:22 | 16 chạm + 5 gõ → **6 chạm + 1 gõ** |
| D2 | Phần đồi, tọa độ, ảnh: nút «Bổ sung thông tin truy xuất» (đã có ở C/41 qua nhãn «thiếu tọa độ / thiếu ảnh»); hộp thoại bổ sung chỉ 3 phần: **Thôn** (nút), **Năm trồng** (số), **Chụp ảnh đồi** (nút chụp trên điện thoại). Tọa độ tự lấy khi chụp ảnh bằng điện thoại (nếu có vị trí); ô dán tọa độ giữ cho chủ. | C/22:32 (phần đồi), C/41:21 | |
| D3 | Chữ: «Luồng» → **«Loại hàng thu mua»** với 2 nút «Quế có đồi, truy xuất tới đồi» và «Quế thương lái, không biết đồi». «Đồng ý hiện tên trên trang truy xuất» → «Cho khách thấy tên người này khi quét tem» (công tắc to). | C/22:32 | |
| D4 | Duyệt: bấm băng báo C/19:26 **mở thẳng hộp thoại của người bán đầu tiên chờ duyệt**; nút «✔ Duyệt» ở đầu hộp thoại, không chìm dưới hai nút «Lưu», «Đóng». Hoặc nút «Duyệt» ngay trong dòng của C/21 khi người bán đủ trường bắt buộc. | C/19:26, C/22b:32 | 3 → **2 chạm** |
| D5 | Bảng giá (C/20): thêm nút «Giống hôm qua» điền sẵn các ô; chỉ sửa ô đổi. Ô `type=date` (C/20:17) thay bằng nút «Hôm nay / Hôm qua» cho phần lớn lần dùng. | C/20:17, C/20:21 | gõ lại 6 giá → 0 gõ khi giá không đổi |

**Màn «Quản lý» (C/31) và «Cài đặt» (C/32)**

- C/31 hiện **2 nhóm × 11 ô = 22 ô** (C/31:17-42), trong đó 7 ô lặp lại ô ở trang chủ chủ (Bảng giá, Cuộn tem QR, Lô thành phẩm, Vùng nguyên liệu, Tra cứu, Khách hàng, Báo cáo: C/31:32-42 so với C/19:29-36) và **6 ô ghi «dùng chung khuôn danh mục, chưa vẽ»** (C/31:21-26 …). Chữ «dùng chung khuôn danh mục, chưa vẽ» là ghi chú của người làm mockup, **không phải chữ cho người dùng** — phải gỡ khỏi bản chạy thật.
- Đề xuất bố cục C/31 sau khi gom:

```
Quản lý
Danh mục (hiếm khi sửa)
  [Người bán & đồi quế] [Sản phẩm] [Nguyên liệu & hạng] [Công thức] [Phụ liệu]
  [Địa bàn] [Khách hàng] [Loại hàng] [Chứng nhận] [Tài khoản]
Hệ thống
  [Cài đặt]
```
  Nhóm «Vận hành» (11 ô) bỏ khỏi C/31 vì đã nằm ở trang chủ chủ, hoặc để thành một dòng «Việc hằng ngày: về trang chủ».
- Tên ô: «Phụ liệu & phiếu nhập phụ liệu» → «Phụ liệu (kho, nhập)»; «Thử lưu hương 28 ngày» giữ vì đã quen xưởng, thêm dòng phụ «xem hương sau 28 ngày».
- C/32 (Cài đặt): 11 ô một trang (C/32:23). Chia hai nhóm: **«Thường chỉnh»** (SĐT liên hệ, ngưỡng cảnh báo giá, ngưỡng hạn dùng, khổ giấy) và **«Không đổi sau khi in»** (tên miền QR, địa danh trên trang QR). Nhãn dài kiểu «Tên miền dùng trong QR (https://…) — CHỐT TRƯỚC KHI IN CUỘN ĐẦU» thành **hai dòng: nhãn + dòng chú nhỏ**; «Khổ giấy in phiếu (A5 hoặc 80mm)» thành hai nút chọn **[A5] [80 mm]** thay vì ô gõ chữ.
- Nút «← Về trang chủ» ở C/21:12, C/32:12, C/41:12 trỏ về `/quan-ly`, không phải trang chủ; C/19-C/30 trỏ về `/`. Đổi chữ ở những màn về `/quan-ly` thành **«← Về Quản lý»**.

---

## 3. Màn chủ / menu theo vai

**Thủ kho (WORKSHOP), đã có ở A/02.** Đề xuất bổ sung (cụm A cũng soát, nên @Mai thống nhất với đoạn này):

```
┌───────────────────────────────────────────┐
│ Quế Văn Yên                  Thủ kho ▸    │
├───────────────────────────────────────────┤
│  [⚖ NHẬP HÀNG] [🚚 XUẤT HÀNG]             │
│  [🏭 LÀM MẺ]   [📦 TỒN KHO]              │   ← 4 nút to, giữ nguyên A/02:16-19
│                                           │
│  Việc cần làm                             │
│   🏷 Lô Q100-…-02: còn 50 chai chưa dán tem [Dán tem]
│   ⏳ Mẻ QC2-…-02 đủ ngày ủ                [Ngửi kiểm tra]
│                                           │
│  [🧾 Phiếu hôm nay] [📋 Đơn hàng] [🏷 In tem*]  ← *thêm nếu sếp chọn B hoặc cho in
└───────────────────────────────────────────┘
```

- «Việc cần làm» lấy từ dữ liệu (lô chưa gán đủ tem, mẻ chờ ngửi, lô chưa lưu mẫu): thủ kho bấm thẳng vào việc, không phải nhớ nơi nào. Hiện trang chủ chủ đã có kiểu này (C/19:24-26); thủ kho chưa.
- Ô «Gán tem / hủy tem» (A/02:27) đổi chữ **«Dán tem lên chai»**. «Hủy tem lỗi» là nút nhỏ trong màn đó.
- Xoá nhãn **«GĐ2»** khỏi mọi ô (A/02:19, A/02:21 … và C/19:31-35, 12,6 px, màu nhạt): nhãn đó chỉ để mockup phân biệt giai đoạn dự án. Bản chạy thật ẩn ô chưa có, không hiện nhãn. Chú giải ở A/02:29 («Nhãn «GĐ2»: …») cũng bỏ.

**Chủ doanh nghiệp (OWNER), C/19 hiện 4 + 3 băng + 9 ô.** Đề xuất:

```
┌──────────────────────────────────────────────────┐
│ Quế Văn Yên                       Chủ doanh nghiệp │
├──────────────────────────────────────────────────┤
│  [⚖ NHẬP HÀNG] [🚚 XUẤT HÀNG] [🏭 LÀM MẺ] [📦 TỒN KHO] │   ← giữ C/19:18-21
│                                                  │
│  Việc cần xử lý                          (gom một chỗ)
│   🔔 1 người bán chờ duyệt                [Duyệt]
│   🧪 1 lô chưa lưu mẫu                    [Lưu mẫu]
│   ⏳ 1 mẻ đang ủ, còn 6 ngày              [Xem]
│                                                  │
│  Hay dùng:  [💰 Giá hôm nay] [🔎 Tra cứu mã] [📊 Báo cáo]
│  [⚙ Quản lý khác ▸]                              │   ← đi tới C/31 (đã gọn)
└──────────────────────────────────────────────────┘
```

- C/19:24-26 (3 băng đứng rời) → một khối «Việc cần xử lý», mỗi dòng có nút bên phải: đỡ phải đoán «bấm vào đâu».
- C/19:29-37 (9 ô) → 3 ô «Hay dùng» + 1 ô «Quản lý khác». Các ô «Người bán & đồi quế», «Cuộn tem QR», «Lô thành phẩm · thu hồi», «Vùng nguyên liệu», «Khách hàng đã mua» chuyển sang C/31. Tới các màn đó vẫn **2 chạm** (Quản lý khác → ô); mất 1 chạm ở 5 việc ít dùng, đổi lấy trang chủ 13 ô → 8 ô.
- Chủ cũng làm được mọi việc của thủ kho (A/02), nên 4 ô to giống hệt.
- Thu hồi lô (cần chủ) chỉ ở C/26 và hộp «Tra cứu» (C/27), giữ ở «Quản lý khác»; không đặt trên trang chủ để khỏi bấm nhầm.

---

## 4. Chuẩn UX chung và CSS cần thêm (đề xuất cho Dev, **không sửa `app.css` trong task này**)

Đã đạt: nút 64 px (CSS:71), ô nhập 52 px (CSS:97), ô số 32 px (CSS:101), ô quét 1,4 rem (CSS:102), ô chọn 84 px (CSS:84), tile nhỏ 96 px (CSS:65), chữ nền 18 px (CSS html).

Chưa đạt, cần sửa:

| # | Vấn đề | Căn cứ | Sửa |
|---|---|---|---|
| U1 | Nút `small` 44 px, chữ 0,9 rem = 16,2 px: **chạm 44 < 48** | CSS:79; dùng ở C/25:25 («In»), C/22:32 (✕, «+ Thêm đồi», «Lưu đồi»), A/11 (✕) | `min-height:48px` |
| U2 | Ô «từ … đến …» 90 px × 44 px | C/25:25 | gom vào `<details>` «In một phần», ô ≥ 48 px, `inputmode=numeric` |
| U3 | Nhãn nhỏ «GĐ2», `.badge` 0,7 rem = 12,6 px | C/19:31-35, C/31:21-26 | bỏ; nếu giữ thì `.tag{font-size:1rem}` |
| U4 | Màu chữ phụ `--muted` #6b625a trên nền #faf7f2: tỉ lệ ≈ 5,5 : 1 (đạt AA) nhưng **chữ nhỏ** 15 px khó đọc | CSS `.muted`, C/36:28 | chữ phụ ≥ 16 px (`.muted{font-size:1rem}` trong app; 16 px trên trang công khai) |
| U5 | Chỉ có `:hover` mà thiếu `:focus-visible` cho nút, ô, tab, `<summary>` | CSS:74-76 (`button:hover`), :60 có `.tile:focus` | thêm khối dưới |
| U6 | Ô `type=date` (chọn lịch) khó dùng ở máy yếu; ô `type=text` tọa độ | C/20:17, C/30:18-19 | nút ngày nhanh (R1, D5) |
| U7 | Thông báo lỗi và nút xoá/thu hồi chỉ dùng **màu** để phân biệt | `.tag.warn`, `.danger` | luôn kèm chữ và biểu tượng (đã có ở phần lớn chỗ); kiểm khi dựng |
| U8 | Bảng nhiều cột trên màn hẹp (30 ở 5 cột, 41 ở 7 cột, 26 ở 15 cột) | C/41:28, B/26:9 | `.table-wrap{overflow-x:auto}` đã có (CSS:`.table-wrap`), thêm bóng đổ hai bên để thấy còn cột |

CSS gợi ý (dán vào cuối `app.css` khi Dev dựng, không phải bản này sửa):

```css
/* Vùng chạm và chữ tối thiểu */
button.small, .btn.small { min-height: 48px; font-size: 1rem; }
.tag, .badge { font-size: 1rem; }
.muted, small { font-size: 1rem; }
input[type=checkbox] { width: 32px; height: 32px; }

/* Focus rõ cho người dùng bàn phím và máy quét */
:focus-visible { outline: 3px solid var(--que); outline-offset: 2px; }
button:focus-visible, .btn:focus-visible, .tile:focus-visible { box-shadow: 0 0 0 4px var(--que-soft); }

/* Nút một hành động chính, gắn đáy, dùng cho «In 90 tem», «Lưu», «Duyệt» */
.cta { display: flex; width: 100%; min-height: 72px; font-size: 1.3rem; justify-content: center; align-items: center; gap: .6rem; }
.cta-bar { position: sticky; bottom: 0; padding: .8rem 1rem; background: var(--bg); border-top: 1px solid var(--line); }

/* Khối «Việc cần xử lý» */
.todo { display: grid; gap: .6rem; margin: 1rem 0; }
.todo-item { display: flex; align-items: center; gap: .8rem; padding: .8rem 1rem; border-radius: var(--radius); background: var(--warn-soft); }
.todo-item .btn { margin-left: auto; min-height: 48px; }

/* Nút ngày nhanh cho báo cáo */
.range-btns { display: flex; flex-wrap: wrap; gap: .6rem; }
.range-btns .choice { min-height: 56px; min-width: 120px; }
```

Quy ước chữ (mọi màn nội bộ): không viết tắt kỹ thuật (NL, TP, PN, PNP, LSX, NCC, GĐ), không «serial», «sinh dải», «CSV», «hộp thoại»; dùng: «tem», «mã trên tem», «lô quế», «phiếu nhập», «Tải bảng Excel». Mã (QC2-261023-02, NL-2611-0004) giữ nguyên vì xưởng đã quen và dán lên chai.

---

## 5. Website công khai (chỉ soát độ dễ đọc, không đổi nội dung)

Phạm vi: C/36, C/37, C/38, C/39, C/40, C/43, C/44. Người xem là khách quét QR bằng điện thoại.

Đạt: chữ nền 17 px (C/36:9), kết quả chính hãng 19 px, biểu tượng 30 px (C/36:13-14), tiêu đề sản phẩm 21 px (C/36:22), nút «Mua lại» 18 px cao ≈ 56 px (C/36:27), màu xanh/đỏ có chữ đi kèm.

| # | Vấn đề | Căn cứ | Sửa |
|---|---|---|---|
| W1 | **Số điện thoại liên hệ** là liên kết chữ nhỏ trong `<small>` (≈ 15 px) ngay trong khối cảnh báo đỏ: khách tìm số khi nghi hàng giả, đây là chỗ cần dễ bấm nhất | C/37:44, C/38:43, C/39:43, C/43:43 (`<small>Liên hệ: <a href="tel:0900000000">`) | đổi thành **nút «📞 Gọi 0900 000 000»** to ≥ 48 px, chữ ≥ 18 px, đặt dưới câu cảnh báo |
| W2 | Tiêu đề khối `.card h2` 15 px VIẾT HOA, màu nâu nhạt | C/36:19 | 17 px, không viết hoa toàn bộ |
| W3 | Chữ phụ `.muted` 15 px, `.note` 13,5 px, footer 14 px | C/36:28, :33, :34 | tất cả ≥ 16 px |
| W4 | Mã đã quét (C/39, C/43) hiện bằng `.muted` 15 px: khách cần đọc lại mã cho nhà bán | C/39 (dòng 44), C/43 | 18 px đậm, cỡ chữ mono |
| W5 | Nhãn ảnh giữ chỗ 12 px («Ảnh sản phẩm», «Ảnh đồi 1») | C/36:50, :73-75 | chỉ là ô giữ chỗ cho ảnh thật; ảnh thật cần chữ thay thế (`alt`), kích thước ≥ 96 px |
| W6 | Trang C/36:82 và C/37:83 hiện chữ **«[ví dụ minh hoạ, chưa có thật]»** trong dòng chứng nhận | C/36:82, C/37:83 | chỉ để mockup; không đưa vào bản chạy. Ghi cho Dev khi dựng. |
| W7 | Ô nhập mã C/40: tự chuyển chữ HOA (đúng, C/40:35); thiếu `autocapitalize="characters"`, `autocorrect="off"`, `spellcheck="false"` nên bàn phím điện thoại vẫn viết hoa chữ đầu và sửa chính tả | C/40:45 | thêm ba thuộc tính. Chữ hướng dẫn «ví dụ K7Q2-MX9P-AT» ở C/40:44 đã tốt. |
| W8 | Thông báo trạng thái chỉ bằng màu nền + biểu tượng, có chữ → đạt | C/36:43, C/38:43, C/39:43 | giữ |
| W9 | Vùng chạm nút «Kiểm tra» C/40 (rộng 100%, ≈ 48–52 px) đạt; liên kết «Quế Văn Yên» đầu trang (C/36 `<header><a>`) là chữ nhỏ trong thanh 19 px | C/36:10-11 | tăng `padding` liên kết đầu trang cho cao ≥ 48 px |

Tiếng Việt trên trang công khai ngắn, đúng giọng thương hiệu; không đề xuất đổi chữ.

---

## 6. Danh sách CẦN SẾP QUYẾT (gửi @Lead gom hỏi một lần)

| # | Câu hỏi | Mặc định nếu sếp chưa trả lời | Ảnh hưởng |
|---|---|---|---|
| Q-C1 | Thủ kho được tạo và in tem cho lô mình vừa làm? (hiện chỉ chủ: thiết kế mục 3) | **Có**, ghi nhật ký người in. Tạo cuộn tự do tới 5.000 tem vẫn chỉ chủ. | 2.1 |
| Q-C2 | Chuyển sang «in theo lô, gán luôn» (phương án B), bỏ bước quét tem đầu / tem cuối? | **Giữ A** (không đổi BR-12); khuyến nghị B vì 9 → 2 chạm | 2.1, đổi BR-12 và mục 7.3 |
| Q-C3 | Tem gộp (serial + mã lô + NSX + HSD) trên 40 × 30 mm có vừa; hay phải đổi khổ lớn hơn (ví dụ 50 × 30)? | **40 × 30**, thử in thật trước khi chốt (QR ≥ 18 mm, chữ ≥ 7 pt) | 2.1 (nếu chọn B) |
| Q-C4 | Số tem dự phòng khi in theo số chai: bao nhiêu? | **+5 tem**, thừa dùng cho lô sau | 2.1 (A1) |
| Q-C5 | Trang chủ chủ: dời 5 ô ít dùng vào «Quản lý khác»? | **Có** | 3 |

Các mục khác ở trên chỉ đổi cách hiển thị, không đổi nghiệp vụ, không cần sếp quyết.

---

## 7. Thứ tự cho Dev (#37, @Dat)

Làm theo ưu tiên (đầu danh sách ít rủi ro, nhiều lợi):

1. **U1, U3, U5, CSS mục 4** (một lần, mọi màn hưởng).
2. **Trang chủ** (mục 3): C/19 gom «Việc cần xử lý», gỡ «GĐ2»; C/31 gọn lại; sửa chữ «← Về Quản lý» (C/21:12, C/32:12, C/41:12).
3. **In**: P1, P3, P4 (A/05b, A/11, C/33, C/34); A1–A5 nếu sếp chọn A hoặc chưa trả lời; B nếu sếp chọn B.
4. **Báo cáo**: R1–R5 (C/30).
5. **Tra cứu**: Q1–Q4 (C/27).
6. **Danh mục**: D1–D5 (C/21, C/22, C/22b, C/20); C/32 chia nhóm.
7. **Trang công khai**: W1–W4, W7, W9 (C/36–C/40, C/43, C/44).

Phụ thuộc: A1, A6 cần dữ liệu «số chai chưa có tem» (đã có ở B/18:36 «đã gán 150/200», B/17:35 «90 chai»); D1 cần danh sách thôn.

---

## 8. Ghi chú, chưa kiểm

- Chưa có `ux/ra-soat-a.md` lúc làm; nếu @Mai đặt chuẩn khác (ví dụ chữ ≥ 18 px) thì theo chuẩn đó.
- Số chạm là **đếm theo thiết kế tĩnh** của mockup, chưa đo trên người dùng thật; «≈» là ước theo số ô trong hộp thoại (C/22:32). Nên thử 2–3 nhân viên thật với bản dựng.
- C/44 (tem đã hủy) và C/38 (thu hồi): chưa đọc chi tiết từng dòng; theo cùng khuôn C/36–C/39 nên áp W1–W3.
- Không soát C/01 – 01c (đăng nhập) và C/29 (chi tiết khách) kỹ; C/29:19 có «Túi thơm … 50 g» như C/28:19 (cần 25 g).
- Số dòng đã đối chiếu bằng `grep -n` trên bản `de-xuat/man/` hiện tại; nếu cụm khác sửa, số dòng có thể lệch.
