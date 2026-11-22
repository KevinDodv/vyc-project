# Lộ trình chuyển đổi số – Quế Văn Yên

Nov 19, 2026 · @Kevin

## Tóm tắt điều hành

Đề xuất số hóa qua giai đoạn chuẩn bị và 4 giai đoạn triển khai, khoảng 19 tháng, từ 12/2026 đến 6/2028. Đội Qwork tự phát triển. Mục tiêu cuối là thương hiệu thành phẩm quế Văn Yên có QR truy xuất đến từng chai, từng túi.

Thứ tự làm đi theo dòng dữ liệu, không đi theo thứ tự anh liệt kê. Phải có dữ liệu thu mua sạch thì truy xuất mới thật, và truy xuất thật thì trang thương hiệu mới có câu chuyện để kể.

- **Giai đoạn 0 – Chuẩn hóa (6–8 tuần):** thống nhất cách mã hóa hộ, đồi, lô. Hoàn thiện tài liệu yêu cầu. Bắt đầu thủ tục an toàn thực phẩm.
- **Giai đoạn 1 – Danh mục + Nhập hàng:** bỏ sổ tay và Zalo. Thủ kho nhập phiếu thu mua trên máy tính tại xưởng.
- **Giai đoạn 2 – Sản xuất + Truy xuất + QR serial:** quản lý công thức và kho phụ liệu theo gram, lệnh sản xuất có giai đoạn ủ, lưu mẫu và thử lưu hương (theo sổ tay sản xuất bản 2); lô thành phẩm đầu tiên (tinh dầu, túi thơm) có QR quét ra nguồn gốc, truy được về lô phụ liệu và lô quế.
- **Giai đoạn 3 – Website thương hiệu chuẩn SEO + Google Ads + kênh bán.**
- **Giai đoạn 4 – Hồ sơ OCOP, hữu cơ, mở dòng thực phẩm (trà, bột quế).**

Chi phí chủ yếu là công sức đội Qwork, ước sơ bộ khoảng 12,5 người-tháng (bản đầu 11,5; thêm 1,0 cho công thức, kho phụ liệu, ủ, lưu mẫu, thử lưu hương ở giai đoạn 2, xem Rủi ro và biện pháp). Chi tiền mặt cho hạ tầng và thiết bị khoảng 8–16 triệu đồng cho năm đầu, chưa gồm ngân sách quảng cáo. Con số chính xác sẽ có ở tài liệu WBS.

Ba quyết định đã chốt ngày 19/11/2026: tách 2 luồng nguồn hàng; làm an toàn thực phẩm trước OCOP cho trà và bột; QR serial theo cuộn tem, gán theo lô khi đóng gói.

## Hiện trạng doanh nghiệp

Mức số hóa hiện là 0: mọi giao dịch ghi trên sổ tay và Zalo, không truy được lô hàng về đồi quế.

| Khía cạnh | Hiện trạng | Hệ quả |
| --- | --- | --- |
| Quy mô | Doanh nghiệp siêu nhỏ, chủ DN tự làm lab thành phẩm | Hệ thống phải rất gọn, ít bước |
| Mảng 1: quế khô xuất khẩu | Bán cho DN xuất khẩu khác, đi Ấn Độ / Trung Đông / Nam Á | Yêu cầu truy xuất của khách còn thấp; cần nhất là quản lý thu mua, kho, công nợ |
| Mảng 2: thành phẩm | Tinh dầu, túi thơm, trà, bột, ống quế nhỏ; đang ở giai đoạn lab | Đây là mảng cần thương hiệu và QR |
| Nguồn nguyên liệu | Đồi nhà, thu mua trực tiếp hộ dân, qua thương lái | Ba nguồn lẫn nhau, hàng thương lái không rõ đồi |
| Ghi chép | Sổ tay, giấy tờ, Zalo | Không tìm lại, không tổng hợp được |
| Người nhập liệu | Thủ kho, công nhân xưởng | Nhập trên máy tính tại xưởng (có wifi, nối thẳng máy chủ); cần màn hình chữ to, thao tác ít, quét mã thay gõ |
| Kênh bán dự kiến | Website + Google Ads, Facebook / Zalo OA, Shopee / TikTok Shop / Lazada, quà tặng DN / đại lý / điểm du lịch | Website làm gốc thương hiệu, các sàn dùng chung dữ liệu sản phẩm |
| Chứng nhận hướng tới | OCOP, hữu cơ (VN / USDA / EU) | Hệ thống phải lưu nhật ký vùng trồng và hồ sơ lô |
| Nguồn lực CNTT | Đội Qwork (đang phát triển Essy Pilates) | Tự phát triển, tái dùng stack và kinh nghiệm sẵn có |

