# Thiết kế chi tiết – Hệ thống Quế Văn Yên

Nov 20, 2026 · @Kevin

Tài liệu cho đội Qwork code giai đoạn 1–3 theo Lộ trình chuyển đổi số. Mọi quyết định nghiệp vụ đã chốt với chủ DN đến ngày 20/11/2026.

## 1. Phạm vi, thuật ngữ, quy ước

Hệ thống gồm 2 ứng dụng dùng chung một cơ sở dữ liệu:

- **App nội bộ (web, cần đăng nhập):** danh mục, nhập hàng, xuất hàng, lệnh sản xuất, tem QR, báo cáo. Chạy trên máy tính xưởng (Windows, Chrome, wifi) và máy tính hoặc điện thoại của chủ DN.
- **Website công khai:** trang thương hiệu, trang sản phẩm chuẩn SEO, trang truy xuất khi quét QR. Render phía máy chủ.

**Trong phạm vi:** giai đoạn 1–3 của lộ trình. **Ngoài phạm vi:** kế toán, hóa đơn điện tử, tích hợp API sàn TMĐT, chế độ offline, đa doanh nghiệp, nhật ký canh tác chi tiết (giai đoạn 4; bảng đã thiết kế sẵn).

**Stack:** theo stack đội Qwork đang dùng. Giả định trong tài liệu: API REST/JSON, cơ sở dữ liệu quan hệ (PostgreSQL), một máy chủ VPS.

### Thuật ngữ

| Thuật ngữ | Nghĩa | Tên trong code |
| --- | --- | --- |
| Nguyên liệu (quế) | Nguyên liệu thu mua từ người bán, chỉ có 2 loại: Vỏ quế, Quế vụn. Quản lý theo cân (kg), cả lô | material |
| Hạng | Loại 1, Loại 2, Loại 3 — áp cho cả 2 nguyên liệu, dùng chung cho cả 2 lần phân loại | grade |
| Người bán | Hộ dân, gia đình hoặc thương lái bán nguyên liệu (nhà cung cấp) | supplier |
| Đồi quế | Một mảnh trồng quế của một người bán | plot |
| Luồng | CONTROLLED (vùng kiểm soát: đồi nhà, hộ mua trực tiếp) hoặc GENERAL (thu mua chung: thương lái) | stream |
| Phiếu nhập | Một lần mua từ một người bán, nhiều dòng | receipt |
| Lô nguyên liệu | Một dòng phiếu nhập = 1 nguyên liệu + 1 hạng + số cân. Đơn vị tồn kho nhỏ nhất, không chia nhỏ | material_lot |
| Phụ liệu | Mọi thứ ngoài quế dùng để làm thành phẩm: tinh dầu cam ngọt, tuyết tùng, hoắc hương, hồi, DPG, sáp đậu nành, sáp ong, bột thạch cao, dăm gỗ… và các **bán thành phẩm** tự làm (dầu quế đã ủ, hương nền TT1/TT2, dung dịch tẩm, vỏ quế cắt hạt lựu). Quản lý theo gram, được dùng từng phần | ingredient |
| Phiếu nhập phụ liệu | Một lần mua phụ liệu từ một nơi bán, nhiều dòng. Không có đồi, không có luồng | ingredient_receipt |
| Lô phụ liệu | Một dòng phiếu nhập phụ liệu, hoặc đầu ra bán thành phẩm của một lệnh sản xuất. Có tồn gram, trừ dần mỗi lần xuất cho lệnh | ingredient_lot |
| Công thức | Danh mục thành phần và gram cho một mẻ chuẩn (QC1, QC2, RQ1, RQ2, TQ1, TQ2, hương nền TT1/TT2, dung dịch tẩm, sáp thơm, viên thạch cao, túi vỏ quế…). Có phiên bản; thành phần có thể là bán thành phẩm của công thức khác (lồng nhau) | recipe, recipe_item |
| Lệnh sản xuất | Chọn công thức và cỡ mẻ; đưa vào lô quế (cả lô, kg) và lô phụ liệu (theo gram); pha xong thì **ủ**; ủ đủ ngày thì nhập đầu ra: một lô thành phẩm hoặc một lô bán thành phẩm. Lệnh không có công thức (trà, ống quế…) vẫn chạy như cũ: sàng lọc phân loại lần 2 không cân | production_order |
| Ủ | Giai đoạn để hỗn hợp đã pha nghỉ kín, ngày đủ tối thiểu thì mới nhập thành phẩm. Lệnh ở trạng thái CURING | cure_*, status CURING |
| Mã mẻ | Mã lô sinh ngay lúc bắt đầu ủ để ghi lên lọ ủ; về sau là mã của lô thành phẩm hoặc lô bán thành phẩm | production_order.batch_code |
| Lô thành phẩm | Kết quả của lệnh, có số cân và số lượng | product_lot |
| Lưu mẫu | Giữ 1 chai của mỗi lô thành phẩm trong 12 tháng để đối chiếu khi khách phản ánh | retained_sample |
| Thử lưu hương | Đợt thử 28 ngày cho sáp thơm, viên thạch cao, túi vỏ quế: cân và chấm điểm ngửi ở ngày 0-1-3-7-14-21-28 | scent_trial |
| Serial | Mã QR riêng của từng chai, túi | serial |
| Cuộn tem | Một dải serial liên tiếp được in cùng lúc | label_roll |
| Phiếu xuất | Bán quế khô theo hạng + cân, hoặc xuất thành phẩm theo serial | issue |

### Quy ước chung

- **Quế (material_lot) — khối lượng chỉ ghi 2 lần:** lúc nhập (số cân mỗi lô nguyên liệu) và lúc ra thành phẩm (số cân lô thành phẩm, hoặc số cân trên phiếu xuất quế khô). Không có bảng hay cột nào lưu khối lượng quế ở bước giữa.
- **Quế — tồn kho tính theo lô:** một lô hoặc còn trong kho, hoặc đã dùng hết. Không có lô quế dùng một phần. Muốn dùng quế với lượng nhỏ (ví dụ 480 g vỏ quế cho 40 túi) thì cho cả lô quế qua một lệnh sơ chế, đầu ra là lô phụ liệu "vỏ quế cắt hạt lựu" tính theo gram.
- **Phụ liệu (ingredient_lot) — ngoại lệ có chủ ý:** sổ tay sản xuất cân từng gram trên cân điện tử (sai số ±0,05 g), một lô phụ liệu dùng được cho nhiều lệnh. Vì vậy lô phụ liệu có tồn gram (remaining_g), và **mỗi lần xuất cho một lệnh ghi một dòng production_ingredient với gram thực tế**. Đó là dòng xuất kho phụ liệu; tồn lô giảm đúng số gram đó.
- Đơn vị: khối lượng quế và thành phẩm kg, kiểu numeric(10,2) (output_weight_kg của lô thành phẩm numeric(10,3) vì mẻ tinh dầu chỉ vài chục gram); khối lượng phụ liệu gram, kiểu numeric(10,2); tiền VND, kiểu bigint, không lẻ. Công thức luôn tính theo gram, không theo ml (ml chỉ để tham khảo, sổ tay trang 3).
- Thời gian lưu UTC, hiển thị giờ Việt Nam (UTC+7). "Trong ngày" tính theo giờ Việt Nam.
- Khóa chính id kiểu bigint tự tăng. Mã nghiệp vụ (code) là cột riêng, duy nhất, sinh phía máy chủ.
- Không xóa cứng dữ liệu nghiệp vụ. Dùng status (ACTIVE/INACTIVE, hoặc CANCELLED với chứng từ).
- Giao diện hiển thị tiếng Việt, dùng đúng chữ ở xưởng: "phiếu cân", "người bán", "loại 1".

## 2. Vai trò và phân quyền

Có 2 vai trò đăng nhập và 1 vai trò công khai. Thủ kho và công nhân dùng chung vai trò WORKSHOP, nhưng mỗi người có tài khoản riêng để nhật ký ghi đúng người.

| Chức năng | OWNER (chủ DN) | WORKSHOP (xưởng) | PUBLIC (khách) |
| --- | --- | --- | --- |
| Danh mục: thêm, sửa, ngừng dùng | Có | Không (chỉ xem) | Không |
| Thêm nhanh người bán mới ngay trên phiếu nhập | Có | Có (tên, thôn, luồng mặc định GENERAL; chủ DN duyệt sau) | Không |
| Bảng giá theo hạng | Có | Không | Không |
| Lập phiếu nhập, phiếu xuất | Có | Có | Không |
| Sửa, hủy phiếu trong ngày lập | Có | Có, chỉ phiếu của mình | Không |
| Sửa, hủy phiếu sau ngày lập | Có, bắt buộc ghi lý do | Không | Không |
| Công thức, danh mục phụ liệu: thêm, sửa, tạo phiên bản | Có | Chỉ xem (không thấy giá) | Không |
| Lập phiếu nhập phụ liệu | Có | Có | Không |
| Tạo lệnh sản xuất | Có | Không | Không |
| Quét lô quế và lô phụ liệu đưa vào, gõ gram, bắt đầu ủ, nhập cân thành phẩm, hoàn thành lệnh | Có | Có | Không |
| Ủ thêm, bỏ qua kiểm tra ngày ủ (bắt buộc lý do) | Có | Ủ thêm: có; bỏ qua kiểm tra: không | Không |
| Lưu mẫu: ghi nhận | Có | Có | Không |
| Lưu mẫu: hủy mẫu hết hạn, bật cờ lưu mẫu cho sản phẩm | Có | Không | Không |
| Thử lưu hương: tạo đợt, đóng đợt; nhập cân và điểm ngửi | Có | Chỉ nhập cân và điểm ngửi | Không |
| Tạo cuộn tem, in tem | Có | Không | Không |
| Gán đoạn tem vào lô thành phẩm, hủy tem lỗi | Có | Có | Không |
| Thu hồi lô thành phẩm | Có | Không | Không |
| Báo cáo tồn kho | Có | Có (không thấy giá) | Không |
| Báo cáo giá vốn, hiệu suất, công nợ | Có | Không | Không |
| Nội dung website, SEO | Có | Không | Không |
| Quản lý tài khoản | Có | Không | Không |
| Xem website, trang truy xuất | Có | Có | Có |

Quyền phải kiểm tra ở API, không chỉ ẩn nút trên giao diện. Với WORKSHOP, mọi trường giá (đơn giá, thành tiền, giá vốn) bị loại khỏi response của báo cáo, trừ chính phiếu người đó đang lập.

## 3. Mô hình dữ liệu

Truy xuất chỉ là đi theo khóa ngoại. Mỗi mũi tên đi từ bảng con (có cột *_id) sang bảng cha. Chuỗi ngược từ một chai về người bán:

```
serial → product_lot → production_order ─┬→ material_lot → receipt → supplier + plot → area      (quế đưa thẳng vào lệnh)
                                          └→ production_ingredient → ingredient_lot ─┬→ ingredient_receipt   (phụ liệu mua ngoài: dừng ở nơi bán)
                                                                                      └→ production_order → (lặp lại)  (bán thành phẩm tự làm)
```

Bán thành phẩm lồng nhau nhiều tầng (ví dụ viên thạch cao ← dung dịch tẩm ← hương nền TT1 ← dầu quế đã ủ ← dầu quế mới chưng ← lô quế NL), nên truy xuất đi theo đệ quy (WITH RECURSIVE) qua production_ingredient, không có số tầng cố định.

ERD · 29 bảng nghiệp vụ (18 bảng cũ + 11 bảng mới), mũi tên = khóa ngoại trỏ về bảng cha. Sơ đồ ảnh trong bản docx chưa chuyển sang md; cần vẽ lại cho đủ 11 bảng mới.

**11 bảng mới (mục 4):** ingredient, ingredient_receipt, ingredient_lot (kho phụ liệu); recipe, recipe_item (công thức); production_ingredient (dòng xuất kho phụ liệu cho lệnh); retained_sample (lưu mẫu); scent_trial, scent_trial_sample, scent_trial_reading, scent_trial_score (thử lưu hương 28 ngày).

Quan hệ cần lưu ý:

- material_lot trỏ tới production_order hoặc issue_line, hoặc chưa trỏ tới đâu — không bao giờ cả hai.
- Một production_order sinh đúng một lô đầu ra: product_lot (output_kind = PRODUCT, UNIQUE theo lệnh) hoặc ingredient_lot (output_kind = INTERMEDIATE, UNIQUE theo lệnh).
- Một ingredient_lot có đúng một nguồn: ingredient_receipt (mua ngoài) hoặc production_order (tự làm). Không có lô phụ liệu mồ côi; nhờ vậy chuỗi truy xuất luôn kết thúc ở người bán quế hoặc nơi bán phụ liệu.
- production_ingredient nối production_order với ingredient_lot, mỗi dòng là một lần xuất kho theo gram; tồn lô: remaining_g = initial_g − Σ actual_g của các dòng.
- recipe_item trỏ tới ingredient. Một ingredient tự làm trỏ ngược về công thức làm ra nó (recipe.output_ingredient_id), nên công thức lồng nhau đi qua ingredient, không qua khóa ngoại recipe → recipe.
- production_order.recipe_id trỏ đúng một phiên bản công thức. Công thức đã có lệnh dùng thì không sửa, chỉ tạo phiên bản mới.
- serial.issue_id là phiếu xuất đang hiệu lực của tem đó.

Các bảng không vẽ trong sơ đồ (chi tiết ở mục 4): goods_type, certificate, farm_log, slug_redirect, site_page, app_user, audit_log, code_counter, setting.

## 4. Đặc tả bảng dữ liệu

DDL dưới đây viết cho PostgreSQL và là nguồn chuẩn cho migration đầu tiên. Enum viết dạng text + CHECK để dễ thêm giá trị. Cột created_at, updated_at (timestamptz) có ở mọi bảng, không ghi lại cho gọn.

