# Vận hành: Docker, deploy 1 VPS, CI

Phạm vi: thư mục `deploy/`, Makefile, GitHub Actions, sao lưu, log. Căn cứ `docs/thiet-ke-chi-tiet.md` mục 11 và các chốt #645, #657, #666/#671.
Trạng thái: **bản thiết kế chờ sếp duyệt**. Chưa có file nào trong `deploy/`; các đoạn cấu hình dưới đây là mẫu để dựng khung, chưa chạy thử.

## 1. Tổng quan

```
Internet ──443──▶ Caddy ──┬─ /api/*   ─▶ backend  (gunicorn :8000)
                          ├─ /media/* ─▶ (đọc thẳng volume media, chỉ đọc)
                          └─ còn lại  ─▶ frontend (Astro Node :4321)
                                              │ SSR gọi API nội bộ
                                              └────▶ backend:8000
                          backend ──▶ postgres:5432
```

- Một domain duy nhất do sếp đăng ký và giữ DNS (#773); tài liệu chỉ dùng biến `SITE_ADDRESS` và `STAGING_ADDRESS`, không ghi cứng tên miền (xem mục 2.3). Cùng origin nên cookie phiên `SameSite=Lax` chạy tự nhiên, không cần CORS.
- Chỉ Caddy mở cổng ra ngoài (80, 443). Postgres, backend, frontend chỉ nằm trong mạng compose.

## 2. Cấu trúc `deploy/`

```
deploy/
  compose.yml              # phần chung: backend, frontend, postgres
  compose.dev.yml          # override dev: mount mã nguồn, runserver, astro dev, mở cổng localhost
  compose.prod.yml         # override chung staging và prod: image đã build, giới hạn RAM, log, healthcheck
  compose.edge.yml         # chỉ prod: Caddy bind 80/443, subnet 172.28.0.0/24, nhìn thấy mạng và media của staging (profile `edge`)
  compose.staging.yml      # chỉ staging: mạng ngoài vyc-staging (172.29.0.0/24), volume media ngoài, alias cho Caddy
  compose.ci.yml           # chỉ job lighthouse: stack giống prod, CÓ Caddy nén zstd/gzip để đo byte thật, chạy http://localhost (mục 9.1)
  caddy/Caddyfile          # một Caddy duy nhất phục vụ prod và staging (mục 3, 2.2)
  backend.Dockerfile
  frontend.Dockerfile
  backend-entrypoint.sh    # migrate rồi exec gunicorn
  deploy.sh                # VPS chạy: validate tham số, backup, pull, up, smoke test, tự lùi (mục 9.2)
  backup/backup.sh
  backup/restore.sh
  backup/collect-logs.sh   # gom log container mỗi giờ ra /var/log/vyc (mục 7)
  backup/crontab.example   # cron prod + staging: sao lưu 23:00, purge_throttle 23:30, gom log hằng giờ (mục 6)
  logrotate/vyc            # cấu hình logrotate, cài vào /etc/logrotate.d/ (mục 7)
  env/.env.example         # chỉ tên biến + giá trị giả
  env/dev-defaults         # giá trị dev công khai, nạp bằng --env-file (make dev, make image)
  env/ci-defaults          # giá trị riêng job CI, nạp thêm sau dev-defaults
  ci/stack.sh              # job lighthouse: dựng stack, tạo OWNER (mật khẩu sinh mỗi lần chạy), seed, dọn
  ci/seed_catalog.py       # dữ liệu seed cho CI (khi `make seed` có dữ liệu thì chuyển sang gọi seed_dev)
frontend/lighthouserc.cjs  # cạnh @lhci/cli trong frontend/package.json: URL kiểm và ngưỡng LHCI (mục 9.1)
scripts/check-budget.mjs   # ở gốc repo: đo ngân sách dung lượng sau build (mục 9.1)
Makefile                   # ở gốc repo (mục 8)
```

Phiên bản ghim (cập nhật có chủ đích, ghi vào PR): `postgres:16.x-alpine`, `caddy:2.x`, `python:3.13-slim`, `node:24-alpine` (Node 24 LTS; 22 hết hỗ trợ 4/2027, trước GĐ3), `ghcr.io/astral-sh/uv:0.x`. Lúc dựng khung sẽ điền số phiên bản đầy đủ (và digest nếu cần) sau khi kiểm bản mới nhất; tài liệu này không đoán số.

### 2.1 Dịch vụ và giới hạn RAM (VPS 2 vCPU / 4 GB)

| Dịch vụ | Image | `mem_limit` | Ghi chú |
| --- | --- | --- | --- |
| postgres | postgres:16 | 1 GB | `shared_buffers=256MB`, `max_connections=50`, `work_mem=8MB` |
| backend | build từ `backend.Dockerfile` | 768 MB | gunicorn 3 worker (2×vCPU−1), `--max-requests 1000 --max-requests-jitter 100` chống rò bộ nhớ |
| frontend | build từ `frontend.Dockerfile` | 384 MB | Node adapter standalone, `NODE_OPTIONS=--max-old-space-size=256` |
| caddy | caddy:2 | 128 MB | |
| Tổng (chỉ prod) | | ≈ 2,3 GB | chừa ~1,7 GB cho hệ điều hành, cache trang, cron sao lưu |

Khi staging chạy cùng VPS (mục 2.2) staging không có Caddy riêng và dùng giới hạn thấp hơn: postgres 384 MB, backend 384 MB (2 worker), frontend 256 MB, tổng ≈ 1,0 GB. Cả hai cùng chạy ≈ 3,3 GB, chỉ còn ~0,7 GB cho hệ điều hành, page cache và cron sao lưu: **sát giới hạn** nên bắt buộc có swap 2 GB, **không build trên VPS** và không chạy `backup.sh` lúc staging đang tải. Vì vậy (sếp chốt #773) staging chạy chung VPS prod, **mặc định tắt**, chỉ bật khi cần thử:

```sh
# Bật (kiểm RAM trống trước: free -m, cần >= 1,2 GB available; không bật lúc đang deploy/backup prod)
/opt/vyc/deploy/backup/compose.sh staging up -d
# Tắt (giữ nguyên volume dữ liệu; KHÔNG dùng `down -v`)
/opt/vyc/deploy/backup/compose.sh staging stop
```

Cảnh báo RAM: cả hai chạy ≈ 3,3 GB trên VPS 4 GB; bật xong thử xong thì tắt ngay. Nếu thấy swap tăng mạnh hoặc `docker stats` báo prod gần `mem_limit` thì tắt staging trước. Khi staging tắt, Caddy trả 502 cho `STAGING_ADDRESS` (bình thường). Nếu sau này cần staging chạy liên tục thì phải thuê VPS nhỏ riêng (việc mới, cần sếp duyệt chi phí).

Có `restart: unless-stopped` và `healthcheck` cho cả bốn (postgres `pg_isready`; backend `GET /api/health`; frontend `GET /healthz`; caddy phụ thuộc `service_healthy` của hai app). Tuỳ chọn thêm swap 2 GB trên VPS để tránh OOM-kill khi build.

### 2.2 Bản dev và bản prod

| | dev (`compose.dev.yml`) | staging / prod (`compose.prod.yml` + `compose.staging.yml` hoặc `compose.edge.yml`) |
| --- | --- | --- |
| Backend | `runserver`, mount `backend/`, `DEBUG=1` | gunicorn, `DEBUG=0`, image build sẵn |
| Frontend | `astro dev`, mount `frontend/` | `node dist/server/entry.mjs` |
| Caddy | không dùng; mở trực tiếp `localhost:4321`, `localhost:8000` | có, HTTPS tự động |
| Postgres | mở `127.0.0.1:5432` để công cụ nhìn DB | không mở cổng |
| Dữ liệu | volume `pgdata-dev`, có lệnh nạp dữ liệu giả | volume `pgdata` riêng cho mỗi môi trường |

Chạy: `docker compose -f deploy/compose.yml -f deploy/compose.dev.yml up` (đã gói trong `make dev`).

Staging và prod dùng **cùng** `compose.yml` + `compose.prod.yml`, thêm `compose.staging.yml` (staging) hoặc `compose.edge.yml` (prod); khác nhau ở file `.env`, project name và subnet. Dùng `deploy/backup/compose.sh <prod|staging> <lệnh>` để khỏi ghép tay bộ file. Staging nằm cùng VPS prod (chốt #773):

- **Subnet cố định, khác nhau** (khai ở `networks.default.ipam.config.subnet`, không để Docker tự chọn):

  | Môi trường | Project | Subnet compose | `TRUSTED_PROXY_CIDRS` |
  | --- | --- | --- | --- |
  | prod | `-p vyc` | `172.28.0.0/24` | `172.28.0.0/24` |
  | staging | `-p vyc-staging` | `172.29.0.0/24` | `172.29.0.0/24` |
  | dev (chạy trên máy, không compose prod) | | | `127.0.0.1/32,::1/128` |

  Mỗi môi trường đặt `TRUSTED_PROXY_CIDRS` trong `.env` của chính nó, khớp subnet của nó; không dùng chung một giá trị.
- **Một Caddy duy nhất**, thuộc project prod, là nơi duy nhất bind 80/443. `compose.edge.yml` (chỉ prod) bật dịch vụ `caddy` qua profile `edge`; staging không có Caddy nên không đụng cổng. Staging không `ports:` ra host.
- Mạng staging `vyc-staging` tạo một lần ngoài compose: `docker network create --subnet 172.29.0.0/24 vyc-staging` (ghi trong `deploy/README.md`); staging khai nó là `external: true` làm mạng mặc định, Caddy của prod gắn thêm vào cả hai mạng. Caddy gọi staging qua alias riêng (`backend-staging`, `frontend-staging`) để tên `backend`/`frontend` không nhập nhằng giữa hai mạng. Django staging thấy Caddy với địa chỉ trong `172.29.0.0/24` nên `TRUSTED_PROXY_CIDRS` ở trên khớp.
- Staging chỉ dùng dữ liệu giả (đúng mục 11), không bao giờ restore dump prod vào staging. Staging phải chặn người lạ và công cụ tìm kiếm (mục 3).

### 2.3 VPS và tên miền (sếp làm, chốt #773)

**VPS đặt trong nước.** Tiêu chí chọn nhà cung cấp:
- 2 vCPU, 4 GB RAM, ổ SSD/NVMe (≥ 60 GB, đủ cho DB, media, log 30 ngày và bản sao lưu cục bộ);
- có **snapshot** (chụp trước thay đổi lớn) và tường lửa ở tầng nhà cung cấp (hoặc dùng `ufw`, mục 11);
- **IPv4 tĩnh**, mở được cổng 80/443/22 (kiểm nhà cung cấp không chặn 80/443 khi chưa có giấy phép web);
- Ubuntu LTS, cho phép cài Docker, truy cập root/sudo qua khoá SSH;
- băng thông đủ cho ảnh sản phẩm; ghi rõ giá gia hạn và điều khoản huỷ.

**Tên miền**: sếp đăng ký và giữ quyền DNS. Sếp cần tạo các bản ghi sau (thay `<IP-VPS>`):

| Bản ghi | Tên | Giá trị | Dùng cho |
| --- | --- | --- | --- |
| A | `@` (tên miền gốc, giá trị `SITE_ADDRESS`) | `<IP-VPS>` | website prod |
| A | `www` | `<IP-VPS>` | chuyển hướng về tên miền gốc (thêm khối Caddy lúc dựng khung nếu dùng) |
| A | `staging` (giá trị `STAGING_ADDRESS`) | `<IP-VPS>` | staging cùng VPS, chỉ có tác dụng khi bật staging |

Tuỳ chọn: bản ghi AAAA nếu VPS có IPv6 tĩnh; CAA `letsencrypt.org` để chỉ cho Let's Encrypt cấp chứng chỉ. Hạ TTL xuống 300 giây trước ngày chuyển DNS để quay lui nhanh. Giá trị `SITE_ADDRESS`, `STAGING_ADDRESS`, `SITE_ORIGIN`, `SITE_URL` đặt trong `.env.*` (mục 4), không ghi vào repo.

## 3. Caddy

```caddyfile
# Khối dùng chung; tham số: {args[0]} = host upstream backend, {args[1]} = host upstream frontend,
# {args[2]} = thư mục media của môi trường, {args[3]} = HSTS max-age (giây)
(vyc_site) {
	encode zstd gzip

	header {
		-Server
		Strict-Transport-Security "max-age={args[3]}"
		X-Content-Type-Options nosniff
		# CSP chung (chốt chính xác lúc dựng khung): img-src cho tile bản đồ Leaflet ở /quan-ly/vung-nguyen-lieu.
		# Hai script inline của trang công khai cần hash trong CSP (frontend-seo.md V7).
		Content-Security-Policy "default-src 'self'; script-src 'self' {$CSP_GTM_SCRIPT:}; img-src 'self' data: https://tile.openstreetmap.org https://*.tile.openstreetmap.org {$CSP_GTM_IMG:}; connect-src 'self' {$CSP_GTM_CONNECT:}; frame-ancestors 'none'"
			# GTM: các biến CSP_GTM_* trong .env.* chỉ có giá trị khi GTM_ID có giá trị (mục 4, 3 dưới); trống thì CSP không mở host nào.
	}

	# Cache theo frontend-seo.md mục 2: bundle có hash thì immutable 1 năm; 4 trang prerender 1 giờ.
	@astro_assets path /_astro/*
	header @astro_assets Cache-Control "public, max-age=31536000, immutable"
	@prerender path /chinh-sach-bao-mat /chinh-sach-doi-tra /chinh-sach-van-chuyen /lien-he
	header @prerender Cache-Control "public, max-age=3600"

	handle /api/* {
		reverse_proxy {args[0]}:8000 {
			# Ghi đè (không nối thêm): Django chỉ tin giá trị này (mục 3, "Tin header IP").
			header_up X-Forwarded-For {remote_host}
			header_up X-Real-IP {remote_host}
		}
	}

	handle_path /media/* {
		root * {args[2]}
		file_server
		header {
			Cache-Control "public, max-age=2592000, immutable"
			X-Content-Type-Options nosniff
			Content-Security-Policy "default-src 'none'; img-src 'self'; style-src 'unsafe-inline'; sandbox"
		}
	}

	handle {
		reverse_proxy {args[1]}:4321 {
			header_up X-Forwarded-For {remote_host}
		}
	}

	# Access log mặc định của Caddy có IP khách; xoá trước khi ghi (mục 11 thiết kế, backend.md mục 5.1).
	log {
		output stdout
		format filter {
			wrap json
			fields {
				request>remote_ip delete
				request>client_ip delete
				request>remote_port delete
				request>headers>X-Forwarded-For delete
				request>headers>Cookie delete
				request>headers>Authorization delete
			}
		}
	}
}

{$SITE_ADDRESS} {
	import vyc_site backend frontend /srv/media 31536000
}

# Chỉ khi staging cùng VPS; bỏ khối này nếu staging ở VPS riêng.
{$STAGING_ADDRESS} {
	header X-Robots-Tag "noindex, nofollow"
	basic_auth {
		{$STAGING_BASIC_USER} {$STAGING_BASIC_HASH}   # hash bcrypt từ `caddy hash-password`, không phải mật khẩu
	}
	import vyc_site backend-staging frontend-staging /srv/media-staging 300
}
```

- **HTTPS tự động**: chỉ cần DNS trỏ về VPS và cổng 80/443 mở; Caddy tự xin và gia hạn chứng chỉ Let's Encrypt, lưu ở volume `caddy_data` (không xoá volume này, kẻo chạm giới hạn xin chứng chỉ). Caddy tự chuyển hướng HTTP→HTTPS nhưng **không** tự bật HSTS, nên Caddyfile mẫu ghi tường minh `Strict-Transport-Security`. Prod bắt đầu `max-age=31536000`, staging chỉ 300 giây (tham số snippet) để không ghim trình duyệt vào HTTPS cho tên miền thử nghiệm; chỉ thêm `includeSubDomains` và `preload` sau khi chắc mọi tên miền phụ chạy HTTPS (khó quay lui).
- **Staging** (nếu cùng VPS) bị chặn hai lớp: basic auth (người lạ và bot không vào được) và `X-Robots-Tag: noindex, nofollow` (phòng khi lộ). Thông tin đăng nhập nằm trong `.env.prod` (`STAGING_BASIC_USER`, `STAGING_BASIC_HASH`), không commit. Smoke test và Lighthouse trên staging phải gửi kèm thông tin này. Staging không đưa vào sitemap.
- **Log Caddy không có IP khách**: khối `log` lọc bỏ `remote_ip`, `client_ip`, `remote_port` và header `X-Forwarded-For`, `Cookie`, `Authorization`. Đường dẫn `/q/<serial>` được giữ trong log 30 ngày để dò lỗi (sếp chốt #773; serial in trên tem, không phải dữ liệu cá nhân, và log không có IP khách). Nếu sau này đổi ý thì thêm bộ lọc `uri` vào khối `log`.
- **`/media/*`** mỗi môi trường có volume media riêng (`media` cho prod, `media-staging` cho staging), Caddy mount chỉ đọc (`:ro`) lần lượt vào `/srv/media` và `/srv/media-staging`; snippet nhận thư mục làm tham số nên staging không bao giờ phục vụ ảnh prod. Phục vụ thẳng từ volume, không đi qua Django. Tên file ảnh có hash nội dung nên cache `immutable` an toàn. Header `nosniff` và CSP `sandbox` chặn trình duyệt chạy file tải lên (ví dụ SVG/HTML giả ảnh) như một trang trong origin của site; ảnh nhúng bằng `<img>` vẫn hiển thị bình thường. Ảnh sinh ở Django lúc upload (#666 d). Ảnh tem, chứng nhận chỉ dành nội bộ (nếu có) **không** để trong `/media/` công khai; đó là `MEDIA_PRIVATE_ROOT` (mục 4), Caddy không mount thư mục này.
- **Cache**: Caddy không lưu phản hồi ở server; chỉ gắn header cho trình duyệt/CDN. `/_astro/*` (tên file có hash) `public, max-age=31536000, immutable`; 4 trang prerender (`/chinh-sach-bao-mat`, `/chinh-sach-doi-tra`, `/chinh-sach-van-chuyen`, `/lien-he`) `public, max-age=3600`. Các trang SSR còn lại giữ `Cache-Control` do Astro gửi (60/600, `/q/` 60).
- **CSP và Leaflet (T11)**: màn `/quan-ly/vung-nguyen-lieu` nạp tile từ `tile.openstreetmap.org` nên `img-src` phải cho phép host này (khối `header` của snippet). Ngoại lệ ngân sách JS 30 KB của màn đó (Leaflet ≈ 40 KB gzip) do frontend-seo.md quy định. Chính sách đầy đủ chốt lúc dựng khung, chưa kiểm. Danh sách cần chốt lúc dựng khung:
  - **GTM (#770)**: khi `GTM_ID` có giá trị, `.env.*` đặt `CSP_GTM_SCRIPT=https://www.googletagmanager.com` (`script-src`), `CSP_GTM_CONNECT=https://www.google-analytics.com https://*.google-analytics.com https://*.analytics.google.com https://*.googletagmanager.com` (`connect-src`) và `CSP_GTM_IMG=https://www.googletagmanager.com` (`img-src`). Danh sách host chính xác kiểm theo thẻ thật mà sếp gắn trong GTM (mỗi thẻ quảng cáo có thể cần thêm host); không đặt `GTM_ID` mà bỏ trống các biến này, kẻo GTM bị CSP chặn. Script GTM nạp thẻ động nên không băm được: cân nhắc nonce hoặc chấp nhận host cho phép.
  - **Style inline của Astro (#770)**: Astro có thể sinh `<style>` inline (CSS scoped nhỏ); `default-src 'self'` chặn chúng. Chốt: hoặc `build.inlineStylesheets: 'never'` để mọi CSS là file (khớp `site.css`), hoặc thêm hash `style-src`. Ưu tiên `'never'` để không phải dùng `'unsafe-inline'`.
  - Hash hai script inline của trang công khai (frontend-seo.md V7).
  - Thứ tự áp CSP của `/media/*` với CSP chung (#772): kiểm `caddy validate` + `curl -I /media/…` xem header cuối cùng là CSP `sandbox` của `/media/` chứ không bị nhân đôi.
- **Tin header IP (chốt #671; khớp `backend.md` mục 5.1)**: header `X-Forwarded-For` chỉ đáng tin khi request đến từ mạng compose nội bộ. Hai nơi gọi Django: Caddy (cho `/api/*`) và Astro SSR (gọi API lúc render). Contract:
  - **Caddy ghi đè** `X-Forwarded-For` bằng IP kết nối tới nó (`header_up X-Forwarded-For {remote_host}`), cho cả `/api/*` lẫn route Astro; giá trị khách tự gửi bị bỏ.
  - **Astro chuyển tiếp nguyên** giá trị nhận từ Caddy khi gọi Django, **không nối thêm** IP nào (frontend-seo.md giữ đúng điều này).
  - **Django** đặt `TRUSTED_PROXY_CIDRS` = subnet compose của môi trường đó (bảng ở mục 2.2; **cố định** bằng `networks.default.ipam.config.subnet` để không đổi khi tạo lại mạng). Chỉ khi `REMOTE_ADDR` thuộc dải này mới đọc `X-Forwarded-For`, duyệt **từ phải sang trái**, bỏ IP thuộc dải compose, lấy IP đầu tiên không thuộc dải. Cách này vẫn đúng nếu Astro lỡ nối thêm IP của Caddy. Header trống hoặc mọi IP đều thuộc dải thì dùng `REMOTE_ADDR`; `REMOTE_ADDR` ngoài dải thì bỏ qua header.
  - Postgres và backend **không** `ports:` ra host ở prod, nên không có đường nào từ Internet tới backend mà bỏ qua Caddy.
  - Mục 11 nói không lưu IP gốc của khách quét: IP chỉ dùng cho giới hạn tần suất; nơi ghi dữ liệu quét lưu bản băm có muối hoặc bỏ đi. Việc này thuộc backend, ghi ở đây để khớp.
- Giới hạn tần suất API công khai (mục 11): làm ở Django theo IP đã xác thực ở trên (đơn giản, 1 VPS). Có thể bổ sung Caddy rate-limit nếu cần, nhưng cần plugin nên không làm mặc định.

## 4. Môi trường và biến

- File mẫu `deploy/env/.env.example` (commit) chỉ có tên biến và giá trị giả. File thật `.env.dev`, `.env.staging`, `.env.prod` **không commit** (`.gitignore` đã có `.env.*` kèm `!.env.example`); đặt trên VPS với quyền `600`, thuộc user deploy.
- Danh sách biến cho `.env.example` (chỉ tên; file thật làm lúc dựng khung, giá trị mẫu là giả hoặc để trống). Cột "Bí mật" = chỉ có trong `.env.*` thật và GitHub/VPS secrets, không bao giờ commit giá trị:

| Nhóm | Biến | Bí mật | Ghi chú |
| --- | --- | --- | --- |
| Chung | `ENVIRONMENT` | | dev / staging / prod |
| | `SITE_ADDRESS` | | host của môi trường (Caddy, prod) |
| | `TZ` | | `Asia/Ho_Chi_Minh` |
| Django | `DJANGO_SECRET_KEY` | có | |
| | `DJANGO_DEBUG` | | `0` ở staging/prod |
| | `DJANGO_ALLOWED_HOSTS` | | gồm cả tên service `backend` (Astro gọi nội bộ) |
| | `SITE_ORIGIN` | | nguồn gốc `https://…`; Django suy ra `CSRF_TRUSTED_ORIGINS` (theo `backend.md` mục 7.4) |
| | `TRUSTED_PROXY_CIDRS` | | theo môi trường: prod `172.28.0.0/24`, staging `172.29.0.0/24`, dev `127.0.0.1/32,::1/128` (mục 2.2) |
| | `IP_HASH_SALT` | có | muối băm IP (`scan_event.ip_hash`, khoá throttle); đổi muối làm mất liên kết thống kê cũ nên đừng đổi tuỳ tiện |
| | `MEDIA_ROOT` | | thư mục ảnh công khai, volume `media` (Caddy mount `:ro`) |
| | `MEDIA_PRIVATE_ROOT` | | thư mục tệp nội bộ, volume riêng; **không** mount vào Caddy |
| | `ERROR_WEBHOOK_URL` | có | Django gửi 5xx về kênh Qwork (URL webhook là bí mật); để trống thì tắt |
| Postgres | `POSTGRES_DB`, `POSTGRES_USER` | | |
| | `POSTGRES_PASSWORD` | có | |
| | `DATABASE_URL` | có | chứa mật khẩu |
| Astro | `API_INTERNAL_URL` | | `http://backend:8000` (staging: `http://backend-staging:8000`) |
| | `SITE_URL` | | nguồn gốc công khai (canonical, sitemap); cùng giá trị với `SITE_ORIGIN` của Django trong một `.env`; đọc lúc chạy (staging và prod chung image) |
| | `GTM_ID` | | ID Google Tag Manager, đọc lúc chạy; để trống thì tắt thẻ |
| Caddy (CSP) | `CSP_GTM_SCRIPT`, `CSP_GTM_CONNECT`, `CSP_GTM_IMG` | | host GTM cho CSP, chỉ điền khi `GTM_ID` có giá trị (mục 3); trống thì không mở host nào |
| Staging (chỉ cùng VPS) | `STAGING_ADDRESS`, `STAGING_BASIC_USER` | | |
| | `STAGING_BASIC_HASH` | có | hash bcrypt của `caddy hash-password` |
| Sao lưu | `BACKUP_REMOTE` | | tên remote rclone kiểu `crypt` bọc Google Drive (ví dụ `vyc-crypt:`), mục 6 |
| | `BACKUP_KEEP` | | `30` |
| | `RCLONE_CONFIG_*` | có | hoặc file `rclone.conf` quyền `600` ngoài repo; chứa token Drive và mật khẩu crypt (đã làm mờ) |
| | `ALERT_WEBHOOK_URL` | có | `backup.sh` báo sao lưu hỏng (kênh Qwork); khác `ERROR_WEBHOOK_URL` của Django, có thể cùng kênh |

- Secret trên VPS do sếp tạo (sinh ngẫu nhiên: `python -c "import secrets;print(secrets.token_urlsafe(50))"`). Trên CI dùng GitHub Secrets/Environments (`staging`, `production`); không bao giờ in secret ra log.
- Cookie `Secure` chỉ bật khi `ENVIRONMENT != dev` (dev chạy http localhost).

## 5. Migration tự động

`backend-entrypoint.sh`:

```sh
#!/bin/sh
set -eu
python manage.py migrate --noinput
python manage.py collectstatic --noinput   # chỉ cho trang admin Django nếu dùng
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 \
  --access-logfile - --error-logfile -
```

- Postgres có `healthcheck`, backend `depends_on: condition: service_healthy`, nên migrate không chạy khi DB chưa sẵn sàng.
- Chạy lại nhiều lần an toàn (migrate idempotent). Chỉ chạy **một** replica backend (1 VPS), nên không có tranh chấp migrate.
- Quy tắc migration: chỉ thêm, không sửa migration đã deploy; đổi phá vỡ (xoá cột) làm hai bước qua hai lần deploy. CI kiểm `makemigrations --check --dry-run` để bắt quên tạo migration.
- Trước mỗi lần deploy prod: chạy `backup.sh <môi trường>` (`prod` hoặc `staging`) lấy bản dump "trước deploy" (xem mục 9, quay lui).

## 6. Sao lưu và khôi phục

**Lịch**: cron của host VPS, 23:00 giờ VN (`CRON_TZ=Asia/Ho_Chi_Minh`, hoặc `0 16 * * *` nếu cron chạy UTC). Cron chạy với `PATH` và thư mục làm việc tối thiểu, nên **mọi đường dẫn đều tuyệt đối** (script, file compose, `--env-file`). Mẫu `deploy/backup/crontab.example`:

```
CRON_TZ=Asia/Ho_Chi_Minh
0 23 * * * /opt/vyc/deploy/backup/backup.sh prod >> /var/log/vyc/backup.log 2>&1
30 23 * * * /bin/bash /opt/vyc/deploy/backup/compose.sh prod exec -T backend python manage.py purge_throttle >> /var/log/vyc/purge-throttle.log 2>&1
5 * * * * /opt/vyc/deploy/backup/collect-logs.sh prod >> /var/log/vyc/collect-logs.log 2>&1

# Staging (chỉ khi cùng VPS và đang bật; môi trường là tham số đầu, giống deploy.sh)
0 22 * * * /opt/vyc/deploy/backup/backup.sh staging >> /var/log/vyc/backup-staging.log 2>&1
#40 23 * * * /bin/bash /opt/vyc/deploy/backup/compose.sh staging exec -T backend python manage.py purge_throttle >> /var/log/vyc/purge-throttle-staging.log 2>&1
15 * * * * /opt/vyc/deploy/backup/collect-logs.sh staging >> /var/log/vyc/collect-logs-staging.log 2>&1
```

Staging dừng (`stop`) thì các dòng staging báo lỗi vô hại; bỏ chúng nếu staging không chạy thường xuyên. Staging chỉ có dữ liệu giả nên sao lưu staging chỉ để thử quy trình: giữ cục bộ trong `/var/backups/vyc/staging/`, không đẩy ra `BACKUP_REMOTE`.

Các dòng gom log container mỗi giờ (phút 05 prod, phút 15 staging) để logrotate giữ 30 ngày; cách tránh trùng/sót ở mục 7.

Dòng 23:30 chạy `purge_throttle` (xoá dòng `throttle_hit` cũ hơn 1 ngày, `backend.md` mục 5.2), đặt sau sao lưu để hai việc không tranh DB. `backup.sh`, `restore.sh` và `collect-logs.sh` nhận **môi trường làm tham số đầu** (`prod` hoặc `staging`, khác thì thoát lỗi, không có mặc định), như `deploy.sh`. Từ tham số suy ra một lần `COMPOSE="docker compose -p <vyc|vyc-staging> --env-file /opt/vyc/.env.<prod|staging> -f compose.yml -f compose.prod.yml -f <compose.edge.yml|compose.staging.yml>"` (đã đóng gói trong `deploy/backup/compose.sh`), cùng thư mục sao lưu (`/var/backups/vyc/<môi trường>/`), thư mục media và thư mục mốc log; mọi lệnh dùng `$COMPOSE`, không dựa vào thư mục hiện tại. Nhờ vậy `deploy.sh staging` gọi `backup.sh staging` và không chạm dữ liệu prod.

**`backup.sh <prod|staging>`** (mô tả, bản đầy đủ viết lúc dựng khung):
1. `$COMPOSE exec -T postgres pg_dump -Fc -U $POSTGRES_USER $POSTGRES_DB > /var/backups/vyc/<môi trường>/db-YYYYmmdd-HHMM.dump` (định dạng custom, đã nén). Ghi ra file tạm rồi đổi tên khi xong để không để lại file dở.
2. Đóng gói media: `tar` (hoặc `rclone sync` trực tiếp thư mục media; ảnh ít đổi nên sync gia tăng nhẹ hơn tar mỗi đêm).
3. Chỉ với `prod`: đẩy ra ngoài VPS bằng `rclone` tới `$BACKUP_REMOTE` (Google Drive qua remote `crypt`, xem "Mã hoá và Google Drive" bên dưới; chốt #773). Tên file và nội dung được mã hoá trước khi rời VPS. Cấu hình rclone nằm ngoài repo.
4. Xoá bản cũ, **giữ 30 bản DB** cả cục bộ lẫn đích: `ls -1t ... | tail -n +31 | xargs -r rm`. Media là bản đồng bộ, không nhân bản theo ngày.
5. Lỗi bất kỳ (`set -euo pipefail`) thì gọi `ALERT_WEBHOOK_URL`. Thành công ghi một dòng log JSON kèm kích thước file; kiểm file > 0 byte.

Dump chứa dữ liệu kinh doanh nên thư mục sao lưu quyền `700`; file dump đã được `.gitignore` chặn (mục 10). 

**Mã hoá và Google Drive (chốt #773)**: đích ngoài VPS là Google Drive, luôn qua remote `crypt` của rclone (mã hoá nội dung và tên file; Google không đọc được). Phương án `age` chỉ dùng nếu sau này bỏ rclone crypt.
- Sếp tạo một lần (ngoài repo): `rclone config` tạo remote `gdrive` (loại `drive`, nên dùng client ID riêng, scope `drive.file`) rồi remote `vyc-crypt` loại `crypt` trỏ `gdrive:vyc-backup`, bật mã hoá tên file; đặt `BACKUP_REMOTE=vyc-crypt:`. `rclone.conf` quyền `600`, ngoài repo.
- **Khoá mã hoá giữ ngoài VPS**: hai mật khẩu crypt (password và password2) sinh ngẫu nhiên, sếp lưu bản chính trong trình quản lý mật khẩu và một bản cất riêng (in/USB). Mất khoá = bản trên Drive thành rác, không ai khôi phục được; phải cất khoá **trước** khi bật cron. Trên VPS, `rclone.conf` chỉ làm mờ (obscure), không phải mã hoá, nên VPS bị chiếm thì Drive bị đọc được: dùng tài khoản Google riêng cho sao lưu, bật xác thực 2 bước, xoay token khi nghi lộ.
- Token Drive hết hạn hoặc bị thu hồi thì `backup.sh` lỗi và báo `ALERT_WEBHOOK_URL`; mỗi tháng kiểm bản mới nhất trên Drive (`rclone lsl "$BACKUP_REMOTE"`).
- **Cách thử khôi phục** (mỗi quý): trên máy khác với `rclone.conf` dựng lại từ khoá đã cất (chứng minh khoá cất đúng): `rclone copy "$BACKUP_REMOTE"db-<ngày>.dump /tmp/thu/` (rclone tự giải mã), kiểm `pg_restore --list` đọc được, rồi khôi phục vào DB tạm trên máy đó. Không restore dump prod vào staging (mục 2.2); thử `restore.sh staging` thì dùng dump của chính staging. Ghi ngày, thời gian khôi phục (RTO) và tuổi bản sao lưu (RPO).

**Khôi phục** (`restore.sh <prod|staging> <file.dump>`), thử trên staging hoặc DB tạm trước. `COMPOSE` định nghĩa như ở trên (đường dẫn tuyệt đối); `file.dump` cũng là đường dẫn tuyệt đối:
```sh
$COMPOSE stop backend frontend
$COMPOSE exec -T postgres dropdb  -U "$POSTGRES_USER" --if-exists "$POSTGRES_DB"
$COMPOSE exec -T postgres createdb -U "$POSTGRES_USER" "$POSTGRES_DB"
$COMPOSE exec -T postgres pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --no-owner < /var/backups/vyc/<môi trường>/db-YYYYmmdd-HHMM.dump
# media: rclone sync "$BACKUP_REMOTE"media <đường dẫn tuyệt đối tới volume media> (hoặc giải tar)
$COMPOSE up -d backend frontend   # migrate chạy lại, đưa schema về mới nhất
```
Script **hỏi xác nhận gõ tên môi trường** (phải trùng tham số đầu) trước khi `dropdb`, từ chối chạy với `prod` nếu không có cờ `--yes-prod`, và từ chối nếu `ENVIRONMENT` trong env-file không khớp tham số. Thử khôi phục trên staging dùng dump của chính staging (dữ liệu giả; không restore dump prod vào staging, mục 2.2). Mục 11 yêu cầu **thử khôi phục mỗi quý**: ghi ngày thử vào `docs/` hoặc issue định kỳ; mỗi lần thử đo RPO/RTO thực tế.

## 7. Log

- Mọi container ghi stdout/stderr; Docker `json-file` với xoay vòng: `max-size: "10m"`, `max-file: "5"` (đặt trong `compose.prod.yml` cho từng dịch vụ).
- Định dạng JSON: Django cấu hình `LOGGING` dùng `python-json-logger` (hoặc formatter tự viết), mỗi dòng có `ts, level, logger, msg, request_id, user_id`. Gunicorn access log định dạng JSON qua `--access-logformat`. **Ràng buộc (để giữ 30 ngày không vướng mục 11)**: format của gunicorn **không** chứa `X-Forwarded-For` (không dùng `%({x-forwarded-for}i)s`), không cookie; log Astro cũng không in `X-Forwarded-For`. Kiểm bằng test hoặc grep lúc dựng khung. Caddy `format json` (ở trên). Astro log qua một hàm in JSON một dòng.
- **Giữ 30 ngày (chốt, mục 11)**: `json-file` 10m×5 chỉ là vùng đệm ngắn hạn (vài ngày khi tải cao), không đủ 30 ngày. Nguồn giữ lâu là file trên host: cron mỗi giờ chạy `deploy/backup/collect-logs.sh` (đường dẫn tuyệt đối, dòng thứ ba trong `crontab.example` ở mục 6), nối log từng dịch vụ vào `/var/log/vyc/<dịch vụ>.jsonl`. Tránh trùng/sót: script đọc mốc thời gian lần chạy trước ở `/var/lib/vyc/logs.since/<dịch vụ>`, chạy `docker logs --timestamps --since <mốc> --until <bây giờ cắt tròn tới giây>`, chỉ khi ghi xong mới cập nhật mốc sang đúng giá trị `--until` đó (ghi file tạm rồi đổi tên). Lần đầu chưa có mốc thì lấy `--since 1h`. Chạy lại cùng khoảng thì ghi trùng ít nhất, không bao giờ sót. Xoay bằng `logrotate` với `deploy/logrotate/vyc` (cài vào `/etc/logrotate.d/vyc`):

  ```
  /var/log/vyc/*.jsonl /var/log/vyc/*.log {
      daily
      rotate 30
      compress
      delaycompress
      missingok
      notifempty
      copytruncate
  }
  ```

  `rotate 30` + `daily` = 30 ngày. Log Caddy đã lọc IP, cookie (mục 3) và log Django không ghi IP gốc, cookie, mật khẩu (dòng dưới) nên giữ 30 ngày không vướng mục 11. Dung lượng ước tính vài chục MB/ngày nén, đo lại sau tuần đầu.
- Lỗi 5xx → webhook kênh Qwork (`ERROR_WEBHOOK_URL`, mục 4): gửi từ Django (middleware/handler logging mức ERROR, có gộp để khỏi spam). Không đưa secret, mật khẩu, cookie, IP gốc khách quét vào log.

## 8. Lệnh dev/build/test/lint

**Chọn `Makefile`** (không dùng `just`). Lý do: không cần cài thêm công cụ; `make` có sẵn trong WSL/Git Bash. Lệnh thực chất nằm trong script của `uv` và `pnpm` nên Makefile chỉ là lớp mỏng, đổi sang `just` sau này không tốn. Windows của sếp: **khuyến nghị chạy trong WSL2 (Ubuntu) với repo nằm trong hệ file WSL** (`~/vyc`, không để ở `/mnt/d` vì chậm và lỗi file watch), hoặc chạy tất cả qua Docker Desktop (`make dev` đã bọc compose). Không cần cài Python/Node trên Windows nếu dùng Docker.

| Mục đích | Lệnh Makefile | Thực chất |
| --- | --- | --- |
| Chạy toàn bộ dev | `make dev` | `docker compose -f deploy/compose.yml -f deploy/compose.dev.yml up --build` |
| Dừng / xoá dữ liệu dev | `make down` / `make reset-db` | `reset-db` hỏi xác nhận, chỉ cho dev |
| Cài phụ thuộc | `make install` | `cd backend && uv sync --frozen`; `cd frontend && pnpm install --frozen-lockfile` |
| Migration | `make migrate` / `make makemigrations` | `uv run python manage.py migrate` / `makemigrations` |
| Tạo tài khoản dev | `make seed` | nạp dữ liệu giả: 1 tài khoản OWNER, 2 WORKSHOP và dữ liệu luồng mẫu (TK mục 2 chỉ có hai vai đăng nhập) |
| Test backend | `make test-be` | `cd backend && uv run pytest` (cần Postgres: dùng DB trong compose dev) |
| Lint backend | `make lint-be` | `uv run ruff check . && uv run ruff format --check . && uv run mypy . && uv run lint-imports` |
| Sửa format backend | `make fmt-be` | `uv run ruff check --fix . && uv run ruff format .` |
| Build frontend | `make build-fe` | `cd frontend && pnpm build` (`astro build`) |
| Lint frontend | `make lint-fe` | `pnpm check` (`astro check && biome ci .`, frontend-seo.md mục 9) |
| Test frontend | `make test-fe` | `pnpm test` |
| Kiểm ngân sách dung lượng | `make budget` | `node scripts/check-budget.mjs` sau build (mục 9) |
| Gộp | `make check` | lint + test + build cả hai phía (chạy trước khi push) |
| Build image prod | `make image` | `docker compose --env-file deploy/env/dev-defaults -f compose.yml -f compose.prod.yml build` (cần `ENVIRONMENT`, lấy từ `dev-defaults`; CI đặt `ENVIRONMENT=dev` rõ ràng) |

Ghi chú: lệnh `make` ở trên là hợp đồng; tên script `pnpm`/`uv` có thể đổi cho khớp với khung code, Makefile là nơi duy nhất cần sửa.

## 9. CI/CD bằng GitHub Actions

Repo: `KevinDodv/vyc-project`. Ghim action theo **commit SHA** (kèm comment số phiên bản) và Dependabot cập nhật.

### 9.1 `.github/workflows/ci.yml` (mỗi PR và push `main`)

| Job | Việc | Chi tiết |
| --- | --- | --- |
| `backend` | lint + test | `services: postgres:16` (healthcheck), `astral-sh/setup-uv`, `uv sync --frozen`, `ruff check`, `ruff format --check`, `mypy .`, `lint-imports` (luật phụ thuộc app, `backend.md` mục 1.3), `makemigrations --check --dry-run`, **kiểm OpenAPI**, `pytest` kèm coverage. Test theo mã BR (mục 11: unit test cho mọi BR). Kiểm OpenAPI: sinh lại `backend/openapi/v1.json` và `public.json` bằng lệnh ở `backend.md` mục 7.3 (`export_openapi_schema … --output`) rồi `git add -N backend/openapi/ && git diff --exit-code backend/openapi/` (`add -N` để file mới chưa track cũng bị tính là lệch); lệch bản đã commit thì job đỏ (nhắc người sửa API chạy lại lệnh sinh và commit). |
| `frontend` | lint + test + build | `pnpm/action-setup`, `setup-node` (Node 24, cache pnpm), `pnpm install --frozen-lockfile`, `pnpm check`, `pnpm test`, kiểm kiểu API sinh (`pnpm gen:api` rồi `git add -N frontend/src/lib/api/ && git diff --exit-code frontend/src/lib/api/`), `pnpm build`. Upload `dist/` làm artifact cho job sau. |
| `budget` | ngân sách dung lượng | chạy sau `frontend`; script đọc `dist/` và **fail** khi vượt ngưỡng (bảng dưới). |
| `lighthouse` | Lighthouse CI + test E2E | `deploy/ci/stack.sh up` dựng stack bằng `compose.ci.yml` (Postgres, Django, Astro, **Caddy** nén zstd/gzip, `ENVIRONMENT=dev`), tạo OWNER với mật khẩu sinh ngẫu nhiên mỗi lần chạy (ghi vào `GITHUB_ENV` thành `E2E_OWNER_PASSWORD`, không nằm trong repo hay secret) và nạp seed bằng `deploy/ci/seed_catalog.py`. Sau đó `lhci autorun` với `frontend/lighthouserc.cjs` (mobile preset, 3 lần/URL, `aggregationMethod: "median"` trên mọi assertion; mặc định của LHCI là lần tốt nhất nên bắt buộc khai). Lighthouse chạy **trước** Playwright để sản phẩm do E2E tạo không lẫn vào trang đo. Cùng stack chạy **Playwright** (luồng mẫu theo backend.md mục 8): bước này **fail** nếu thiếu `E2E_OWNER_PASSWORD`, và dùng reporter JSON để fail khi `skipped > 0`, `unexpected > 0` hoặc không có test nào chạy (spec tự `skip` khi thiếu biến nên nếu không kiểm thì CI xanh giả). `playwright-report/` và `.lighthouseci/` upload làm artifact. |
| `makefile` | kiểm Makefile (nghiệm thu thay máy thiếu make/pnpm/Docker) | `make install`, `make check`, rồi sinh lại OpenAPI và `.d.ts` và `git add -N … && git diff --exit-code` (cây làm việc không được lệch), cuối cùng `make image`. Job đặt `ENVIRONMENT=dev` rõ ràng vì settings mặc định là prod và `compose.yml` dùng `${ENVIRONMENT:?}`. |
| `images` | build thử Dockerfile | `docker build` hai image (không push) để bắt lỗi Dockerfile sớm. |
| `infra` | kiểm cấu hình hạ tầng | `shellcheck` cho `deploy/**/*.sh`, `actionlint`, `docker compose config -q` cho bốn bộ file (prod, staging, ci, dev), `caddy validate` với `SITE_ADDRESS` là tên miền và là `http://localhost`. |

Ngân sách và ngưỡng Lighthouse (**căn theo #648**, Huy4 đã đối chiếu ở #714: điểm ≥ 95, SEO = 100, INP < 200 ms với lab dùng TBT):

| Hạng mục | Ngưỡng | Cách kiểm |
| --- | --- | --- |
| CSS trang công khai (`site.css`, byte đã nén) | < 15 KB | chỉ đo ở job `lighthouse` (qua Caddy có nén); job `budget` không đo CSS (đã chốt #666 a) |
| JS trang công khai | 0 KB framework; trang tĩnh không có `<script>` ngoài đoạn nhỏ cần thiết | `budget` quét HTML đã build (kiểm tĩnh), fail nếu thấy bundle framework |
| Font | tự host, chỉ subset tiếng Việt, woff2 | `budget` kiểm không có request tới Google Fonts |
| Ảnh LCP | AVIF/WebP, có `preload`, có `width/height` | Lighthouse audit |
| LCP | ≤ 2,5 s (mobile, 4G mô phỏng) | LHCI assertion `error` |
| CLS | ≤ 0,1 | LHCI assertion `error` |
| TBT (thay INP trong lab) | ≤ 200 ms | LHCI assertion `error`; INP chỉ đo được trên dữ liệu thật |
| INP | < 200 ms (#648) | theo dõi thực địa (CrUX/Search Console) sau go-live |
| Điểm Lighthouse | Performance ≥ 95, Accessibility ≥ 95, Best Practices ≥ 95, SEO = 100 | LHCI `minScore` |

URL kiểm (`frontend/lighthouserc.cjs`): `/` và `/san-pham/tinh-dau-que-van-yen-10ml` (slug của seed CI). `/san-pham`, `/chinh-sach-bao-mat` thêm vào ngay khi trang tồn tại (khung chưa có hai trang này). **Ở bước dựng khung chưa đo `/q/<serial>`**: `operations` còn trống nên chưa có serial `ISSUED`; thêm URL `/q/<serial-seed>` và dữ liệu seed khi làm GĐ2. Mọi assertion để mức `error` (chốt #779) với trung vị 3 lần chạy để bớt nhiễu của runner CI. **Chưa kiểm trên CI thật**; sẽ chỉnh ngưỡng sau lần chạy đầu nếu nhiễu quá. **Đang đỏ đã biết:** font woff2 công khai 67 KB (latin + vietnamese, độ đậm 400 và 700) vượt ngưỡng 50 KB ở `budget` và `resource-summary:font:size`; cần bỏ một độ đậm hoặc sếp nới ngưỡng (xem thẻ #78).

### 9.2 Deploy: `.github/workflows/deploy.yml`

**Chọn: build image trên CI, đẩy lên GHCR, VPS `pull` qua SSH.** Lý do:
- VPS 4 GB không phải gánh `pnpm build`/`docker build` (dễ OOM và làm chậm site đang chạy).
- Image bất biến, gắn tag theo commit SHA: deploy và quay lui đều là "chạy lại tag X", đúng yêu cầu chạy lại nhiều lần cho cùng kết quả.
- Không cần mở thêm dịch vụ; chỉ cần một khoá SSH chỉ chạy được một lệnh deploy.

Luồng:
1. Kích hoạt: push tag `v*` (prod) hoặc push `main` (staging). Prod dùng GitHub Environment `production` có **bắt buộc duyệt tay**.
2. Job `build-push`: build hai image, tag `ghcr.io/kevindodv/vyc-backend:<sha>` và `…-frontend:<sha>`, đẩy GHCR bằng `GITHUB_TOKEN`. Khi kích hoạt bởi tag `vX.Y.Z`, mỗi image được gắn **cả hai tag**: `<sha>` (sha của commit được tag) và `vX.Y.Z`; nhờ vậy `deploy.sh vX.Y.Z` (quay lui bằng tay) luôn có image tương ứng để `pull`. Job `deploy` của workflow luôn truyền `<sha>` của commit đó.
3. Job `deploy`: SSH vào VPS (khoá/host/user lưu ở Secrets của Environment: `DEPLOY_SSH_KEY`, `DEPLOY_HOST`, `DEPLOY_USER`; ghim `known_hosts`), chạy `/opt/vyc/deploy/deploy.sh` với đúng một tham số `<sha>` (môi trường do khoá SSH quyết định, bước 4):
   `backup.sh <môi trường>` (bản trước deploy; môi trường là hằng trong `authorized_keys`) → `IMAGE_TAG=<sha> $COMPOSE pull` → `up -d` → chờ healthcheck → smoke test `curl -fsS https://$SITE/api/health` → thất bại thì tự đưa về tag cũ (lưu ở file `.last-good-tag`). Staging cùng VPS có basic auth nên smoke test gửi kèm thông tin đăng nhập (mục 3).
4. Khoá SSH deploy: user riêng không có sudo, mỗi môi trường **một khoá riêng** (Secret của Environment `production` / `staging`), mỗi khoá một dòng `authorized_keys` cố định môi trường: `command="/opt/vyc/deploy/deploy.sh prod"` hoặc `command="/opt/vyc/deploy/deploy.sh staging"`, kèm `restrict`. Script dùng đối số đầu (`prod`/`staging`, hằng trong `authorized_keys`, không do client gửi) để chọn project (`-p vyc` / `-p vyc-staging`), `--env-file` và subnet; khoá staging không deploy được prod. Tham số do client gửi nằm trong `SSH_ORIGINAL_COMMAND`, là **dữ liệu không tin cậy**. `deploy.sh` phải:
   - lấy tham số duy nhất từ `SSH_ORIGINAL_COMMAND`, từ chối nếu có nhiều hơn một từ;
   - chỉ chấp nhận đúng mẫu: sha hex `^[0-9a-f]{7,40}$` hoặc tag phát hành `^v[0-9]+\.[0-9]+\.[0-9]+$`; khác thì thoát mã lỗi, không chạy gì;
   - dùng giá trị đã validate dưới dạng đối số có nháy (`"$TAG"`), không đưa vào `eval`, `sh -c` hay chuỗi lệnh ghép.
   - **Cảnh báo quyền**: user deploy phải điều khiển được Docker, mà quyền Docker (nhóm `docker`) **tương đương root** trên VPS (mount được `/` vào container). Hạn chế duy nhất là `command=` + validate ở trên, nên khoá `DEPLOY_SSH_KEY` coi như khoá root: chỉ để trong GitHub Environment có duyệt, xoay khi nghi lộ, không dùng chỗ khác. Docker rootless là phương án mạnh hơn nếu sau này cần, nhưng chưa làm ở bản này.

Việc bước này đòi hỏi sếp làm một lần (ngoài repo, tôi không tự chạy): tạo VPS, DNS, cài Docker, tạo user deploy và khoá SSH, điền `.env.prod`, cấu hình rclone, thêm Secrets/Environment trên GitHub, bật gói GHCR. Hướng dẫn từng bước sẽ viết thành `deploy/README.md` lúc dựng khung.

**Quay lui**: `deploy.sh <tag cũ>` (chạy tay hoặc workflow `workflow_dispatch`). Migration đã chạy không tự lùi: vì quy tắc "chỉ thêm" ở mục 5, mã cũ vẫn chạy được với schema mới; trường hợp bất khả kháng thì khôi phục dump "trước deploy" (mục 6).

## 10. `.gitignore` cần bổ sung lúc dựng khung (finding #664)

Thêm vào `.gitignore` hiện có (tôi chưa sửa file đó vì ngoài phạm vi task này):

```gitignore
# --- Khoá, chứng chỉ ---
*.pem
*.key
*.p12

# --- Dữ liệu DB và sao lưu ---
db.sqlite3
*.sql
*.dump
*.sql.gz
*.bak
```

Lưu ý: `*.sql` sẽ chặn cả file SQL migration viết tay nếu có; nếu cần commit thì dùng `!path/to/file.sql`. Ngoài ra #664 nêu `.env.*` không che file kiểu `*.env` hoặc `secrets.*`: nên thêm `*.env` và `secrets.*` (giữ `!.env.example`). CI nên có bước quét secret (gitleaks) trên mỗi PR.

## 11. Quy ước vận hành

- Một PR đổi `deploy/` hoặc workflow phải kèm cách quay lui trong mô tả.
- Không `latest` cho image chạy thật; luôn tag SHA hoặc phiên bản.
- Không sửa tay trên VPS ngoài `.env.*`; mọi thay đổi qua repo.
- Cập nhật bảo mật: `unattended-upgrades` cho OS, Dependabot cho action/pip/pnpm/Docker base, kiểm hàng tháng.
- VPS: tường lửa chỉ mở 22 (nên giới hạn IP hoặc dùng khoá, tắt đăng nhập mật khẩu), 80, 443.

## 12. Chưa kiểm / câu hỏi đã trả lời

- Chưa có gì chạy thử: không có Dockerfile, compose, workflow trong repo. Cú pháp Caddyfile, compose, workflow sẽ kiểm (`docker compose config`, `caddy validate`, `actionlint`) lúc dựng khung; Lighthouse/CI thật chỉ kiểm được sau khi push.
- Ngưỡng #648 đã đối chiếu (Huy4, #714). Playwright, LHCI và CSP chỉ kiểm được trên CI thật / khi dựng khung (danh sách CSP cần chốt ở mục 3).
- **Sếp đã trả lời (#773)**: (1) tên miền: sếp tự đăng ký và giữ DNS, tài liệu dùng `SITE_ADDRESS`/`STAGING_ADDRESS` (mục 2.3); (2) VPS trong nước (tiêu chí mục 2.3); (3) staging chung VPS prod, chỉ bật khi cần thử (mục 2.1); (4) sao lưu lên Google Drive, có mã hoá (mục 6); (8) giữ `/q/<serial>` trong log Caddy 30 ngày để dò lỗi (mục 3, 7).
- **Việc sếp tự làm (ngoài repo)**: đăng ký tên miền và tạo bản ghi DNS (mục 2.3); thuê VPS (mục 2.3); tạo remote rclone crypt và cất khoá mã hoá (mục 6).
- Đã chốt trong bản này: log giữ 30 ngày bằng `logrotate` (mục 7); subnet compose prod `172.28.0.0/24`, staging `172.29.0.0/24` (mục 2.2); staging dùng chung một Caddy, có basic auth + noindex (mục 3).
- Backend cần cung cấp `/api/health`, `TRUSTED_PROXY_CIDRS`, logging JSON, webhook 5xx; frontend cần `/healthz` và gửi `X-Forwarded-For` với IP khách khi gọi API (báo Minh2/Huy4 trong tài liệu của họ).