Địa bàn: từ 1/7/2025 Yên Bái đã nhập vào tỉnh Lào Cai và bỏ cấp huyện. Huyện Văn Yên cũ nay là 9 xã: Phong Dụ Hạ, Phong Dụ Thượng, Châu Quế, Lâm Giang, Đông Cuông, Tân Hợp, Mậu A, Xuân Ái, Mỏ Vàng (Báo Lào Cai).

## Mục tiêu và nguyên tắc thiết kế

Mục tiêu số 1 trong 12 tháng là xây thương hiệu thành phẩm. Hai mục tiêu còn lại là nền móng để thương hiệu đó đáng tin.

- **Thương hiệu:** mỗi sản phẩm bán ra kể được câu chuyện thật, có bằng chứng: quế từ đồi nào, thôn nào, hộ nào, năm trồng, ngày sản xuất.
- **Vận hành:** biết nhập của ai, bao nhiêu, giá nào; tồn kho đúng theo thời gian thực; không thất thoát.
- **Hồ sơ:** dữ liệu đủ để làm hồ sơ OCOP và hữu cơ mà không phải ghi chép lại từ đầu.

Nguyên tắc thiết kế:

- **Ghi một lần, dùng nhiều nơi.** Phiếu thu mua vừa là chứng từ kho, vừa là mắt xích truy xuất, vừa là nội dung trang sản phẩm.
- **Máy tính xưởng là trạm nhập liệu.** Máy tính tại xưởng có wifi, dữ liệu ghi thẳng lên máy chủ, không cần chế độ offline. Mỗi nghiệp vụ tối đa 3 thao tác, dùng máy quét QR cắm USB thay cho gõ.
- **Quét thay vì gõ.** Chọn hộ, đồi, lô bằng QR hoặc danh sách có sẵn, không gõ tên tự do.
- **Dữ liệu công khai tách khỏi dữ liệu nội bộ.** Trang truy xuất chỉ hiện thông tin được phép. Giá thu mua, công nợ, tên thương lái không bao giờ lộ ra ngoài.
- **Làm cho mình, không làm nền tảng.** Không thiết kế đa doanh nghiệp, giảm khoảng 20–30% công sức so với hướng SaaS (ước tính). Vẫn giữ mã nguồn sạch để sau này có thể mở rộng.

## Các quyết định đã chốt

Cả ba quyết định được chủ doanh nghiệp đồng ý ngày 19/11/2026 và là ràng buộc cho thiết kế hệ thống.

### 1. Tách 2 luồng nguồn hàng

- **Luồng "vùng kiểm soát":** đồi quế của gia đình và các hộ thu mua trực tiếp. Mỗi đồi có mã, vị trí, diện tích, năm trồng và nhật ký canh tác. Thành phẩm có QR và hàng hướng tới hữu cơ **chỉ** được lấy từ luồng này.
- **Luồng "thu mua chung":** hàng qua thương lái, chỉ biết đến mức xã. Chỉ dùng cho quế khô xuất khẩu.
- Hệ thống chặn cứng: một lệnh sản xuất thành phẩm không được xuất nguyên liệu từ lô thuộc luồng thu mua chung. Kho cũng phải tách vị trí vật lý (khu A / khu B).

### 2. An toàn thực phẩm trước OCOP cho trà và bột quế

- Tinh dầu, túi thơm, ống quế trang trí không phải thực phẩm, nên được đi trước.
- Trà và bột quế chỉ mở bán sau khi có hồ sơ công bố sản phẩm và điều kiện an toàn thực phẩm. Đây là việc pháp lý song song với phần mềm, chủ DN cần xác minh thủ tục cụ thể với cơ quan quản lý tại Lào Cai.
- Trong hệ thống, sản phẩm thuộc loại "thực phẩm" không được đăng bán khi chưa nhập số và ngày hiệu lực của giấy tờ.

### 3. QR serial từng đơn vị, gán theo cuộn tem