```sql
-- ===== DANH MỤC =====
CREATE TABLE area ( -- địa bàn hành chính: Tỉnh > Xã > Thôn
 id bigserial PRIMARY KEY,
 code text UNIQUE NOT NULL,
 level text NOT NULL CHECK (level IN ('PROVINCE','COMMUNE','VILLAGE')),
 name text NOT NULL, -- 'Lào Cai', 'Châu Quế', 'Thôn 3' ...
 parent_id bigint REFERENCES area(id), -- NULL chỉ với PROVINCE
 former_name text, -- 'địa danh cũ': 'huyện Văn Yên, tỉnh Yên Bái'
 valid_from date NOT NULL DEFAULT '2025-07-01',
 valid_to date,
 status text NOT NULL DEFAULT 'ACTIVE'
);

CREATE TABLE goods_type ( -- loại hàng hóa
 id bigserial PRIMARY KEY,
 code text UNIQUE NOT NULL,
 name text NOT NULL, -- 'Nguyên liệu quế', 'Tinh dầu', 'Túi thơm', 'Trà', 'Bột', 'Ống quế', 'Quế khô XK'
 grp text NOT NULL CHECK (grp IN ('MATERIAL','PRODUCT')),
 is_food boolean NOT NULL DEFAULT false, -- true: chặn đăng bán khi chưa có giấy tờ ATTP (BR-14)
 status text NOT NULL DEFAULT 'ACTIVE'
);

CREATE TABLE material ( -- chỉ 2 bản ghi: VQ Vỏ quế, QV Quế vụn
 id bigserial PRIMARY KEY,
 code text UNIQUE NOT NULL,
 name text NOT NULL,
 goods_type_id bigint NOT NULL REFERENCES goods_type(id),
 image_url text, -- ảnh trên nút bấm
 sort_order int NOT NULL DEFAULT 0,
 status text NOT NULL DEFAULT 'ACTIVE'
);

CREATE TABLE grade ( -- Loại 1/2/3 cho mỗi nguyên liệu
 id bigserial PRIMARY KEY,
 material_id bigint NOT NULL REFERENCES material(id),
 rank smallint NOT NULL CHECK (rank BETWEEN 1 AND 9),
 name text NOT NULL, -- 'Loại 1'
 status text NOT NULL DEFAULT 'ACTIVE',
 UNIQUE (material_id, rank)
);

CREATE TABLE price ( -- bảng giá theo hạng, theo ngày
 id bigserial PRIMARY KEY,
 grade_id bigint NOT NULL REFERENCES grade(id),
 price_date date NOT NULL,
 buy_price bigint NOT NULL CHECK (buy_price >= 0), -- VND/kg
 sell_price bigint NOT NULL CHECK (sell_price >= 0), -- VND/kg
 updated_by bigint NOT NULL REFERENCES app_user(id),
 UNIQUE (grade_id, price_date)
);

CREATE TABLE supplier ( -- người bán
 id bigserial PRIMARY KEY,
 code text UNIQUE NOT NULL, -- NCC-CQ-012
 name text NOT NULL,
 kind text NOT NULL CHECK (kind IN ('FAMILY','FARMER','TRADER')),
 phone text,
 area_id bigint NOT NULL REFERENCES area(id), -- FAMILY/FARMER: cấp VILLAGE; TRADER: tối thiểu COMMUNE
 stream text NOT NULL CHECK (stream IN ('CONTROLLED','GENERAL')),
 public_consent boolean NOT NULL DEFAULT false, -- đồng ý hiện tên trên trang truy xuất
 approved boolean NOT NULL DEFAULT true, -- false khi xưởng thêm nhanh (BR-03)
 status text NOT NULL DEFAULT 'ACTIVE',
 CHECK (kind <> 'TRADER' OR stream = 'GENERAL')
);

CREATE TABLE plot ( -- đồi quế
 id bigserial PRIMARY KEY,
 code text UNIQUE NOT NULL, -- D-CQ-012-02
 supplier_id bigint NOT NULL REFERENCES supplier(id),
 area_id bigint NOT NULL REFERENCES area(id), -- cấp VILLAGE
 area_ha numeric(6,2),
 planted_year smallint,
 lat numeric(9,6),
 lng numeric(9,6),
 photo_urls jsonb NOT NULL DEFAULT '[]',
 is_default boolean NOT NULL DEFAULT false, -- đồi tự gắn khi người bán có 1 đồi hoặc đồi mặc định
 status text NOT NULL DEFAULT 'ACTIVE'
);

CREATE TABLE farm_log ( -- nhật ký canh tác (giai đoạn 4)
 id bigserial PRIMARY KEY, plot_id bigint NOT NULL REFERENCES plot(id),
 log_date date NOT NULL, activity text NOT NULL, note text, photo_urls jsonb NOT NULL DEFAULT '[]'
);

CREATE TABLE customer ( -- người mua
 id bigserial PRIMARY KEY,
 code text UNIQUE NOT NULL,
 name text NOT NULL,
 kind text NOT NULL CHECK (kind IN ('EXPORTER','AGENT','CORPORATE','RETAIL','MARKETPLACE')),
 phone text, address text,
 status text NOT NULL DEFAULT 'ACTIVE'
);

CREATE TABLE product ( -- sản phẩm thành phẩm (cả quế khô XK nếu bán theo SKU)
 id bigserial PRIMARY KEY,
 sku text UNIQUE NOT NULL, -- TD10
 name text NOT NULL, -- 'Tinh dầu quế Văn Yên 10 ml'
 slug text UNIQUE NOT NULL, -- 'tinh-dau-que-van-yen-10ml'
 goods_type_id bigint NOT NULL REFERENCES goods_type(id),
 size_label text NOT NULL, -- '10 ml', '50 g'
 unit text NOT NULL, -- 'chai', 'túi', 'hộp'
 shelf_life_months smallint, -- hạn dùng mặc định của lô (BR-11): 18 tinh dầu khuếch tán, 24 tinh dầu quế 100% (sổ tay tr.6, tr.8). NULL với sáp thơm, viên thạch cao, túi vỏ quế (sổ tay chưa ghi): khi tạo lô thành phẩm bắt buộc nhập exp_date tay
 requires_retention_sample boolean NOT NULL DEFAULT false, -- true: mỗi lô thành phẩm phải lưu mẫu (BR-29). Seed true cho 6 sản phẩm tinh dầu khuếch tán; bật thêm cho sản phẩm khác khi chủ DN chốt
 recipe_code text, -- mã công thức mặc định (QC1, Q100...); nhiều sản phẩm (10 ml, 30 ml) dùng chung một mã. NULL: sản phẩm không có công thức (trà, ống quế)
 retail_price bigint,
 short_desc text,
 story_md text, -- câu chuyện sản phẩm (markdown)
 usage_md text, -- cách dùng, lưu ý
 seo_title varchar(70),
 seo_description varchar(170),
 images jsonb NOT NULL DEFAULT '[]', -- [{url, alt}]
 buy_links jsonb NOT NULL DEFAULT '[]', -- [{channel, url}] nút mua trên sàn
 serial_tracked boolean NOT NULL DEFAULT true, -- false: hàng quà tặng không dán tem (thiếp, túi giấy…)
 status text NOT NULL DEFAULT 'DRAFT' CHECK (status IN ('DRAFT','PUBLISHED','HIDDEN'))
);

CREATE TABLE slug_redirect ( -- 301 khi đổi slug sản phẩm
 old_slug text PRIMARY KEY, product_id bigint NOT NULL REFERENCES product(id)
);

CREATE TABLE certificate ( -- OCOP, hữu cơ, ATTP, công bố sản phẩm
 id bigserial PRIMARY KEY,
 kind text NOT NULL CHECK (kind IN ('OCOP','ORGANIC','FOOD_SAFETY','DECLARATION')),
 number text NOT NULL, issuer text, issued_on date, expires_on date,
 stars smallint, -- OCOP 3-5 sao
 file_url text,
 product_id bigint REFERENCES product(id),
 plot_id bigint REFERENCES plot(id),
 is_public boolean NOT NULL DEFAULT true,
 CHECK (product_id IS NOT NULL OR plot_id IS NOT NULL)
);

-- ===== NHẬP HÀNG / KHO =====
CREATE TABLE receipt ( -- phiếu nhập (phiếu cân)
 id bigserial PRIMARY KEY,
 code text UNIQUE NOT NULL, -- PN-261120-001
 receipt_date date NOT NULL,
 supplier_id bigint NOT NULL REFERENCES supplier(id),
 total_kg numeric(10,2) NOT NULL,
 total_amount bigint NOT NULL,
 note text, photo_url text,
 status text NOT NULL DEFAULT 'SAVED' CHECK (status IN ('SAVED','CANCELLED')),
 cancel_reason text,
 created_by bigint NOT NULL REFERENCES app_user(id)
);

CREATE TABLE material_lot ( -- 1 dòng phiếu nhập = 1 lô
 id bigserial PRIMARY KEY,
 code text UNIQUE NOT NULL, -- NL-2611-0045
 receipt_id bigint NOT NULL REFERENCES receipt(id),
 line_no smallint NOT NULL,
 material_id bigint NOT NULL REFERENCES material(id),
 grade_id bigint NOT NULL REFERENCES grade(id), -- hạng lần 1
 weight_kg numeric(10,2) NOT NULL CHECK (weight_kg > 0),
 unit_price bigint NOT NULL CHECK (unit_price >= 0),
 amount bigint NOT NULL, -- = round(weight_kg * unit_price)
 plot_id bigint REFERENCES plot(id),
 stream text NOT NULL, -- chụp từ supplier.stream lúc lưu
 status text NOT NULL DEFAULT 'IN_STOCK'
 CHECK (status IN ('IN_STOCK','RESERVED','USED','SOLD','CANCELLED')),
 production_order_id bigint REFERENCES production_order(id), -- khi RESERVED/USED
 issue_line_id bigint REFERENCES issue_line(id), -- khi SOLD
 UNIQUE (receipt_id, line_no)
);

-- ===== PHỤ LIỆU / CÔNG THỨC (theo sổ tay sản xuất) =====
CREATE TABLE ingredient ( -- danh mục phụ liệu và bán thành phẩm, tính theo gram
 id bigserial PRIMARY KEY,
 code text UNIQUE NOT NULL, -- Q, QM, CAM, TTV, HH, HOI, DPG, SD, SO, TC, TT1, DDT... (mã lô phụ liệu lấy mã này)
 name text NOT NULL, -- 'Dầu quế đã ủ', 'Tinh dầu cam ngọt'
 kind text NOT NULL CHECK (kind IN ('ESSENTIAL_OIL','SOLVENT','WAX','MINERAL','BOTANICAL','BLEND','OTHER')), -- BLEND: hương nền, dung dịch tẩm
 density_g_ml numeric(5,3), -- g/ml, chỉ để quy đổi tham khảo (sổ tay tr.4-5), công thức không dùng
 track_stock boolean NOT NULL DEFAULT true, -- false: nước sạch, không quản lý lô và tồn
 requires_coa boolean NOT NULL DEFAULT false, -- true: tinh dầu mua ngoài, nhà cung cấp phải gửi phiếu kiểm nghiệm cho từng lô (tr.4)
 shelf_life_months smallint, -- hạn dùng mặc định của lô tự làm (Q: 24 tháng, tr.8); lô mua ngoài lấy hạn trên nhãn
 status text NOT NULL DEFAULT 'ACTIVE'
);

CREATE TABLE ingredient_receipt ( -- phiếu nhập phụ liệu
 id bigserial PRIMARY KEY,
 code text UNIQUE NOT NULL, -- PNP-261117-001
 receipt_date date NOT NULL,
 vendor_name text NOT NULL, -- nơi bán; 'Nguồn gia đình' với dầu quế mới chưng nhận từ gia đình
 vendor_phone text,
 note text, photo_url text,
 status text NOT NULL DEFAULT 'SAVED' CHECK (status IN ('SAVED','CANCELLED')),
 cancel_reason text,
 created_by bigint NOT NULL REFERENCES app_user(id)
);

CREATE TABLE recipe ( -- công thức, một dòng = một phiên bản
 id bigserial PRIMARY KEY,
 code text NOT NULL, -- QC1, QC2, RQ1, RQ2, TQ1, TQ2, TT1, TT2, DDT, SAP, VTC, TUI, U-Q, Q100, SC-VQH
 version smallint NOT NULL DEFAULT 1,
 name text NOT NULL, -- 'Quế Cam – dịu nhẹ'
 output_kind text NOT NULL CHECK (output_kind IN ('PRODUCT','INTERMEDIATE')),
 output_ingredient_id bigint REFERENCES ingredient(id), -- bắt buộc khi INTERMEDIATE: bán thành phẩm làm ra
 base_batch_g numeric(10,2) NOT NULL CHECK (base_batch_g > 0), -- tổng gram mẻ chuẩn = Σ qty_g (mỗi nhóm lựa chọn tính 1 phương án)
 base_label text, -- 'mẻ 100 ml ≈ 89,72 g', 'mẻ nhỏ 2 tấm sáp'
 cure_min_days smallint NOT NULL DEFAULT 0, -- ngày ủ tối thiểu; 0 = không ủ
 cure_max_days smallint, -- tham khảo, không chặn
 retain_months smallint, -- số tháng giữ mẫu (12 cho QC1–TQ2); NULL = dùng setting.retain_default_months (12). Lô có phải lưu mẫu hay không do product.requires_retention_sample quyết định, không do cột này
 status text NOT NULL DEFAULT 'DRAFT' CHECK (status IN ('DRAFT','ACTIVE','RETIRED')),
 note text, -- các bước thủ công, nhiệt độ, lưu ý (sổ tay)
 UNIQUE (code, version),
 CHECK ((output_kind = 'INTERMEDIATE') = (output_ingredient_id IS NOT NULL))
);
-- Mỗi code chỉ có tối đa một phiên bản ACTIVE: CREATE UNIQUE INDEX ON recipe(code) WHERE status = 'ACTIVE'

CREATE TABLE recipe_item ( -- thành phần công thức, gram trên mẻ chuẩn
 id bigserial PRIMARY KEY,
 recipe_id bigint NOT NULL REFERENCES recipe(id),
 line_no smallint NOT NULL,
 ingredient_id bigint NOT NULL REFERENCES ingredient(id), -- có thể là bán thành phẩm của công thức khác (lồng nhau)
 qty_g numeric(10,2) NOT NULL CHECK (qty_g > 0),
 alt_group smallint, -- các dòng cùng alt_group là phương án thay nhau (TT1 hoặc TT2); lệnh chọn đúng một
 is_optional boolean NOT NULL DEFAULT false, -- bột màu khoáng
 note text,
 UNIQUE (recipe_id, line_no)
);
-- % khối lượng không lưu: = qty_g / base_batch_g × 100 (khớp cột "% khối lượng" của sổ tay)

-- ===== SẢN XUẤT / TRUY XUẤT =====
CREATE TABLE production_order (
 id bigserial PRIMARY KEY,
 code text UNIQUE NOT NULL, -- LSX-2611-003
 order_date date NOT NULL,
 output_kind text NOT NULL DEFAULT 'PRODUCT' CHECK (output_kind IN ('PRODUCT','INTERMEDIATE')),
 product_id bigint REFERENCES product(id), -- NULL khi INTERMEDIATE (đầu ra là lô phụ liệu)
 recipe_id bigint REFERENCES recipe(id), -- phiên bản công thức; NULL với lệnh không công thức
 target_batch_g numeric(10,2), -- cỡ mẻ định pha (gram); máy gợi ý lượng cân = qty_g × target_batch_g / base_batch_g
 output_grade_id bigint REFERENCES grade(id), -- loại sau sàng lọc (lần 2), chỉ lệnh PRODUCT có lô quế đưa thẳng vào
 batch_code text UNIQUE, -- mã mẻ = mã lô đầu ra; sinh khi bắt đầu ủ (lệnh có ủ) hoặc khi hoàn thành (lệnh không ủ)
 status text NOT NULL DEFAULT 'DRAFT' CHECK (status IN ('DRAFT','CURING','DONE','CANCELLED')),
 cure_started_at timestamptz, -- lúc bấm "Đã pha xong, bắt đầu ủ"
 cure_ready_on date, -- ngày sớm nhất được nhập đầu ra = ngày bắt đầu ủ + cure_min_days; gia hạn được
 cure_check_note text, -- kết quả ngửi kiểm tra cuối ủ, lý do gia hạn (sổ tay A.1 bước 6)
 note text,
 created_by bigint NOT NULL REFERENCES app_user(id),
 started_by bigint REFERENCES app_user(id),
 done_by bigint REFERENCES app_user(id),
 done_at timestamptz,
 cancel_reason text,
 CHECK ((output_kind = 'PRODUCT' AND product_id IS NOT NULL)
 OR (output_kind = 'INTERMEDIATE' AND product_id IS NULL AND recipe_id IS NOT NULL))
);

CREATE TABLE ingredient_lot ( -- lô phụ liệu: mua ngoài hoặc đầu ra bán thành phẩm của một lệnh
 id bigserial PRIMARY KEY,
 code text UNIQUE NOT NULL, -- Q-2610-01 (mẫu <mã phụ liệu>-YYMM-NN, BR-20)
 ingredient_id bigint NOT NULL REFERENCES ingredient(id),
 ingredient_receipt_id bigint REFERENCES ingredient_receipt(id), -- nguồn 1: mua ngoài
 line_no smallint,
 production_order_id bigint UNIQUE REFERENCES production_order(id), -- nguồn 2: tự làm (lệnh INTERMEDIATE DONE)
 vendor_lot_no text, -- số lô trên nhãn nhà cung cấp
 coa_url text, -- phiếu kiểm nghiệm
 initial_g numeric(10,2) NOT NULL CHECK (initial_g > 0), -- gram nhập hoặc gram làm ra
 remaining_g numeric(10,2) NOT NULL CHECK (remaining_g >= 0 AND remaining_g <= initial_g), -- trừ khi thêm dòng production_ingredient
 exp_date date, -- mua ngoài: theo nhãn; tự làm: mfg + ingredient.shelf_life_months
 input_weight_kg numeric(10,2), -- lô tự làm từ quế: Σ kg lô quế đưa vào (cho báo cáo hiệu suất)
 status text NOT NULL DEFAULT 'IN_STOCK' CHECK (status IN ('IN_STOCK','DEPLETED','CANCELLED')),
 UNIQUE (ingredient_receipt_id, line_no),
 CHECK ((ingredient_receipt_id IS NOT NULL AND line_no IS NOT NULL AND production_order_id IS NULL)
 OR (ingredient_receipt_id IS NULL AND line_no IS NULL AND production_order_id IS NOT NULL))
);

CREATE TABLE production_ingredient ( -- dòng xuất kho phụ liệu cho lệnh: một dòng = một lần múc theo gram
 id bigserial PRIMARY KEY,
 production_order_id bigint NOT NULL REFERENCES production_order(id),
 line_no smallint NOT NULL,
 recipe_item_id bigint REFERENCES recipe_item(id), -- NULL: dòng ngoài công thức (ví dụ trang trí sáp)
 ingredient_lot_id bigint NOT NULL REFERENCES ingredient_lot(id),
 suggested_g numeric(10,2), -- lượng máy gợi ý; NULL với dòng ngoài công thức
 actual_g numeric(10,2) NOT NULL CHECK (actual_g > 0), -- gram thực tế trên cân điện tử, lỡ tay thì ghi số thật
 created_by bigint NOT NULL REFERENCES app_user(id),
 UNIQUE (production_order_id, line_no)
);
-- Thêm dòng: remaining_g -= actual_g (SELECT … FOR UPDATE lô). Xóa dòng (chỉ khi lệnh DRAFT): cộng lại. Lệnh CURING trở đi: dòng bất biến.

CREATE TABLE product_lot ( -- 1 lệnh PRODUCT DONE sinh đúng 1 lô thành phẩm
 id bigserial PRIMARY KEY,
 code text UNIQUE NOT NULL, -- QC1-261117-01 (= production_order.batch_code)
 production_order_id bigint UNIQUE NOT NULL REFERENCES production_order(id),
 product_id bigint NOT NULL REFERENCES product(id),
 blend_date date NOT NULL, -- ngày pha = ngày bắt đầu ủ (lệnh không ủ: = mfg_date); là phần YYMMDD trong mã lô
 mfg_date date NOT NULL, -- ngày xong ủ, đóng chai, nhập thành phẩm
 exp_date date NOT NULL, -- mặc định mfg_date + product.shelf_life_months; product.shelf_life_months NULL thì không có mặc định, bắt nhập tay (BR-11)
 input_weight_kg numeric(10,2) NOT NULL DEFAULT 0, -- tổng weight_kg các lô QUẾ đưa vào (chụp lại); 0 khi chỉ dùng phụ liệu
 input_cost bigint NOT NULL DEFAULT 0, -- tổng amount các lô quế đưa vào (phụ liệu chưa tính giá, BR-10)
 input_ingredient_g numeric(10,2) NOT NULL DEFAULT 0, -- Σ actual_g phụ liệu (chụp lại)
 output_weight_kg numeric(10,3) NOT NULL CHECK (output_weight_kg > 0),
 quantity int NOT NULL CHECK (quantity > 0), -- số chai/túi bán được, không gồm chai lưu mẫu
 yield_pct numeric(5,2), -- output_weight_kg / input_weight_kg * 100; NULL khi input_weight_kg = 0
 unit_cost bigint NOT NULL, -- round(input_cost / quantity)
 status text NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','RECALLED')),
 recall_reason text
);

CREATE TABLE retained_sample ( -- lưu mẫu: 1 chai mỗi lô thành phẩm, giữ 12 tháng (sổ tay A.1 bước 8, tr.6)
 id bigserial PRIMARY KEY,
 product_lot_id bigint UNIQUE NOT NULL REFERENCES product_lot(id),
 sample_qty smallint NOT NULL DEFAULT 1,
 stored_on date NOT NULL,
 retain_until date NOT NULL, -- mặc định stored_on + recipe.retain_months
 location text, -- tủ, kệ
 status text NOT NULL DEFAULT 'RETAINED' CHECK (status IN ('RETAINED','DISPOSED')),
 disposed_on date, note text,
 created_by bigint NOT NULL REFERENCES app_user(id)
);

CREATE TABLE scent_trial ( -- đợt thử lưu hương 28 ngày (sổ tay C.1, tr.13): sáp thơm, viên thạch cao, túi vỏ quế
 id bigserial PRIMARY KEY,
 code text UNIQUE NOT NULL, -- TL-2611-01
 recipe_id bigint NOT NULL REFERENCES recipe(id),
 goal text, -- ví dụ 'so dung dịch tẩm 25% / 35% / 45%'
 started_on date NOT NULL,
 status text NOT NULL DEFAULT 'RUNNING' CHECK (status IN ('RUNNING','DONE','CANCELLED')),
 chosen_variant text, -- biến thể được chọn làm công thức; phải là biến thể đạt cả 4 tiêu chí (mục 7.5). Điểm PASS/FAIL từng biến thể được tính lại khi xem, không lưu
 result text CHECK (result IN ('PASS','FAIL')), -- kết luận cả đợt, người dùng xác nhận: PASS khi đã chọn một biến thể đạt (chosen_variant); FAIL khi không biến thể nào đạt
 longevity_weeks smallint, -- thời gian lưu hương đo thật; chỉ khi có số này mới được in lên bao bì
 conclusion text,
 created_by bigint NOT NULL REFERENCES app_user(id)
);

CREATE TABLE scent_trial_sample ( -- mỗi biến thể làm 3 mẫu giống nhau, đặt 3 nơi
 id bigserial PRIMARY KEY,
 trial_id bigint NOT NULL REFERENCES scent_trial(id),
 sample_code text NOT NULL, -- mã dán trên mẫu
 variant_label text NOT NULL, -- '35%'
 placement text NOT NULL CHECK (placement IN ('WARDROBE','CAR','ROOM')), -- tủ quần áo đóng kín / ô tô / phòng thường
 product_lot_id bigint REFERENCES product_lot(id), -- lô làm ra mẫu, nếu có
 UNIQUE (trial_id, sample_code)
);

CREATE TABLE scent_trial_reading ( -- cân mẫu ở các ngày 0-1-3-7-14-21-28
 id bigserial PRIMARY KEY,
 sample_id bigint NOT NULL REFERENCES scent_trial_sample(id),
 day_no smallint NOT NULL CHECK (day_no IN (0,1,3,7,14,21,28)),
 weight_g numeric(8,2) NOT NULL, -- cân 0,01 g, cùng giờ trong ngày
 read_at timestamptz NOT NULL DEFAULT now(),
 recorded_by bigint NOT NULL REFERENCES app_user(id),
 UNIQUE (sample_id, day_no)
);

CREATE TABLE scent_trial_score ( -- mỗi người ngửi (5-7 người) chấm riêng, không xem điểm người khác
 id bigserial PRIMARY KEY,
 reading_id bigint NOT NULL REFERENCES scent_trial_reading(id),
 panelist text NOT NULL, -- tên người ngửi, có thể không phải người dùng hệ thống
 intensity smallint NOT NULL CHECK (intensity BETWEEN 1 AND 5), -- 1 gần như không ngửi thấy, 5 rất mạnh
 pleasantness smallint NOT NULL CHECK (pleasantness BETWEEN 1 AND 5), -- 1 khó chịu, 5 rất thích
 note text,
 UNIQUE (reading_id, panelist)
);

CREATE TABLE label_roll ( -- cuộn tem
 id bigserial PRIMARY KEY,
 code text UNIQUE NOT NULL, -- CT-2611-01
 serial_count int NOT NULL CHECK (serial_count BETWEEN 1 AND 5000),
 printed_at timestamptz,
 created_by bigint NOT NULL REFERENCES app_user(id)
);

CREATE TABLE serial (
 id bigserial PRIMARY KEY,
 code char(10) UNIQUE NOT NULL, -- Crockford Base32, ngẫu nhiên (BR-16)
 roll_id bigint NOT NULL REFERENCES label_roll(id),
 seq int NOT NULL, -- thứ tự trong cuộn, 1..serial_count
 product_lot_id bigint REFERENCES product_lot(id),
 status text NOT NULL DEFAULT 'UNASSIGNED'
 CHECK (status IN ('UNASSIGNED','IN_STOCK','ISSUED','VOID','RECALLED')),
 issue_id bigint REFERENCES issue(id),
 assigned_at timestamptz, issued_at timestamptz, void_reason text,
 scan_count int NOT NULL DEFAULT 0,
 first_scan_at timestamptz, last_scan_at timestamptz,
 UNIQUE (roll_id, seq)
);

CREATE TABLE scan_event ( -- mỗi lượt khách quét QR
 id bigserial PRIMARY KEY,
 serial_id bigint REFERENCES serial(id), -- NULL khi mã không tồn tại
 code_raw text NOT NULL,
 scanned_at timestamptz NOT NULL DEFAULT now(),
 ip_hash text, -- SHA-256(ip + salt), không lưu IP gốc
 user_agent text
);

-- ===== NGƯỜI MUA CUỐI (mục 6.6) =====
CREATE TABLE buyer ( -- người mua / người dùng cuối cùng
 id bigserial PRIMARY KEY,
 code text UNIQUE NOT NULL, -- NM-000123
 full_name text NOT NULL,
 phone text UNIQUE, -- chuẩn hóa 0xxxxxxxxx (BR-23); NULL khi sàn ẩn số
 email text,
 area_id bigint REFERENCES area(id), -- tỉnh hoặc xã
 address_line text, -- số nhà, đường
 marketing_consent boolean NOT NULL DEFAULT false,
 consent_at timestamptz,
 anonymized_at timestamptz, -- đã xóa thông tin cá nhân theo yêu cầu
 status text NOT NULL DEFAULT 'ACTIVE'
);

-- ===== XUẤT HÀNG =====
CREATE TABLE issue ( -- phiếu xuất
 id bigserial PRIMARY KEY,
 code text UNIQUE NOT NULL, -- PX-261120-002
 issue_date date NOT NULL,
 kind text NOT NULL CHECK (kind IN ('DRY_CINNAMON','PRODUCT')),
 customer_id bigint NOT NULL REFERENCES customer(id),
 channel text NOT NULL CHECK (channel IN ('DIRECT','WEBSITE','SHOPEE','TIKTOK','LAZADA','FACEBOOK_ZALO','AGENT','CORPORATE','EXPORTER','OTHER')),
 order_ref text, -- mã đơn sàn / đơn web
 buyer_id bigint REFERENCES buyer(id), -- người mua cuối (BR-22)
 total_amount bigint NOT NULL,
 status text NOT NULL DEFAULT 'SAVED' CHECK (status IN ('SAVED','CANCELLED')),
 cancel_reason text,
 created_by bigint NOT NULL REFERENCES app_user(id)
);

CREATE TABLE issue_line (
 id bigserial PRIMARY KEY,
 issue_id bigint NOT NULL REFERENCES issue(id),
 line_no smallint NOT NULL,
 -- DRY_CINNAMON: material_id + grade_id + weight_kg (số cân lúc bán)
 material_id bigint REFERENCES material(id),
 grade_id bigint REFERENCES grade(id),
 weight_kg numeric(10,2),
 -- PRODUCT: product_id + quantity (= số serial quét)
 product_id bigint REFERENCES product(id),
 quantity int,
 is_gift boolean NOT NULL DEFAULT false, -- dòng quà tặng kèm đơn: unit_price = 0 (BR-25)
 unit_price bigint NOT NULL, -- VND/kg hoặc VND/đơn vị
 amount bigint NOT NULL,
 CHECK ((material_id IS NOT NULL AND grade_id IS NOT NULL AND weight_kg > 0 AND product_id IS NULL)
 OR (product_id IS NOT NULL AND quantity > 0 AND material_id IS NULL))
);
-- Lô nguồn của dòng quế khô: material_lot.issue_line_id

-- ===== HỆ THỐNG / WEB =====
CREATE TABLE app_user (
 id bigserial PRIMARY KEY, username text UNIQUE NOT NULL, full_name text NOT NULL,
 password_hash text NOT NULL, -- bcrypt/argon2
 role text NOT NULL CHECK (role IN ('OWNER','WORKSHOP')),
 status text NOT NULL DEFAULT 'ACTIVE', last_login_at timestamptz
);

CREATE TABLE audit_log (
 id bigserial PRIMARY KEY, entity text NOT NULL, entity_id bigint NOT NULL,
 action text NOT NULL CHECK (action IN ('CREATE','UPDATE','CANCEL','RECALL','VOID')),
 before jsonb, after jsonb, reason text,
 user_id bigint NOT NULL REFERENCES app_user(id), at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE site_page ( -- trang tĩnh: câu chuyện thương hiệu, giới thiệu, liên hệ
 id bigserial PRIMARY KEY, slug text UNIQUE NOT NULL, title text NOT NULL, body_md text NOT NULL,
 seo_title varchar(70), seo_description varchar(170), og_image_url text,
 status text NOT NULL DEFAULT 'DRAFT' CHECK (status IN ('DRAFT','PUBLISHED'))
);

CREATE TABLE code_counter ( -- số thứ tự mã nghiệp vụ (BR-20), khóa hàng khi cấp số
 prefix text NOT NULL, period text NOT NULL, last_no int NOT NULL DEFAULT 0,
 PRIMARY KEY (prefix, period) -- ví dụ ('PN','261120'), ('QC1','261117'), ('Q','2611')
);

CREATE TABLE setting ( -- cấu hình: domain, ngưỡng cảnh báo quét, khổ tem...
 key text PRIMARY KEY, value jsonb NOT NULL
);
```

