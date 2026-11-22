# Kiến trúc frontend: Astro, SEO và Google Ads

Trạng thái: bản nháp chờ sếp duyệt (task #57; sửa theo README mục 6 ở task #68). Ngày viết: 21/11/2026.

Căn cứ:
- `docs/thiet-ke-chi-tiet.md` (TK) mục 2 (phân quyền), 8 (website, /q/), 9 (API), 11 (phi chức năng), BR-16, BR-17, BR-18.
- Các quyết định của Lead ở tin #666 và #671 (theo phản biện #654 và #657):
  - Một project Astro.
  - Tách `site.css` và `admin.css`.
  - Trang SSR trả `Cache-Control` 60/600, chưa cache ở Caddy.
  - Ảnh sinh ở Django lúc upload.
  - Astro chuyển tiếp IP thật của khách.
- Tiêu chí cứng của sếp ở #647/#648:
  - Trang công khai không có JS framework.
  - Đạt Core Web Vitals «Tốt».
  - Đủ các trang chính sách mà Google Ads và Merchant Center yêu cầu.
  - Có Consent Mode v2.
- Mockup đã duyệt `docs/mockup/ban-chinh.html` (route lấy từ `docs/mockup/_tools/vo.html:208-226`).

Các file cùng bộ: `backend.md` (API, xác thực, OpenAPI), `van-hanh.md` (Docker, Caddy, CI), `README.md` (tổng quan). Mục 11 liệt kê những điểm file này giả định ở hai file kia.

---

## 1. Project và cây thư mục

Có **một** project Astro nằm trong `frontend/`, quản lý bằng pnpm:

- Adapter `@astrojs/node` ở chế độ `standalone`.
- `output: 'server'`. Trang nào cần tĩnh thì tự bật `export const prerender = true`.
- Tailwind CSS v4 qua `@tailwindcss/vite`, cùng daisyUI 5.
- Node theo image ghim ở van-hanh.md 2 (đề xuất 24 LTS, xem mục 11, V8).
- Mọi thư viện ghim đúng phiên bản trong `pnpm-lock.yaml`. Lấy bản ổn định mới nhất tại lúc dựng khung.

```
frontend/
├─ astro.config.mjs
├─ package.json
├─ pnpm-lock.yaml
├─ tsconfig.json              # extends "astro/tsconfigs/strict"
├─ biome.json
├─ lighthouserc.cjs           # Lighthouse CI: URL, ngưỡng điểm, ngân sách (mục 8)
├─ public/                    # favicon, logo, ảnh tĩnh của layout (không chứa ảnh sản phẩm)
├─ scripts/
│  └─ gen-api.mjs             # chạy openapi-typescript (mục 5.4)
└─ src/
   ├─ middleware.ts           # chuẩn hoá URL, chặn /quan-ly, gắn Cache-Control (mục 2, 5)
   ├─ env.d.ts                # kiểu App.Locals
   ├─ content.config.ts       # content collection «chinh-sach»
   ├─ content/
   │  └─ chinh-sach/          # bao-mat.md, doi-tra.md, van-chuyen.md, lien-he.md
   ├─ styles/
   │  ├─ site.css             # chỉ cho trang công khai (mục 4)
   │  └─ admin.css            # chỉ cho /quan-ly
   ├─ layouts/
   │  ├─ SiteLayout.astro     # <html lang="vi">, SeoHead, Header, Footer, ConsentBanner, TagLoader
   │  ├─ TraceLayout.astro    # layout gọn cho /q/ và /truy-xuat (không có menu lớn)
   │  ├─ AdminLayout.astro    # menu trái, thanh trên, admin.css
   │  └─ PrintLayout.astro    # phiếu A5/80 mm, tem 50×30 (CSS @page)
   ├─ components/
   │  ├─ site/                # SeoHead, JsonLd, Breadcrumb, Picture, Header, Footer,
   │  │                       # ProductCard, BuyButtons, ConsentBanner, TagLoader, TraceResult
   │  └─ admin/               # Sidebar, Topbar, ScanBox, WeightInput, DataTable, Toast, ...
   ├─ scripts/
   │  └─ admin/               # TypeScript thuần cho màn quản lý (mục 3)
   │     ├─ api.ts            # fetch trình duyệt → /api/v1, kèm X-CSRFToken
   │     ├─ scan.ts           # ô quét luôn giữ focus, Enter, tách serial từ URL
   │     ├─ weight.ts         # ô số cân, đọc số «12,5» và «12.5»
   │     ├─ beep.ts           # bíp ngắn/dài bằng Web Audio
   │     ├─ page-data.ts      # đọc <script type="application/json" id="page-data"> (mục 3.2)
   │     └─ raw-material-map.ts  # entry màn vùng nguyên liệu, nạp Leaflet (mục 3.3)
   ├─ lib/
   │  ├─ api/
   │  │  ├─ v1.d.ts           # SINH TỰ ĐỘNG từ backend/openapi/v1.json, có commit, không sửa tay
   │  │  ├─ public.d.ts       # SINH TỰ ĐỘNG từ backend/openapi/public.json
   │  │  └─ server.ts         # client cho SSR: URL nội bộ, chuyển cookie và IP (mục 5)
   │  ├─ image.ts            # dựng srcset từ ImageRef (mục 4.3)
   │  ├─ format.ts           # định dạng tiền (int VND) và số cân dạng chuỗi "120.50"
   │  ├─ cache.ts            # hằng Cache-Control
   │  ├─ seo.ts              # dựng title, canonical, JSON-LD, breadcrumb
   │  ├─ safe-json.ts        # JSON nhúng trong <script> an toàn (mục 3.2, 6.2)
   │  ├─ xml.ts              # escape XML cho sitemap, feed (mục 6.4, 7.5)
   │  ├─ url.ts              # chuẩn hoá URL công khai, dựng Location 301 (mục 5.5)
   │  ├─ serial.ts           # chuẩn hoá serial theo BR-16
   │  ├─ business.ts         # tên, địa chỉ, SĐT, email, MST (dùng chung footer, JSON-LD, /q/)
   │  └─ access.ts           # bảng tiền tố route chỉ OWNER (mục 5.5)
   └─ pages/
      ├─ index.astro                     # /
      ├─ san-pham/index.astro            # /san-pham
      ├─ san-pham/[slug].astro           # /san-pham/<slug>, 301 slug cũ
      ├─ [slug].astro                    # /<slug trang tĩnh> từ site_page (câu chuyện, vùng quế…)
      ├─ chinh-sach-bao-mat.astro        # prerender
      ├─ chinh-sach-doi-tra.astro        # prerender
      ├─ chinh-sach-van-chuyen.astro     # prerender
      ├─ lien-he.astro                   # prerender
      ├─ truy-xuat.astro                 # ô nhập mã tay, form GET không JS
      ├─ q/[serial].astro                # trang truy xuất, noindex
      ├─ sitemap.xml.ts
      ├─ robots.txt.ts
      ├─ feed/google-merchant.xml.ts     # để dành, chưa dựng (mục 7.5)
      ├─ healthz.ts                      # 200 "ok", không gọi API, no-store (healthcheck compose)
      ├─ 404.astro
      ├─ 500.astro
      └─ quan-ly/                        # toàn bộ app nội bộ (mục 1.1)
         ├─ dang-nhap.astro
         ├─ index.astro                  # trang chủ theo vai (OWNER / WORKSHOP)
         ├─ nhap-hang/ ...  xuat-hang/ ...  ton-kho/ ...  san-xuat/ ...
         ├─ dong-goi.astro  in/ ...  mau-luu.astro  thu-luu-huong/ ...   # hai vai, nút theo vai
         └─ danh-muc/ ...  bang-gia.astro  cong-thuc/ ...  phu-lieu/ ...  lo-thanh-pham/ ...
            cuon-tem.astro  tra-cuu.astro  khach-hang/ ...  bao-cao.astro  vung-nguyen-lieu.astro
```

Quy tắc ranh giới, chặn bằng lint (mục 9):
- `components/site/` và các trang công khai **không import** gì từ `components/admin/`, `scripts/admin/` hay `styles/admin.css`. Chiều ngược lại cũng vậy.
- Chỉ có `lib/` là dùng chung.

### 1.1 Route của app nội bộ

Mockup đặt app xưởng ở gốc (`/nhap-hang`, `/ton-kho`…). Nhưng website công khai cũng nằm ở gốc cùng tên miền, nên **mọi màn nội bộ dời vào dưới `/quan-ly`**. Phần đuôi giữ đúng như mockup:

| Mockup (`vo.html`) | Route thật |
| --- | --- |
| `/` (home_owner, home_shop) | `/quan-ly` |
| `/login` | `/quan-ly/dang-nhap` |
| `/nhap-hang…`, `/phieu-nhap`, `/xuat-hang…`, `/don-hang`, `/ton-kho…`, `/san-xuat…`, `/dong-goi`, `/in/…`, `/mau-luu` | thêm tiền tố `/quan-ly`, ví dụ `/quan-ly/san-xuat/ua/12/ngui` |
| `/quan-ly/…` (danh mục, công thức, cuộn tem, tra cứu, báo cáo…) | giữ nguyên |
| `/q/…`, `/truy-xuat` | giữ nguyên, thuộc website công khai |

Cái giá của cách này: URL dài hơn mockup một đoạn. Bù lại:
- Không đụng không gian URL của website.
- Chỉ cần một tiền tố để chặn đăng nhập, gắn `no-store` và `noindex`.

---

## 2. Render và Cache-Control

| Nhóm trang | Cách render | `Cache-Control` | Ghi chú |
| --- | --- | --- | --- |
| `/`, `/san-pham`, `/san-pham/<slug>`, `/<slug trang tĩnh>` | SSR | `public, max-age=60, stale-while-revalidate=600` | Không chuyển cookie sang Django, nên mọi khách nhận cùng một HTML (mục 5.2) |
| `/chinh-sach-*`, `/lien-he` | prerender lúc build | Caddy gắn `public, max-age=3600` (van-hanh.md) | Nội dung trong `src/content/chinh-sach/` |
| `/truy-xuat` | SSR | như trang công khai | Form `GET /truy-xuat?ma=…` trả 302 sang `/q/<mã đã chuẩn hoá>` |
| `/q/<serial>` | SSR | `private, max-age=60, stale-while-revalidate=600` | Có `noindex` (mục 6.6) và `Vary: Cookie`. Ngân sách < 300 KB |
| `/sitemap.xml`, `/robots.txt` | SSR | `public, max-age=3600` | |
| `/feed/google-merchant.xml` | SSR | `public, max-age=3600` | Để dành, chưa dựng (mục 7.5) |
| `/quan-ly/**` | SSR | `private, no-store` | Có `X-Robots-Tag: noindex, nofollow` |
| `/_astro/*` (CSS/JS có hash) | file tĩnh | `public, max-age=31536000, immutable` | Caddy gắn |
| Lỗi 5xx | | `no-store` | Không để trình duyệt giữ trang lỗi |

**Vì sao /q/ để `private` chứ không `public`:**
- Mỗi lần mở /q/ phải ghi một `scan_event` (TK 8.4).
- Nếu sau này đặt cache dùng chung (Caddy, CDN), `public` sẽ làm Django không thấy lượt quét. `private` chặn trước rủi ro đó.
- Trong 60 giây đầu, trình duyệt mở lại cùng mã thì dùng bản đã giữ, không đếm thêm lượt. Đây là hành vi mong muốn: F5 liên tục không thổi phồng `scan_count`.

**Cài đặt:**
- `middleware.ts` gắn header theo tiền tố đường dẫn, sau khi trang đã render. Trang nào tự đặt `Cache-Control` thì middleware giữ nguyên.
- Hằng số đặt trong `lib/cache.ts`:

```ts
export const CACHE_PUBLIC = "public, max-age=60, stale-while-revalidate=600";
export const CACHE_TRACE = "private, max-age=60, stale-while-revalidate=600";
export const CACHE_PRIVATE = "private, no-store";
export const CACHE_FEED = "public, max-age=3600";
```

**Chưa có cache dùng chung (theo #666 ý d):** mọi lượt tải trang công khai đều SSR và gọi Django một lần. Với 100 lượt quét/phút (TK 11) thì 2 vCPU chịu được. Khi đo thấy chậm, bật cache ở Caddy cho nhóm `public`; nhóm /q/ và `/quan-ly` không bị ảnh hưởng nhờ `private`.

**Prerender và dữ liệu:**
- Trang prerender không được gọi API lúc build, vì CI build không có Django.
- Vì vậy thông tin doanh nghiệp nằm trong `lib/business.ts` (có commit). Trang chính sách là Markdown trong repo.

---

## 3. JavaScript

### 3.1 Trang công khai

Trang công khai **không gửi JS framework và không có island**. JS chỉ gồm hai script inline (`is:inline`), tổng ≤ 2 KB gzip:

1. `TagLoader`: đặt Consent Mode mặc định, nạp GTM muộn, bắt click nút mua (mục 7).
2. `ConsentBanner`: hiện banner khi khách chưa chọn, lưu lựa chọn.

Phần còn lại không cần JS:
- Carousel ảnh sản phẩm dùng `scroll-snap` CSS và các nút là link neo `#anh-2`.
- Menu di động dùng `<details>`.
- Ô tra mã là form GET.
- Khối «Câu chuyện», «Cách dùng» dùng `<details>` (daisyUI `collapse`).

### 3.2 Màn quản lý (quét, cân): chọn TypeScript thuần, không dùng Preact

Màn quản lý dùng `<script>` của Astro, viết TypeScript thuần trong `src/scripts/admin/`. Astro tự đóng gói các script này thành module có hash.

Lý do:
- Máy quét USB hoạt động như bàn phím (TK 9, TK 11). Logic chỉ gồm:
  - giữ focus ở ô quét;
  - bắt Enter;
  - tách 10 ký tự sau `/q/`;
  - gọi API;
  - bíp;
  - thêm một dòng vào bảng.
- Tất cả chưa tới vài trăm dòng, Preact không mang lại gì đáng kể.
- Preact thêm runtime khoảng 4 KB và JSX. Tệ hơn, nó tạo hai đường render cho cùng một bảng: `.astro` ở server và `.tsx` ở client. Dev phải giữ hai bản HTML khớp nhau.
- Với TS thuần, dòng mới clone từ `<template>` mà server đã render sẵn. Chỉ có một nguồn markup.

Cái giá: màn có nhiều trạng thái (phiếu nhập nhiều dòng, lệnh sản xuất có công thức) phải viết code thao tác DOM. Ranh giới để xét lại:
- Nếu một màn vượt khoảng 300 dòng code DOM, hoặc phải đồng bộ trạng thái giữa nhiều khối, thì được dùng **một island Preact cho riêng màn đó** (`client:load`).
- Việc này cần Lead duyệt. Island Preact **không bao giờ** dùng ở trang công khai.

Quy ước cho `scripts/admin/`:
- Mỗi màn một file entry, import các module chung (`api.ts`, `scan.ts`, `weight.ts`, `beep.ts`, `page-data.ts`).
- Không có state toàn cục. Dữ liệu ban đầu do SSR render vào HTML. Khi cần, script đọc thêm từ `<script type="application/json" id="page-data">`.
- Ngân sách: JS của một màn quản lý ≤ 30 KB gzip. Mục tiêu tham khảo, không chặn CI. Ngoại lệ duy nhất là màn vùng nguyên liệu (mục 3.3).

**JSON nhúng phải qua `lib/safe-json.ts`.** Dữ liệu trong `page-data` có giá trị do người dùng nhập (tên khách, ghi chú của WORKSHOP). Nếu giá trị chứa `</script>` mà nhúng nguyên `JSON.stringify` thì thoát được khỏi thẻ và thành stored XSS chạy trong phiên OWNER. Quy tắc: **mọi** JSON đặt trong thẻ `<script>` (cả `page-data` lẫn JSON-LD ở mục 6.2) đi qua đúng một hàm:

```ts
// src/lib/safe-json.ts
/** JSON.stringify rồi thay ký tự "<" (U+003C) bằng 6 ký tự "\u003c", U+2028 bằng "\u2028", U+2029 bằng "\u2029".
 *  Kết quả vẫn là JSON hợp lệ, JSON.parse ra đúng giá trị gốc. */
export function safeJson(value: unknown): string;
```

```astro
<script type="application/json" id="page-data" set:html={safeJson(data)} />
```

- `set:html` chỉ được nhận kết quả của `safeJson` hoặc trường `*_html` của DTO (mục 10). Không `set:html={JSON.stringify(…)}`.
- `scripts/admin/page-data.ts` có `readPageData<T>(): T`, đọc `textContent` rồi `JSON.parse`.
- Test vitest: giá trị `"</script><img src=x onerror=alert(1)>"` ra chuỗi chứa `\u003c/script>`, không còn ký tự `<` nào; chuỗi có U+2028, U+2029 ra `\u2028`, `\u2029` (6 ký tự ASCII); `JSON.parse` kết quả trả lại đúng giá trị gốc.

### 3.3 Bản đồ vùng nguyên liệu: Leaflet + OpenStreetMap

TK 7.1 yêu cầu bản đồ các đồi có tọa độ trên màn `/quan-ly/vung-nguyen-lieu`, chỉ OWNER dùng, bằng Leaflet + OpenStreetMap, không cần khoá API.

- **Gói:** `leaflet` (thêm vào nhóm «Chạy» ở mục 9), kèm `@types/leaflet` ở nhóm Dev. Không dùng plugin, không dùng wrapper.
- **Cách nạp:** entry `scripts/admin/raw-material-map.ts` chỉ được import trong `pages/quan-ly/vung-nguyen-lieu.astro`. Trong entry dùng `await import("leaflet")` để Vite tách Leaflet thành chunk riêng, màn khác không tải. CSS `leaflet/dist/leaflet.css` import trong cùng entry, không đưa vào `admin.css`.
- **Ảnh marker:** chép `marker-icon.png`, `marker-icon-2x.png`, `marker-shadow.png` vào `public/leaflet/` và đặt `L.Icon.Default.imagePath = "/leaflet/"`. Lý do: Leaflet tự dò đường dẫn ảnh theo CSS và hỏng khi Vite đổi tên file.
- **Dữ liệu:** SSR gọi `GET /api/v1/…` (đồi, tọa độ, theo TK 9) rồi render bảng đồi bằng HTML và nhúng danh sách ghim vào `page-data` qua `safeJson`. Bản đồ chỉ đọc `page-data`, không gọi API thêm. Đồi thiếu tọa độ không có ghim, chỉ hiện trong bảng với nhãn «thiếu thông tin truy xuất».
- **Tile:** `https://tile.openstreetmap.org/{z}/{x}/{y}.png`, `maxZoom: 19`, giữ dòng ghi công `© OpenStreetMap contributors` (bắt buộc theo chính sách tile OSM). Màn này chỉ có một người dùng nên lượng tải nằm xa giới hạn của chính sách đó. Nếu sau này đưa bản đồ ra trang công khai thì phải đổi sang nhà cung cấp tile khác, vì tile OSM không dành cho tải lớn.
- **CSP:** màn này cần `img-src 'self' data: https://tile.openstreetmap.org https://*.tile.openstreetmap.org`. Caddy đã gắn đúng `img-src` này cho cả site (van-hanh.md 3, điểm V9 ở mục 11). Để chung chấp nhận được vì `img-src` chỉ cho tải ảnh, không cho chạy mã; `script-src` và `connect-src` vẫn chỉ `'self'`, nên Leaflet phải đóng gói trong bundle, không nạp từ CDN.
- **Ngân sách JS:** Leaflet khoảng 40 KB gzip, cộng CSS khoảng 4 KB. Màn này được tới **60 KB gzip** JS. Đây là ngoại lệ ghi rõ, không phải tiền lệ cho màn khác. Trang công khai không bao giờ nạp Leaflet; bản đồ ở trang liên hệ vẫn là link OSM (mục 7.4).
- **Lỗi tải tile** (mất mạng ở xưởng): bảng đồi vẫn đọc được vì là HTML do SSR render, bản đồ chỉ trống.

---

## 4. CSS, font, ảnh

### 4.1 Hai file CSS

`src/styles/site.css`:

```css
@import "tailwindcss" source(none);
@source "../pages";
@source not "../pages/quan-ly";
@source "../layouts/SiteLayout.astro";
@source "../layouts/TraceLayout.astro";
@source "../components/site";
@source "../content/chinh-sach";

@plugin "daisyui" {
  include: button, navbar, footer, breadcrumbs, card, badge, alert, collapse, link;
  themes: false;
  logs: false;
}
@plugin "daisyui/theme" {
  name: "vyc";
  default: true;
  --color-primary: #0f6b3a;      /* nút chính xanh lá, theo quyết định mockup */
  --color-secondary: #8a3b12;    /* nâu quế */
  /* các biến còn lại chốt lúc dựng theo mockup */
}

@font-face { /* xem 4.2 */ }
```

`src/styles/admin.css` có cùng khung:
- `@source` trỏ `../pages/quan-ly`, `../layouts/AdminLayout.astro`, `../layouts/PrintLayout.astro`, `../components/admin`.
- daisyUI `include` thêm các component admin dùng (`table`, `input`, `select`, `modal`, `tabs`, `toast`…).
- Admin **không dùng web font**: xưởng chạy Windows và mockup dùng `"Segoe UI", system-ui…` (`app.css:29`).

Quy tắc:
- `site.css` chỉ được import trong `SiteLayout` và `TraceLayout`. `admin.css` chỉ được import trong `AdminLayout` và `PrintLayout`.
- `include` của daisyUI là danh sách đóng: thêm component mới thì sửa danh sách và đo lại ngân sách.
- Giữ `build.inlineStylesheets: 'auto'` mặc định của Astro: CSS < 4 KB thì nhúng vào HTML, lớn hơn thì là file có hash, cache một năm. Nếu Lighthouse cho thấy CSS chặn render làm LCP vượt ngưỡng, đổi sang `'always'` cho trang công khai.

**Ngân sách** (CI chặn, mục 8): CSS của mỗi trang công khai **< 15 KB sau nén**.

### 4.2 Font

- Trang công khai dùng **Be Vietnam Pro** tự host qua `@fontsource/be-vietnam-pro`. Gói này cung cấp file woff2 đã cắt theo `unicode-range` (`vietnamese`, `latin`, `latin-ext`).
- Chỉ import 2 độ đậm, 400 và 700, mỗi độ đậm 2 subset: `vietnamese` và `latin`. Trình duyệt chỉ tải subset có ký tự xuất hiện trên trang.
- `font-display: swap`.
- Chỉ `preload` một file: 400 latin. File subset tiếng Việt tải theo `unicode-range`, không preload, để khỏi tranh băng thông với ảnh LCP.
- Font dự phòng khai báo `size-adjust`, `ascent-override` theo Arial để chữ không nhảy khi đổi font (CLS).
- Ngân sách font: ≤ 50 KB mỗi trang.

### 4.3 Ảnh

- Django sinh sẵn biến thể AVIF và WebP lúc upload (#666 ý d). Caddy phục vụ thẳng `/media/`.
- Astro **không** xử lý ảnh sản phẩm (không dùng `astro:assets` cho ảnh từ API).

Kiểu ảnh lấy đúng `ImageRef` của `backend.md` mục 6.5 (kiểu TS sinh từ `public.json`, đây chỉ là bản chép để đọc):

```ts
type ImageRef = {
  url: string;       // bản WebP lớn nhất, ví dụ "/media/img/3f/3fa9…-1440.webp"
  alt: string;
  key: string;       // "3f/3fa9…" (2 ký tự đầu / sha256)
  w: number;         // kích thước bản lớn nhất, để đặt width/height chống CLS
  h: number;
  widths: number[];  // các bề rộng có thật, trong [480, 960, 1440]; ảnh nhỏ thì thiếu bề rộng lớn
};
```

File của mỗi bề rộng nằm ở `/media/img/{key}-{w}.{avif|webp}`. `src/lib/image.ts` dựng srcset từ quy tắc đó, không cần backend trả từng URL:

```ts
export function srcset(img: ImageRef, ext: "avif" | "webp"): string;
// → "/media/img/3f/3fa9…-480.avif 480w, /media/img/3f/3fa9…-960.avif 960w, …"
export function heightFor(img: ImageRef, w: number): number; // giữ tỉ lệ w/h
```

Ảnh OG 1200×630 (JPEG) do backend sinh cho ảnh đầu của sản phẩm (backend.md 6.5). `ImageRef` không có đường dẫn tới bản này; `PublicProductOut` trả riêng trường `og_image: string | null` (backend.md 8, mục 11 G5). Trống thì `og:image` dùng `url` của ảnh đầu.

Component `components/site/Picture.astro`:

```ts
interface Props {
  image: ImageRef;
  sizes: string;            // ví dụ "(min-width: 768px) 50vw, 100vw"
  priority?: boolean;       // true cho ảnh LCP
}
```

`Picture` render ra:
- `<picture>` với `<source type="image/avif" srcset>` và `<source type="image/webp" srcset>`.
- `<img>` lấy `image.url` (WebP lớn nhất) làm `src`, luôn có `width={image.w}`, `height={image.h}`, `alt`, `decoding="async"`.
- Khi `priority` bật: `loading="eager"` và `fetchpriority="high"`. Còn lại: `loading="lazy"`.

**Preload ảnh LCP:** ảnh đầu của trang sản phẩm, và ảnh sản phẩm trên /q/, được `SeoHead` preload:

```html
<link rel="preload" as="image" type="image/avif"
      imagesrcset="…-480.avif 480w, …-960.avif 960w, …-1440.avif 1440w"
      imagesizes="(min-width: 768px) 50vw, 100vw" fetchpriority="high">
```

Trình duyệt không đọc được AVIF sẽ bỏ qua lệnh preload này nhờ thuộc tính `type`.

---

## 5. Gọi API

### 5.1 Hai đường gọi

| Ai gọi | URL | Dùng khi |
| --- | --- | --- |
| Astro SSR (server) | `API_INTERNAL_URL` = `http://backend:8000`, mạng nội bộ compose | Đọc dữ liệu để render mọi trang |
| Trình duyệt (chỉ ở `/quan-ly`) | `/api/v1/...`, cùng tên miền. Caddy chuyển `/api/*` sang Django | Mọi thao tác ghi: quét, lưu phiếu, hoàn thành lệnh… |

Quyết định: Astro **không làm proxy cho thao tác ghi**. Trình duyệt gọi thẳng Django qua Caddy, cùng origin, nên cookie phiên và CSRF của Django chạy đúng như thiết kế. SSR chỉ đọc. Ngoại lệ duy nhất là `/q/`: đó là GET và Django tự ghi `scan_event`.

Lý do: proxy ghi qua Astro sẽ nhân đôi xử lý lỗi, CSRF và timeout mà không thêm gì.

Cái giá: Caddy phải route `/api/*`, và Django phải chịu được request trực tiếp từ Internet. Thực ra Django đã phải chịu từ đầu, vì `/api/public` có rate limit.

Biến môi trường của frontend:

| Biến | Ví dụ | Dùng ở |
| --- | --- | --- |
| `API_INTERNAL_URL` | `http://backend:8000` | `lib/api/server.ts` |
| `SITE_URL` | `https://<tên miền chính>` | canonical, sitemap, feed, og:url (tuyệt đối) |
| `GTM_ID` | `GTM-XXXXXXX` hoặc rỗng | `TagLoader`. Rỗng thì không nạp thẻ (dev, CI, staging) |

Cả ba khai bằng `astro:env` (`envField.string({ context: "server", access: "secret" })`), đọc **lúc chạy**, không phải lúc build. Lý do: một image dùng cho cả staging và prod (van-hanh.md 2.2). Không dùng `access: "public"`: giá trị loại này bị nhúng cứng vào bundle lúc build, staging sẽ mang tên miền và GTM của prod, và `API_INTERNAL_URL` lúc chạy bị bỏ qua (Vinh thử ở #833). Vì vậy cũng không dùng `PUBLIC_SITE_URL` như bản nháp van-hanh.md mục 4 (mục 11, V3).

### 5.2 Client SSR: cookie, CSRF, IP thật

`src/lib/api/server.ts`:

```ts
import createClient, { type Client } from "openapi-fetch";
import { API_INTERNAL_URL } from "astro:env/server";
import type { paths as PublicPaths } from "./public";
import type { paths as V1Paths } from "./v1";

type ForwardMode = "anon" | "session";

/** Header chung: chuyển NGUYÊN X-Forwarded-For nhận từ Caddy, không nối thêm, không sửa. */
export function forwardHeaders(request: Request, mode: ForwardMode): Record<string, string>;

/** /api/public: mode "anon" cho trang nội dung, "session" cho /q/ (BR-18). */
export function publicApi(request: Request, mode: ForwardMode): Client<PublicPaths>;

/** /api/v1: luôn "session". Kiểu trả về chỉ có GET, nên SSR không gọi được lệnh ghi. */
export function v1Api(request: Request): Pick<Client<V1Paths>, "GET">;
// cả hai: baseUrl = API_INTERNAL_URL, timeout 3000 ms qua AbortSignal.timeout
```

`forwardHeaders` trả `{"Accept": "application/json", "X-Forwarded-For": <nguyên giá trị request đến>}` và thêm `Cookie` khi `mode = "session"`. Request đến không có `X-Forwarded-For` (dev không qua Caddy) thì không gửi header này; Django dùng `REMOTE_ADDR`.

`v1Api` chỉ để gọi GET, và kiểu `Pick<…, "GET">` bắt lỗi lúc `astro check` nếu ai gọi `.POST`. Lý do theo backend.md 4.2: Django kiểm Origin/Referer, request server-to-server từ Astro sẽ bị chặn.

**Cookie:**

| Trang | `mode` | Lý do |
| --- | --- | --- |
| Website công khai (`/`, `/san-pham…`, trang tĩnh, sitemap, feed) | `"anon"`: **không** chuyển Cookie | HTML giống nhau cho mọi khách, nên cache `public` được |
| `/q/<serial>` | `"session"` | Django cần biết người đang mở là nhân viên đã đăng nhập, để không đếm `scan_count` (BR-18) |
| `/quan-ly/**` | `"session"` | Gọi `/api/v1` cần phiên |

**CSRF:**
- SSR chỉ gọi GET (backend.md 4.2), nên Django không kiểm CSRF ở đường này. Astro **không bao giờ** ghi thay trình duyệt.
- Phía trình duyệt, `scripts/admin/api.ts` đọc cookie `csrftoken` và gửi header `X-CSRFToken` với mọi request không phải GET.
- Trang đăng nhập gọi `GET /api/v1/auth/csrf` trước (trả 204, đặt cookie), rồi `POST /api/v1/auth/login` (backend.md 4.1).

**IP thật (khớp backend.md 5.1 và van-hanh.md mục 3):**
1. Caddy ghi đè `X-Forwarded-For` bằng `{remote_host}` cho cả `/api/*` lẫn request vào Astro. Header lúc này chỉ có một IP là IP khách.
2. Astro chuyển **nguyên** giá trị đó sang Django, không nối IP của Caddy, không sửa.
3. Django chỉ tin header khi `REMOTE_ADDR` thuộc `TRUSTED_PROXY_CIDRS` (mạng compose, #671), duyệt từ phải sang trái và bỏ IP trong dải. IP chỉ dùng cho throttle và băm, không lưu (TK 11).
4. Request trình duyệt gọi thẳng `/api` cũng qua Caddy nên có cùng header. Django không phải phân biệt hai đường.

Throttle của `/api/public` tính theo IP của **người xem trang**, vì SSR chuyển IP của họ: `products`, `pages` 300 lượt/phút, `trace` 60 lượt/phút (backend.md 5.2). Mỗi trang công khai chỉ được gọi `/api/public` **một lần** (riêng sitemap hai lần, trang chủ hai lần khi có dưới 6 sản phẩm nổi bật, mục 5.3), để Googlebot hay AdsBot duyệt nhanh cũng không chạm 300. Bị 429 thì trang công khai trả 503 kèm `Retry-After` và `no-store`, không render trang rỗng.

**Lỗi và timeout:**
- Timeout 3 giây cho mỗi lần gọi SSR.
- Trang công khai: Django trả 5xx hoặc quá giờ thì render `500.astro` với mã 503 và `no-store`.
- Trang quản lý: lỗi 401 thì chuyển về trang đăng nhập.
- Lỗi nghiệp vụ theo TK 9 (`{code, message, details}`): `message` hiện nguyên văn. Đó là câu tiếng Việt đọc được ngay.

### 5.3 Ánh xạ trang → API

| Trang | API | Ghi chú |
| --- | --- | --- |
| `/` | `GET /api/public/products?featured=1&limit=6`; trả ít hơn 6 (kể cả rỗng) thì gọi thêm `GET /api/public/products?limit=6` để bù | Sếp tự chọn sản phẩm nổi bật (#773 câu 6). Backend lọc `featured_rank IS NOT NULL`, sắp theo hạng (backend.md 8). DTO công khai **không** có `featured_rank`: frontend giữ nguyên thứ tự API trả, không tự sắp. Bù: nối các sản phẩm mới cập nhật chưa có trong danh sách (so theo `slug`) vào sau, cắt còn 6. Rỗng nghĩa là sếp chưa chọn sản phẩm nào, trang chủ vẫn đủ 6 |
| `/san-pham` | `GET /api/public/products?goods_type=` | |
| `/san-pham/<slug>` | `GET /api/public/products/{slug}` | Xem 301 ở mục 6.5 |
| `/<slug>` | `GET /api/public/pages/{slug}` | Không có thì 404 |
| `/q/<serial>` | `GET /api/public/trace/{code}` | 6 trường hợp ở TK 8.4 |
| `/sitemap.xml`, feed | `GET /api/public/products`, `GET /api/public/pages` | |
| `/quan-ly/**` | `GET /api/v1/...` theo TK 9 | |

### 5.4 Kiểu sinh từ OpenAPI

- Backend xuất hai file có commit: `backend/openapi/v1.json` và `backend/openapi/public.json` (backend.md 3.4).
- Frontend sinh hai file kiểu bằng `openapi-typescript`:

```jsonc
// frontend/package.json (trích)
"scripts": {
  "gen:api": "openapi-typescript ../backend/openapi/v1.json -o src/lib/api/v1.d.ts && openapi-typescript ../backend/openapi/public.json -o src/lib/api/public.d.ts"
}
```

- `v1.d.ts` và `public.d.ts` có commit. CI chạy lại `gen:api` rồi `git diff --exit-code frontend/src/lib/api/`: kiểu lệch với backend thì đỏ.
- Trang công khai chỉ import `public.d.ts`. Như vậy kiểu của API nội bộ (có trường giá) không lọt vào code trang công khai.
- Quy ước kiểu từ backend.md 3.1 mà frontend phải theo: tiền là số nguyên VND; số cân, gram là **chuỗi** thập phân (`"120.50"`), định dạng bằng `lib/format.ts` chứ không `parseFloat` rồi tính; thời điểm là ISO UTC; ngày là `YYYY-MM-DD`.
- Client dùng `openapi-fetch` cho cả SSR lẫn `scripts/admin/api.ts`. Thư viện khoảng 2 KB, chỉ bọc `fetch`, có kiểu theo `paths`. Trang công khai chỉ dùng nó ở server, nên trình duyệt không tải byte nào.

### 5.5 Middleware: đăng nhập và vai

`src/middleware.ts` chạy theo thứ tự:

1. **Chuẩn hoá URL (website công khai):**
   - Có `/` ở cuối (trừ `/`) hoặc có chữ hoa thì trả 301 sang bản chữ thường, không `/` cuối.
   - Query string giữ nguyên, để UTM không mất khi chuyển hướng.
   - `/q/` không áp quy tắc chữ thường: serial chuẩn là chữ hoa (mục 6.6).
   - Đường dẫn chứa `\` (cả dạng `%5C`) thì trả 404, không chuyển hướng.
   - **`Location` luôn là URL tuyệt đối dựng bằng `new URL(path, SITE_URL)`**, sau khi gộp nhiều `/` ở đầu thành một. Không bao giờ ghép chuỗi `Location: ${path}`. Lý do: request `//evil.com/` sau khi bỏ `/` cuối thành `//evil.com`, mà trình duyệt hiểu `Location: //evil.com` là sang tên miền khác. Open redirect trên tên miền chạy Ads là công cụ phishing sẵn.

   ```ts
   // src/lib/url.ts
   /** Trả path đã chuẩn hoá (một "/" đầu, chữ thường trừ /q/, không "/" cuối), hoặc null nếu path không cần đổi.
    *  Ném lỗi khi path có "\" để middleware trả 404. */
   export function canonicalPath(pathname: string): string | null;
   /** new URL(path + search, SITE_URL); kết quả luôn cùng origin với SITE_URL. */
   export function redirectLocation(path: string, search: string): string;
   ```

   Test vitest bắt buộc: `//evil.com/`, `///evil.com/`, `/\evil.com`, `/%5Cevil.com`, `/San-Pham/` đều cho `Location` có origin bằng `SITE_URL` hoặc 404.
2. **Chặn `/quan-ly`** (trừ `/quan-ly/dang-nhap`):
   - Gọi `GET /api/v1/auth/me` với cookie của request.
   - 200: gán `locals.user`.
   - 401: trả 302 sang `/quan-ly/dang-nhap?next=<đường dẫn>`. `next` chỉ nhận đường dẫn bắt đầu bằng `/quan-ly/` (không `//`, không `\`), chống open redirect.
   - **Mọi kết quả khác thì chặn (fail-closed):** 403, 5xx, timeout, lỗi mạng hay body không đúng kiểu đều render `500.astro` với mã 503 và `no-store`, không gán `locals.user`, không render trang được yêu cầu. Không có nhánh nào «lỗi thì cho qua».
3. **Kiểm vai:**
   - Đường dẫn khớp tiền tố trong `lib/access.ts` mà `locals.user.role !== "OWNER"` thì render trang 403.
   - Đây chỉ là lớp báo sớm. **Quyền thật kiểm ở API** (TK 2: «Quyền phải kiểm tra ở API, không chỉ ẩn nút»).
4. **Gắn header** sau khi render: `Cache-Control` theo mục 2, `X-Robots-Tag` cho `/quan-ly` và `/q/`.

```ts
// src/env.d.ts
declare namespace App {
  interface Locals {
    user?: { id: number; username: string; full_name: string; role: "OWNER" | "WORKSHOP" };
  }
}

// src/lib/access.ts: theo TK mục 2 và 7.1
export const OWNER_ONLY_PREFIXES = [
  "/quan-ly/danh-muc", "/quan-ly/bang-gia", "/quan-ly/cuon-tem", "/quan-ly/tra-cuu",
  "/quan-ly/khach-hang", "/quan-ly/bao-cao", "/quan-ly/vung-nguyen-lieu",
] as const;
```

Màn hai vai dùng chung, **không** nằm trong danh sách trên: `/quan-ly/thu-luu-huong` (TK 2: WORKSHOP nhập cân và điểm ngửi, chỉ OWNER tạo và đóng đợt), `/quan-ly/mau-luu` (WORKSHOP ghi nhận mẫu), `/quan-ly/cong-thuc` và `/quan-ly/phu-lieu` (WORKSHOP chỉ xem, không thấy giá). Trên các màn này trang ẩn nút theo `locals.user.role`, API vẫn chặn.

Mỗi trang `/quan-ly` tốn thêm một lần gọi `auth/me` nội bộ, cỡ vài ms. Với 5 người dùng (TK 11) thì không đáng kể. Không cache kết quả này, để khoá tài khoản có hiệu lực ngay.

---

## 6. SEO

### 6.1 Thẻ head: `components/site/SeoHead.astro`

```ts
interface Props {
  title: string;              // đã ghép theo TK 8.2: seo_title || `${name} | ${BRAND}`
  description: string;        // seo_description, ≤ 160 ký tự
  path: string;               // đường dẫn canonical, không query
  ogImage?: string | null;    // og_image của sản phẩm, trống thì url ảnh đầu (mục 4.3)
  type?: "website" | "product" | "article";
  noindex?: boolean;          // /q/, 404, 500
  preloadImage?: ImageRef;    // ảnh LCP (mục 4.3)
  jsonLd?: object[];          // các khối JSON-LD
}
```

`SeoHead` render các thẻ sau:
- `<title>` và `meta description`.
- `link rel="canonical"`, URL tuyệt đối lấy theo `SITE_URL`.
- `link rel="alternate" hreflang="vi"` và `hreflang="x-default"`, cả hai trỏ về canonical.
- Open Graph: `og:title`, `og:description`, `og:image` (1200×630), `og:url`, `og:type`, `og:locale=vi_VN`.
- `meta robots="noindex, nofollow"` khi `noindex` bật.
- Các khối `<script type="application/ld+json" set:html={safeJson(block)} />`. JSON-LD chứa tên và mô tả sản phẩm do người nhập, nên cũng đi qua `safeJson` (mục 3.2) như `page-data`.

`<html lang="vi">` nằm ở layout.

Mỗi trang chỉ có một `h1` (TK 11). Dev kiểm bằng Lighthouse SEO và một test đơn vị trên HTML render (mục 8.3).

### 6.2 JSON-LD: dựng trong `lib/seo.ts`

```ts
type PublicProductOut = components["schemas"]["PublicProductOut"];  // từ lib/api/public.d.ts
export function productJsonLd(p: PublicProductOut, url: string): object;   // Product + Offer
export function offerOf(p: PublicProductOut): { price: number; availability: "in_stock" | "out_of_stock" } | null;
// null khi retail_price trống: không có Offer trong JSON-LD, không vào feed (mục 7.5)
export function breadcrumbJsonLd(items: Crumb[]): object;                  // BreadcrumbList
export function organizationJsonLd(): object;                              // chỉ ở trang chủ
export type Crumb = { name: string; path: string };
```

- **Product** gồm `name`, `image`, `description`, `sku`, `brand`, và `offers`. `offers` là một `Offer` với:
  - `price`;
  - `priceCurrency: "VND"`;
  - `availability`: `https://schema.org/InStock` hoặc `OutOfStock`;
  - `url`;
  - `itemCondition: NewCondition`.

  Không tự tạo `AggregateRating` (TK 8.2).
- **BreadcrumbList** dựng từ **cùng** mảng `Crumb[]` mà `Breadcrumb.astro` dùng để hiển thị, nên hai bên không lệch nhau.
- **Organization** (trang chủ) gồm `name`, `url`, `logo`, `address`, `telephone`, `email`, `sameAs` (Shopee, TikTok Shop, Zalo OA). Khi sếp chốt chính sách đổi trả, thêm `hasMerchantReturnPolicy` ở cấp Organization.

### 6.3 Breadcrumb hiển thị

`components/site/Breadcrumb.astro` dùng daisyUI `breadcrumbs`, nhận `items: Crumb[]`:
- Trang sản phẩm: Trang chủ › Sản phẩm › <tên>.
- Trang tĩnh, trang chính sách: Trang chủ › <tiêu đề>.
- Trang chủ và /q/ không có breadcrumb.

### 6.4 Sitemap, robots

`/sitemap.xml` chứa:
- `/`, `/san-pham`, `/truy-xuat`;
- mọi sản phẩm `PUBLISHED`, mọi `site_page` đã xuất bản;
- 4 trang chính sách.

Mỗi mục có `<lastmod>` lấy từ `updated_at` (có trong `PublicProductOut` và `GET /api/public/pages`, backend.md 8). Sitemap không chứa `/q/` và `/quan-ly`.

**Escape XML:** sitemap và feed (mục 7.5) dựng XML bằng chuỗi, nên mọi giá trị lấy từ API (URL, tên, mô tả) đi qua một hàm chung. Tên sản phẩm có `&` («Quế & Trà») mà không escape thì cả file XML hỏng và Google bỏ toàn bộ.

```ts
// src/lib/xml.ts
/** Thay & < > " ' bằng thực thể XML; bỏ ký tự điều khiển không hợp lệ trong XML 1.0. */
export function escapeXml(s: string): string;
```

Test vitest: tên có `&`, `<`, `"` và ký tự `\u0001` cho ra XML parse được.

`/robots.txt`:

```
User-agent: *
Disallow: /q/
Disallow: /quan-ly
Disallow: /api/
Sitemap: <SITE_URL>/sitemap.xml
```

Ghi chú: `/q/` vừa bị Disallow vừa mang `noindex`. Google không đọc được `noindex` của trang đã bị chặn, nhưng cũng không thu thập trang đó. Đây đúng là TK 8.1 yêu cầu, và URL /q/ chỉ đến từ mã QR chứ không có link công khai nào.

### 6.5 Chuyển hướng 301 slug cũ

- `GET /api/public/products/{slug}` với slug cũ: Django tra bảng `slug_redirect` (backend.md 8: `update_product` thêm dòng khi đổi slug), rồi trả sản phẩm với `slug` hiện tại thay vì 404 (mục 11, G5).
- Astro so sánh: slug trên URL khác `product.slug` thì trả `301` sang `/san-pham/<slug mới>`, giữ query string.
- `site_page` làm giống vậy nếu backend có bảng redirect cho trang. Chưa có thì trả 404.

Cách này không cần endpoint riêng để tra redirect. Trường hợp slug cũ trùng slug của một sản phẩm khác do Django chặn lúc đổi slug.

### 6.6 Trang /q/<serial>

- Chuẩn hoá theo BR-16 trong `lib/serial.ts`:

```ts
/** Chữ hoa, bỏ '-', O→0, I/L→1. Trả null nếu không đúng 10 ký tự Crockford Base32. */
export function normalizeSerial(raw: string): string | null;
```

- Mã sau chuẩn hoá khác URL thì trả 301 sang bản chuẩn.
- Mã sai định dạng thì render «Mã không có trong hệ thống…» với mã 404 và **không gọi API**, để khỏi tốn lượt rate limit.
- Header `X-Robots-Tag: noindex, nofollow` và `meta robots` cùng nội dung.
- Thứ tự nội dung và 6 trường hợp theo đúng TK 8.4. Dữ liệu chỉ lấy từ DTO công khai (BR-17). Frontend không tự ghép thêm trường nào.
- Ngân sách < 300 KB lần tải đầu (TK 8.4). Ảnh sản phẩm là ảnh LCP và được preload. Tối đa 3 ảnh đồi, `loading="lazy"`.
- Đẩy sự kiện `trace_scan` vào `dataLayer` với `{sku, result}` (mục 7.3).

---

## 7. Google Ads, Consent Mode v2, trang chính sách

### 7.1 Nạp thẻ muộn: `components/site/TagLoader.astro`

Đây là script inline đặt **trước mọi thẻ khác** trong `<head>`:

```js
window.dataLayer = window.dataLayer || [];
function gtag(){ dataLayer.push(arguments); }
const saved = JSON.parse(localStorage.getItem("vyc-consent") || "null");
gtag("consent", "default", {
  ad_storage: "denied", ad_user_data: "denied", ad_personalization: "denied",
  analytics_storage: "denied", wait_for_update: 500,
});
if (saved) gtag("consent", "update", toConsent(saved));
// nạp GTM một lần, khi có tương tác đầu tiên hoặc 4 giây sau load (cái nào đến trước)
```

- **Thời điểm nạp:** lần đầu có một trong các sự kiện `pointerdown`, `keydown`, `scroll`, `touchstart` (listener `{once:true, passive:true}`). Nếu không có tương tác thì nạp sau sự kiện `load` cộng 4 giây, trong `requestIdleCallback`.
- `GTM_ID` (biến `astro:env` đọc lúc chạy, mục 5.1) rỗng thì không nạp gì (dev, CI, staging).
- GA4 và thẻ chuyển đổi Google Ads cấu hình **trong GTM** (TK 8.3). Code chỉ biết ID container.
- **Trang prerender (4 trang chính sách) không có `TagLoader` và `ConsentBanner`.** Lúc build không có `GTM_ID` của môi trường thật, và một image dùng chung cho staging lẫn prod. Layout kiểm `Astro.isPrerendered` để bỏ hai component này. Cái giá: GA4 không đếm lượt xem 4 trang chính sách. Các trang đó không phải trang đích quảng cáo nên chấp nhận được. Trên 4 trang này link «Cài đặt cookie» ở footer đổi đích (mục 7.2).

**Lệch so với TK 8.3** («mã cấu hình lưu trong setting»): ID GTM để trong biến môi trường `GTM_ID`, không lấy từ bảng `setting`. Lý do:
- Đọc `setting` qua API thì mỗi trang tốn thêm một lần gọi `/api/public`, dễ chạm throttle 300/phút (mục 5.2).
- ID container gần như không bao giờ đổi. Mã GA4 và mã chuyển đổi Ads (thứ hay đổi) nằm trong GTM, chủ DN sửa trên giao diện GTM, không cần sửa code.

Đổi ID GTM thì sửa `.env` rồi khởi động lại container frontend, không phải build lại. Đã ghi để Lead trình sếp.

**Rủi ro của việc nạp muộn:** khách thoát trước khi có tương tác hoặc trước 4 giây thì mất lượt xem trang trong GA4. Đổi lại là LCP và INP không bị thẻ bên thứ ba kéo xuống. Chuyển đổi quan trọng (`click_buy`) luôn đi sau một lần bấm, nên GTM đã được nạp. Thêm vào đó:
- Link mua mở tab mới (`target="_blank" rel="noopener"`), trang không bị huỷ ngay khi bấm.
- Sự kiện gửi với `transport_type: "beacon"`.

### 7.2 Banner đồng ý: `components/site/ConsentBanner.astro`

- HTML render sẵn với thuộc tính `hidden`, script chỉ bỏ `hidden` khi chưa có lựa chọn. Banner `position: fixed` ở đáy, không đẩy nội dung, nên không gây CLS. Banner không che nội dung chính (không phải interstitial).
- Nội dung: một câu ngắn, link «Chính sách bảo mật», hai nút **cùng kích thước**: «Đồng ý» và «Chỉ cần thiết».
- Lưu vào `localStorage["vyc-consent"]`:

```ts
type ConsentChoice = { v: 1; ads: boolean; analytics: boolean; at: string /* ISO */ };
```

- Bấm nút thì gọi `gtag("consent", "update", …)`:

| Nút | `ad_storage`, `ad_user_data`, `ad_personalization` | `analytics_storage` |
| --- | --- | --- |
| «Đồng ý» | `granted` | `granted` |
| «Chỉ cần thiết» | `denied` | `denied` |

- Footer có link «Cài đặt cookie» để mở lại banner. Link là `<a href="/chinh-sach-bao-mat#rut-lai-dong-y" data-consent-open>`:
  - Trang SSR có `ConsentBanner`: script bắt click trên `[data-consent-open]`, `preventDefault()` rồi mở banner.
  - Trang prerender (không có banner) và khi JS tắt: link chạy như link thường, sang đoạn «Cách rút lại đồng ý» của `bao-mat.md` (id `rut-lai-dong-y`). Đoạn đó hướng dẫn mở một trang bất kỳ khác để chọn lại, hoặc xoá dữ liệu trang web trong trình duyệt.
  - Như vậy link không bao giờ «bấm không có tác dụng», kể cả trên chính trang chính sách bảo mật.
- Chọn **advanced mode** của Consent Mode v2: GTM vẫn nạp khi khách từ chối và chỉ gửi ping không cookie, để Google mô hình hoá chuyển đổi. Phương án basic (không nạp GTM khi từ chối) mất hẳn dữ liệu mô hình hoá, nên không chọn.
- Căn cứ pháp lý trong nước: Nghị định 13/2023/NĐ-CP về dữ liệu cá nhân yêu cầu có sự đồng ý. Nội dung chính sách bảo mật do sếp duyệt.

### 7.3 Sự kiện đo lường (TK 8.3)

| Sự kiện | Ở đâu | Cách đẩy |
| --- | --- | --- |
| `view_item` | `/san-pham/<slug>` | Script inline đẩy `dataLayer` với `{items:[{item_id: sku, price}]}` |
| `click_buy` | Nút mua (`BuyButtons`) | Một listener ủy quyền trong `TagLoader` đọc `data-channel` |
| `trace_scan` | `/q/` | Script inline đẩy `dataLayer` với `{sku, result}` |
| Web Vitals | Mọi trang công khai | Thư viện `web-vitals` (~2 KB) nạp **cùng lúc với GTM**, gửi LCP, INP, CLS vào `dataLayer` |

Các sự kiện đẩy trước khi GTM nạp vẫn nằm trong `dataLayer`, GTM xử lý khi nạp xong.

UTM:
- GA4 giữ nguồn theo phiên, nên link nội bộ không cần nối UTM.
- Middleware giữ query string khi trả 301 (mục 5.5).
- Nút mua tự gắn `utm_source=website` vào link sàn (TK 8.3). Việc gắn làm ở server lúc render `BuyButtons`, không cần JS.

### 7.4 Trang chính sách và thông tin doanh nghiệp

| URL | Nguồn | Nội dung tối thiểu |
| --- | --- | --- |
| `/chinh-sach-bao-mat` | `src/content/chinh-sach/bao-mat.md` | Dữ liệu thu thập (cookie, GA4, Ads), mục đích, thời gian giữ, cách rút lại đồng ý (đoạn có id `rut-lai-dong-y`, mục 7.2), liên hệ |
| `/chinh-sach-doi-tra` | `doi-tra.md` | Điều kiện, thời hạn, cách đổi; riêng lô bị thu hồi (TK 8.4 RECALLED) |
| `/chinh-sach-van-chuyen` | `van-chuyen.md` | Mua qua sàn thì theo chính sách sàn. Mua trực tiếp, Zalo thì ghi phí, thời gian, khu vực |
| `/lien-he` | `lien-he.md` + `lib/business.ts` | Tên doanh nghiệp, địa chỉ, SĐT, email, MST, giờ làm việc, bản đồ (link OSM, không nhúng iframe) |

- Footer của **mọi** trang công khai có: tên doanh nghiệp, địa chỉ, SĐT, email, MST, và link tới 4 trang trên.
- `lien-he` trong TK 8.1 là một `site_page`. Ở đây chuyển thành trang prerender trong repo, vì thông tin pháp lý cần ổn định và trang prerender không gọi được API. Các `site_page` khác (câu chuyện, vùng quế) vẫn để chủ DN sửa qua API.
- **Nội dung 4 trang do sếp cung cấp.** Đội chỉ dựng khung.

### 7.5 Feed Merchant: `/feed/google-merchant.xml` (để dành, chưa dựng)

**Sếp đã chốt (#773 câu 5):** website không bán trực tiếp, chỉ dẫn sang sàn; chỉ chạy quảng cáo tìm kiếm (Search Ads), **không dùng Shopping và Merchant Center**. Vì vậy bước dựng khung và GĐ3 **không** làm route feed. Thiết kế dưới đây giữ lại để khi sếp đổi ý thì làm theo, không phải thiết kế lại. Trang sản phẩm vẫn có JSON-LD `Offer` qua `offerOf` (mục 6.2) vì nó phục vụ SEO, không phụ thuộc Merchant.

RSS 2.0 với namespace `g:`, mỗi sản phẩm `PUBLISHED` là một `<item>`:

| Trường | Lấy từ |
| --- | --- |
| `g:id` | `sku` |
| `g:title` | `name` + `spec` |
| `g:description` | `short_description` |
| `g:link` | `SITE_URL/san-pham/<slug>` |
| `g:image_link` | `og_image`, trống thì `images[0].url` (URL tuyệt đối) |
| `g:price` | `"<retail_price> VND"` |
| `g:availability` | `in_stock` hoặc `out_of_stock` |
| `g:brand` | thương hiệu |
| `g:condition` | `new` |
| `g:identifier_exists` | `no` (chưa có GTIN) |

Mọi giá trị chữ và URL trong feed đi qua `escapeXml` của `lib/xml.ts` (mục 6.4).

**Giá và tình trạng khớp feed:**
- Trang sản phẩm, JSON-LD `Offer` và feed đều đọc **cùng** hai trường `retail_price` và `availability` của DTO công khai, qua **cùng** hàm `lib/seo.ts#offerOf(p)`.
- Không tính lại ở frontend, không hard-code.
- `retail_price` trống (backend.md 8: `int | None`) thì trang hiện «Liên hệ», JSON-LD không có `offers`, sản phẩm không vào feed. Merchant từ chối item không có giá, nên bỏ khỏi feed là đúng.
- Cả ba có thể lệch nhau tối đa 60 giây do cache trang. Feed cache 1 giờ, nhưng Merchant thu feed theo lịch dài hơn thế nên không ảnh hưởng.
- `availability` do backend tính, ví dụ còn serial `IN_STOCK` thì là `in_stock`. Định nghĩa chính xác nằm ở `backend.md`.

---

## 8. Đo lường và chặn trong CI

### 8.1 Chỉ tiêu

Ghi chú về cột «Cách đo»: «trang công khai» trong mục này gồm 5 URL `/`, `/san-pham`, `/san-pham/<seed>`, `/q/<seed>`, `/chinh-sach-bao-mat`. Ở bước dựng khung chỉ đo 4 URL, chưa có `/q/<seed>` (mục 8.2). Đo bằng Lighthouse CI (LHCI) ở cấu hình mobile mặc định (Moto G Power, mạng 4G chậm), chạy 3 lần, lấy trung vị (`aggregationMethod: "median"` ở mọi assertion). CI tắt GTM (`GTM_ID` rỗng).

Ngưỡng ở đây là bản chốt cho bảng van-hanh.md 9.1 (Lan3 nhờ đối chiếu): Performance, Accessibility, Best practices ≥ 95 theo #648 (van-hanh.md đang để 90), SEO = 100 cho trang được lập chỉ mục, INP < 200 ms đúng như brief task #57 ghi lại tiêu chí #648.

| Chỉ tiêu (tiêu chí #648, TK 11) | Ngưỡng | Cách đo | Chặn CI |
| --- | --- | --- | --- |
| LCP | < 2,5 s | LHCI `largest-contentful-paint`, mỗi trang công khai. Thực tế: CrUX và báo cáo CWV của Search Console, cùng `web-vitals` gửi về GA4 | Có (lab) |
| INP | < 200 ms | Lab không đo được INP. LHCI dùng `total-blocking-time` < 200 ms làm chỉ số thay. Thực tế: `web-vitals` và CrUX | Có (TBT) |
| CLS | < 0,1 | LHCI `cumulative-layout-shift`. Thực tế: `web-vitals` và CrUX | Có |
| Điểm Lighthouse mobile, Performance | ≥ 95 | LHCI `categories:performance` ≥ 0.95, mọi trang công khai | Có |
| Điểm SEO | = 100 | `categories:seo` = 1, chỉ trang được lập chỉ mục. /q/ có `noindex` nên bỏ | Có |
| Accessibility, Best practices | ≥ 95 | `categories:*` ≥ 0.95 | Có |
| CSS trang công khai | < 15 KB nén | Budget `stylesheet` ≤ 15 (KB truyền, qua Caddy có nén) | Có |
| JS trang công khai | không có framework | Budget `script` ≤ 3 KB (chỉ còn script inline), `third-party` = 0 | Có |
| Trang sản phẩm, lần tải đầu | < 200 KB | Budget `total` ≤ 200 cho `/san-pham/<seed>`. Kèm `font` ≤ 50, `image` ≤ 120, `document` ≤ 30 | Có |
| Trang /q/, lần tải đầu | < 300 KB | Budget `total` ≤ 300 cho `/q/<seed>` | Có |
| Trang chủ | ≤ 250 KB | Budget `total` ≤ 250 (đội tự đặt) | Có |
| Một `h1`, có canonical, có JSON-LD hợp lệ | | Test vitest trên HTML render (8.3). Thủ công: Rich Results Test trước khi go-live | Có (vitest) |
| Byte thẻ bên thứ ba (GTM, gtag) | theo dõi | PageSpeed Insights trên production mỗi tháng, ghi vào báo cáo | Không |

**Vì sao ngân sách tính khi tắt GTM:**
- GTM cộng gtag khoảng 100–150 KB, và theo 7.1 chỉ nạp sau tương tác. Nếu tính vào, trang sản phẩm không thể dưới 200 KB với bất kỳ thiết kế nào.
- Ngân sách 200/300 KB vì vậy là byte của chính website **trước tương tác**. Byte bên thứ ba theo dõi riêng ở dòng cuối bảng.
- Điểm này đã ghi để Lead trình sếp.

### 8.2 Công cụ: Lighthouse CI chạy trên stack thật

- Job CI `lighthouse` (tên chung với van-hanh.md 9.1) dựng stack bằng `deploy/compose.ci.yml` (Postgres, Django có dữ liệu seed, Astro, Caddy có `encode zstd gzip`). Sau đó chạy `pnpm lhci autorun`.
- Lý do chạy qua Caddy: ngân sách tính theo byte **đã nén**. Astro Node không tự nén, nên đo thẳng Astro sẽ ra số sai. Vì vậy `compose.ci.yml` phải **có** Caddy.
- Dữ liệu seed (`make seed`, van-hanh.md 8) phải có ít nhất 1 sản phẩm `PUBLISHED` có 3 ảnh và slug `tinh-dau-que-van-yen-10ml`.
- **Bước dựng khung không đo `/q/`.** Khung backend để operations trống (backend.md 8), nên chưa có serial nào để quét. Khi làm GĐ2, seed thêm 1 serial `ISSUED` có đủ vùng nguyên liệu (để /q/ hiện khối dài nhất) và thêm URL `/q/<serial seed>` vào `collect.url`; nhóm assertion `/q/` dưới đây đã viết sẵn cho lúc đó.

`frontend/lighthouserc.cjs` (khung):

```js
// Mọi assertion lấy trung vị 3 lần chạy. Mặc định LHCI lấy lần tốt nhất ("optimistic"), trái với chỉ tiêu ở 8.1.
const err = (opts) => ["error", { ...opts, aggregationMethod: "median" }];

module.exports = {
  ci: {
    collect: {
      url: [
        "http://localhost/", "http://localhost/san-pham",
        "http://localhost/san-pham/tinh-dau-que-van-yen-10ml",
        "http://localhost/chinh-sach-bao-mat",
        // GĐ2: thêm "http://localhost/q/<serial seed>"
      ],
      numberOfRuns: 3,
    },
    assert: {
      assertMatrix: [
        { matchingUrlPattern: ".*", assertions: {
          "categories:performance": err({ minScore: 0.95 }),
          "categories:accessibility": err({ minScore: 0.95 }),
          "categories:best-practices": err({ minScore: 0.95 }),
          "largest-contentful-paint": err({ maxNumericValue: 2500 }),
          "cumulative-layout-shift": err({ maxNumericValue: 0.1 }),
          "total-blocking-time": err({ maxNumericValue: 200 }),
          "resource-summary:stylesheet:size": err({ maxNumericValue: 15360 }),
          "resource-summary:script:size": err({ maxNumericValue: 3072 }),
          "resource-summary:third-party:count": err({ maxNumericValue: 0 }),
        }},
        { matchingUrlPattern: "^(?!.*/q/).*$", assertions: {
          "categories:seo": err({ minScore: 1 }),
        }},
        { matchingUrlPattern: ".*/san-pham/[^/]+$", assertions: {
          "resource-summary:total:size": err({ maxNumericValue: 204800 }),
          "resource-summary:font:size": err({ maxNumericValue: 51200 }),
          "resource-summary:image:size": err({ maxNumericValue: 122880 }),
          "resource-summary:document:size": err({ maxNumericValue: 30720 }),
        }},
        { matchingUrlPattern: ".*/q/.*", assertions: {   // chưa khớp URL nào tới GĐ2
          "resource-summary:total:size": err({ maxNumericValue: 307200 }),
        }},
        { matchingUrlPattern: "^http://localhost/$", assertions: {
          "resource-summary:total:size": err({ maxNumericValue: 256000 }),
        }},
      ],
    },
    upload: { target: "filesystem", outputDir: ".lighthouseci" },
  },
};
```

Kết quả LHCI lưu thành artifact của CI. Không dùng server LHCI riêng.

**Không dùng size-limit.** Lý do:
- size-limit đo file trong `dist/`. Astro đặt tên CSS theo trang và component, nên không tách được CSS công khai khỏi CSS admin một cách chắc chắn.
- Trang công khai không có bundle JS nào để size-limit đo.
- Budget `resource-summary` của LHCI đo đúng thứ khách tải, theo từng trang, sau nén.

Cái giá: job `lighthouse` cần Docker, chạy lâu khoảng 3–5 phút. Vì vậy nó chạy ở PR chạm `frontend/` hoặc `backend/` và trên `main`, không chạy ở mọi commit.

**Job `budget` của van-hanh.md 9.1** (`scripts/check-budget.mjs` đọc `dist/`) vẫn giữ, vì nó nhanh và chạy được ở mọi PR, nhưng chỉ kiểm những gì đọc tĩnh được:
1. `dist/client/_astro/` không có runtime framework: không file nào khớp `preact|react|vue|svelte|solid`, và không có `astro-island` trong HTML prerender.
2. Không chuỗi `fonts.googleapis.com` hay `fonts.gstatic.com` trong `dist/`.
3. Tổng file `.woff2` mà `site.css` tham chiếu ≤ 50 KB.

CSS < 15 KB **không** đo ở job `budget` (lý do ở trên), chỉ đo ở `lighthouse`.

### 8.3 Test frontend

- **vitest** cho `lib/`:
  - `normalizeSerial` (bảng ca BR-16);
  - `productJsonLd`, `breadcrumbJsonLd`, `offerOf`;
  - dựng title theo TK 8.2;
  - `forwardHeaders` (chuyển nguyên `X-Forwarded-For`, chỉ thêm `Cookie` khi `mode = "session"`);
  - `srcset`, `heightFor` của `lib/image.ts`;
  - `safeJson` với `</script>` và U+2028/U+2029 (mục 3.2);
  - `canonicalPath`, `redirectLocation` với `//evil.com/`, `\` (mục 5.5);
  - `escapeXml` (mục 6.4);
  - middleware: `auth/me` trả 5xx, timeout thì 503, không render trang (mục 5.5);
  - kiểm `next` của trang đăng nhập.
- **vitest với Astro Container API**: render `SeoHead`, `Picture`, trang sản phẩm từ dữ liệu giả, rồi kiểm:
  - đúng một `h1`;
  - có canonical tuyệt đối;
  - JSON-LD parse được và có `offers.price`;
  - ảnh đầu có `fetchpriority="high"`, ảnh sau có `loading="lazy"`;
  - /q/ có `noindex`.
- Test đầu cuối (đăng nhập → quét → lưu) thuộc luồng mẫu của khung dự án: Playwright, chạy trên `compose.ci.yml` cùng job `lighthouse` (README mục 6, T12; vị trí và lệnh chốt ở van-hanh.md 9.1).

---

## 9. Lệnh, lint, format

Lint và format chọn **Biome**, một công cụ cho cả lint và format TS, JS, JSON, CSS:
- Một file cấu hình, chạy nhanh, ít gói phụ thuộc hơn ESLint + Prettier + plugin.
- Kiểm kiểu file `.astro` bằng `astro check`.

Đây là bản chốt cho `make lint-fe` ở van-hanh.md 8 (đang ghi tạm «ESLint + astro check»): `pnpm check` = `astro check && biome ci .`.

Cái giá: Biome hỗ trợ `.astro` chưa đầy đủ. Phần frontmatter và script được lint, còn phần template chỉ được định dạng ở mức Biome hỗ trợ. Không chọn ESLint + Prettier vì cái lợi duy nhất là định dạng template `.astro` tốt hơn, không đáng thêm 5–6 gói và hai cấu hình.

Quy tắc ranh giới ở mục 1 chặn bằng `noRestrictedImports` của Biome:
- File trong `components/site/` và `pages/` (trừ `pages/quan-ly/`) không được import `**/admin/**`.
- Chiều ngược lại cũng vậy.

| Lệnh (`frontend/`) | Việc |
| --- | --- |
| `pnpm dev` | `astro dev`, cổng 4321. Gọi Django ở `API_INTERNAL_URL=http://localhost:8000` |
| `pnpm build` | `astro build` |
| `pnpm start` | `node dist/server/entry.mjs` (dùng trong container) |
| `pnpm check` | `astro check && biome ci .`, chỉ đọc, dùng trong CI |
| `pnpm lint` | `biome lint .` |
| `pnpm format` | `biome format --write <file…>`, chỉ format file mình sửa |
| `pnpm test` | `vitest run` |
| `pnpm gen:api` | sinh `src/lib/api/v1.d.ts` và `public.d.ts` từ `backend/openapi/*.json` |
| `pnpm lhci` | `lhci autorun`, cần stack chạy sẵn (mục 8.2) |

Khi chạy dev, trình duyệt gọi `/api/v1` cùng origin. Vì vậy `astro.config.mjs` khai `vite.server.proxy` để chuyển `/api` và `/media` sang `http://localhost:8000`. Chỉ cấu hình này ở dev; production thì Caddy làm.

Thư viện dự kiến:

| Nhóm | Gói |
| --- | --- |
| Chạy | `astro`, `@astrojs/node`, `openapi-fetch`, `@fontsource/be-vietnam-pro`, `web-vitals`, `qrcode` (sinh SVG QR ở SSR cho trang in tem, không gửi xuống trình duyệt), `leaflet` (chỉ màn vùng nguyên liệu, mục 3.3) |
| Dev | `tailwindcss`, `@tailwindcss/vite`, `daisyui`, `typescript`, `@astrojs/check`, `@biomejs/biome`, `openapi-typescript`, `vitest`, `@lhci/cli`, `@types/leaflet`, `@playwright/test` |

Không có thư viện Markdown ở frontend: nội dung từ DB đã được backend render (mục 10), trang chính sách dùng Markdown có sẵn của content collection.

Thêm gói ngoài danh sách thì ghi lý do trên thẻ task.

---

## 10. Quy ước code frontend

- Tên file (theo README mục 3.1, 3.2):
  - component `PascalCase.astro`;
  - module TS `kebab-case.ts`, **tên tiếng Anh** (`image.ts`, `weight.ts`, `access.ts`); id phần tử trong HTML cũng tiếng Anh (`page-data`);
  - route và nội dung `content/chinh-sach/` theo URL tiếng Việt không dấu (`nhap-hang`, `lo-thanh-pham`, `bao-mat.md`), vì là URL khách nhìn thấy.
- Chữ trên giao diện viết thẳng tiếng Việt trong template. Chưa làm i18n vì chỉ có `vi`.
- Không dùng `set:html` với dữ liệu thô. `set:html` chỉ nhận đúng hai nguồn:
  1. Trường `*_html` của DTO (`story_html`, `usage_html` của `PublicProductOut`, HTML của `site_page`). **Backend là nơi duy nhất render Markdown lấy từ DB** và đã làm sạch bằng `nh3` với `url_schemes` http, https, mailto, tel (backend.md 8, `core/markdown.py`). Frontend không render lại, không làm sạch lại.
  2. Kết quả `safeJson(...)` trong thẻ `<script>` (mục 3.2).

  Trang chính sách trong `src/content/chinh-sach/` là Markdown trong repo, render bằng content collection có sẵn của Astro (`render(entry)`), không qua `set:html`.
- Số và tiền:
  - hiển thị bằng `Intl.NumberFormat("vi-VN")`;
  - ô nhập cân nhận cả `,` và `.` (`scripts/admin/weight.ts`);
  - gửi API luôn dùng dấu `.`.
- Ngày giờ: API trả UTC, hiển thị giờ Việt Nam bằng `Intl.DateTimeFormat("vi-VN", { timeZone: "Asia/Ho_Chi_Minh" })` (TK 1).
- Giao diện xưởng theo TK 11 và chuẩn mockup:
  - chữ thân 18 px, chữ phụ ≥ 16 px;
  - vùng chạm ≥ 48 px, nút chính cuối màn 72 px;
  - số cân và số tiền 32 px;
  - ô quét luôn giữ focus;
  - bíp ngắn khi đúng, bíp dài khi sai.

  Các giá trị này nằm trong `admin.css`, không lặp lại ở từng màn.
- Không ẩn nút để thay cho kiểm quyền. Ẩn nút chỉ giúp gọn giao diện; quyền kiểm ở API.

---

## 11. Điểm ghép với backend.md và van-hanh.md

Đối chiếu với `backend.md` và `van-hanh.md` bản ngày 21/11/2026. Cột «Trạng thái»: **khớp** là hai bên đã ghi giống nhau; **cần thêm** là bên kia chưa có, nhờ người viết bổ sung.

| # | Cần ở | Nội dung | Trạng thái |
| --- | --- | --- | --- |
| G1 | backend | Caddy ghi đè XFF, Astro chuyển nguyên, Django tin khi `REMOTE_ADDR` thuộc `TRUSTED_PROXY_CIDRS` (mục 5.2) | khớp backend.md 5.1 |
| G2 | backend | `GET /api/v1/auth/csrf` (204, đặt `csrftoken`), `POST /auth/login`, `GET /auth/me` → `{id, username, full_name, role}`, 401 khi chưa đăng nhập | khớp backend.md 4.1 |
| G3 | backend | SSR chỉ GET `/api/v1` kèm Cookie; mọi lệnh ghi từ trình duyệt kèm `X-CSRFToken`; cookie phiên `SameSite=Lax`, `HttpOnly`; `csrftoken` không HttpOnly | khớp backend.md 4.1, 4.2 |
| G4 | backend | `/api/public/trace/{code}` nhận Cookie để bỏ qua đếm lượt quét của nhân viên (BR-18) | khớp backend.md 5.3 |
| G5 | backend | `PublicProductOut` có `availability: "in_stock" \| "out_of_stock"` (mục 7.5), `updated_at` (sitemap), `og_image: str \| None` (mục 4.3), `story_html`/`usage_html` đã làm sạch (mục 10), `origin` (khung để `None`). `GET /api/public/products/{slug}` với slug cũ trả 200 kèm `slug` mới, Astro tự 301 (mục 6.5) | khớp backend.md 8 |
| G6 | backend | Ảnh dạng `ImageRef {url, alt, key, w, h, widths}`, file `/media/img/{key}-{w}.{avif\|webp}`, bề rộng 480/960/1440 | khớp backend.md 6.5 |
| G7 | backend | `GET /api/public/products` có `?goods_type=` và `?limit=` (mặc định 50, tối đa 100, mới cập nhật trước); `?featured=1` lọc sản phẩm có `featured_rank`, sắp theo hạng; trang chủ gọi `?featured=1&limit=6`, dưới 6 thì gọi thêm `?limit=6` để bù (mục 5.3). `PublicProductOut` không có `featured_rank`. `GET /api/public/pages` trả `[{slug, title, updated_at}]` của trang đã xuất bản | khớp backend.md 8 |
| G8 | backend | OpenAPI ở `backend/openapi/v1.json` và `public.json`; frontend sinh `v1.d.ts`, `public.d.ts` | khớp backend.md 3.4 |
| G9 | backend | Throttle `/api/public`: trace 60/phút, products và pages 300/phút, theo IP người xem | khớp backend.md 5.2 |
| V1 | van-hanh | Caddy: `/api/*` → Django; `/media/*` → file tĩnh; còn lại → Astro. `encode zstd gzip`. Ghi đè XFF bằng `{remote_host}` | khớp van-hanh.md 3 |
| V2 | van-hanh | Caddy gắn `Cache-Control: public, max-age=31536000, immutable` cho `/_astro/*` và `public, max-age=3600` cho 4 trang prerender | khớp van-hanh.md 3 (T6) |
| V3 | van-hanh | Biến frontend là `API_INTERNAL_URL`, `SITE_URL`, `GTM_ID`, khai bằng `astro:env` access `secret`, đọc lúc chạy (mục 5.1) | khớp van-hanh.md 4 (T3) |
| V4 | van-hanh | Healthcheck frontend là `GET /healthz` (`src/pages/healthz.ts`, 200, không gọi API) | khớp van-hanh.md 2.1 |
| V5 | van-hanh | Job `lighthouse`, `frontend/lighthouserc.cjs`, `compose.ci.yml` có Caddy nén, `aggregationMethod: "median"`, ngưỡng mục 8.1 (Performance, A11y, BP ≥ 95; SEO = 100); bước khung chưa đo `/q/`. Job `budget` chỉ làm 3 việc ở mục 8.2 | khớp van-hanh.md 2, 9.1 (T1, T2, T13). Còn lệch nhỏ: van-hanh.md 9.1 liệt kê URL «trang chủ, một trang sản phẩm, một bài viết» và để chỉ số phụ ở `warn`; file này đo 4 URL ở mục 8.2 và mọi assertion là `error` |
| V6 | van-hanh | `make lint-fe` = `pnpm check`; job `frontend` chạy `pnpm check`, `pnpm test`, kiểm kiểu sinh, `pnpm build` | khớp van-hanh.md 8, 9.1 (T4) |
| V7 | van-hanh | CSP: hai script inline của trang công khai cần hash trong CSP, hoặc dùng tính năng CSP của Astro nếu bản đang dùng đã có | **cần thêm** khi dựng khung (van-hanh.md 3 đã ghi «chốt lúc dựng khung») |
| V8 | van-hanh | Node 24 LTS | khớp van-hanh.md 2 (T5) |
| V9 | van-hanh | CSP `img-src` cho `tile.openstreetmap.org` và `*.tile.openstreetmap.org` (mục 3.3) | khớp van-hanh.md 3 (T11) |
| V10 | van-hanh | Playwright chạy trên `compose.ci.yml` cùng job `lighthouse` (mục 8.3) | khớp van-hanh.md 9.1 (T12) |

---

## 12. Rủi ro và các điểm sếp đã chốt

Sếp trả lời ở #773: câu 5, 6, 7 áp vào mục này; các điểm lệch TK (điểm 4, 6, 8) sếp để đội tự quyết (câu 9), đội giữ nguyên phương án đã ghi.

1. **Chỉ chạy Search Ads, không dùng Shopping và Merchant Center (đã chốt).** Website không bán trực tiếp, chỉ có nút sang Shopee, TikTok Shop, Zalo (TK 8.2). Shopping cần trang đích mua được ngay nên không chạy. Feed Merchant (mục 7.5) để dành, chưa dựng. File này không thiết kế giỏ hàng.
2. **Nội dung 4 trang chính sách và thông tin doanh nghiệp** (địa chỉ, MST, email, chính sách đổi trả và vận chuyển) do sếp cung cấp khi chuẩn bị chạy quảng cáo (#773 câu 7). Khung dựng với nội dung giữ chỗ; đội báo sếp trước khi gửi xét duyệt Google Ads, vì thiếu thì không duyệt được.
3. **Thông báo website với Bộ Công Thương.** Website chỉ giới thiệu sản phẩm, không có chức năng đặt hàng (đã chốt), nên nhiều khả năng không phải đăng ký. Nếu sau này thêm đặt hàng thì phải thông báo.
4. **ID GTM để trong biến môi trường thay vì `setting`** (lệch TK 8.3, mục 7.1). Đổi container thì sửa `.env` và khởi động lại frontend. 4 trang chính sách không có GA4.
5. **Nạp GTM muộn làm mất một phần lượt xem trang** của khách thoát sớm (mục 7.1). Đây là cái giá cho CWV.
6. **Ngân sách byte tính khi chưa có thẻ bên thứ ba** (mục 8.1). Nếu sếp muốn tính cả GTM thì 200 KB không đạt được.
7. **Không có cache dùng chung:** mỗi lượt xem trang đều gọi Django. Lúc bị bot quét hoặc đợt quảng cáo lớn, tải dồn lên VPS 2 vCPU. Phương án dự phòng là bật cache Caddy cho nhóm `public` (mục 2), không phải sửa code.
8. **Đổi route app nội bộ sang `/quan-ly/…`** so với mockup (mục 1.1). Không đổi màn hình, chỉ đổi URL.