- Hệ thống sinh trước dải serial ngẫu nhiên, không đoán được (ví dụ 10 ký tự). Mỗi serial là một đường dẫn ngắn trên tên miền thương hiệu.
- In cả cuộn tem bằng máy in nhiệt. Tem ở trạng thái "chưa kích hoạt".
- Khi đóng gói, thủ kho quét tem đầu và tem cuối của đoạn tem dùng cho lô → toàn bộ dải serial giữa hai tem được gán vào lô sản xuất.
- Khi bán, giao đại lý hoặc gửi đơn sàn: quét tem để cập nhật trạng thái "đã xuất".
- Khách quét QR → trang truy xuất; hệ thống đếm lượt quét. Một serial được quét bất thường nhiều lần hoặc chưa kích hoạt mà đã bị quét sẽ hiện cảnh báo nghi giả.

Vòng đời một serial: Chưa kích hoạt → Đã gán lô → Trong kho → Đã xuất / Đã bán → (Hủy / Thu hồi).

## Kiến trúc giải pháp tổng thể

Bốn phân hệ dùng chung một cơ sở dữ liệu. Nhập hàng sinh ra lô nguyên liệu, truy xuất nối lô đó với lô thành phẩm và QR, còn trang giới thiệu chỉ đọc phần dữ liệu được phép công khai.

kiến trúc 4 phân hệ và người dùng

Truy xuất nằm ở giữa và là phần quan trọng nhất: nếu nó thiếu dữ liệu thì trang sản phẩm chỉ còn là quảng cáo.

Lựa chọn kỹ thuật đề xuất:

- **Ứng dụng web chạy trực tuyến** trên máy tính tại xưởng qua wifi, kèm máy quét QR cắm USB; không cần chế độ offline nên bỏ được phần đồng bộ dữ liệu, vốn là phần khó làm nhất. Giao diện vẫn mở được trên điện thoại để chủ DN xem báo cáo, không làm app riêng.
- **Stack đội Qwork đang quen** (như bên Essy Pilates) để không tốn thời gian học công nghệ mới.
- **Website thương hiệu render phía máy chủ** (SSR hoặc trang tĩnh), có dữ liệu có cấu trúc schema.org/Product để Google đọc được, chạy nhanh trên điện thoại.
- **Kênh bán:** giai đoạn 3 đồng bộ thủ công (xuất file sản phẩm, nhập đơn). Chỉ tích hợp API Shopee / TikTok Shop khi số đơn trên sàn đủ lớn để đáng công.

## Lộ trình theo giai đoạn

Năm giai đoạn, mỗi giai đoạn kết thúc bằng một thứ dùng thật được ngay và một cổng kiểm tra trước khi sang giai đoạn sau. Các mốc ngày là dự kiến.

lộ trình 5 giai đoạn, 12/2026 – 6/2028

Giai đoạn 2 khớp với lộ trình sản phẩm: lab 1–3 tháng rồi vào sản xuất, nên lô có QR đầu tiên là tinh dầu hoặc túi thơm.

- **GĐ0 – Chuẩn hóa (12/2026 – 1/2027).** Đầu ra: quy tắc mã hóa; danh sách hộ và đồi; BRD, ERD, WBS; hồ sơ ATTP bắt đầu nộp.
  - Cổng: tài liệu yêu cầu được chủ DN và thủ kho duyệt.
- **GĐ1 – Danh mục + Nhập hàng (2 – 5/2027).** Đầu ra: 5 danh mục, phiếu thu mua trên điện thoại, lô nguyên liệu có tem QR nội bộ, tồn kho, công nợ nhà cung cấp, xuất bán quế khô.
  - Cổng: ≥ 95% phiếu thu mua trên hệ thống trong 4 tuần, bỏ sổ tay.
- **GĐ2 – Sản xuất + Truy xuất + QR (5 – 9/2027).** Đầu ra: danh mục công thức (QC1/2, RQ1/2, TQ1/2, hương nền TT1/2, dung dịch tẩm, sáp thơm, viên thạch cao, túi vỏ quế), kho phụ liệu theo gram (phiếu nhập phụ liệu, lô phụ liệu, bán thành phẩm tự làm), lệnh sản xuất nhiều nguyên liệu có giai đoạn ủ, lô thành phẩm theo mẫu mã mới, lưu mẫu 12 tháng, thử lưu hương 28 ngày, QR serial theo cuộn, trạng thái hàng, truy xuất hai chiều tới lô phụ liệu và lô quế, trang truy xuất công khai.
  - Cổng: một lô thành phẩm thật (qua đủ ngày ủ), mọi chai quét ra đúng lô, lô phụ liệu dùng và (nếu dầu quế chưng tại xưởng) đúng đồi quế.
  - Lưu ý lịch: ủ 21–28 ngày (dầu quế 4–6 tuần) nằm giữa pha trộn và lô thành phẩm đầu tiên, nên lô QR thật đầu tiên có sớm nhất sau 1 tháng kể từ ngày xưởng chạy lệnh đầu. Phải có phần lệnh sản xuất chạy được từ đầu GĐ2.