Thứ tự tạo bảng khi chạy migration phải xử lý khóa ngoại vòng (material_lot ↔ production_order, issue_line; production_order ↔ ingredient_lot, production_ingredient): tạo bảng trước, thêm FOREIGN KEY sau.

**Index bắt buộc:** material_lot(status, material_id, grade_id), material_lot(production_order_id), serial(product_lot_id), serial(issue_id), scan_event(serial_id, scanned_at), receipt(receipt_date), issue(issue_date), issue(buyer_id), buyer(phone), price(price_date); ingredient_lot(ingredient_id, status, exp_date), production_ingredient(ingredient_lot_id), production_ingredient(production_order_id), production_order(status, cure_ready_on), retained_sample(status, retain_until), recipe_item(ingredient_id), UNIQUE một phiên bản ACTIVE mỗi recipe.code. Truy xuất đệ quy đi qua production_ingredient(ingredient_lot_id) và ingredient_lot(production_order_id), hai index này không được thiếu.

**Dữ liệu khởi tạo (seed):** 2 material (VQ Vỏ quế, QV Quế vụn); 6 grade (Loại 1–3 cho mỗi nguyên liệu); area gồm tỉnh Lào Cai và 9 xã thuộc huyện Văn Yên cũ (Phong Dụ Hạ, Phong Dụ Thượng, Châu Quế, Lâm Giang, Đông Cuông, Tân Hợp, Mậu A, Xuân Ái, Mỏ Vàng) với former_name = 'huyện Văn Yên, tỉnh Yên Bái'; thôn do chủ DN nhập; 1 tài khoản OWNER.

**Seed phụ liệu và công thức** (nguồn: sổ tay sản xuất, bản 2, ngày 17/11/2026; số trang là trang trong PDF):

- **ingredient** (tr.4–5, 9–12): Q dầu quế đã ủ (1,05), QM dầu quế mới chưng (1,05), CAM cam ngọt (0,845), TTV tuyết tùng Virginia, không dùng Atlas (0,95), HH hoắc hương (0,96), HOI hồi (0,98), DPG loại mỹ phẩm (1,02), SD sáp đậu nành loại cột, SO sáp ong vàng đã lọc, TC bột thạch cao, BM bột màu khoáng nâu quế (tùy chọn), DG dăm gỗ thông bào mỏng, HT hạt thạch cao 3–5 mm, VQH vỏ quế cắt hạt lựu 0,5–1 cm, DEC đồ trang trí sáp (thanh quế, hoa hồi, lá quế khô), NUOC nước sạch (track_stock = false), và 3 bán thành phẩm TT1, TT2 (hương nền), DDT (dung dịch tẩm). Số trong ngoặc là tỷ trọng g/ml. 5 tinh dầu (Q, CAM, TTV, HH, HOI) có requires_coa = true.
- **recipe** (gram trên mẻ chuẩn; mẻ tinh dầu chuẩn là 100 ml; ngày ủ theo tr.6, 8, 9, 10, 12, 13). Sáu công thức tinh dầu khuếch tán, đều output_kind = PRODUCT, retain_months = 12; "1" là dầu nhẹ ủ 21 ngày, "2" là đậm đà ủ 28 ngày (tr.6):

| Mã | Tên | Thành phần (g) | Tổng | Ủ tối thiểu |
| --- | --- | --- | --- | --- |
| QC1 | Quế Cam, dầu nhẹ | TTV 31,40; Q 8,97; CAM 49,35 | 89,72 | 21 |
| QC2 | Quế Cam, đậm đà | TTV 36,87; Q 18,43; CAM 36,87 | 92,17 | 28 |
| RQ1 | Rừng Quế, dầu nhẹ | HH 9,21; TTV 46,07; Q 7,37; CAM 29,48 | 92,13 | 21 |
| RQ2 | Rừng Quế, đậm đà | HH 14,14; TTV 46,18; Q 15,08; CAM 18,85 | 94,25 | 28 |
| TQ1 | Tết Quế, dầu nhẹ | TTV 26,88; HOI 2,69; Q 8,96; CAM 51,07 | 89,60 | 21 |
| TQ2 | Tết Quế, đậm đà | TTV 32,17; HOI 4,60; Q 16,55; CAM 38,61 | 91,93 | 28 |

- Hương nền, dung dịch tẩm, sản phẩm sáp, viên, túi, dầu quế (output_kind như cột Đầu ra):

| Mã | Đầu ra | Thành phần (g) | Tổng | Ủ (ngày) | Ghi chú |
| --- | --- | --- | --- | --- | --- |
| TT1 | bán thành phẩm TT1 | HH 28,33; TTV 42,50; Q 9,44; CAM 14,17 | 94,44 | tối thiểu 14 | Hương nền dầu nhẹ (tr.9) |
| TT2 | bán thành phẩm TT2 | HH 28,73; TTV 40,22; Q 17,24; CAM 9,58 | 95,77 | tối thiểu 14 | Hương nền đậm đà (tr.9) |
| DDT | bán thành phẩm DDT | DPG 65; TT1 hoặc TT2 35 (alt_group 1) | 100 | 2 (48 giờ) | Dung dịch tẩm (tr.9–10) |
| SAP | sản phẩm | SD 70; SO 30; TT1 hoặc TT2 9 (alt_group 1) | 109 | tối thiểu 14 | Sáp thơm, mẻ nhỏ 2 tấm ≈ 55 g/tấm; trang trí 3–5 g/tấm nhập dòng ngoài công thức (tr.10–11) |
| VTC | sản phẩm | TC 100; NUOC 55; BM 0,5 (tùy chọn); DDT 18 | 173,5 | 7 | Mẻ nhỏ ≈ 6 viên 20 g; DDT 3 g/viên; phơi khô 5–7 ngày trước khi tẩm không theo dõi bằng lệnh (tr.11–12) |
| TUI | sản phẩm | VQH 480; DG 320; HT 200; DDT 100 | 1.100 | 5 (tối đa 7) | 40 túi 25 g; DDT chỉ tẩm dăm gỗ và hạt (tr.12–13) |
| U-Q | bán thành phẩm Q | QM 100 | 100 | 28 (tối đa 42) | Ủ dầu quế 4–6 tuần (tr.8); lắng 3–5 ngày và thoát khí 7 ngày đầu làm trước, không theo dõi bằng lệnh |
| Q100 | sản phẩm | Q 100 | 100 | 0 | Đóng chai 10 ml hổ phách; hạn 24 tháng (tr.8) |
| SC-VQH | bán thành phẩm VQH | không có dòng phụ liệu; đưa lô quế (Quế vụn) vào | — | 0 | Sơ chế: sấy rồi cắt hạt lựu |

Công thức chưng cất dầu quế mới (CHUNG-QM: lô quế → QM) **không seed**: sổ tay chỉ mô tả từ lúc đã có dầu mới chưng (tr.8). Khi chủ DN chốt chưng tại xưởng (mục 13) thì tạo công thức này, mô hình đã sẵn sàng (mục 7.4).

## 5. Phân hệ 1 – Danh mục

Mọi danh mục dùng chung một mẫu màn hình: danh sách có ô tìm kiếm và lọc trạng thái, bấm một dòng để mở form sửa, nút "Ngừng dùng" thay cho nút xóa. Chỉ OWNER được sửa. Trường có dấu * là bắt buộc.

| Màn hình | Trường trên form | Kiểm tra khi lưu |
| --- | --- | --- |
| Địa bàn | Cấp*, tên*, thuộc (cha), địa danh cũ, hiệu lực từ | Cha đúng cấp trên (Xã → Tỉnh, Thôn → Xã); không trùng tên trong cùng cha. Hiển thị dạng cây Tỉnh › Xã › Thôn |
| Loại hàng hóa | Mã*, tên*, nhóm* (nguyên liệu / thành phẩm), là thực phẩm | Không đổi nhóm khi đã có sản phẩm dùng |
| Nguyên vật liệu | Mã*, tên*, loại hàng*, ảnh nút bấm, thứ tự; bảng con: các hạng (tên*, bậc*) | Không ngừng dùng hạng đang có lô trong kho. Seed sẵn Vỏ quế, Quế vụn × Loại 1–3 |
| Phụ liệu (ingredient) | Mã*, tên*, nhóm* (tinh dầu / dung môi / sáp / khoáng / thực vật / hương nền – dung dịch tẩm / khác), đơn vị* (cố định **gram**; ô ml chỉ là tỷ trọng g/ml để tham khảo), theo dõi tồn (tắt với nước sạch), yêu cầu phiếu kiểm nghiệm COA, hạn dùng mặc định của lô tự làm (tháng) | Mã duy nhất, chữ hoa, 1–6 ký tự (dùng làm đầu mã lô, BR-20). Không đổi mã hay bật "theo dõi tồn" khi đã có lô. Không ngừng dùng khi còn lô IN_STOCK hoặc còn nằm trong công thức ACTIVE (BR-21). Seed theo mục 4: 19 phụ liệu (gồm các bán thành phẩm Q, QM, VQH, TT1, TT2, DDT) |
| Công thức (recipe + recipe_item) | Mã*, tên*, đầu ra* (thành phẩm / bán thành phẩm; bán thành phẩm phải chọn phụ liệu làm ra), mẻ chuẩn (gram, máy cộng từ các dòng), ghi chú mẻ chuẩn, ngày ủ tối thiểu*, ngày ủ tham khảo tối đa, số tháng lưu mẫu, ghi chú các bước; bảng con thành phần: phụ liệu*, gram*, nhóm lựa chọn (TT1 hoặc TT2), tùy chọn, ghi chú. Hiện cột "% khối lượng" tính sẵn | Gram > 0, tính theo gram không theo ml. Sửa trực tiếp chỉ khi bản đó DRAFT hoặc chưa có lệnh dùng; công thức đã có lệnh thì nút "Tạo phiên bản mới" (sao chép, version + 1) (BR-26). Mỗi mã chỉ một bản ACTIVE; kích hoạt bản mới thì bản cũ → RETIRED. Công thức bán thành phẩm không được tự chứa chính nó, trực tiếp hay gián tiếp. Công thức ACTIVE phải có ít nhất 1 dòng, trừ công thức sơ chế (SC-VQH) đầu vào là lô quế |
| Bảng giá | Lưới 2 hàng (nguyên liệu) × 3 cột (loại), mỗi ô có giá mua* và giá bán*; chọn ngày (mặc định hôm nay) | Mở ra đã điền sẵn giá ngày gần nhất; chỉ cần sửa ô thay đổi rồi Lưu. Giá ≥ 0. Xem được lịch sử 30 ngày |
| Nhà cung cấp (người bán) | Tên*, kiểu* (gia đình / hộ dân / thương lái), SĐT, địa bàn*, luồng*, đồng ý công khai tên; bảng con: đồi quế | Mã tự sinh. Thương lái: luồng khóa là GENERAL. Hộ dân / gia đình: địa bàn phải là thôn; luồng CONTROLLED chỉ được chọn khi có ít nhất 1 đồi. Cảnh báo khi trùng tên + thôn |
| Đồi quế (trong form người bán) | Thôn*, diện tích (ha), năm trồng, tọa độ (dán từ Google Maps), ảnh, đồi mặc định | Mã tự sinh D-<xã>-<số NCC>-<stt>. Năm trồng 1950 ≤ năm ≤ năm nay. Đúng 1 đồi mặc định khi có ≥ 1 đồi |
| Khách hàng (người mua) | Tên*, kiểu* (DN xuất khẩu / đại lý / quà tặng DN / khách lẻ / sàn), SĐT, địa chỉ | Mã tự sinh KH-<stt>. Seed sẵn 1 khách "Khách lẻ" và mỗi sàn 1 khách |
| Sản phẩm | SKU*, tên*, loại hàng*, quy cách*, đơn vị tính*, mã công thức (chọn từ danh mục công thức; trống với trà, ống quế), hạn dùng (tháng), bắt buộc lưu mẫu (cờ), giá bán lẻ, ảnh; tab "Website": slug, mô tả ngắn, câu chuyện, cách dùng, tiêu đề SEO, mô tả SEO, trạng thái | Hạn dùng (tháng) để trống được: lô thành phẩm của sản phẩm đó phải nhập hạn tay (BR-11). Mã công thức phải trỏ tới một recipe.code có bản ACTIVE; sản phẩm PUBLISHED mà công thức không còn bản ACTIVE thì cảnh báo, không chặn. Slug tự sinh từ tên (bỏ dấu, gạch nối), sửa được, duy nhất. Bộ đếm ký tự: tiêu đề SEO ≤ 60 (cứng 70), mô tả SEO ≤ 160 (cứng 170). Mỗi ảnh bắt buộc có alt. Đổi sang PUBLISHED phải qua BR-14 |
| Chứng nhận | Loại*, số*, cơ quan cấp, ngày cấp, hết hạn, số sao (OCOP), file, áp dụng cho (sản phẩm hoặc đồi)*, công khai | Hết hạn ≥ ngày cấp. Trang công khai chỉ hiện chứng nhận còn hiệu lực |
| Tài khoản | Tên đăng nhập*, họ tên*, vai trò*, mật khẩu | Mật khẩu ≥ 8 ký tự. Không tự ngừng dùng chính mình |

**Duyệt người bán mới:** người bán do xưởng thêm nhanh có approved = false, hiện huy hiệu "Chờ duyệt" ở trang chủ của OWNER. Chủ DN bổ sung đồi, đổi luồng nếu cần, rồi duyệt. Phiếu nhập vẫn lưu được trước khi duyệt, nhưng lô của người bán chưa duyệt luôn mang luồng GENERAL (xem BR-03).

## 6. Phân hệ 4 – Nhập hàng và xuất hàng

Xưởng chỉ làm 4 thứ: chọn người, chọn loại, chọn hạng, gõ số cân. Phiếu nhập và phiếu xuất quế khô cùng một khuôn màn hình.

### 6.1 Trang chủ xưởng

Bốn nút lớn, mỗi nút tối thiểu 240 × 160 px: **Nhập hàng** , **Xuất hàng** , **Sản xuất / đóng gói** , **Xem tồn kho** . Không có menu bên. Mỗi màn hình con có nút "← Về trang chủ" cố định góc trái.

### 6.2 Phiếu nhập (phiếu cân)

- **Chọn người bán.** Ô tìm kiếm tự focus, tìm không phân biệt dấu (gõ "hung" ra "Hùng"). Bên dưới là lưới 12 nút người bán gần đây nhất, mỗi nút hiện tên + thôn. Nút "+ Người bán mới" mở form nhỏ: tên*, kiểu*, thôn* (chọn Xã → Thôn bằng nút).
- **Chọn đồi** (chỉ hiện khi người bán có ≥ 2 đồi): nút từng đồi, đã chọn sẵn đồi mặc định. Người bán có 1 đồi thì tự gắn, không hiện bước này.
- **Thêm dòng hàng:**
  - Bấm nút nguyên liệu (ảnh + chữ): Vỏ quế | Quế vụn.
  - Bấm nút hạng: Loại 1 | Loại 2 | Loại 3. Dưới mỗi nút hiện giá mua hôm nay, ví dụ "45.000 đ/kg".
  - Gõ số cân vào ô số cỡ chữ 32px, nhận cả dấu phẩy và dấu chấm thập phân. Enter = thêm dòng.
  - Dòng vừa thêm hiện trong bảng: nguyên liệu, loại, kg, đơn giá, thành tiền. Bấm vào dòng để sửa hoặc xóa trước khi lưu.
  - Link nhỏ "Sửa giá" trên từng dòng. Giá lệch quá 20% so với bảng giá thì hiện cảnh báo vàng, vẫn cho lưu.
- **Tổng phiếu** hiện cố định ở chân màn hình, chữ lớn: tổng kg, tổng tiền.
- **Lưu và in.** Một giao dịch DB: tạo receipt + mỗi dòng một material_lot (IN_STOCK, chụp stream từ người bán) + audit_log. Sau đó mở hộp thoại in: 1 phiếu nhập + 1 tem lô cho mỗi dòng (QR chứa mã lô NL-..., dòng chữ: mã lô, nguyên liệu, loại, kg, ngày, tên người bán). Tem lô luồng GENERAL in thêm chữ **"CHUNG"** đậm để xưởng phân biệt khi xếp kho.

Không có giá hôm nay thì dùng giá ngày gần nhất và hiện banner "Chưa có giá hôm nay, đang dùng giá ngày dd/mm". Chưa từng có giá thì bắt buộc gõ đơn giá tay.

### 6.3 Phiếu xuất quế khô (bán theo hạng + cân)

- Chọn người mua (giống chọn người bán). Kênh mặc định theo kiểu khách, ví dụ EXPORTER.
- Mỗi dòng: bấm nguyên liệu → bấm loại bán → **quét tem các lô đem xuất** , hoặc bấm chọn trong danh sách lô tồn cùng nguyên liệu, lô cũ nhất lên đầu → gõ **số cân lúc bán** .
- Đơn giá mặc định = giá bán hôm nay của loại đó. Thành tiền tự tính.
- Dòng hiện thêm dòng phụ cho OWNER: "Cân lúc mua 1.250 kg → cân lúc bán 1.180 kg (94,4%)".
- Lưu: tạo issue (DRY_CINNAMON) + issue_line; các lô đã quét chuyển SOLD, gán issue_line_id. In phiếu xuất.

Lô thuộc luồng nào cũng được xuất bán quế khô. Lô có loại lần 1 khác loại bán thì vẫn cho chọn (đã phân loại lại bằng tay), chỉ hiện nhãn xám "mua là loại 2".

### 6.4 Phiếu xuất thành phẩm (theo serial)

- Chọn người mua, kênh, gõ mã đơn (không bắt buộc).
- Quét tem QR trên từng chai, túi. Mỗi lần quét hợp lệ phát tiếng bíp ngắn. Hệ thống tự gom thành dòng theo sản phẩm, số lượng = số serial đã quét.
- Quét sai thì phát tiếng bíp dài kèm thông báo đỏ ghi rõ lý do: mã không tồn tại, tem chưa gán lô, đã xuất ngày dd/mm, đã hủy, lô bị thu hồi, hoặc đã quét trong phiếu này.
- Đơn giá mặc định = giá bán lẻ sản phẩm, sửa được. Lưu: serial chuyển ISSUED, gán issue_id, issued_at.

**Quà tặng kèm đơn (nếu có).** Nút "+ Thêm quà tặng" chuyển màn hình sang chế độ quà. Trong chế độ này:

- Quét tem sản phẩm có serial, hoặc bấm chọn món quà không dán tem (serial_tracked = false) rồi gõ số lượng.
- Dòng quà có is_gift = true, đơn giá 0 đ, hiện nhãn "Quà tặng" trên màn hình và phiếu in.
- Serial quà tặng vẫn chuyển ISSUED và truy xuất bình thường.

**Quản lý đơn hàng.** Trên giao diện, phiếu xuất thành phẩm gọi là "Đơn hàng". Màn hình danh sách đơn:

- Lọc theo ngày, kênh, sản phẩm, người mua (tìm bằng số điện thoại), đơn có quà.
- Mở một đơn thấy: người mua, dòng hàng, dòng quà, từng serial.
- Thao tác: in lại, hủy đơn theo BR-06.

### 6.5 Xem tồn kho

- **Nguyên liệu:** bảng nguyên liệu × loại → số lô, tổng kg theo cân lúc mua, ngày nhập cũ nhất; tách 2 cột luồng kiểm soát / chung. Bấm ô để xem danh sách lô.
- **Phụ liệu:** bảng phụ liệu → số lô, tổng remaining_g (gram), hạn dùng gần nhất. Lô dưới 60 ngày đến hạn tô cam, lô quá hạn tô đỏ, tinh dầu mua ngoài chưa có COA hiện chấm vàng. Gồm cả bán thành phẩm (dầu quế đã ủ, hương nền, dung dịch tẩm). Bấm ô để xem từng lô và các lệnh đã lấy gram từ lô đó. Mục này cho WORKSHOP xem, không có giá.
- **Thành phẩm:** sản phẩm × lô → số serial IN_STOCK, hạn dùng. Lô còn dưới 60 ngày đến hạn tô cam.
- **Kiểm kê:** nút "Kiểm kê" cho xưởng quét lần lượt tem các bao trong kho. Hệ thống so với danh sách lô IN_STOCK và báo lô thiếu, lô thừa. Không cân.

### 6.5a Phiếu nhập phụ liệu

Dùng khuôn màn hình của phiếu nhập (mục 6.2) nhưng không có đồi, luồng, giá. Vào từ nút "Nhập hàng" → tab "Phụ liệu".

- **Nơi bán:** gõ tên (vendor_name*), SĐT; tìm lại được nơi bán gần đây. Dầu quế mới chưng nhận từ gia đình: ghi nơi bán "Nguồn gia đình".
- **Dòng hàng:** chọn phụ liệu (ingredient) bằng nút, gõ **gram nhập*** (ml đọc trên nhãn chỉ để tham khảo, hệ thống quy đổi bằng density_g_ml nếu có), số lô nhà cung cấp, hạn dùng theo nhãn, đính kèm ảnh phiếu kiểm nghiệm (COA). Phụ liệu requires_coa = true mà chưa có COA thì cảnh báo vàng, vẫn lưu.
- **Lưu và in:** tạo ingredient_receipt + mỗi dòng một ingredient_lot (IN_STOCK, initial_g = remaining_g, mã theo BR-20) + audit_log; in 1 tem lô phụ liệu cho mỗi dòng (QR chứa mã, ví dụ CAM-2611-01).
- Phụ liệu track_stock = false (nước sạch) không có lô, không hiện ở màn hình này.
- Sửa, hủy phiếu: cùng quyền như BR-05; chỉ khi mọi lô của phiếu còn nguyên tồn (chưa có dòng production_ingredient nào).

### 6.6 Thông tin người mua

Mỗi sản phẩm đã bán lẻ phải tra được tới người mua cuối: serial → phiếu xuất → người mua. Hệ thống tách 2 khái niệm:

- customer = đối tác hoặc kênh trả tiền (đại lý, DN quà tặng, DN xuất khẩu, sàn, "Khách lẻ").
- buyer = người mua cuối, người dùng sản phẩm. Một người là một bản ghi, ghép theo số điện thoại.

**Nhập trên đơn hàng (mục 6.4).** Sau khi chọn kênh có khối "Người mua":

- Gõ số điện thoại. Nếu đã có trong hệ thống thì tự điền tên, địa chỉ và hiện dòng "Đã mua 3 lần, lần gần nhất 02/11".
- Chưa có thì nhập: tên, tỉnh / xã (chọn bằng nút), số nhà – đường, và ô tích "Đồng ý nhận tin ưu đãi qua Zalo / SMS".
- Mức bắt buộc phụ thuộc kênh bán (BR-22):
  - Bán trực tiếp, website, Facebook / Zalo: bắt buộc tên và số điện thoại.
  - Sàn TMĐT: bắt buộc tên và tỉnh, không bắt buộc số điện thoại vì sàn thường ẩn số.
  - Đại lý, quà tặng DN, xuất khẩu: không bắt buộc, vì người dùng cuối chưa biết lúc xuất.

**Nguồn duy nhất là đơn hàng.** Thông tin người mua chỉ được ghi khi lập và quản lý đơn hàng. Không có form đăng ký trên website hay trang QR.

**Hiển thị che thông tin (BR-24):**

- **Tên:** chỉ lấy chữ cái đầu của mỗi từ, viết hoa, cách nhau bằng dấu cách. Ví dụ: "Nguyễn Văn An" → N V A; "Đỗ Thị Ánh" → Đ T Á.
- **Số điện thoại:** chỉ hiện 3 số cuối, các số còn lại thay bằng *. Ví dụ: "0912345678" → *******678.
- **Phạm vi:** áp dụng mặc định ở mọi danh sách, màn hình đơn hàng và phiếu in, cho cả 2 vai trò.
- **Xem đầy đủ:** chỉ OWNER, bằng nút "Xem đầy đủ" trong chi tiết một người mua. Mỗi lần bấm ghi audit_log.
- **Lúc đang nhập:** trường gõ hiện rõ để kiểm tra; lưu xong thì hiển thị dạng che.
- **Hàm dùng chung:** maskName() và maskPhone() đặt ở phía máy chủ. API trả sẵn giá trị đã che, không để client tự che.

**Màn hình "Khách hàng đã mua"** (chỉ OWNER):

- **Danh sách:** tên, số điện thoại, tỉnh, số lần mua, tổng tiền, sản phẩm đã mua, ngày mua gần nhất, có đồng ý nhận tin hay không.
- **Lọc:** theo sản phẩm, kênh, khoảng ngày, tỉnh. Thêm lọc "đã mua trên 60 ngày" để nhắn chăm sóc, mời mua lại.
- **Chi tiết một khách:** từng phiếu xuất; từng serial kèm sản phẩm, lô, hạn dùng; quà tặng đã nhận.
- **Xuất CSV:** chỉ gồm khách đã đồng ý nhận tin, dùng cho Zalo OA hoặc SMS.
- **Tra cứu nội bộ** (mục 7.4) hiện người mua ở cuối chiều xuôi. Khi thu hồi lô, xem ngay danh sách người mua cần liên hệ.

**Dữ liệu cá nhân:**

- Thông tin người mua không bao giờ xuất hiện trên website hay trang truy xuất.
- Tên và số điện thoại hiển thị dạng che theo quy tắc ở trên.
- Lưu thời điểm khách đồng ý.
- OWNER có nút "Xóa thông tin cá nhân" khi khách yêu cầu. Thao tác này đổi tên thành "Đã xóa", xóa số điện thoại, email, địa chỉ và ghi anonymized_at. Lịch sử bán hàng vẫn giữ.
- Chủ DN cần rà lại nội dung câu xin đồng ý theo quy định bảo vệ dữ liệu cá nhân hiện hành.

## 7. Phân hệ 2 – Truy xuất nguồn gốc

Truy xuất là chuỗi khóa ngoại: serial → product_lot → production_order → (a) các material_lot đưa thẳng vào lệnh → receipt → supplier + plot → area, và (b) các dòng production_ingredient → ingredient_lot → nguồn của lô phụ liệu. Nguồn là phiếu nhập phụ liệu (mua ngoài, chuỗi dừng ở nơi bán) hoặc một lệnh sản xuất khác (bán thành phẩm tự làm, chuỗi lặp lại từ production_order cho tới khi gặp lô quế hoặc phiếu nhập phụ liệu). Không có bảng truy xuất riêng. Mọi màn hình dưới đây chỉ là cách để mỗi mắt xích được ghi đúng lúc. Ví dụ một chai QC1: serial → QC1-261117-01 → lệnh LSX-… → Q-2610-01 (dầu quế đã ủ) → lệnh ủ U-Q → QM-2610-02 (dầu mới chưng) → lệnh chưng → NL-2610-0031 → PN-… → người bán + đồi; cùng lúc nhánh CAM-2609-01 → PNP-… → nơi bán.

vòng đời lô nguyên liệu và tem QR serial

Bất kỳ chuyển trạng thái nào khác ngoài các mũi tên trên đều phải bị API từ chối (HTTP 409). Lệnh sản xuất và lô phụ liệu có vòng đời riêng (sơ đồ cần vẽ thêm):

| Đối tượng | Trạng thái | Chuyển được sang |
| --- | --- | --- |
| production_order | DRAFT | CURING (bắt đầu ủ), DONE (chỉ khi công thức không ủ hoặc lệnh không công thức), CANCELLED |
| production_order | CURING | DONE (khi đủ ngày ủ), CANCELLED (OWNER, bắt buộc lý do, không hoàn kho) |
| production_order | DONE, CANCELLED | không chuyển nữa |
| ingredient_lot | IN_STOCK | DEPLETED (remaining_g về 0), CANCELLED (hủy phiếu nhập phụ liệu khi chưa xuất gram nào) |
| ingredient_lot | DEPLETED | IN_STOCK (khi dòng xuất bị xóa trên lệnh DRAFT hoặc lệnh DRAFT bị hủy làm tồn tăng lại) |

### 7.1 Vùng nguyên liệu

Vùng = người bán luồng CONTROLLED + các đồi của họ, khai báo ở phân hệ 1. Màn hình "Vùng nguyên liệu" chỉ có OWNER dùng:

- Bản đồ các đồi có tọa độ, dùng Leaflet + OpenStreetMap, không cần khóa API.
- Bảng đồi: xã, thôn, diện tích, năm trồng, tổng kg đã mua 12 tháng, hiệu suất trung bình.
- Đồi thiếu tọa độ hoặc ảnh được đánh dấu "thiếu thông tin truy xuất".

### 7.2 Lệnh sản xuất

Một lệnh có 4 bước: **chọn công thức và cỡ mẻ → đưa nguyên liệu vào (cân từng gram) → ủ → nhập đầu ra**. Đầu ra là lô thành phẩm (output_kind = PRODUCT) hoặc lô bán thành phẩm như dầu quế đã ủ, hương nền, dung dịch tẩm (output_kind = INTERMEDIATE). Lệnh không có công thức (trà, ống quế…) bỏ qua bước công thức và bước ủ, chạy như thiết kế cũ.

**Tạo lệnh** (OWNER)

- Chọn sản phẩm (hoặc chọn bán thành phẩm cần làm), ngày, ghi chú.
- Công thức: máy chọn sẵn phiên bản ACTIVE của recipe.code khớp product.recipe_code; chọn lại được phiên bản khác còn hiệu lực. Công thức có nhóm lựa chọn (TT1 hoặc TT2) thì bắt chọn một phương án.
- Cỡ mẻ: gõ tổng gram muốn pha (target_batch_g), mặc định = base_batch_g. Máy gợi ý lượng cân từng thành phần = qty_g × target_batch_g / base_batch_g, làm tròn 2 số lẻ. Ví dụ QC1 cỡ 897,2 g cho 314,0 / 89,7 / 493,5 g, đúng cột "mẻ 1 lít" của sổ tay (tr.6).
- Lưu → DRAFT.

**Xưởng mở lệnh** từ nút "Sản xuất / đóng gói". Danh sách hiện lệnh DRAFT và CURING, mỗi lệnh một thẻ lớn: tên sản phẩm, mã công thức, ngày dự kiến xong ủ. Thẻ CURING còn thiếu ngày hiện chữ xám "Còn N ngày".

**Đưa nguyên liệu vào** (lệnh DRAFT). Có hai loại, xử lý khác nhau:

- **Lô quế** (material_lot, cả lô, kg): quét tem NL-…. Hợp lệ khi lô IN_STOCK và stream = CONTROLLED (BR-08); khi đó lô chuyển RESERVED. Bấm × để bỏ, lô về IN_STOCK. **BR-08 chỉ áp cho lô quế.** Lô phụ liệu không có luồng nên không bị kiểm; lô phụ liệu do lệnh làm ra từ quế (ví dụ dầu quế) đã qua kiểm CONTROLLED ở chính lệnh đó. Lô quế GENERAL vẫn bị từ chối.
- **Lô phụ liệu** (ingredient_lot, theo gram): màn hình hiện danh sách thành phần của công thức, mỗi dòng có lượng gợi ý (gram). Xưởng quét tem lô phụ liệu (QR chứa mã, ví dụ Q-2610-01) rồi gõ **gram thực tế** đọc trên cân. Máy gợi ý lô có hạn dùng gần nhất, còn đủ tồn. Mỗi lần gõ là một dòng production_ingredient (dòng xuất kho phụ liệu) và remaining_g của lô giảm đúng số gram đó; lô hết tồn → DEPLETED. Bấm × để bỏ dòng, tồn cộng lại. Từ chối khi: lô không đúng phụ liệu của dòng công thức, tồn không đủ, lô quá hạn (exp_date nhỏ hơn ngày lệnh), lô CANCELLED. Cảnh báo vàng, vẫn lưu: gram thực tế lệch gợi ý quá ±0,05 g (sai số sổ tay cho phép; lỡ tay thì ghi số thật, không múc bớt ra, tr.5); lô tinh dầu mua ngoài chưa có phiếu kiểm nghiệm (COA).
- **Dòng ngoài công thức:** thêm một dòng phụ liệu không nằm trong công thức (ví dụ đồ trang trí sáp 3–5 g mỗi tấm); recipe_item_id để trống.
- Lệnh có công thức phải đủ mọi dòng bắt buộc trước khi bắt đầu ủ; dòng is_optional (bột màu) được bỏ qua.
- Thành phần là bán thành phẩm (TT1, DDT, Q…) chọn trong cùng danh sách lô phụ liệu; lô bán thành phẩm chỉ xuất hiện sau khi lệnh làm ra nó đã DONE, nên chưa ủ đủ thì chưa dùng được.
- **Chọn loại sau sàng lọc:** chỉ lệnh PRODUCT có lô quế đưa thẳng vào mới hiện 3 nút Loại 1 / 2 / 3, chọn một, không cân. Lệnh chỉ dùng phụ liệu, và lệnh INTERMEDIATE, không có bước này.

**Bắt đầu ủ** (nút "Đã pha xong, bắt đầu ủ"; lệnh có công thức với cure_min_days > 0) — một giao dịch DB:

- các lô quế RESERVED → USED; các dòng production_ingredient trở thành bất biến;
- sinh batch_code (mã mẻ, BR-20): lệnh PRODUCT theo mẫu lô thành phẩm `<mã công thức>-YYMMDD-NN`, lệnh INTERMEDIATE theo mẫu lô phụ liệu `<mã phụ liệu>-YYMM-NN` của ingredient đầu ra; in tem mẻ để dán lên lọ ủ;
- cure_started_at = bây giờ, cure_ready_on = ngày bắt đầu + cure_min_days;
- lệnh → CURING.

Trong khi ủ, xưởng không sửa được dòng nguyên liệu. Hết ủ, nút "Hoàn thành" mới sáng; trước đó bị API từ chối 409 kèm câu "Mẻ QC1-261117-01 còn 6 ngày mới đủ ủ". OWNER được bỏ qua kiểm tra này nhưng bắt buộc ghi lý do vào cure_check_note, có audit_log. Số ngày ủ theo sổ tay: tinh dầu khuếch tán 21 ngày (dầu nhẹ) hoặc 28 ngày (đậm đà), hương nền tối thiểu 14, dung dịch tẩm 48 giờ, sáp thơm 14, viên thạch cao 7 sau khi tẩm, túi vỏ quế 5–7, dầu quế 4–6 tuần (tr.6, 8, 9, 10, 12, 13). Khoảng "14–28 ngày" ở bảng so sánh tr.2 là số của bản 1; bản 2 chốt 21 và 28 (tr.2, tr.6).