- **GĐ3 – Website SEO + Ads + kênh bán (8 – 12/2027).** Đầu ra: website thương hiệu, trang sản phẩm chuẩn SEO, Google Search Console, Merchant Center, Ads chạy thử, Zalo OA, danh sách sản phẩm đăng sàn. Kịp mùa quà Tết 2028.
  - Cổng: 100% trang sản phẩm được Google lập chỉ mục; đơn đầu tiên từ quảng cáo.
- **GĐ4 – OCOP, hữu cơ, thực phẩm (1 – 6/2028).** Đầu ra: nhật ký canh tác vùng kiểm soát, báo cáo sản lượng và truy xuất cho hồ sơ, mở bán trà và bột quế khi giấy tờ ATTP có hiệu lực.
  - Cổng: hồ sơ OCOP nộp được từ dữ liệu hệ thống.

## Quy trình nghiệp vụ mục tiêu

Một chai tinh dầu đi qua 7 bước. Ở mỗi bước có một người ghi một chứng từ, và chứng từ sau tham chiếu chứng từ trước. Nhờ vậy khi quét QR, hệ thống lần ngược được về lô phụ liệu và nơi bán, và về đến đồi quế (với quế đưa thẳng vào lệnh, hoặc dầu quế chưng tại xưởng; dầu quế nhận từ ngoài thì chuỗi dừng ở nơi bán; đã chốt hỗ trợ cả hai nguồn). Mã lô phụ liệu và nơi bán phụ liệu chỉ dùng nội bộ, không ra trang truy xuất công khai.

- **Khai báo vùng** (chủ DN, làm một lần, cập nhật theo mùa): hộ trồng → đồi quế (mã đồi, thôn, xã, diện tích, năm trồng, tọa độ, ảnh) → gắn luồng "vùng kiểm soát" hoặc "thu mua chung".
- **Thu mua / nhập hàng** (thủ kho): chỉ nhập 4 thông tin — người bán, loại nguyên liệu, hạng chất lượng, số cân. Đơn giá tự điền theo bảng giá hạng trong ngày, thành tiền tự tính, đồi quế tự lấy theo người bán. Mỗi dòng (một loại, một hạng) sinh ra một **lô nguyên liệu** có tem QR nội bộ dán lên bao.
  - Phụ liệu (tinh dầu cam ngọt, tuyết tùng, hoắc hương, hồi, DPG, sáp đậu nành, sáp ong, thạch cao…) nhập bằng **phiếu nhập phụ liệu** riêng: nơi bán, phụ liệu, số gram, hạn dùng, số lô nhà cung cấp. Không có đồi và luồng. Mỗi dòng sinh một lô phụ liệu có tem QR, tồn tính theo gram và trừ dần theo từng lệnh.
  - Hàng thương lái → lô thuộc luồng thu mua chung, chỉ đi tiếp sang **bước 2b: xuất bán quế khô** cho DN xuất khẩu.
- **Sơ chế / lưu kho** (thủ kho): phơi, sấy, không cân lại; hệ thống chỉ cần biết lô nào còn trong kho. Trước khi đưa vào sản xuất, nguyên liệu được sàng lọc và phân loại lần 2 bằng tay, không cân; việc này ghi ngay trên lệnh sản xuất ở bước 4.
- **Lệnh sản xuất** (chủ DN tạo, xưởng thực hiện): chọn sản phẩm, công thức và cỡ mẻ (gram) → đưa nguyên liệu vào: lô quế cả lô không cân lại (chỉ luồng vùng kiểm soát; chọn loại sau sàng lọc khi lệnh có quế đưa thẳng vào), lô phụ liệu quét tem rồi gõ gram thực tế đọc trên cân → **ủ** (mã mẻ sinh lúc bắt đầu ủ, dán lên lọ; chưa đủ ngày ủ thì chưa hoàn thành) → sinh **lô thành phẩm** (hoặc lô bán thành phẩm như dầu quế đã ủ, hương nền, dung dịch tẩm): ngày sản xuất, hạn dùng, số cân và số lượng. Sau đó lưu 1 chai mẫu 12 tháng cho tinh dầu khuếch tán.
- **Đóng gói + gán QR** (công nhân xưởng): quét tem đầu và tem cuối của đoạn tem → dải serial được gán vào lô thành phẩm, chuyển trạng thái "trong kho".
- **Bán / xuất kho** (thủ kho): quế khô xuất bán theo cân và theo hạng, giống phiếu nhập — người mua, loại, hạng, số cân. Thành phẩm xuất theo đơn website, sàn, đại lý, quà tặng doanh nghiệp: quét từng tem → trạng thái "đã xuất", gắn kênh và đơn.
- **Khách quét QR** (công khai): trang truy xuất hiện sản phẩm, lô, ngày sản xuất, hạn dùng, vùng quế (xã, thôn, năm trồng, ảnh đồi), chứng nhận, câu chuyện thương hiệu, nút mua lại.