Cuối kỳ ủ, xưởng ngửi kiểm tra theo sổ tay (nhúng que thử, ngửi ngay, sau 1 giờ, sau 4 giờ, so với mẫu chuẩn, tr.6): ghi kết quả vào cure_check_note. Còn gắt thì bấm "Ủ thêm" (mặc định 7 ngày): cure_ready_on dời lại, lý do vào cure_check_note, lệnh vẫn CURING.

**Nhập kết quả và hoàn thành** (lệnh CURING đủ ngày, hoặc lệnh DRAFT không ủ)

- Đầu ra PRODUCT: số cân thành phẩm (kg)*, số lượng bán được (chai / túi)*, ngày xong (mfg_date, mặc định hôm nay); hạn dùng tự tính theo BR-11, sửa được. Với tinh dầu nhập thêm ghi chú ngửi kiểm tra.
- Đầu ra INTERMEDIATE: số gram làm ra* (cân bằng cân điện tử); hạn dùng = ngày xong + ingredient.shelf_life_months (dầu quế 24 tháng), sửa được.
- **Hoàn thành** — một giao dịch DB:
  - (lệnh không ủ) các lô quế RESERVED → USED; sinh batch_code;
  - PRODUCT: tạo product_lot với code = batch_code, blend_date, input_weight_kg = Σ weight_kg lô quế (0 nếu chỉ phụ liệu), input_cost = Σ amount, input_ingredient_g = Σ actual_g, yield_pct (NULL khi không có quế), unit_cost;
  - INTERMEDIATE: tạo ingredient_lot với code = batch_code, production_order_id, initial_g = remaining_g = gram làm ra, input_weight_kg = Σ weight_kg lô quế, status IN_STOCK;
  - lệnh → DONE;
  - PRODUCT: màn hình hiện hiệu suất (nếu có), hỏi lưu mẫu theo mục 7.5, rồi chuyển sang bước gán tem. INTERMEDIATE: in tem lô phụ liệu (QR chứa mã, ví dụ Q-2610-01).

**Hạn dùng** lấy theo từng sản phẩm: tinh dầu khuếch tán 18 tháng "do có nhiều cam ngọt" (sổ tay tr.6), tinh dầu quế 100% 24 tháng nếu bảo quản kín, tối, mát (tr.8). Sổ tay không ghi hạn cho sáp thơm, viên thạch cao, túi vỏ quế: product.shelf_life_months để trống, nên khi hoàn thành lệnh xưởng **bắt buộc nhập exp_date tay**, không có giá trị mặc định (BR-11, mục 13).

**Hủy lệnh**

- DRAFT: mọi lô quế RESERVED quay về IN_STOCK; mọi dòng production_ingredient bị hủy và gram cộng lại vào lô (remaining_g tăng, DEPLETED về IN_STOCK).
- CURING: chỉ OWNER, bắt buộc lý do (mẻ hỏng, đổ bỏ). **Không hoàn kho:** quế đã USED và phụ liệu đã trộn không lấy lại được. Lệnh → CANCELLED; batch_code giữ lại, không sinh lô, audit_log ghi.
- DONE: không hủy được; muốn làm lại thì dùng thu hồi lô ở mục 7.4.

### 7.3 Cuộn tem và gán tem

- **Tạo cuộn** (OWNER): nhập số tem (1–5.000). Máy chủ sinh serial với seq = 1..n. Mã là 10 ký tự Crockford Base32 ngẫu nhiên từ CSPRNG; trùng thì sinh lại.
- **In cuộn:** trang in HTML theo khổ tem cấu hình trong setting (mặc định 40 × 30 mm, chờ chủ DN chốt). Mỗi tem gồm: QR chứa URL https://<tên miền>/q/<mã>, dòng chữ mã dạng K7Q2-MX9P-AT, số thứ tự nhỏ. In tuần tự theo seq để tem trên cuộn đúng thứ tự.
- **Gán đoạn tem vào lô thành phẩm** (xưởng):
  - Quét tem đầu rồi tem cuối của đoạn tem sẽ dán.
  - Hệ thống kiểm tra 2 tem cùng cuộn, lấy mọi serial có seq trong khoảng; serial VOID nằm trong khoảng thì bỏ qua.
  - Mọi serial còn lại phải đang UNASSIGNED, không thì từ chối cả đoạn và báo serial vi phạm.
  - Gán product_lot_id, chuyển IN_STOCK.
  - Thanh tiến độ "Đã gán 120 / 150". Được gán nhiều đoạn cho một lô, nhưng tổng không vượt quantity.
- **Hủy tem lỗi:** quét tem rách hoặc in hỏng → chọn lý do → VOID. Tem đã ISSUED không hủy được.

### 7.4 Thu hồi và tra cứu

- **Thu hồi lô thành phẩm** (OWNER, bắt buộc lý do): product_lot.status = RECALLED; mọi serial IN_STOCK / ISSUED của lô → RECALLED, issue_id giữ nguyên. Trang truy xuất của các serial này hiện cảnh báo thu hồi.
- **Thu hồi theo lô phụ liệu hoặc lô quế** (OWNER): từ tra cứu xuôi (dưới) chọn một hay nhiều lô thành phẩm trong danh sách ảnh hưởng, bấm "Thu hồi các lô đã chọn". Mỗi lô vẫn thu hồi theo BR-15 với lý do riêng và audit_log riêng; hệ thống không tự thu hồi hàng loạt.
- **Tra cứu hai chiều** (OWNER): một ô nhận mọi loại mã: serial, lô thành phẩm (QC1-261117-01), lô phụ liệu (Q-2610-01), lô nguyên liệu (NL-…), lệnh, phiếu nhập quế, phiếu nhập phụ liệu, người bán. Máy nhận dạng loại mã theo mẫu BR-20; các mẫu không trùng nhau.
  - Ngược: serial → lô TP → lệnh → (a) các lô NL đưa thẳng vào, (b) các lô phụ liệu qua production_ingredient. Mỗi lô phụ liệu hiện nguồn: phiếu nhập phụ liệu và nơi bán (dừng), hoặc lệnh làm ra nó, rồi lặp lại cho các lô đưa vào lệnh đó, cho tới lô NL → phiếu nhập → người bán, đồi, thôn, xã. Kết quả là một cây nhiều tầng, mỗi nhánh kết thúc ở lô NL hoặc phiếu nhập phụ liệu.
  - Xuôi: lô NL, lô phụ liệu hoặc người bán → các lệnh dùng nó (trực tiếp hoặc qua bán thành phẩm, theo đệ quy) → lô TP → serial → phiếu xuất → khách hàng và người mua cuối. Từ một lô cam ngọt có vấn đề, tìm ra mọi chai đã bán có dùng lô đó, kể cả chai làm từ hương nền hay dung dịch tẩm pha từ lô đó.
  - **Dầu quế nối về lô quế:** khi dầu quế được chưng tại xưởng, chuỗi là Q (lô dầu đã ủ) ← lệnh ủ U-Q ← QM (lô dầu mới chưng) ← lệnh chưng ← lô NL. Khi dầu quế nhận từ gia đình hoặc mua ngoài, QM đến từ phiếu nhập phụ liệu với nơi bán là nguồn đó và chuỗi dừng ở đó; cây truy xuất hiện dòng "nguồn ngoài, chưa nối về lô quế" để chủ DN biết chỗ đứt. Lô thành phẩm dùng dầu quế loại này không có vùng nguyên liệu và đồi trên trang truy xuất công khai (xem mục 8.4).
  - Dùng khi có khiếu nại: từ một hộ bán nguyên liệu lỗi, hoặc một lô phụ liệu lỗi, tìm ra mọi khách đã nhận hàng.
- **Báo cáo hiệu suất** (OWNER): theo tháng, theo sản phẩm, theo người bán. Mỗi lô TP chia hiệu suất cho các người bán theo tỷ trọng kg đưa vào. Với bán thành phẩm từ quế (dầu quế, vỏ quế cắt), hiệu suất tính ngay trên lệnh làm ra nó: gram làm ra / kg quế đưa vào (ingredient_lot.input_weight_kg); lô TP dùng bán thành phẩm đó không tính hiệu suất lần nữa. Lô TP chỉ dùng phụ liệu (yield_pct NULL) không vào báo cáo này.

### 7.5 Lưu mẫu và thử lưu hương

**Lưu mẫu** (sổ tay A.1 bước 8, tr.6: "lưu mẫu 1 chai 10 ml mỗi lô trong 12 tháng")

- Áp dụng cho lô thành phẩm của sản phẩm có product.requires_retention_sample = true (BR-29). Seed bật cho sản phẩm tinh dầu khuếch tán của sáu công thức QC1–TQ2; số tháng giữ lấy recipe.retain_months (12), công thức để trống thì lấy setting.retain_default_months (12). Sổ tay chưa nói cho dầu quế 100%, sáp, viên, túi: cờ để tắt, OWNER bật khi chủ DN chốt (mục 13), không cần sửa code.
- Ngay sau Hoàn thành lệnh (mục 7.2), màn hình hỏi "Đã lấy chai lưu mẫu chưa?" với ô vị trí (tủ, kệ). Bấm Lưu tạo retained_sample: product_lot_id, stored_on = hôm nay, retain_until = stored_on + retain_months, status RETAINED. Chai lưu mẫu không dán tem serial và không tính vào quantity của lô.
- Lô cần lưu mẫu mà chưa có retained_sample hiện ở danh sách "Lô chưa lưu mẫu" trên trang chủ OWNER. Không chặn gán tem hay xuất hàng.
- Màn hình "Mẫu lưu" (OWNER, xưởng xem): danh sách theo hạn lưu. Mẫu còn dưới 30 ngày tới retain_until tô cam. Hết hạn thì bấm "Hủy mẫu" (DISPOSED, disposed_on, ghi chú). Mẫu của lô đã RECALLED: không cho hủy mẫu.
- Khi có khiếu nại, tra cứu lô (mục 7.4) hiện nút "Xem mẫu lưu": vị trí và hạn giữ.

**Thử lưu hương 28 ngày** (sổ tay C.1, tr.13; chỉ cho sáp thơm, viên thạch cao, túi vỏ quế)

- **Tạo đợt thử** (OWNER): chọn công thức, ghi mục tiêu (ví dụ "so dung dịch tẩm 25% / 35% / 45%"), ngày bắt đầu. Mã TL-YYMM-NN.
- **Thêm mẫu:** mỗi biến thể làm 3 mẫu giống nhau, đặt 3 nơi: tủ quần áo đóng kín, ô tô (nếu là sản phẩm treo xe), phòng thường. Ví dụ viên thạch cao 3 biến thể × 3 nơi = 9 mẫu. Mỗi mẫu có mã dán trên mẫu và nhãn biến thể.
- **Ghi kết quả:** màn hình theo ngày 0, 1, 3, 7, 14, 21, 28. Mỗi ngày, mỗi mẫu: gõ khối lượng (g, cân 0,01 g, cùng giờ trong ngày), rồi mỗi người ngửi (5–7 người, chấm riêng, không thấy điểm người khác) nhập cường độ 1–5 và độ dễ chịu 1–5 và ghi chú (mùi nào nổi, có gắt không). Màn hình in được phiếu chấm điểm cho từng mẫu như sổ tay C.2 (tr.14).
- **Đánh giá tự động** cho mỗi biến thể, theo 4 tiêu chí chọn công thức của sổ tay (tr.13):
  1. Ngày 1, cường độ trung bình không quá 4 (không bốc gắt).
  2. Ngày 28, mẫu trong tủ kín, cường độ trung bình từ 2,5 trở lên.
  3. Độ dễ chịu trung bình từ 3,5 trở lên.
  4. Khối lượng mất trong 3 ngày đầu không quá 1/3 tổng khối lượng mất sau 28 ngày (hương ra đều, không dồn vào lúc đầu).
- Biến thể đạt cả 4 tiêu chí → PASS; ngược lại FAIL (tính khi xem, không lưu). Người dùng chọn một biến thể PASS làm chosen_variant (hoặc kết luận không biến thể nào đạt), xác nhận scent_trial.result, ghi longevity_weeks (thời gian lưu hương đo thật) và kết luận rồi đóng đợt (DONE). Máy chỉ tính, không tự đóng, không cho chọn biến thể FAIL.
- **Thời gian lưu hương chỉ được in lên bao bì khi có đợt thử DONE, PASS cho công thức đó và longevity_weeks có số** (sổ tay tr.13: "chỉ ghi thời gian lưu hương lên bao bì sau khi đã đo thật"). Mục tiêu tham khảo của sổ tay: sáp thơm 6–10 tuần, viên thạch cao 3–4 tuần mỗi lần tẩm, túi vỏ quế 4–6 tuần (tr.8); số này chưa phải số đo.
- Tinh dầu khuếch tán thử theo cách khác (chạy máy 30 phút, chấm điểm ở phút 5, 30, 60; tr.13) và không nằm trong đợt thử này; hệ thống chưa lưu, xem ghi chú mục 13.

## 8. Phân hệ 3 – Website và trang truy xuất công khai

Website render phía máy chủ (SSR hoặc trang tĩnh sinh lại khi nội dung đổi), đọc dữ liệu qua API công khai chỉ đọc. Trang sản phẩm để Google lập chỉ mục. Trang truy xuất từng serial thì không.

### 8.1 Sơ đồ URL

| URL | Nội dung | Lập chỉ mục |
| --- | --- | --- |
| / | Trang chủ: câu chuyện quế Văn Yên, sản phẩm nổi bật, kênh mua | Có |
| /san-pham | Danh sách sản phẩm PUBLISHED, lọc theo loại hàng | Có |
| /san-pham/<slug> | Trang sản phẩm | Có |
| /<slug trang tĩnh> | Ví dụ /cau-chuyen, /vung-que-van-yen, /lien-he (từ site_page) | Có |
| /q/<serial> | Trang truy xuất khi quét QR | Không (noindex, nofollow) |
| /truy-xuat | Ô nhập mã tay cho khách không quét được | Có |
| /sitemap.xml | Tự sinh: trang chủ, danh sách, sản phẩm, trang tĩnh. Không chứa /q/ | — |
| /robots.txt | Disallow: /q/, khai báo sitemap | — |
| /feed/google-merchant.xml | Feed sản phẩm cho Google Merchant Center: id = SKU, title, description, link, image_link, price, availability | — |

Slug đổi thì tự tạo chuyển hướng 301 từ slug cũ (bảng slug_redirect(old_slug, product_id)).

### 8.2 Trang sản phẩm

- **Thứ tự nội dung:** ảnh (carousel), tên (h1), quy cách, giá bán lẻ, nút mua (Shopee / TikTok Shop / Zalo / gọi), mô tả ngắn, câu chuyện, cách dùng, khối "Nguồn gốc" (xã, ảnh đồi, chứng nhận còn hiệu lực), sản phẩm khác.
- **Thẻ head:** <title> = seo_title, hoặc nếu trống thì <tên> | <tên thương hiệu>; meta description = seo_description; link rel=canonical; Open Graph (og:title, og:description, og:image 1200×630, og:type=product); html lang="vi".
- **Dữ liệu có cấu trúc** JSON-LD: Product (name, image, description, sku, brand, offers: Offer với price, priceCurrency VND, availability) + BreadcrumbList. Trang chủ có thêm Organization. Không tự tạo AggregateRating khi không có đánh giá thật.
- **Nút mua trên sàn** là link ngoài, lưu trong product (cột buy_links jsonb: [{channel, url}]).
- **Ảnh:** tự sinh WebP nhiều kích cỡ (srcset), ảnh đầu không lazy-load, các ảnh sau lazy-load. Alt lấy từ images[].alt.

### 8.3 Đo lường và quảng cáo

- Google Analytics 4 và thẻ chuyển đổi Google Ads, nạp qua Google Tag Manager. Mã cấu hình lưu trong setting, không hard-code.
- Sự kiện GA4: view_item (trang sản phẩm), click_buy (tham số channel), trace_scan (trang /q/, tham số sku, result).
- Giữ nguyên tham số UTM khi chuyển trang. Nút mua tự gắn utm_source=website vào link sàn nếu sàn cho phép.
- Xác minh tên miền trong Google Search Console; gửi sitemap.

### 8.4 Trang truy xuất /q/<serial>

Mỗi lần mở trang: ghi một scan_event, tăng serial.scan_count, cập nhật first_scan_at / last_scan_at. Riêng người dùng đang đăng nhập nội bộ thì không đếm, để xưởng kiểm tra tem không làm sai số liệu.

| Trường hợp | Hiển thị |
| --- | --- |
| Mã không tồn tại | "Mã không có trong hệ thống — sản phẩm có thể không chính hãng" + số điện thoại liên hệ |
| UNASSIGNED | "Mã chưa được kích hoạt — sản phẩm có thể không chính hãng" |
| VOID | "Mã đã bị hủy" |
| RECALLED | Khung đỏ "Lô sản phẩm này đã được thu hồi, vui lòng liên hệ để đổi" + thông tin sản phẩm |
| IN_STOCK / ISSUED | Nội dung truy xuất đầy đủ (dưới) |
| scan_count vượt ngưỡng (mặc định 20, cấu hình trong setting) | Thêm dòng vàng "Mã này đã được quét N lần, lần đầu ngày dd/mm/yyyy. Nếu bạn vừa mua mới, hãy liên hệ chúng tôi." |

**Nội dung truy xuất đầy đủ** (đúng thứ tự): dấu tích "Sản phẩm chính hãng" → ảnh, tên sản phẩm → mã lô thành phẩm, ngày sản xuất, hạn dùng → "Vùng nguyên liệu" (danh sách xã / thôn không trùng của các đồi trong lô, địa danh cũ "Văn Yên, Yên Bái", năm trồng sớm nhất–muộn nhất, tối đa 3 ảnh đồi) → tên hộ trồng, chỉ khi họ có public_consent → chứng nhận còn hiệu lực → câu chuyện sản phẩm (rút gọn) → nút "Mua lại" (link trang sản phẩm) → số lần quét.

**Tuyệt đối không hiện:** giá mua, giá vốn, hiệu suất, tên thương lái, tên khách hàng, mã phiếu, số điện thoại hộ dân, nơi bán phụ liệu, mã lô phụ liệu (Q-2610-01…), mã lô dầu quế. Vùng nguyên liệu chỉ lấy từ các lô quế ở cuối chuỗi truy xuất; lô thành phẩm không có lô quế nào (nhánh dầu quế mua ngoài) thì ẩn khối "Vùng nguyên liệu", không hiện nơi bán thay thế. API công khai chỉ trả đúng các trường được phép (DTO riêng), không trả nguyên entity.

Trang phải tải nhanh trên mạng 4G yếu: HTML render sẵn, tổng dung lượng lần tải đầu dưới 300 KB, ảnh đồi nén WebP.

## 9. Danh sách API

API nội bộ nằm dưới /api/v1, xác thực bằng cookie phiên HttpOnly. API công khai nằm dưới /api/public, chỉ có GET, có giới hạn tần suất. Mọi thao tác ghi là một giao dịch DB và ghi audit_log.

**Lỗi trả về chung:** {"code": "LOT_NOT_IN_STOCK", "message": "<câu tiếng Việt hiển thị được ngay>", "details": {...}}. Mã HTTP: 400 dữ liệu sai, 401 chưa đăng nhập, 403 không đủ quyền, 404 không tìm thấy, 409 sai trạng thái hoặc vi phạm quy tắc nghiệp vụ. message phải là câu xưởng đọc hiểu, ví dụ "Lô NL-2611-0045 đã được dùng trong lệnh LSX-2611-003".