### Phiếu tối giản cho người không rành phần mềm

Nguồn hàng mua theo cân và phân hạng chất lượng, xuất bán cũng vậy. Vì thế phiếu nhập và phiếu xuất cùng một khuôn: chọn người, chọn loại, chọn hạng, gõ số cân. Mọi thứ khác máy tự điền.

| Thông tin | Người dùng làm gì | Máy tự làm |
| --- | --- | --- |
| Người bán / người mua | Bấm chọn trong danh sách (tìm bằng vài chữ đầu tên) | Hiện thôn, xã; gắn đồi quế và luồng nguồn hàng của hộ đó |
| Loại nguyên liệu / hàng | Bấm nút to có ảnh (vỏ quế, quế vụn) | — |
| Hạng chất lượng | Bấm nút hạng của loại vừa chọn | Lấy đơn giá của hạng trong ngày |
| Số cân (kg) | Gõ số | Nhân ra thành tiền, cộng tổng phiếu |
| Ngày, người lập, số phiếu | Không nhập | Tự điền |
| Đơn giá | Chỉ sửa khi trả giá khác bảng | Điền sẵn theo hạng |
| Ghi chú, ảnh | Không bắt buộc, ẩn sau nút "Thêm" | — |

Một phiếu có nhiều dòng khi một người bán nhiều hạng cùng lúc. Mỗi dòng là một lô riêng, nên tồn kho và truy xuất luôn tách theo hạng.

**Phân loại 2 lần, đều làm bằng tay (áp cho quế).** Nguyên liệu quế chỉ có 2 loại: vỏ quế và quế vụn. Phụ liệu không phân hạng và cân theo gram nên không theo các quy tắc cân và giá vốn dưới đây. Lần 1 lúc mua: phân loại sơ bộ và cân, ghi trên phiếu nhập. Lần 2 lúc sàng lọc trước sản xuất: chỉ phân loại, không cân, chỉ cân thành phẩm.

- Không có phiếu sàng lọc riêng. Chọn lô đem sàng và chọn loại sau sàng làm ngay trên lệnh sản xuất, bớt một màn hình cho xưởng.
- Khối lượng quế chỉ ghi 2 lần: cân lúc nhập và cân thành phẩm. Các bước giữa (phơi, sấy, sàng lọc) không cân; lô quế đem sàng bị trừ kho cả lô. Muốn dùng quế lượng nhỏ (ví dụ vỏ quế cho túi thơm) thì cho cả lô qua một lệnh sơ chế, đầu ra là lô phụ liệu "vỏ quế cắt hạt lựu" tính theo gram. Phụ liệu là ngoại lệ có chủ ý: cân từng gram theo sổ tay, mỗi lần xuất cho lệnh ghi một dòng gram thực tế.
- Máy tự tính **hiệu suất** = số cân thành phẩm / số cân nguyên liệu đưa vào, theo từng lệnh và từng người bán. Hiệu suất thấp bất thường là dấu hiệu nguyên liệu kém hoặc hao hụt lớn — anh dùng số này khi thương lượng giá với từng hộ.
- Giá vốn thành phẩm = tổng giá mua các lô quế đưa vào, chia cho số thành phẩm. Phụ liệu, bao bì, nhân công chưa tính (thiết kế chi tiết BR-10); có tính thêm hay không là câu hỏi mở với chủ DN.

**Bảng giá theo hạng** nằm trong danh mục loại hàng hóa. Chủ DN cập nhật giá mỗi sáng, có giá mua và giá bán riêng, lưu lịch sử. Đã chốt: cả vỏ quế và quế vụn đều có 3 hạng — loại 1, loại 2, loại 3 — dùng chung cho cả hai lần phân loại. Bảng giá vì vậy có 6 ô giá mua và 6 ô giá bán.