| Nhóm | Method + path | Quyền | Ghi chú |
| --- | --- | --- | --- |
| Xác thực | POST /auth/login, POST /auth/logout, GET /auth/me | — | Khóa 15 phút sau 5 lần sai mật khẩu |
| Danh mục | GET·POST·PATCH /areas, /goods-types, /materials (kèm grades), /customers, /products, /certificates, /users, /site-pages, /settings | GET: cả hai; ghi: OWNER | PATCH {status:'INACTIVE'} = ngừng dùng |
| Người bán | GET·POST·PATCH /suppliers, POST /suppliers/{id}/approve, GET·POST·PATCH /suppliers/{id}/plots | POST nhanh: cả hai; còn lại: OWNER | GET /suppliers?q=&recent=12 cho lưới nút |
| Bảng giá | GET /prices?date=, PUT /prices/{date} | GET: cả hai; PUT: OWNER | GET trả giá ngày đó hoặc gần nhất, kèm effective_date |
| Phiếu nhập | GET /receipts?from=&to=&supplier_id=, POST /receipts, PATCH /receipts/{id}, POST /receipts/{id}/cancel, GET /receipts/{id}/print | cả hai (BR-05) | Body POST: {supplier_id, plot_id?, note?, lines:[{material_id, grade_id, weight_kg, unit_price?}]} |
| Lô nguyên liệu | GET /material-lots?status=&material_id=&grade_id=&stream=, GET /material-lots/by-code/{code} | cả hai | WORKSHOP: bỏ trường giá |
| Phiếu xuất | GET /issues, POST /issues, POST /issues/{id}/cancel, GET /issues/{id}/print | cả hai | Quế khô: lines:[{material_id, grade_id, weight_kg, unit_price?, lot_codes:[]}]; thành phẩm: serial_codes:[], máy chủ tự gom dòng |
| Kiểm tra serial khi quét | GET /serials/{code} | cả hai | Trả trạng thái, sản phẩm, lô — cho màn hình quét xuất |
| Phụ liệu | GET·POST·PATCH /ingredients | GET: cả hai; ghi: OWNER | PATCH {status:'INACTIVE'} = ngừng dùng (BR-21). Bảng: ingredient |
| Công thức | GET /recipes?code=&status=&output_kind=, GET /recipes/{id}, POST /recipes, PATCH /recipes/{id}, PUT /recipes/{id}/items, POST /recipes/{id}/new-version, POST /recipes/{id}/activate, POST /recipes/{id}/retire, GET /recipes/{id}/scale?batch_g= | GET: cả hai; ghi: OWNER | Bảng: recipe, recipe_item. GET {id} trả items kèm % khối lượng. scale trả lượng cân gợi ý từng dòng = qty_g × batch_g / base_batch_g. PATCH và PUT items chỉ khi bản DRAFT hoặc chưa có lệnh dùng, không thì 409 (BR-26). new-version sao chép thành version + 1 ở DRAFT |
| Phiếu nhập phụ liệu | GET /ingredient-receipts?from=&to=, POST /ingredient-receipts, PATCH /ingredient-receipts/{id}, POST /ingredient-receipts/{id}/cancel, GET /ingredient-receipts/{id}/print | cả hai (quyền sửa, hủy như BR-05) | Body POST: {vendor_name, vendor_phone?, note?, lines:[{ingredient_id, initial_g, vendor_lot_no?, exp_date?, coa_url?}]}. Tạo mỗi dòng một ingredient_lot. **Nơi bán chỉ OWNER thấy (BR-17):** response của OWNER có vendor_name và vendor_phone; WORKSHOP dùng schema riêng không có hai trường này (loại ở máy chủ, giống cách ẩn giá ở phần phân quyền), nhưng vẫn nhập được vendor_name khi POST. Hủy chỉ khi chưa có dòng production_ingredient nào lấy từ các lô của phiếu |
| Lô phụ liệu | GET /ingredient-lots?status=&ingredient_id=&expiring_within_days=, GET /ingredient-lots/by-code/{code}, PATCH /ingredient-lots/{id} {coa_url?, vendor_lot_no?, exp_date?} | cả hai | by-code trả lô, tồn, nguồn (vendor_name, vendor_phone chỉ cho OWNER; WORKSHOP dùng schema không có vendor_*, kể cả trong dòng nguồn) và các lệnh đã lấy gram (production_ingredient). Mọi PATCH ghi audit_log. Không có API sửa remaining_g: tồn chỉ đổi qua dòng xuất của lệnh. Bảng: ingredient_lot |
| Lệnh sản xuất | POST /production-orders, GET /production-orders?status=&output_kind=, GET /production-orders/{id}, POST /production-orders/{id}/cancel | tạo, hủy: OWNER; đọc: cả hai | Body POST: {output_kind, product_id? (PRODUCT), recipe_id? (bắt buộc với INTERMEDIATE), alt_choices:[{alt_group, ingredient_id}]?, target_batch_g?, order_date, note?}. GET {id} trả gợi ý lượng cân từng dòng công thức, lô quế đã đưa vào, các dòng production_ingredient, cure_ready_on. Bảng: production_order |
| Lệnh SX: lô quế | POST /production-orders/{id}/material-lots {lot_code}, DELETE /production-orders/{id}/material-lots/{lot_id} | cả hai | Endpoint dành riêng cho lô quế (material_lot), kiểm theo BR-08: lô GENERAL bị từ chối 409. Phụ liệu đưa vào bằng /ingredients ở dòng dưới. Thay cho POST …/lots cũ. Lệnh phải DRAFT |
| Lệnh SX: phụ liệu | POST /production-orders/{id}/ingredients {ingredient_lot_code, actual_g, recipe_item_id?}, PATCH /production-orders/{id}/ingredients/{line_id} {actual_g}, DELETE /production-orders/{id}/ingredients/{line_id} | cả hai | Mỗi lần gọi POST = một dòng production_ingredient, trừ remaining_g của lô trong cùng giao dịch (SELECT … FOR UPDATE). recipe_item_id trống = dòng ngoài công thức. Từ chối 409: lô sai phụ liệu so với dòng công thức, tồn không đủ, lô quá hạn hoặc CANCELLED, lệnh không còn DRAFT (BR-27). Response kèm cảnh báo `warnings:[{code:'GRAM_OFF_SUGGESTION'\|'COA_MISSING'}]` (không chặn) |
| Lệnh SX: ủ | POST /production-orders/{id}/start-curing, POST /production-orders/{id}/extend-curing {days?, note} | cả hai | start-curing: một giao dịch ở mục 7.2, sinh batch_code, trả mã mẻ để in tem. 409 nếu thiếu dòng bắt buộc của công thức (BR-26). extend-curing dời cure_ready_on (mặc định +7 ngày), bắt buộc note |
| Lệnh SX: hoàn thành | POST /production-orders/{id}/complete | cả hai; bỏ qua kiểm tra ủ: OWNER | PRODUCT: {output_grade_id? (chỉ khi có lô quế đưa thẳng), output_weight_kg, quantity, mfg_date, exp_date? (bắt buộc khi product.shelf_life_months trống), cure_check_note?}. INTERMEDIATE: {output_g, mfg_date, exp_date?}. Chưa đủ ngày ủ → 409 CURE_NOT_READY {ready_on, days_left} (BR-28). OWNER thêm {override_cure_reason} để bỏ qua |
| Lô thành phẩm | GET /product-lots?needs_retained_sample=, POST /product-lots/{id}/assign-labels {first_code, last_code}, POST /product-lots/{id}/recall {reason} | assign: cả hai; recall: OWNER | assign trả {assigned, total, skipped_void}. needs_retained_sample=true trả các lô thuộc sản phẩm bắt buộc lưu mẫu mà chưa có retained_sample |
| Lưu mẫu | GET /retained-samples?status=&retain_until_before=, POST /product-lots/{id}/retained-sample {location?, sample_qty?, note?}, POST /retained-samples/{id}/dispose {note?} | ghi nhận: cả hai; hủy mẫu: OWNER | Bảng: retained_sample. POST 409 khi lô đã có mẫu (UNIQUE). Lô của sản phẩm không bắt buộc lưu mẫu vẫn lưu được (lưu tự nguyện). dispose bị 409 khi lô RECALLED hoặc chưa đến retain_until (BR-29) |
| Thử lưu hương | GET·POST /scent-trials, GET /scent-trials/{id}, POST /scent-trials/{id}/samples, PUT /scent-trials/{id}/readings {sample_id, day_no, weight_g}, PUT /scent-trials/{id}/readings/{reading_id}/scores {panelist, intensity, pleasantness, note?}, GET /scent-trials/{id}/score-sheets/print, POST /scent-trials/{id}/close {chosen_variant?, result, longevity_weeks?, conclusion?} | tạo, đóng: OWNER; nhập cân, điểm: cả hai | Bảng: scent_trial, scent_trial_sample, scent_trial_reading, scent_trial_score. GET {id} trả đánh giá tự động từng biến thể theo 4 tiêu chí (tính khi gọi, không lưu). Chỉ nhận công thức SAP, VTC, TUI (BR-30). close 409 khi chosen_variant không đạt cả 4 tiêu chí hoặc result = PASS mà thiếu chosen_variant |
| Tem | POST /label-rolls {serial_count}, GET /label-rolls/{id}/print, POST /serials/{code}/void {reason} | tạo, in: OWNER; void: cả hai |  |
| Tồn kho | GET /inventory/materials, GET /inventory/ingredients, GET /inventory/products, POST /stocktakes {scanned_codes:[]} | cả hai | Kiểm kê trả {missing:[], unexpected:[]}, không tự sửa dữ liệu. /inventory/ingredients trả tồn gram theo phụ liệu và theo lô, kèm hạn dùng; kiểm kê chỉ áp cho lô quế và thành phẩm, chưa có kiểm kê phụ liệu |
| Truy xuất nội bộ | GET /trace?code=&direction=up\|down\|both | OWNER | Nhận mọi loại mã theo mẫu BR-20: serial, lô thành phẩm, lô phụ liệu, lô NL, lệnh, phiếu nhập quế, phiếu nhập phụ liệu, người bán. Trả cây {upstream, downstream} gồm **cả nhánh phụ liệu** (BR-31). Mỗi nút có type (SERIAL, PRODUCT_LOT, PRODUCTION_ORDER, MATERIAL_LOT, RECEIPT, SUPPLIER, PLOT, INGREDIENT_LOT, INGREDIENT_RECEIPT, ISSUE, CUSTOMER, BUYER), mã và children. Nút cuối nhánh có `end: 'MATERIAL_SOURCE'` (đã nối tới người bán quế) hoặc `end: 'EXTERNAL_VENDOR'` (mua ngoài, chuỗi dừng ở nơi bán). Truy vấn đệ quy qua production_ingredient, giới hạn 12 tầng và chống lặp; vượt thì 409 TRACE_TOO_DEEP |
| Báo cáo | GET /reports/yield?from=&to=&group_by=product\|supplier, GET /reports/purchases, GET /reports/sales, GET /reports/scans | OWNER | Có xuất CSV |
| Công khai | GET /api/public/products, GET /api/public/products/{slug}, GET /api/public/pages/{slug}, GET /api/public/trace/{code} | PUBLIC | trace: {code} phải khớp định dạng serial (10 ký tự Crockford Base32, BR-16); sai định dạng (kể cả mã lô, mã phụ liệu) thì trả "không tồn tại" như serial không có, không ghi scan_event, nên không dò được mã lô; hợp lệ thì ghi scan_event; giới hạn 60 lượt/phút mỗi IP. DTO chỉ gồm trường mục 8.4; **không trả** nơi bán phụ liệu, ingredient_receipt, mã lô phụ liệu, mã lô dầu quế hay bất kỳ nút nào của nhánh phụ liệu (BR-17). Vùng nguyên liệu lấy từ các lô quế ở cuối chuỗi, kể cả qua bán thành phẩm tự chưng |

**Bổ sung cho người mua (mục 6.6):**

| Method + path | Quyền | Ghi chú |
| --- | --- | --- |
| GET /buyers/by-phone/{phone} | cả hai | Dùng khi lập đơn; trả tên, địa chỉ đã che và số lần mua |
| GET /buyers?q=&product_id=&channel=&from=&to=&area_id=&inactive_days= | OWNER | Màn hình "Khách hàng đã mua", trả dữ liệu đã che |
| GET /buyers/{id}/purchases | OWNER | Đơn hàng + serial + quà tặng |
| GET /buyers/{id}/reveal | OWNER | Trả tên, số điện thoại đầy đủ; ghi audit_log |
| PATCH /buyers/{id}, POST /buyers/{id}/anonymize | OWNER | Xóa thông tin cá nhân, không hoàn tác |
| GET /buyers/export.csv | OWNER | Chỉ khách marketing_consent = true, dữ liệu đầy đủ, ghi audit_log |
| GET /issues?kind=PRODUCT&has_gift=&buyer_phone= | cả hai | Màn hình "Quản lý đơn hàng" |

POST /issues loại thành phẩm nhận thêm buyer: {id} hoặc buyer: {full_name, phone?, area_id?, address_line?, marketing_consent}. Máy chủ ghép theo số điện thoại trước khi tạo mới. Quà tặng gửi trong gifts: [{serial_codes}] hoặc [{product_id, quantity}], máy chủ tạo dòng is_gift = true, đơn giá 0.

Với màn hình quét, máy quét USB hoạt động như bàn phím: gõ chuỗi rồi Enter. QR serial chứa cả URL, nên client phải tách lấy 10 ký tự cuối sau /q/ trước khi gọi API. QR lô nguyên liệu chỉ chứa mã NL-.... QR lô phụ liệu và tem mẻ chỉ chứa mã lô (Q-2610-01, QC1-261117-01), không phải URL: không mở được trên website, chỉ máy quét của xưởng nhận (BR-17).

## 10. Quy tắc nghiệp vụ

Mỗi quy tắc phải được kiểm tra ở tầng service phía máy chủ, có unit test riêng. Giao diện kiểm tra thêm chỉ để báo sớm. Mã BR dùng làm mã lỗi và tên test.

| Mã | Quy tắc |
| --- | --- |
| BR-01 | **Quế:** khối lượng chỉ ghi 2 lần: material_lot.weight_kg lúc nhập và product_lot.output_weight_kg / issue_line.weight_kg lúc ra thành phẩm. Mỗi dòng phiếu nhập quế là một lô, lô quế không chia nhỏ. **Phụ liệu là ngoại lệ có chủ ý:** tính theo gram, ghi lúc nhập (ingredient_lot.initial_g, hoặc gram làm ra của bán thành phẩm) và mỗi lần xuất cho lệnh (production_ingredient.actual_g); lô phụ liệu được dùng từng phần (BR-27). |
| BR-02 | material_lot.stream chụp từ người bán tại thời điểm lưu. Đổi luồng của người bán sau đó không làm đổi lô cũ. |
| BR-03 | Người bán chưa duyệt (approved = false) hoặc kiểu TRADER → lô luôn mang stream = GENERAL. |
| BR-04 | Đơn giá mặc định lấy từ price của ngày phiếu, hoặc ngày gần nhất trước đó. Đơn giá thực tế lưu trên dòng. Lệch quá 20% so với bảng giá thì cảnh báo nhưng không chặn. amount = round(weight_kg × unit_price). |
| BR-05 | Sửa hoặc hủy phiếu nhập: WORKSHOP chỉ được với phiếu do mình lập, trong ngày lập (giờ VN). OWNER được bất kỳ lúc nào, bắt buộc lý do nếu đã qua ngày. Chỉ cho phép khi mọi lô của phiếu còn IN_STOCK. Hủy phiếu → các lô → CANCELLED. |
| BR-06 | Phiếu xuất không sửa được, chỉ hủy rồi lập lại, theo cùng quyền như BR-05. Hủy → lô SOLD về IN_STOCK; serial ISSUED về IN_STOCK, trừ serial RECALLED giữ nguyên. |
| BR-07 | **Lô quế** chỉ thuộc tối đa một lệnh sản xuất hoặc một dòng xuất. **Lô phụ liệu** thì được dùng cho nhiều lệnh, mỗi lần là một dòng production_ingredient, tổng gram đã xuất không vượt initial_g. Dùng SELECT … FOR UPDATE khi đổi trạng thái lô quế và khi trừ tồn lô phụ liệu, để chống 2 máy quét cùng lúc. |
| BR-08 | **Lô quế** đưa vào lệnh sản xuất phải IN_STOCK và có stream = CONTROLLED. Lô GENERAL bị từ chối với thông báo "Lô hàng chung, chỉ dùng xuất bán quế khô". Quy tắc này **chỉ áp cho lô quế (material_lot)**: lô phụ liệu không có luồng và không bị kiểm theo BR-08 (kiểm theo BR-27). |
| BR-09 | Hoàn thành lệnh cần: có ít nhất một đầu vào (một lô quế hoặc một dòng production_ingredient); lệnh có công thức đủ mọi dòng bắt buộc (BR-26) và, nếu có ủ, đã đủ ngày ủ (BR-28). Lệnh PRODUCT: output_weight_kg > 0, quantity > 0, và đã chọn loại sau sàng **chỉ khi có lô quế đưa thẳng vào**. Lệnh INTERMEDIATE: gram làm ra > 0. yield_pct = output / input × 100, làm tròn 2 số, chỉ tính khi input_weight_kg > 0 (không có quế đưa thẳng vào thì NULL). yield_pct > 100 thì cảnh báo, không chặn. |
| BR-10 | unit_cost = round(input_cost / quantity). input_cost **chỉ gồm tiền lô quế đưa thẳng vào lệnh**. Phụ liệu **không tính vào giá vốn**: phiếu nhập phụ liệu không có đơn giá (chi phí bao bì, nhân công cũng ngoài phạm vi). Quế đã đi qua bán thành phẩm (dầu quế, vỏ quế cắt hạt lựu) cũng chưa vào giá vốn của lô thành phẩm dùng nó. Hệ quả: lô thành phẩm chỉ dùng phụ liệu có input_cost = 0 và unit_cost = 0, nghĩa là "chưa tính", không phải miễn phí; báo cáo giá vốn hiện chú thích "chưa gồm phụ liệu" và không xếp các lô này vào so sánh lãi lỗ. Tính cả phụ liệu là câu hỏi mở ở mục 13. |
| BR-11 | exp_date của lô thành phẩm: mặc định = mfg_date + product.shelf_life_months, sửa được, phải > mfg_date. Theo sổ tay: tinh dầu khuếch tán 18 tháng, tinh dầu quế 100% 24 tháng. **product.shelf_life_months để trống** (sáp thơm, viên thạch cao, túi vỏ quế, và mọi sản phẩm chưa khai báo) thì không có mặc định, hoàn thành lệnh phải nhập exp_date tay, thiếu thì 400 và không tạo lô. Lô bán thành phẩm: exp_date = mfg_date + ingredient.shelf_life_months (dầu quế đã ủ 24 tháng), trống thì nhập tay được hoặc để trống (không kiểm hạn khi dùng). |
| BR-12 | Gán đoạn tem: 2 tem cùng cuộn; lấy seq trong đoạn, bỏ qua VOID; mọi serial còn lại phải UNASSIGNED; tổng đã gán của lô ≤ quantity. Vi phạm bất kỳ điều nào thì không gán serial nào (all-or-nothing). |
| BR-13 | Serial chỉ xuất được khi đang IN_STOCK và lô thành phẩm ACTIVE. Mỗi serial thuộc tối đa một phiếu xuất đang hiệu lực. |
| BR-14 | Sản phẩm có goods_type.is_food = true chỉ được chuyển PUBLISHED và được lập phiếu xuất khi có certificate loại DECLARATION và FOOD_SAFETY còn hiệu lực, gắn với sản phẩm đó. |
| BR-15 | Thu hồi lô thành phẩm: chỉ OWNER, bắt buộc lý do, không hoàn tác. Serial IN_STOCK / ISSUED của lô → RECALLED; serial UNASSIGNED / VOID giữ nguyên. |
| BR-16 | Mã serial: 10 ký tự Crockford Base32 (bỏ I, L, O, U), sinh từ CSPRNG, duy nhất toàn hệ thống, không suy ra được thứ tự hay số lượng. Khi tra cứu: chuyển thành chữ hoa, bỏ gạch nối, đổi O→0, I/L→1. |
| BR-17 | API công khai chỉ trả trường được liệt kê ở mục 8.4. Tên hộ trồng chỉ hiện khi public_consent = true. Không bao giờ hiện người bán TRADER. **Nhánh phụ liệu không bao giờ ra API công khai:** nơi bán phụ liệu (ingredient_receipt, vendor_name, vendor_phone), số lô nhà cung cấp, mã lô phụ liệu (Q-2610-01, CAM-2609-01…) và mã lô dầu quế không có trong response nào của /api/public và không dùng làm URL hay nội dung QR công khai; chỉ API nội bộ của OWNER trả. |
| BR-18 | Lượt quét của người dùng nội bộ đang đăng nhập không tính vào scan_count. Ngưỡng cảnh báo quét lấy từ setting.scan_warning_threshold. |
| BR-19 | Không xóa cứng dữ liệu nghiệp vụ. Mọi thao tác tạo, sửa, hủy, thu hồi, hủy tem đều ghi audit_log kèm trước / sau. |
| BR-20 | Mã nghiệp vụ sinh phía máy chủ theo bảng dưới, số thứ tự lấy từ bảng đếm có khóa hàng, không dùng MAX()+1. |
| BR-21 | Không ngừng dùng được nguyên liệu, hạng, người bán hay sản phẩm đang có lô IN_STOCK / RESERVED hoặc serial IN_STOCK. Tương tự với phụ liệu còn lô IN_STOCK hoặc còn nằm trong công thức ACTIVE, và công thức còn lệnh DRAFT / CURING. |

| Mã | Quy tắc về người mua và đơn hàng |
| --- | --- |
| BR-22 | Đơn hàng (phiếu xuất thành phẩm) kênh DIRECT, WEBSITE, FACEBOOK_ZALO bắt buộc người mua có tên và số điện thoại. Kênh SHOPEE, TIKTOK, LAZADA bắt buộc tên và tỉnh. AGENT, CORPORATE, EXPORTER không bắt buộc. Người mua chỉ được tạo qua đơn hàng. |
| BR-23 | Số điện thoại chuẩn hóa trước khi lưu và tra cứu: bỏ khoảng trắng, dấu chấm, gạch; +84 / 84 → 0; phải đủ 10 số. Cùng số điện thoại = cùng một người mua. |
| BR-24 | Hiển thị che: tên → chữ cái đầu mỗi từ, viết hoa, cách nhau bằng dấu cách (N V A); số điện thoại → 3 số cuối, còn lại là * (*******678). Áp dụng mặc định cho mọi API, màn hình và phiếu in; chỉ /reveal và CSV của OWNER trả bản đầy đủ. Không bao giờ trả qua API công khai. Người mua đã xóa thông tin cá nhân không được ghép lại theo số cũ. |
| BR-25 | Dòng quà tặng (is_gift = true) có unit_price = 0, amount = 0, không tính vào doanh thu nhưng vẫn trừ kho. Quà có serial phải quét và tuân theo BR-13. Quà không dán tem (serial_tracked = false) nhập số lượng. Một đơn phải có ít nhất 1 dòng không phải quà. |

| Mã | Quy tắc về công thức, phụ liệu, ủ, lưu mẫu và truy xuất phụ liệu (theo sổ tay sản xuất) |
| --- | --- |
| BR-26 | **Công thức.** (a) Mỗi recipe.code có tối đa một phiên bản ACTIVE. (b) Phiên bản đã có lệnh sản xuất dùng thì bất biến; muốn đổi tạo phiên bản mới, lệnh cũ vẫn trỏ phiên bản cũ. (c) base_batch_g = Σ qty_g (mỗi nhóm lựa chọn tính một phương án); công thức tính theo gram, không theo ml. (d) Công thức bán thành phẩm không được tham chiếu chính nó, trực tiếp hay qua công thức khác. (e) Lệnh có công thức phải chọn đúng một phương án cho mỗi nhóm lựa chọn và có đủ mọi dòng không is_optional trước khi bắt đầu ủ hoặc hoàn thành; thiếu thì 409. (f) Lượng cân máy gợi ý = qty_g × target_batch_g / base_batch_g, làm tròn 2 số lẻ; xưởng cân thực tế khác gợi ý vẫn lưu (BR-27). |
| BR-27 | **Kho phụ liệu.** (a) Mỗi lần xuất phụ liệu cho lệnh là một dòng production_ingredient, remaining_g = initial_g − Σ actual_g, không bao giờ âm. (b) Từ chối 409 khi: lô không đúng phụ liệu của dòng công thức; tồn không đủ; lô CANCELLED; lô quá hạn (exp_date < ngày lệnh; lô exp_date trống thì không kiểm); lệnh không còn DRAFT. (c) Cảnh báo, không chặn: actual_g lệch gợi ý quá ±0,05 g (sai số cân điện tử của sổ tay); tinh dầu requires_coa chưa có phiếu kiểm nghiệm. (d) Lô phụ liệu có đúng một nguồn: phiếu nhập phụ liệu hoặc lệnh INTERMEDIATE DONE; không có lô mồ côi. (e) Lệnh CURING trở đi: dòng production_ingredient bất biến. (f) Phụ liệu track_stock = false (nước sạch) không có lô, không có dòng xuất. |
| BR-28 | **Ủ.** (a) Công thức có cure_min_days > 0 thì lệnh phải qua CURING: bấm "Đã pha xong, bắt đầu ủ" sinh batch_code, cure_ready_on = ngày bắt đầu + cure_min_days. (b) Chưa đến cure_ready_on thì POST …/complete bị 409 CURE_NOT_READY, không tạo lô thành phẩm hay lô bán thành phẩm, không nhập được thành phẩm. (c) OWNER được bỏ qua kiểm tra, bắt buộc override_cure_reason, ghi cure_check_note và audit_log; WORKSHOP không. (d) "Ủ thêm" dời cure_ready_on (mặc định +7 ngày) kèm lý do, lệnh vẫn CURING. (e) cure_max_days chỉ tham khảo, không chặn. (f) Hủy lệnh CURING chỉ OWNER, bắt buộc lý do, không hoàn kho; batch_code giữ lại. Số ngày ủ tối thiểu theo sổ tay: QC1/RQ1/TQ1 21, QC2/RQ2/TQ2 28, hương nền 14, dung dịch tẩm 2, sáp thơm 14, viên thạch cao 7, túi vỏ quế 5, dầu quế 28 (ủ 4–6 tuần). |
| BR-29 | **Lưu mẫu.** (a) Lô thành phẩm của sản phẩm có product.requires_retention_sample = true phải có một retained_sample (1 chai, không dán tem serial, không tính vào quantity). Seed bật cho 6 công thức tinh dầu khuếch tán; sản phẩm khác để tắt cho đến khi chủ DN chốt. (b) retain_until = stored_on + số tháng giữ (recipe.retain_months, trống thì setting.retain_default_months = 12). (c) Lô chưa lưu mẫu hiện trong danh sách "Lô chưa lưu mẫu" của OWNER; không chặn gán tem hay xuất hàng. (d) Không hủy mẫu (DISPOSED) trước retain_until, và không hủy mẫu của lô RECALLED. |
| BR-30 | **Thử lưu hương 28 ngày.** (a) Chỉ cho công thức sáp thơm (SAP), viên thạch cao (VTC), túi vỏ quế (TUI). (b) Mốc đo cố định: ngày 0, 1, 3, 7, 14, 21, 28; cường độ và độ dễ chịu chấm thang 1–5, mỗi người ngửi chấm riêng. (c) Biến thể PASS khi đạt cả 4 tiêu chí của mục 7.5; đợt chỉ PASS khi OWNER chọn một biến thể PASS. (d) Thời gian lưu hương chỉ được in lên bao bì khi có đợt DONE, PASS cho công thức đó và longevity_weeks có số đo thật; số tham khảo của sổ tay (sáp 6–10 tuần, viên 3–4 tuần, túi 4–6 tuần) không được dùng thay. |
| BR-31 | **Truy xuất phụ liệu.** (a) Từ một serial phải đi được về mọi lô phụ liệu đã dùng và, nếu có, về lô quế: serial → lô thành phẩm → lệnh → lô quế và production_ingredient → lô phụ liệu → (phiếu nhập phụ liệu hoặc lệnh làm ra nó, lặp lại). (b) Dầu quế chưng tại xưởng: chuỗi nối tới lô quế, phiếu nhập quế, người bán, đồi. Dầu quế mua hoặc nhận ngoài: chuỗi dừng ở nơi bán, cây hiện "nguồn ngoài, chưa nối về lô quế". (c) Truy xuôi từ một lô phụ liệu tìm ra mọi lô thành phẩm, serial, phiếu xuất và người mua có dùng lô đó, kể cả qua bán thành phẩm nhiều tầng. (d) Chuỗi truy xuất đi theo đệ quy, không giới hạn số tầng cứng nhưng chặn ở 12 tầng và chống lặp. (e) Nhánh phụ liệu chỉ có ở API nội bộ, theo BR-17. |

**Mẫu mã nghiệp vụ (BR-20):**

| Đối tượng | Mẫu | Đếm lại theo | Ví dụ |
| --- | --- | --- | --- |
| Phiếu nhập | PN-YYMMDD-NNN | ngày | PN-261120-001 |
| Phiếu xuất | PX-YYMMDD-NNN | ngày | PX-261120-002 |
| Lô nguyên liệu | NL-YYMM-NNNN | tháng | NL-2611-0045 |
| Lệnh sản xuất | LSX-YYMM-NNN | tháng | LSX-2611-003 |
| Lô thành phẩm (= mã mẻ) | <mã công thức>-YYMMDD-NN; lệnh không có công thức thì <SKU>-YYMMDD-NN | ngày pha + mã công thức | QC1-261117-01 |
| Phiếu nhập phụ liệu | PNP-YYMMDD-NNN | ngày | PNP-261117-001 |
| Lô phụ liệu và bán thành phẩm | <mã phụ liệu>-YYMM-NN | tháng + mã phụ liệu | Q-2610-01, QM-2610-02, CAM-2609-01, TT1-2611-01 |
| Đợt thử lưu hương | TL-YYMM-NN | tháng | TL-2611-01 |
| Cuộn tem | CT-YYMM-NN | tháng | CT-2611-01 |
| Người bán | NCC-<mã xã>-NNN | xã | NCC-CQ-012 |
| Đồi quế | D-<mã xã>-<số NCC>-NN | người bán | D-CQ-012-02 |
| Khách hàng | KH-NNNN | không | KH-0007 |

<mã xã> là area.code viết tắt 2–3 chữ của xã, ví dụ CQ = Châu Quế, ĐC = Đông Cuông (bỏ dấu: DC). Các ví dụ trong bảng là minh họa.

**Chốt mẫu mã lô thành phẩm và lô phụ liệu.** Sổ tay (tr.14, mục C.3) ghi lô tinh dầu theo mẫu `[Mã công thức]-[Năm tháng ngày]-[Số mẻ]` (QC1-261117-01) và lô dầu quế là Q-2611-01. Mục này trước đây dùng `TP-<SKU>-YYMM-NN` (TP-TD10-2611-03). Hai mẫu khác nhau; đội chốt **theo sổ tay**:

- **Lô thành phẩm = `<mã công thức>-YYMMDD-NN`.** Lý do: (1) xưởng đã ghi sổ và dán lọ theo mẫu này, không phải học mẫu mới; (2) nhìn mã biết ngay công thức và ngày pha, khi khách phản ánh tra được mẻ nào, dùng dầu quế lô nào, ai làm (sổ tay tr.14); (3) lô có giai đoạn ủ 2–6 tuần nên mã phải có từ ngày pha để dán lên lọ ủ trước khi nhập thành phẩm, dùng ngày pha chứ không phải tháng; (4) một mẻ chia nhiều quy cách (10 ml, 30 ml) thành nhiều lệnh nhận NN khác nhau trong cùng ngày, nên mã không cần SKU. SKU và quy cách tra qua product_lot.product_id và in riêng trên tem. Bộ đếm theo (mã công thức, ngày). Lệnh không có công thức dùng SKU thay mã công thức, ví dụ TRA10-261117-01.
- **Lô phụ liệu và bán thành phẩm = `<mã phụ liệu>-YYMM-NN`**, đếm theo (mã phụ liệu, tháng). Giữ đúng mẫu Q-2611-01 của sổ tay cho dầu quế rồi áp cho mọi phụ liệu, cả mua ngoài lẫn tự làm, để cột "lô tinh dầu quế dùng" của sổ tay tổng quát thành "lô phụ liệu dùng" mà không đổi cách ghi. Phụ liệu mua ngoài còn lưu số lô nhà cung cấp ở vendor_lot_no. NN hết 99 trong tháng thì sang NNN.
- Hai họ mã không nhầm nhau: lô thành phẩm có 6 chữ số ngày, lô phụ liệu có 4. Tra cứu (mục 7.4) tách theo mẫu.
- **Đổi so với bản trước:** mẫu lô thành phẩm cũ `TP-<SKU>-YYMM-NN` và ví dụ TP-TD10-2611-03 bị bỏ; ví dụ trong code_counter đổi theo. Chưa có lô nào theo mẫu cũ vì hệ thống chưa chạy.

## 11. Yêu cầu phi chức năng