Quy tắc giao diện cho máy tính xưởng:

- Một màn hình một việc; trang đầu chỉ có 3 nút lớn: **Nhập hàng** , **Xuất hàng** , **Xem tồn kho** .
- Chọn bằng nút, không dùng danh sách thả xuống dài; chữ từ 18px, số tiền hiển thị to.
- Bấm "Lưu" là in ngay phiếu và tem lô. Không có bước duyệt ở xưởng.
- Sai thì sửa được trong ngày. Qua ngày chỉ chủ DN sửa, có ghi lại ai sửa gì.
- Không dùng thuật ngữ phần mềm; dùng đúng chữ ở xưởng: "phiếu cân", "người bán", "loại 1".

Mã hóa đề xuất, sẽ chốt ở giai đoạn 0:

| Đối tượng | Mẫu mã | Ví dụ |
| --- | --- | --- |
| Hộ / nhà cung cấp | NCC-xã-số | NCC-CQ-012 |
| Đồi quế | D-xã-số | D-CQ-012-02 |
| Lô nguyên liệu | NL-năm tháng-số | NL-2702-0045 |
| Lô thành phẩm (= mã mẻ, sinh lúc bắt đầu ủ) | mã công thức-năm tháng ngày-số mẻ | QC1-261117-01; lệnh không có công thức: <SKU>-YYMMDD-NN (TRA10-261117-01), theo BR-20 |
| Lô phụ liệu / bán thành phẩm | mã phụ liệu-năm tháng-số | Q-2611-01 (dầu quế đã ủ) |
| Phiếu nhập phụ liệu | PNP-năm tháng ngày-số | PNP-261117-001 |
| Serial QR | 10 ký tự ngẫu nhiên | K7Q2-MX9P-AT |

Các ví dụ trong bảng là minh họa. Mẫu lô thành phẩm và lô phụ liệu đã chốt theo sổ tay sản xuất (mẫu cũ TP-mã SP-năm tháng-số bị bỏ); lý do ở BR-20 của thiết kế chi tiết.

## Chi phí ước tính và nguồn lực

Tổng công sức ước sơ bộ khoảng 12,5 người-tháng của đội Qwork. Chi tiền mặt năm đầu khoảng 8–16 triệu đồng, chưa gồm quảng cáo và tem. Mọi con số dưới đây là gần đúng, sẽ được thay bằng WBS chi tiết và báo giá thật.

**Công sức phát triển (nội bộ Qwork)**

| Giai đoạn | Vai trò chính | Công sức (người-tháng) |
| --- | --- | --- |
| 0 – Chuẩn hóa | PM / BA | 1,0 |
| 1 – Danh mục + Nhập hàng + Kho nguyên liệu | 1 BE, 1 FE, 0,5 QA | 3,0 |
| 2 – Sản xuất + Truy xuất + QR serial | 1 BE, 1 FE, 0,5 QA | 4,5 (bản đầu 3,5; +1,0 là ước đã duyệt, đầu GĐ2 lập WBS rồi chỉnh) |
| 3 – Website SEO + Ads + kênh bán | 1 FE, 0,5 BE, thiết kế, nội dung | 2,5 |
| 4 – Hồ sơ OCOP / hữu cơ + báo cáo | 0,5 BE, 0,5 FE, BA | 1,5 |
| **Tổng** |  | **12,5** |

**Chi tiền mặt (ước tính, cần báo giá)**

| Hạng mục | Mức gần đúng | Ghi chú |
| --- | --- | --- |
| Tên miền thương hiệu (.vn + .com) | 1–2 triệu đ/năm | Đăng ký sớm, giữ cả tên tiếng Việt không dấu |
| Máy chủ (VPS) + sao lưu | 3–6 triệu đ/năm | Có thể dùng chung hạ tầng Qwork |
| Máy in tem nhiệt | 3–6 triệu đ, mua một lần | In tem QR serial theo cuộn |
| Tem decal chống nước, ruy băng mực | theo sản lượng | Tính vào giá vốn mỗi sản phẩm |
| Máy quét QR 2D cắm USB cho máy tính xưởng | 1–2 triệu đ | Quét tem lô và serial khi đóng gói, xuất kho |
| Ngân sách Google Ads | do chủ DN quyết | Chạy thử nhỏ trước, đo chuyển đổi rồi mới tăng |