| Nhóm | Yêu cầu |
| --- | --- |
| Thiết bị xưởng | Máy tính Windows, Chrome bản mới, màn hình tối thiểu 1366 × 768, wifi. Máy quét QR 2D cắm USB chế độ bàn phím (HID), hậu tố Enter. Máy in tem nhiệt cài driver Windows. |
| Giao diện xưởng | Chữ thân tối thiểu 18px, nút tối thiểu 64px cao, số tiền và số cân 32px. Ô quét luôn giữ focus, tự focus lại sau mỗi lần quét. Phản hồi âm thanh: bíp ngắn khi đúng, bíp dài khi sai. Không dùng hộp thoại xác nhận trừ khi hủy. |
| Hiệu năng | API nội bộ p95 < 300 ms. Quét 1 serial → có kết quả trên màn hình < 500 ms. Gán đoạn 1.000 tem < 2 giây. Trang truy xuất và trang sản phẩm: LCP < 2,5 giây trên 4G, đạt Core Web Vitals "Tốt". |
| Quy mô thiết kế | 5 người dùng nội bộ cùng lúc; 50.000 lô nguyên liệu; 1 triệu serial; 100 lượt quét công khai mỗi phút. Một VPS 2 vCPU / 4 GB là đủ. |
| Bảo mật | HTTPS bắt buộc (Let's Encrypt). Mật khẩu hash bằng argon2id hoặc bcrypt (cost ≥ 12). Cookie HttpOnly, Secure, SameSite=Lax, phiên hết hạn sau 12 giờ. Chống CSRF cho API ghi. Kiểm tra quyền ở mọi endpoint. Giới hạn tần suất API công khai. Không lưu IP gốc của khách quét. |
| Sao lưu | Dump DB tự động mỗi ngày lúc 23:00 giờ VN, giữ 30 bản, đẩy sang nơi lưu trữ ngoài VPS. Ảnh tải lên cũng sao lưu ngoài VPS. Thử khôi phục mỗi quý. |
| In ấn | Phiếu nhập / xuất: mẫu HTML in khổ A5 hoặc giấy nhiệt 80 mm, chọn trong setting. Tem lô và tem serial: mẫu HTML theo khổ tem trong setting, QR mức sửa lỗi M, kích thước QR ≥ 18 mm. Không phụ thuộc ngôn ngữ riêng của máy in. |
| Nhật ký | Log ứng dụng có cấu trúc (JSON), giữ 30 ngày. Mọi lỗi 5xx báo về kênh của đội Qwork. |
| SEO kỹ thuật | HTML render sẵn. URL không dấu, chữ thường. Canonical, sitemap, robots như mục 8. Chỉ một h1 mỗi trang. Giữ 301 cho slug cũ. |
| Kiểm thử | Unit test cho mọi BR. Test tích hợp cho 8 luồng: nhập quế, nhập phụ liệu, xuất quế khô, lệnh sản xuất (cả lệnh có công thức, ủ và bán thành phẩm), gán tem, xuất thành phẩm, quét công khai, truy xuất hai chiều qua nhánh phụ liệu. Kiểm thử thật với máy quét và máy in tại xưởng trước khi go-live. |
| Môi trường | dev, staging (dữ liệu giả, tên miền phụ), production. Migration DB có phiên bản, chạy tự động khi deploy. |

## 12. Tiêu chí nghiệm thu

Mỗi kịch bản dưới đây là một test tích hợp hoặc test tay bắt buộc. Giai đoạn chỉ được nghiệm thu khi tất cả kịch bản của giai đoạn đó đạt.

| ID | GĐ | Given (cho trước) | When (khi) | Then (thì) |
| --- | --- | --- | --- | --- |
| AC-01 | 1 | Giá mua hôm nay Vỏ quế loại 1 = 45.000 đ/kg; người bán A (hộ dân, CONTROLLED, 1 đồi) | Xưởng chọn A → Vỏ quế → Loại 1 → gõ 120,5 → Enter → Lưu | Tạo 1 phiếu PN-… và 1 lô NL-… IN_STOCK, 120,50 kg, 5.422.500 đ, stream = CONTROLLED, đồi = đồi duy nhất của A; hộp thoại in mở với 1 phiếu + 1 tem lô |
| AC-02 | 1 | Người bán A bán cả 3 loại | Thêm 3 dòng Loại 1, 2, 3 trong một phiếu, lưu | 1 phiếu, 3 lô riêng; tồn kho tách đúng theo loại |
| AC-03 | 1 | Thương lái B | Lập phiếu nhập từ B | Lô có stream = GENERAL; tem lô in chữ "CHUNG" |
| AC-04 | 1 | Xưởng thêm nhanh người bán mới C loại hộ dân | Lập phiếu từ C | Lô GENERAL (BR-03); trang chủ OWNER hiện "1 người bán chờ duyệt" |
| AC-05 | 1 | Phiếu do xưởng lập hôm qua | Tài khoản WORKSHOP bấm sửa | Bị từ chối 403 với thông báo "Chỉ chủ doanh nghiệp được sửa phiếu ngày trước" |
| AC-06 | 1 | Lô L1 (1.250 kg, GENERAL) và giá bán quế khô loại 2 đã có | Lập phiếu xuất quế khô: loại 2, quét L1, gõ 1.180 kg, lưu | L1 → SOLD; dòng xuất 1.180 kg; OWNER thấy "94,4%"; WORKSHOP không thấy giá trên báo cáo tồn kho |
| AC-07 | 1 | Có đúng 10 lô IN_STOCK, 1 bao bị thất lạc | Kiểm kê: quét 9 bao còn lại | Báo "Thiếu 1 lô: NL-…"; không tự đổi dữ liệu |
| AC-08 | 2 | Lệnh DRAFT cho Trà quế (không công thức, đưa lô quế vào); lô quế L2 CONTROLLED 80 kg, lô quế L3 GENERAL | Xưởng quét L3 | Từ chối 409 BR-08 "Lô hàng chung, chỉ dùng xuất bán quế khô"; L3 vẫn IN_STOCK. BR-08 chỉ áp cho lô quế: lô phụ liệu không bị kiểm luồng (xem AC-25) |
| AC-09 | 2 | Lệnh trên đã có L2 (RESERVED), giá mua L2 = 3.600.000 đ | Chọn Loại 1, nhập 40 kg, 400 gói, Hoàn thành | L2 → USED; lô TP: input_weight_kg 80, output 40 kg, yield_pct = 50,00, unit_cost = 9.000, input_ingredient_g = 0; lệnh DONE ngay, không qua CURING (không công thức) |
| AC-10 | 2 | Lô TP cần 400 tem; cuộn CT có serial seq 1–500, seq 37 đã VOID | Quét tem seq 1 rồi seq 401 | Gán 400 serial (bỏ qua seq 37) → IN_STOCK; trả về assigned = 400, skipped_void = 1 |
| AC-11 | 2 | Lô TP đã gán đủ 400 | Quét thêm đoạn mới | Từ chối BR-12, không gán serial nào |
| AC-12 | 2 | Serial S thuộc lô TP ACTIVE, đang IN_STOCK | Phiếu xuất thành phẩm: quét S 2 lần | Lần 1 bíp ngắn, số lượng = 1; lần 2 bíp dài "Đã quét trong phiếu này" |
| AC-13 | 2 | Serial S ISSUED, lô có đồi ở xã Châu Quế, hộ A chưa đồng ý công khai | Khách mở /q/S trên điện thoại | Trang hiện "Sản phẩm chính hãng", ngày SX, hạn dùng, xã Châu Quế (Văn Yên, Yên Bái); không có tên hộ A, không có giá; scan_count +1 |
| AC-14 | 2 | Serial S2 UNASSIGNED | Khách mở /q/S2 | Hiện cảnh báo "Mã chưa được kích hoạt" |
| AC-15 | 2 | Lô TP có 200 serial ISSUED, 200 IN_STOCK | OWNER thu hồi lô với lý do | 400 serial → RECALLED; /q/ của chúng hiện khung đỏ thu hồi; không xuất được nữa |
| AC-16 | 2 | Đã tạo công thức CHUNG-QM. Hộ A đã bán hai lô quế: L2 vào lệnh Trà quế (AC-09) và L4 vào một lệnh chưng dầu quế cho lô Q-2610-01, lô Q này đã dùng trong lô QC1-261117-01 | OWNER tra cứu xuôi từ NCC của A | Thấy cả hai nhánh: lệnh Trà quế → lô TP → 400 serial; và lệnh chưng → lô QM → lệnh ủ → lô Q → lô QC1-261117-01 → serial. Kèm các phiếu xuất và khách hàng đã nhận của từng nhánh |
| AC-17 | 3 | Sản phẩm Trà quế (is_food) chưa có giấy tờ ATTP | OWNER chuyển PUBLISHED | Từ chối BR-14, nêu rõ thiếu giấy tờ nào |
| AC-18 | 3 | Sản phẩm PUBLISHED | Kiểm tra /san-pham/<slug> bằng Rich Results Test và PageSpeed Insights (mobile) | JSON-LD Product hợp lệ, không lỗi; LCP < 2,5 giây; có trong sitemap.xml; /q/ bị chặn trong robots.txt |
| AC-19 | 3 | Đổi slug sản phẩm | Mở URL cũ | Chuyển hướng 301 sang URL mới |

| ID | GĐ | Given (cho trước) | When (khi) | Then (thì) |
| --- | --- | --- | --- | --- |
| AC-20 | 2 | Người mua D đã có số 0912 345 678 | Lập đơn kênh DIRECT, gõ +84912345678 | Tự điền thông tin của D; đơn lưu với buyer_id = D, không tạo người mua mới |
| AC-21 | 2 | Đơn kênh WEBSITE chưa có số điện thoại người mua | Bấm Lưu | Từ chối BR-22 "Cần tên và số điện thoại người mua" |
| AC-22 | 2 | Đơn có 2 chai tinh dầu 10 ml, giá 150.000 đ/chai | Thêm quà: quét 1 túi thơm có serial + chọn 1 thiếp (không tem), lưu | Đơn có 3 dòng; tổng tiền 300.000 đ; serial túi thơm → ISSUED; phiếu in có nhãn "Quà tặng" |
| AC-23 | 2 | Lô TP có serial đã bán cho 12 người mua | OWNER thu hồi lô rồi mở tra cứu xuôi | Thấy đủ 12 người mua; bấm "Xem đầy đủ" ra số điện thoại để liên hệ, mỗi lần bấm có trong audit_log |
| AC-24 | 2 | Người mua "Nguyễn Văn An", 0912345678 | Mở danh sách đơn hoặc in phiếu, bằng tài khoản bất kỳ | Hiển thị N V A và *******678 |

Các kịch bản AC-25 trở đi thuộc phần sản xuất theo sổ tay (công thức, kho phụ liệu, ủ, lưu mẫu, thử lưu hương, truy xuất phụ liệu). Ngày dùng trong ví dụ lấy từ sổ tay (QC1-261117-01, mẻ pha 17/11/2026).

| ID | GĐ | Given (cho trước) | When (khi) | Then (thì) | BR |
| --- | --- | --- | --- | --- | --- |
| AC-25 | 2 | Công thức QC1 ACTIVE (TTV 31,40; Q 8,97; CAM 49,35 g trên mẻ 89,72 g); lô TTV-2611-01 còn 500 g, Q-2610-01 còn 200 g, CAM-2611-01 còn 600 g (không có luồng); OWNER tạo lệnh QC1 với target_batch_g = 897,2 | Xưởng mở lệnh, quét 3 lô, gõ gram thực tế 314,02 / 89,70 / 493,50 | Máy gợi ý 314,00 / 89,70 / 493,50 g. Tạo 3 dòng production_ingredient (có suggested_g); tồn còn 185,98 / 110,30 / 106,50 g; không có lỗi BR-08 dù lô phụ liệu không có luồng; không có cảnh báo lệch (lệch 0,02 g ≤ 0,05 g) | BR-26, BR-27, BR-08 |
| AC-26 | 2 | Lệnh QC1 DRAFT; lô CAM-2611-02 còn 100 g, lô CAM-2608-01 quá hạn, lô DPG-2611-01 | (a) Gõ 493,50 g từ CAM-2611-02; (b) quét CAM-2608-01; (c) quét DPG-2611-01 vào dòng cam ngọt; (d) gõ 314,50 g cho dòng TTV gợi ý 314,00 g | (a)(b)(c) từ chối 409 (tồn không đủ, lô quá hạn, sai phụ liệu), tồn các lô không đổi, không có dòng production_ingredient mới; (d) lưu được kèm cảnh báo vàng "lệch gợi ý 0,50 g", tồn trừ đúng 314,50 g | BR-27 |
| AC-27 | 2 | Lệnh QC1 bắt đầu ủ ngày 17/11/2026, batch_code = QC1-261117-01, cure_ready_on = 08/12/2026; các dòng nguyên liệu bất biến | (a) 20/11/2026 WORKSHOP bấm Hoàn thành; (b) OWNER hoàn thành cùng ngày có override_cure_reason; (c) WORKSHOP sửa gram một dòng | (a) 409 CURE_NOT_READY "Mẻ QC1-261117-01 còn 18 ngày mới đủ ủ"; không có lô thành phẩm; lệnh vẫn CURING. (b) được, ghi cure_check_note và audit_log. (c) từ chối 409. Bấm "Ủ thêm" 7 ngày: cure_ready_on = 15/12/2026, có lý do | BR-28 |
| AC-28 | 2 | Lệnh QC1 trên (số lượng nhân 10 lần so với sổ tay: 99 chai / 897,2 g thay vì 9 chai / 89,72 g), đã ủ đủ 21 ngày; sản phẩm tinh dầu khuếch tán có shelf_life_months = 18; phụ liệu cân tổng 897,22 g; không có lô quế đưa thẳng | Ngày 08/12/2026 hoàn thành: 0,897 kg, 99 chai | Tạo product_lot code QC1-261117-01, blend_date 17/11/2026, mfg_date 08/12/2026, exp_date 08/06/2028 (18 tháng); input_weight_kg = 0, input_ingredient_g = 897,22, yield_pct = NULL, input_cost = 0, unit_cost = 0 (nghĩa là chưa tính phụ liệu, BR-10); lệnh DONE; màn hình hỏi lưu mẫu rồi sang gán tem | BR-09, BR-10, BR-11, BR-28 |
| AC-29 | 2 | Sản phẩm Sáp thơm (shelf_life_months trống) và Tinh dầu quế 100% 10 ml (24 tháng), lệnh đã đủ ngày ủ | (a) Hoàn thành lô sáp không nhập exp_date; (b) nhập exp_date rồi hoàn thành lại; (c) hoàn thành lô Q100 ngày 01/12/2026 | (a) 400 "Cần nhập hạn dùng", không tạo lô, lệnh vẫn CURING; (b) tạo lô với hạn đã nhập; (c) exp_date mặc định 01/12/2028 | BR-11 |
| AC-30 | 2 | Đã tạo công thức CHUNG-QM. Dầu quế chưng tại xưởng: NL-2610-0031 (người bán S, đồi P) → lệnh chưng → QM-2610-02 → lệnh ủ U-Q 28 ngày → Q-2610-01 → lô QC1-261117-01; cùng lô dùng CAM-2609-01 mua ở PNP-260915-001 (nơi bán V); serial X thuộc lô QC1 | OWNER gọi GET /trace?code=X&direction=up (và nhập mã X ở ô tra cứu) | Cây đi đủ: serial → QC1-261117-01 → lệnh → Q-2610-01 → lệnh ủ → QM-2610-02 → lệnh chưng → NL-2610-0031 → phiếu nhập → S → đồi P → xã (nút cuối end = MATERIAL_SOURCE); nhánh khác: CAM-2609-01 → PNP-260915-001 → V (end = EXTERNAL_VENDOR). Cũng ra kết quả khi nhập mã lô QC1-261117-01 hoặc Q-2610-01 | BR-31 |
| AC-31 | 2 | Lô QM-2610-03 nhận từ gia đình qua phiếu nhập phụ liệu (vendor_name "Nguồn gia đình"), đã ủ thành Q-2610-02 và dùng cho lô RQ1-261120-01 | OWNER truy xuất ngược một serial của lô đó; khách mở /q/ của serial | Cây dừng ở phiếu nhập phụ liệu và hiện dòng "nguồn ngoài, chưa nối về lô quế"; trang công khai không hiện vùng nguyên liệu hay đồi, không hiện "Nguồn gia đình" | BR-31, BR-17 |
| AC-32 | 2 | Lô CAM-2609-01 đã dùng trực tiếp cho lô QC1-261117-01 và gián tiếp qua TT1 → DDT → lô viên thạch cao VTC-261125-01; các serial đã bán cho 5 người mua | OWNER tra cứu xuôi từ CAM-2609-01 | Thấy cả hai lô thành phẩm, mọi serial, phiếu xuất và 5 người mua (che theo BR-24); chọn các lô cần thu hồi, mỗi lô thu hồi riêng có audit_log | BR-31, BR-15 |
| AC-33 | 2 | Lô thành phẩm dùng lô CAM-2609-01 (nơi bán V) và Q-2610-01; serial ISSUED | Gọi GET /api/public/trace/{serial}; mở /q/{serial}; mở /q/Q-2610-01; WORKSHOP và OWNER gọi API phiếu nhập và lô phụ liệu | Response và HTML không chứa V, số phiếu PNP, số lô nhà cung cấp, mã CAM-2609-01 hay Q-2610-01; /q/Q-2610-01 không phải đường dẫn hợp lệ (mã không tồn tại, không lộ rằng đó là mã lô). WORKSHOP đăng nhập cũng không thấy nơi bán trên trang công khai. Mở /api/public/trace/Q-2610-01 trả "không tồn tại" giống serial không có và không ghi scan_event. WORKSHOP gọi GET /ingredient-receipts, GET /ingredient-lots/by-code/CAM-2609-01 thì response không có vendor_name, vendor_phone; OWNER gọi thì có | BR-17 |
| AC-34 | 2 | Sản phẩm QC1 có requires_retention_sample = true; lô QC1-261117-01 vừa DONE ngày 08/12/2026 | (a) Bấm Lưu mẫu, vị trí "Tủ A2"; (b) lô khác bỏ qua bước này, gán tem rồi xuất hàng; (c) OWNER hủy mẫu ngày 01/06/2027; (d) lô QC1 đã bị thu hồi, hủy mẫu sau 08/12/2027 | (a) retained_sample RETAINED, retain_until = 08/12/2027, quantity của lô không đổi, chai lưu mẫu không có serial. (b) lô nằm trong "Lô chưa lưu mẫu" của OWNER, nhưng gán tem và xuất vẫn được. (c) 409 chưa đến hạn. (d) 409 vì lô RECALLED. Mẫu còn dưới 30 ngày tới hạn tô cam | BR-29 |
| AC-35 | 2 | Sản phẩm Tinh dầu quế 100% có requires_retention_sample = false; lô Q100 vừa DONE | (a) Xem "Lô chưa lưu mẫu"; (b) OWNER bật cờ rồi hoàn thành lô Q100 mới | (a) lô Q100 không có trong danh sách; (b) lô mới xuất hiện trong danh sách, retain_until tính theo setting.retain_default_months = 12 (công thức Q100 để trống retain_months). Lô cũ không bị truy thu | BR-29 |
| AC-36 | 2 | Công thức VTC (viên thạch cao); đợt TL-2611-01 gồm 3 biến thể 25% / 35% / 45% × 3 nơi (tủ kín, ô tô, phòng) = 9 mẫu; đã nhập cân và điểm của 5 người cho ngày 0, 1, 3, 7, 14, 21, 28. Biến thể 35%: ngày 1 cường độ TB 3,6; ngày 28 trong tủ kín cường độ TB 2,8; độ dễ chịu TB 4,0; mất 0,6 g trong 3 ngày đầu, tổng mất 2,4 g. Biến thể 45%: ngày 1 cường độ TB 4,4 | (a) Xem đánh giá; (b) OWNER đóng đợt chọn 45%; (c) đóng đợt chọn 35%, longevity_weeks = 4; (d) tạo đợt cho công thức QC1 | (a) 35% PASS (cả 4 tiêu chí; 0,6 ≤ 2,4/3 = 0,8); 45% FAIL (tiêu chí 1). (b) 409, biến thể không đạt. (c) đợt DONE, result PASS, chosen_variant 35%; từ lúc này mới in được "lưu hương 4 tuần" cho viên thạch cao; trước đó không in. (d) 400, chỉ SAP, VTC, TUI | BR-30 |
| AC-37 | 2 | Công thức QC1 version 1 đã có lệnh dùng | (a) OWNER sửa gram một dòng của v1; (b) bấm "Tạo phiên bản mới", sửa, kích hoạt | (a) 409, v1 giữ nguyên. (b) tạo v2 (DRAFT) rồi ACTIVE, v1 → RETIRED; lệnh cũ vẫn trỏ v1; lệnh mới tự chọn v2; công thức TT1 tự tham chiếu chính nó bị từ chối khi lưu | BR-26 |
| AC-38 | 2 | Lệnh ủ dầu quế U-Q (INTERMEDIATE) bắt đầu ủ ngày 20/10/2026, cure_min_days = 28; lệnh QC1 đang DRAFT | (a) Ngày 05/11/2026 tìm lô Q-… để đưa vào lệnh QC1; (b) ngày 17/11/2026 hoàn thành lệnh U-Q với 95,50 g | (a) chưa có lô Q nào của lệnh này (lệnh U-Q còn CURING, chỉ đủ ngày 17/11/2026), không đưa vào được; (b) tạo ingredient_lot Q-2610-01 (mã sinh lúc bắt đầu ủ nên mang tháng 10, BR-20), initial_g = remaining_g = 95,50, exp_date = mfg + 24 tháng, status IN_STOCK, in tem lô phụ liệu; lệnh DONE | BR-28, BR-27 |

## 13. Câu hỏi mở

Đội dev dùng giá trị mặc định ghi trong ngoặc cho đến khi chủ DN chốt. Các giá trị này đều nằm trong setting hoặc dữ liệu danh mục, đổi không cần sửa code.

- ☐ Khổ tem serial và tem lô, dòng máy in nhiệt (mặc định 40 × 30 mm)
- ☐ In phiếu bằng máy in A5 hay giấy nhiệt 80 mm (mặc định A5)
- ☐ Tên miền thương hiệu dùng trong URL QR — phải chốt trước khi in cuộn tem đầu tiên, vì đã in thì không đổi được
- ☐ Ngưỡng cảnh báo số lần quét một serial (mặc định 20)
- ☐ Ngưỡng cảnh báo giá mua lệch bảng giá (mặc định 20%)
- ☑ Hạn dùng mặc định: tinh dầu khuếch tán 18 tháng, tinh dầu quế 100% 24 tháng (sổ tay tr.6, tr.8). Sáp thơm, viên thạch cao, túi vỏ quế: sổ tay không ghi, để trống, xưởng nhập exp_date tay mỗi lô (BR-11). Còn ☐ trà, ống quế…: chủ DN điền product.shelf_life_months, trống thì cũng nhập tay
- ☐ Danh sách sản phẩm đợt 1, SKU và quy cách
- ☐ Danh sách thôn và các hộ thu mua trực tiếp để seed dữ liệu
- ☐ Hộ nào đồng ý hiện tên trên trang truy xuất (mặc định: không hiện)
- ☐ Giá vốn có cần tính thêm bao bì và phụ liệu không (mặc định: không, BR-10). Nếu có: thêm đơn giá vào phiếu nhập phụ liệu và tính giá gram cho bán thành phẩm; đây là việc thêm, không đổi mô hình hiện có

**Câu hỏi mở thêm từ sổ tay sản xuất** (sổ tay bản 2 ngày 17/11/2026). Mỗi câu ghi giá trị mặc định đội đang dùng; đều đổi được bằng dữ liệu, không sửa code:

- ☑ Dầu quế đưa vào pha chế lấy từ đâu? Sổ tay chỉ mô tả từ lúc đã có dầu mới chưng (tr.8). Đã chốt: hỗ trợ cả hai. Chưng tại xưởng thì chuỗi truy xuất nối về lô quế (cần tạo công thức chưng CHUNG-QM, hiện chưa seed vì sổ tay không có công thức này); nhận hoặc mua ngoài thì chuỗi dừng ở nơi bán và trang công khai không hiện vùng nguyên liệu (BR-31, AC-31). Lead duyệt theo ủy quyền của sếp #799
- ☑ Lưu mẫu 12 tháng áp cho sản phẩm nào ngoài 6 công thức tinh dầu khuếch tán? Đã chốt: chỉ 6 công thức đó, bật thêm bằng cờ product.requires_retention_sample (BR-29). Lead duyệt theo ủy quyền của sếp #799
- ☐ Tinh dầu khuếch tán có thử theo cách riêng (chạy máy 30 phút, chấm điểm phút 5, 30, 60; sổ tay tr.13). Hệ thống chưa lưu kết quả này; mặc định: ghi trên giấy theo sổ tay, hỏi chủ DN có muốn số hóa không
- ☐ Các bước làm trước khi vào ủ không theo dõi bằng lệnh: lắng dầu quế 3–5 ngày, thoát khí 7 ngày đầu, phơi viên thạch cao 5–7 ngày trước khi tẩm (sổ tay tr.8, tr.11–12). Mặc định: ghi trong recipe.note, chỉ ủ chính thức mới có lệnh CURING
- ☐ Hạn dùng của lô thành phẩm có được vượt hạn dùng sớm nhất của phụ liệu bên trong không? Sổ tay không nói; mặc định: không kiểm; phụ liệu đã quá hạn thì bị chặn khi đưa vào lệnh (BR-27)
- ☑ Mẫu mã lô thành phẩm và lô phụ liệu: đội đã chốt theo sổ tay (QC1-261117-01; mẫu Q-2611-01 của sổ tay), lý do ở mục 10. Lead duyệt theo ủy quyền của sếp #799. Mã lô bán thành phẩm sinh lúc bắt đầu ủ nên mang tháng bắt đầu ủ (ví dụ lô dầu ủ từ 20/10 là Q-2610-01 dù xong ủ tháng 11). Xưởng cần xác nhận cách ghi này có hợp thói quen dán lọ không