Ngân sách 10 triệu đồng cho nguyên liệu giai đoạn lab giữ nguyên, không dùng cho phần mềm. Có thể hoãn máy in tem tới giai đoạn 2 mới mua.

## KPI đo lường thành công

Mỗi giai đoạn chỉ qua cổng khi đạt KPI của mình. Mục tiêu dưới đây là đề xuất, chủ DN chỉnh lại theo thực tế.

| KPI | Giai đoạn | Mục tiêu đề xuất | Cách đo |
| --- | --- | --- | --- |
| Phiếu thu mua nhập trên hệ thống | 1 | ≥ 95% trong 4 tuần liên tục | Đối chiếu với sổ cân |
| Số lô trên hệ thống khớp số bao trong kho | 1 | 100% | Đếm bao hằng tháng |
| Thời gian nhập 1 phiếu tại máy tính xưởng | 1 | ≤ 2 phút | Bấm giờ khi thử với thủ kho |
| Lô thành phẩm truy được về lô quế, người bán và đồi (nhánh quế) và về lô phụ liệu, nơi bán (nhánh phụ liệu) | 2 | 100% (trừ nhánh dầu quế nhận từ ngoài, ghi rõ "nguồn ngoài") | Báo cáo lô thiếu liên kết |
| Lô tinh dầu khuếch tán có mẫu lưu 12 tháng | 2 | 100% | Danh sách "Lô chưa lưu mẫu" |
| Lô hoàn thành khi chưa đủ ngày ủ (không có ghi chú lý do của chủ DN) | 2 | 0 | Nhật ký hệ thống |
| Serial đã bán có trạng thái đúng | 2 | ≥ 98% | Kiểm ngẫu nhiên khi giao hàng |
| Tỉ lệ khách quét QR | 2–3 | ≥ 10% sản phẩm đã bán | Lượt quét / số serial đã xuất |
| Trang sản phẩm được Google lập chỉ mục | 3 | 100% trang sản phẩm | Google Search Console |
| Truy cập tự nhiên từ Google | 3 | Tăng đều mỗi tháng sau 3 tháng | Search Console, Google Analytics |
| Chi phí quảng cáo trên một đơn | 3 | Chủ DN đặt sau 1 tháng chạy thử | Google Ads + đơn trên hệ thống |
| Hồ sơ OCOP xuất được từ hệ thống | 4 | Đủ dữ liệu truy xuất, vùng nguyên liệu, sản lượng | Danh mục hồ sơ OCOP |

Riêng tỉ lệ quét QR không có chuẩn ngành để so. Mức 10% là giả định ban đầu, sẽ đo rồi điều chỉnh.

## Rủi ro và biện pháp

Rủi ro lớn nhất không nằm ở công nghệ mà ở thói quen: nếu xưởng tiếp tục ghi sổ và nhắn Zalo, dữ liệu truy xuất sẽ rỗng và câu chuyện thương hiệu mất gốc.

| Rủi ro | Mức | Biện pháp |
| --- | --- | --- |
| Thủ kho, công nhân không dùng hệ thống, quay lại sổ | Cao | Thiết kế cùng họ từ giai đoạn 0; chạy song song sổ và hệ thống 4 tuần rồi bỏ sổ; chủ DN duyệt phiếu hàng ngày |
| Mất wifi hoặc mất điện tại xưởng | Thấp | Phát 4G dự phòng từ điện thoại; giữ mẫu phiếu giấy để nhập bù khi có mạng; sao lưu máy chủ hằng ngày |
| Dán nhầm tem, gán nhầm lô | Trung bình | Gán theo đoạn tem đầu–cuối; cảnh báo khi dải serial chồng lấn; cho phép tách / hủy tem có ghi lý do |
| Lẫn hàng thương lái vào thành phẩm | Trung bình | Chặn cứng trong lệnh sản xuất; tách khu kho A/B; tem nội bộ khác màu cho 2 luồng |
| Phần sản xuất ở GĐ2 nặng hơn lộ trình gốc (công thức, kho phụ liệu theo gram, ủ, lưu mẫu, thử lưu hương, truy xuất đệ quy; thêm 11 bảng) | Trung bình | Đã tăng GĐ2 từ 3,5 lên 4,5 người-tháng (ước đã duyệt, đầu GĐ2 lập WBS rồi chỉnh), mốc 5–9/2027 giữ nguyên nhưng chưa có dư địa. Nếu trễ, hoãn trước lưu mẫu và thử lưu hương (không chặn gán tem hay xuất hàng theo thiết kế), không hoãn công thức, kho phụ liệu, ủ, truy xuất. Chủ DN và Lead quyết trước khi chốt WBS |
| Lô QR thật đầu tiên đến chậm vì phải ủ 21–28 ngày (dầu quế 4–6 tuần) | Trung bình | Lệnh sản xuất và kho phụ liệu chạy được từ đầu GĐ2; xưởng chạy mẻ thử sớm để cổng GĐ2 không dồn vào cuối giai đoạn |
| Nhập công thức và tồn đầu kỳ phụ liệu chậm hoặc sai gram | Trung bình | Seed 10 công thức từ sổ tay bản 2; chủ DN duyệt công thức trước khi chạy lệnh đầu; công thức đã có lệnh dùng thì không sửa, chỉ tạo phiên bản mới |
| Dầu quế nhận từ ngoài làm chuỗi truy xuất dừng ở nơi bán | Trung bình | Hệ thống hỗ trợ cả hai nguồn và hiện rõ "nguồn ngoài, chưa nối về lô quế"; đã chốt hỗ trợ cả hai nguồn theo ủy quyền #799 |
| Đội Qwork bị kéo sang Essy Pilates | Trung bình | Phân bổ cố định người theo giai đoạn; mỗi giai đoạn ra sản phẩm dùng được ngay, không phụ thuộc giai đoạn sau |
| Lộ thông tin nhạy cảm (giá mua, công nợ, dữ liệu hộ dân) | Trung bình | Trang công khai chỉ đọc dữ liệu được đánh dấu công khai; tên hộ dân chỉ hiện khi họ đồng ý |
| QR bị sao chép để làm hàng giả | Thấp (giai đoạn đầu) | Serial ngẫu nhiên; đếm lượt và nơi quét; cảnh báo trên trang truy xuất |
| Thủ tục ATTP, OCOP, hữu cơ kéo dài | Trung bình | Làm song song từ giai đoạn 0; trà và bột không nằm trên đường găng của các giai đoạn 1–3 |
| Đơn vị hành chính còn thay đổi | Thấp | Danh mục địa bàn có hiệu lực theo ngày và trường "địa danh cũ" |

## Việc cần làm ngay

Có thể bắt đầu giai đoạn 0 ngay từ tuần tới. Phần lớn việc trong 6 tuần đầu là việc của chủ DN, chưa phải việc viết code.

- ☐ Đăng ký tên miền thương hiệu (.vn và .com)
- ☐ Liệt kê các hộ thu mua trực tiếp và đồi quế của gia đình: tên, thôn, xã, diện tích gần đúng, năm trồng
- ☐ Chụp ảnh 1 sổ cân và 1 phiếu nhập thật để thiết kế màn hình đúng thói quen xưởng
- ☐ Ngồi 30 phút với thủ kho: họ đang ghi gì, ở đâu, lúc nào, khó ở đâu
- ☐ Chốt danh sách sản phẩm thành phẩm đợt 1 và quy cách đóng gói (dung tích chai, trọng lượng túi)
- ☑ Chốt 3 điểm sổ tay chưa ghi (đã chốt theo ủy quyền #799): dầu quế hỗ trợ cả hai nguồn (chưng tại xưởng hoặc nhận ngoài); hạn dùng sáp thơm, viên thạch cao, túi vỏ quế nhập tay mỗi lô; lưu mẫu 12 tháng chỉ 6 công thức tinh dầu khuếch tán, có cờ bật thêm
- ☐ Duyệt danh mục công thức và danh sách phụ liệu (kèm nơi mua) do đội seed từ sổ tay sản xuất bản 2, và kiểm tra gram từng công thức trước GĐ2
- ☐ Hỏi cơ quan quản lý tại Lào Cai về hồ sơ công bố sản phẩm và điều kiện ATTP cho trà, bột quế
- ☐ Chỉ định người của đội Qwork cho giai đoạn 1

Tài liệu tiếp theo: Tài liệu yêu cầu (BRD, user story), ERD và WBS có ước lượng chi tiết. Sau đó là thiết kế trang giới thiệu sản phẩm chuẩn SEO.

## Nguồn

- Báo Lào Cai – Yên Bái chỉ còn 51 xã, phường sau sắp xếp
- Báo Lào Cai – Lào Cai có 99 đơn vị hành chính cấp xã sau sắp xếp
