# Dựng VPS và vận hành deploy/sao lưu

Dành cho sếp (người làm các việc ngoài repo). Thiết kế gốc: `docs/kien-truc/van-hanh.md`; tài liệu này là bản làm từng bước. Mọi lệnh có `<...>` là chỗ cần thay giá trị thật. **Không dán secret vào repo, chat hay issue.**

Bản này mới được viết, **chưa chạy thật trên VPS nào** (xem mục 12). Lần dựng đầu tiên nên làm từng bước và báo đội chỗ nào lệch.

## 0. Tổng quan: ai làm gì

| Việc | Ai | Mục |
| --- | --- | --- |
| Đăng ký tên miền, tạo bản ghi DNS | Sếp | 1 |
| Thuê VPS trong nước, dựng hệ điều hành, cài Docker | Sếp | 1, 2 |
| Tạo user `deploy`, khoá SSH, clone repo, file `.env.*` | Sếp | 3, 4, 8 |
| Tạo rclone crypt trên Google Drive, **cất khoá mã hoá** | Sếp | 6 |
| Tạo Environment và Secrets trên GitHub | Sếp | 8 |
| Script, workflow, compose, Dockerfile | Đội (đã có trong repo) | |

Thứ tự: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9. Đừng bật cron (mục 7) trước khi cất khoá rclone (mục 6).

## 1. VPS và tên miền

Tiêu chí chọn VPS, giá trị `SITE_ADDRESS`/`STAGING_ADDRESS`: xem `van-hanh.md` mục 2.3. Tóm tắt:

- VPS **đặt trong nước**, 2 vCPU, 4 GB RAM, SSD ≥ 60 GB, IPv4 tĩnh, có snapshot, Ubuntu LTS, không chặn cổng 80/443.
- Sếp đăng ký tên miền và giữ quyền DNS. Tạo bản ghi (thay `<IP-VPS>`):

  | Loại | Tên | Giá trị | Dùng cho |
  | --- | --- | --- | --- |
  | A | `@` | `<IP-VPS>` | website prod |
  | A | `www` | `<IP-VPS>` | chuyển hướng về tên miền gốc (nếu dùng) |
  | A | `staging` | `<IP-VPS>` | staging, chỉ có tác dụng khi bật staging |

- Hạ TTL xuống 300 giây trước ngày chuyển DNS để quay lui nhanh. Có thể thêm CAA `letsencrypt.org`.
- Caddy tự xin chứng chỉ HTTPS khi DNS đã trỏ về VPS và cổng 80/443 mở; không xoá volume `caddy_data` (kẻo chạm giới hạn xin chứng chỉ).

## 2. Chuẩn bị VPS (một lần, bằng sudo)

```sh
sudo apt update && sudo apt -y upgrade
sudo apt -y install unattended-upgrades ufw git curl rclone util-linux
sudo dpkg-reconfigure -plow unattended-upgrades

# Tường lửa: chỉ 22, 80, 443
sudo ufw default deny incoming && sudo ufw default allow outgoing
sudo ufw allow 22/tcp && sudo ufw allow 80/tcp && sudo ufw allow 443/tcp
sudo ufw enable

# Swap 2 GB (bắt buộc khi staging chạy chung, tránh OOM-kill)
sudo fallocate -l 2G /swapfile && sudo chmod 600 /swapfile
sudo mkswap /swapfile && sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

- Tắt đăng nhập SSH bằng mật khẩu (`PasswordAuthentication no` trong `/etc/ssh/sshd_config`), chỉ dùng khoá. Kiểm tra bằng phiên SSH thứ hai trước khi đóng phiên cũ.
- `rclone` trong apt có thể cũ; nếu thiếu remote `crypt` hay scope Drive thì cài bản mới theo hướng dẫn trên rclone.org.
- Cài Docker Engine và plugin Compose theo hướng dẫn chính thức của Docker cho Ubuntu (kho apt của Docker), rồi kiểm: `docker compose version`.

## 3. User `deploy`, thư mục, mã nguồn

```sh
sudo adduser --disabled-password --gecos "" deploy
sudo usermod -aG docker deploy
```

> **Cảnh báo**: nhóm `docker` tương đương root trên VPS. Khoá SSH của user `deploy` (mục 8) vì vậy phải coi như khoá root: chỉ để trong GitHub Environment, xoay khi nghi lộ, không dùng chỗ khác. Không cho user này `sudo`.

```sh
sudo mkdir -p /opt/vyc /var/log/vyc /var/lib/vyc /var/backups/vyc
sudo chown -R deploy:deploy /opt/vyc /var/log/vyc /var/lib/vyc /var/backups/vyc
sudo chmod 700 /var/backups/vyc
# Mạng staging, tạo một lần ngoài compose (van-hanh.md 2.2)
sudo docker network create --subnet 172.29.0.0/24 vyc-staging
# Volume media của staging: Caddy (project prod) mount chỉ đọc nên phải tồn tại trước khi prod chạy
sudo docker volume create vyc-staging_media
# Cấp quyền ghi cho user của image backend (uid 10001): Caddy mount volume này chỉ đọc trước khi staging chạy lần đầu
sudo docker run --rm -v vyc-staging_media:/m alpine chown 10001:10001 /m
```

Mã nguồn: `deploy.sh` tự `git fetch` rồi `git checkout` đúng commit của lần deploy, nên `/opt/vyc` phải là bản clone. Nếu repo riêng tư, tạo **deploy key chỉ đọc** cho repo:

```sh
sudo -iu deploy
ssh-keygen -t ed25519 -f ~/.ssh/vyc_repo_ro -N "" -C "vyc-repo-readonly"
cat ~/.ssh/vyc_repo_ro.pub          # dán vào GitHub: repo > Settings > Deploy keys (KHÔNG tick Allow write)
printf 'Host github.com\n  IdentityFile ~/.ssh/vyc_repo_ro\n  IdentitiesOnly yes\n' >> ~/.ssh/config
git clone git@github.com:KevinDodv/vyc-project.git /opt/vyc
git -C /opt/vyc config core.fileMode false
```

Từ đây **không sửa tay** trong `/opt/vyc` ngoài các file `.env.*` (không nằm trong git). Sửa tay làm `git checkout` ở lần deploy sau từ chối chạy.

## 4. File `.env.prod` (và `.env.staging`)

File thật nằm ở `/opt/vyc/.env.prod`, **ngoài git**, quyền `600`, thuộc user `deploy`. Mẫu: `deploy/env/.env.example` (danh sách biến và ý nghĩa: `van-hanh.md` mục 4).

```sh
cp /opt/vyc/deploy/env/.env.example /opt/vyc/.env.prod
chmod 600 /opt/vyc/.env.prod
python3 -c "import secrets;print(secrets.token_urlsafe(50))"   # chạy cho từng secret: DJANGO_SECRET_KEY, IP_HASH_SALT, POSTGRES_PASSWORD
```

Phải sửa lại các giá trị mẫu sau (mẫu đặt sẵn giá trị dev):

- `ENVIRONMENT=prod` (staging: `staging`). `deploy.sh` và `restore.sh` từ chối chạy nếu giá trị này không khớp môi trường.
- `DJANGO_DEBUG=0`.
- `SITE_ADDRESS=<tên miền>`; `SITE_ORIGIN=https://<tên miền>` và `SITE_URL=https://<tên miền>` (cùng giá trị).
- `DJANGO_ALLOWED_HOSTS=<tên miền>,backend`.
- `TRUSTED_PROXY_CIDRS=172.28.0.0/24` (staging: `172.29.0.0/24`).
- `DJANGO_SECRET_KEY`, `IP_HASH_SALT`, `POSTGRES_PASSWORD`: giá trị ngẫu nhiên, **không dùng** `deploy/env/dev-defaults`. `IP_HASH_SALT` đổi thì mất liên kết thống kê cũ, đừng đổi tuỳ tiện.
- `BACKUP_REMOTE=vyc-crypt:` (phải kết thúc bằng `:` hoặc `/`, nếu có thư mục con thì `vyc-crypt:backups/`), `BACKUP_KEEP=30`, `ALERT_WEBHOOK_URL=<webhook kênh Qwork>` (để trống nếu chưa có).
- Staging cùng VPS: `STAGING_ADDRESS`, `STAGING_BASIC_USER`, `STAGING_BASIC_HASH` điền trong **`.env.prod`** (Caddy thuộc project prod đọc chúng). Sinh hash: `docker run --rm caddy:2 caddy hash-password` (nhập mật khẩu ở dấu nhắc, chỉ dán hash). Hash bcrypt có ký tự `$`, nên **bọc trong nháy đơn**: `STAGING_BASIC_HASH='$2a$14$...'`; không bọc thì Compose nội suy `$...` và làm hỏng hash (hoặc nhân đôi mỗi `$` thành `$$`).
- Staging dùng `.env.staging` riêng, dữ liệu giả, mật khẩu/khoá **khác** prod. Staging nhỏ hơn prod (van-hanh.md 2.1) nên thêm vào `.env.staging`: `PG_MEM_LIMIT=384m`, `PG_SHARED_BUFFERS=96MB`, `BACKEND_MEM_LIMIT=384m`, `WEB_CONCURRENCY=2`, `FRONTEND_MEM_LIMIT=256m`, `FRONTEND_HEAP_MB=160`.

Cú pháp: mỗi dòng `TÊN=giá trị`, không `export`, không cần nháy; script đọc từng biến bằng `grep`, không `source` file.

## 5. Image trên GHCR

CI đẩy image `ghcr.io/<chủ-repo-chữ-thường>/vyc-backend` và `vyc-frontend` (tag = sha commit, thêm `vX.Y.Z` khi phát hành). Gói mới tạo mặc định riêng tư, nên VPS cần đăng nhập để `pull`:

1. GitHub > Settings > Developer settings > Personal access tokens: tạo token (classic) **chỉ** scope `read:packages`.
2. Trên VPS, user `deploy`: `echo '<token>' | docker login ghcr.io -u <tên-GitHub> --password-stdin`.

Token lưu trong `~/.docker/config.json` của user `deploy`; xoay khi nghi lộ.

## 6. Sao lưu lên Google Drive qua rclone crypt (cất khoá trước!)

Mọi bản sao lưu prod được **mã hoá (nội dung và tên file) trước khi rời VPS**. Google chỉ thấy file vô nghĩa. Chốt #773.

### 6.1 Tạo remote (làm một lần, ngoài repo)

Dùng **tài khoản Google riêng cho sao lưu**, bật xác thực 2 bước. Trên VPS, user `deploy`: `rclone config`:

1. Remote `gdrive`, loại `drive`.
   - Nên tạo **client ID riêng** (Google Cloud Console > APIs & Services > Credentials > OAuth client ID loại "Desktop app", bật Google Drive API) thay vì dùng client ID chung của rclone (hay bị giới hạn tốc độ).
   - **Scope**: chọn `drive.file` (rclone chỉ thấy file do chính nó tạo, không đọc được phần còn lại của Drive). Xem 6.4 về việc kiểm scope này.
   - Màn hình đồng ý OAuth (consent screen) phải để **"In production"**. Nếu để "Testing", refresh token hết hạn sau 7 ngày và sao lưu sẽ im lặng hỏng.
   - VPS không có trình duyệt: ở câu "Use auto config?" chọn `n`, rồi chạy `rclone authorize "drive" "<client_id>" "<client_secret>" --drive-scope drive.file` trên máy có trình duyệt và dán token về.
2. Remote `vyc-crypt`, loại `crypt`:
   - `remote` = `gdrive:vyc-backup`
   - `filename_encryption` = `standard`, `directory_name_encryption` = `true`
   - **password và password2: để rclone tự sinh ngẫu nhiên** (chọn "Generate random password", độ dài 1024 bit).
3. Quyền file: `chmod 600 ~/.config/rclone/rclone.conf`. Trong `.env.prod` đặt `BACKUP_REMOTE=vyc-crypt:`. Nếu để `rclone.conf` ở chỗ khác thì thêm dòng `RCLONE_CONFIG=<đường dẫn tuyệt đối>` vào `.env.prod` (script nạp mọi biến `RCLONE_*` từ file đó).

### 6.2 CẤT KHOÁ (bắt buộc, trước khi bật cron)

`rclone.conf` trên VPS chỉ **làm mờ** (obscure) hai mật khẩu crypt, không phải mã hoá: ai vào được VPS thì đọc được Drive. Vì vậy:

- Lấy hai mật khẩu dạng gốc: `rclone config show vyc-crypt` rồi `rclone reveal <chuỗi password>` và `rclone reveal <chuỗi password2>`.
- Lưu **cả hai** vào trình quản lý mật khẩu của sếp, và **một bản nữa cất riêng** (in ra giấy hoặc USB, để chỗ an toàn khác VPS). Ghi kèm tên remote, `filename_encryption`, và client ID/secret của Google.
- **Mất khoá = mọi bản trên Drive thành rác, không ai khôi phục được.** Không có cách lấy lại.

### 6.3 Thử nghiệm

```sh
echo "thu nghiem" > /tmp/thu.txt
rclone copy /tmp/thu.txt vyc-crypt:thu/
rclone lsl vyc-crypt:thu/          # thấy file
rclone lsl gdrive:vyc-backup       # tên file phải là chuỗi mã hoá, không đọc được
rclone purge vyc-crypt:thu/ && rm /tmp/thu.txt
/bin/bash /opt/vyc/deploy/backup/backup.sh prod    # sao lưu thật lần đầu (cần stack prod đã chạy, mục 9)
rclone lsl vyc-crypt:              # thấy db-*.dump, media/, media-private/
```

### 6.4 Chống mất bản sao lưu do Drive (finding #786)

Sao lưu trên Drive vẫn có thể mất: xoá nhầm, token bị lộ (kẻ chiếm VPS có `rclone.conf` thì xoá được cả bản trên Drive), hoặc scope hạn chế. Làm ba việc:

1. **Kiểm scope `drive.file`**: remote `gdrive` chỉ thấy file do chính ứng dụng (client ID) đó tạo ra. Hệ quả: (a) thư mục `vyc-backup` phải do rclone tạo (đừng tạo tay trên giao diện Drive rồi kỳ vọng rclone thấy); (b) khi thử khôi phục trên máy khác (6.6) phải dùng **đúng client ID/secret** và token của cùng tài khoản. Cách kiểm: sau 6.3, trên **máy khác** cấu hình lại hai remote bằng thông tin đã cất và chạy `rclone lsl vyc-crypt:`; phải thấy file. Nếu không thấy gì, chuyển scope sang `drive` (rộng hơn, đổi lại rủi ro khi lộ token cao hơn) và báo đội. Việc này **chưa được kiểm trên Drive thật**.
2. **Bật lịch sử phiên bản và thùng rác**: không dọn thùng rác Drive của tài khoản sao lưu (Drive giữ file đã xoá 30 ngày; script xoá bản cũ bằng `rclone deletefile`, mặc định đưa vào thùng rác, đừng thêm `--drive-use-trash=false`). Media được `rclone sync` nên file bị ghi đè/xoá do lỗi nằm trong lịch sử phiên bản/thùng rác tới khi hết hạn.
3. **Giữ một bản sao ngoại tuyến mỗi tháng** (ổ USB/ổ cứng rời, để ngoài VPS và ngoài tài khoản Google đó). Bản chép là bản đã mã hoá, nên cần cả hai mật khẩu crypt đã cất ở 6.2 để dùng lại:

   ```sh
   rclone copy gdrive:vyc-backup /mnt/usb/vyc-offline-$(date +%Y%m)   # chép nguyên văn dạng mã hoá
   ```

### 6.5 Kiểm hằng tháng

`rclone lsl vyc-crypt:` và xem bản `db-*.dump` mới nhất có đúng ngày hôm qua không. Token Drive hết hạn hoặc bị thu hồi thì `backup.sh` lỗi và báo `ALERT_WEBHOOK_URL`, nhưng đừng chỉ trông vào cảnh báo.

### 6.6 Thử khôi phục (mỗi quý, bắt buộc: `van-hanh.md` mục 11)

Trên **máy khác** với `rclone.conf` dựng lại **từ khoá đã cất** (chứng minh khoá cất đúng):

```sh
rclone copy vyc-crypt:db-<ngày>.dump /tmp/thu/        # rclone tự giải mã
pg_restore --list /tmp/thu/db-<ngày>.dump | head       # đọc được danh mục
# rồi khôi phục vào một Postgres tạm trên máy đó, kiểm vài bảng
```

Ghi lại ngày thử, thời gian khôi phục (RTO) và tuổi bản sao lưu (RPO). Không restore dump prod vào staging.

## 7. Cài logrotate và cron (sau khi đã cất khoá)

```sh
sudo cp /opt/vyc/deploy/logrotate/vyc /etc/logrotate.d/vyc
sudo logrotate --debug /etc/logrotate.d/vyc      # phải không báo lỗi
sudo -iu deploy crontab -e                        # dán nội dung deploy/backup/crontab.example
```

- `deploy/logrotate/vyc` có dòng `su deploy deploy`: đổi nếu user/nhóm trên VPS không phải `deploy`.
- Cron chạy bằng user `deploy`, không phải root. Mẫu đã dùng đường dẫn tuyệt đối và `/bin/bash` (không phụ thuộc bit thực thi của file).
- Log giữ 30 ngày: `/var/log/vyc/*.jsonl` do `collect-logs.sh` gom mỗi giờ, logrotate xoay hằng ngày giữ 30 bản.
- Staging: các dòng staging trong mẫu đang để comment; bỏ comment khi dùng staging thường xuyên.

## 8. GitHub: Environment, Secrets, khoá SSH deploy

### 8.1 Khoá SSH (mỗi môi trường một khoá riêng)

Trên máy của sếp (không phải VPS):

```sh
ssh-keygen -t ed25519 -f vyc-deploy-prod    -N "" -C "gh-actions-prod"
ssh-keygen -t ed25519 -f vyc-deploy-staging -N "" -C "gh-actions-staging"
```

Trên VPS, thêm vào `/home/deploy/.ssh/authorized_keys` (mỗi khoá **một dòng**, môi trường cố định ngay trong `command=`; client không đổi được):

```
command="/bin/bash /opt/vyc/deploy/deploy.sh prod",restrict ssh-ed25519 AAAA...(nội dung vyc-deploy-prod.pub) gh-actions-prod
command="/bin/bash /opt/vyc/deploy/deploy.sh staging",restrict ssh-ed25519 AAAA...(nội dung vyc-deploy-staging.pub) gh-actions-staging
```

Tham số client gửi lên (tag) chỉ nằm ở biến `SSH_ORIGINAL_COMMAND`; `deploy.sh` từ chối mọi thứ không phải đúng một sha hex 7-40 ký tự hoặc `vX.Y.Z`. Chỉ giữ dòng staging nếu dùng staging. Sau khi dán vào GitHub (8.2), **xoá file khoá riêng khỏi máy** hoặc cất vào trình quản lý mật khẩu.

Lấy dòng khoá host của VPS để ghim (dùng làm secret `DEPLOY_KNOWN_HOSTS`):

```sh
cut -d' ' -f1,2 /etc/ssh/ssh_host_ed25519_key.pub     # chạy trên VPS
ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub      # vân tay để đối chiếu
```

### 8.2 Environment và Secrets

Repo > Settings > Environments, tạo hai Environment:

| Environment | Bắt buộc duyệt | Secrets |
| --- | --- | --- |
| `production` | **Required reviewers: sếp** (đây là bước duyệt tay trước khi lên prod). **Deployment branches and tags: Selected** = `main` và `v*` (bắt buộc, xem dưới) | `DEPLOY_SSH_KEY` (nội dung `vyc-deploy-prod`), `DEPLOY_HOST` (IP hoặc tên máy chủ SSH), `DEPLOY_USER` (`deploy`), `DEPLOY_KNOWN_HOSTS` (dòng ở 8.1) |
| `staging` | không duyệt tay, nhưng **Deployment branches and tags: Selected** = chỉ `main` (bắt buộc) | cùng bốn tên, giá trị của khoá `vyc-deploy-staging` |

Secret khai ở **Environment**, không khai ở mức repo, để khoá staging không dùng được cho prod.

**Vì sao phải giới hạn nhánh**: user `deploy` thuộc nhóm `docker` (tương đương root) và staging chạy chung VPS với prod. Ai chạy được workflow từ một nhánh tự chọn (kể cả sửa `deploy.yml` trên nhánh đó) sẽ dùng được secret của Environment. Giới hạn nhánh ở Environment chặn việc đó ở phía GitHub; `deploy.sh` chặn thêm ở phía VPS: nó chỉ checkout commit nằm trên `origin/main` và từ chối mọi thứ khác (tag cũng phải trỏ vào commit trên `main`). Chỉ nên cho người đáng tin ghi vào `main` (bật branch protection, bắt buộc PR).

Gói GHCR: lần chạy đầu tiên tạo gói; nếu sau đó `docker pull` bị từ chối thì vào Packages > gói > Package settings, kiểm quyền truy cập của repo (gói gắn với repo thì `GITHUB_TOKEN` đã đẩy được).

## 9. Deploy lần đầu

Điều kiện: DNS đã trỏ, `.env.prod` đã điền, đã `docker login ghcr.io`, đã làm mục 6 và 7.

1. Trên máy sếp: `git tag v0.1.0` rồi `git push origin v0.1.0` (đội không push; sếp tự đẩy).
2. GitHub > Actions > "Deploy": job build chạy, rồi dừng chờ duyệt ở Environment `production`. Bấm duyệt.
3. `deploy.sh prod <sha>` trên VPS: đồng bộ git, bỏ qua backup (lần đầu chưa có dữ liệu), `pull`, `up -d --wait`, kiểm `https://<tên miền>/api/health`, ghi tag chạy tốt vào `/opt/vyc/.last-good-tag.prod`.
4. Kiểm: `/bin/bash /opt/vyc/deploy/backup/compose.sh prod ps` (mọi dịch vụ `healthy`), mở `https://<tên miền>`.

Các lần sau: mỗi tag `vX.Y.Z` mới trên `main` là một lần phát hành. Trước mỗi lần, `deploy.sh` chạy `backup.sh prod` (bản "trước deploy"); backup lỗi thì **dừng, chưa đụng gì tới prod**. Sau `up`, nếu healthcheck hoặc smoke test hỏng, script tự đưa về tag chạy tốt trước đó và workflow báo đỏ.

## 10. Bật và tắt staging (mặc định tắt)

Staging chạy chung VPS prod, tốn khoảng 1 GB RAM; cả hai cùng chạy sát giới hạn 4 GB. Chỉ bật khi cần thử, thử xong thì tắt. Không bật lúc đang deploy hoặc sao lưu prod.

**Bật**

1. Kiểm RAM trống: `free -m` (cột `available` phải ≥ 1200 MB; `deploy.sh staging` cũng tự từ chối nếu thấp hơn).
2. Điền `.env.staging`; `STAGING_ADDRESS`, `STAGING_BASIC_USER`, `STAGING_BASIC_HASH` có trong `.env.prod`; DNS `staging` đã trỏ. Nếu vừa sửa `.env.prod`: `/bin/bash /opt/vyc/deploy/backup/compose.sh prod up -d caddy` để Caddy nạp lại.
3. GitHub > Settings > Secrets and variables > Actions > **Variables**: tạo biến `STAGING_ENABLED` = `true`.
4. Mỗi lần đẩy lên `main` khi biến này là `true` sẽ deploy staging (và bật stack nếu đang tắt). Muốn bật ngay: đẩy một commit mới lên `main`.

**Lưu ý smoke test**: staging có basic auth nên `deploy.sh` không gọi HTTPS công khai; chỉ dựa vào healthcheck của compose (`up --wait`). Thử thủ công sau khi bật: `curl -u <user> https://<STAGING_ADDRESS>/api/health`.

**Tắt**

```sh
/bin/bash /opt/vyc/deploy/backup/compose.sh staging stop    # giữ nguyên volume dữ liệu
```

và đổi biến `STAGING_ENABLED` về `false`. **Không dùng `down -v`** (xoá volume). Khi staging tắt, Caddy trả 502 cho `STAGING_ADDRESS` (bình thường). Nếu cron staging đang bật thì các dòng đó báo lỗi vô hại.

## 11. Vận hành hằng ngày

| Việc | Lệnh |
| --- | --- |
| Trạng thái | `/bin/bash /opt/vyc/deploy/backup/compose.sh prod ps` |
| Log trực tiếp | `/bin/bash /opt/vyc/deploy/backup/compose.sh prod logs -f --tail 100 backend` |
| Sao lưu tay | `/bin/bash /opt/vyc/deploy/backup/backup.sh prod` |
| Quay lui | GitHub > Actions > Deploy > Run workflow: chọn `production` và nhập tag cũ (`vX.Y.Z` hoặc sha đã có image). Migration đã chạy không tự lùi; mã cũ vẫn chạy được với schema mới (quy tắc "chỉ thêm", `van-hanh.md` mục 5). Bất khả kháng thì khôi phục dump "trước deploy" |
| Khôi phục | xem dưới |

**Khôi phục** (`restore.sh`; xoá DB hiện tại, tự chụp bản `prerestore-*.dump` trước, hỏi gõ lại tên môi trường):

```sh
# thử trên staging bằng dump của chính staging trước
/bin/bash /opt/vyc/deploy/backup/restore.sh staging /var/backups/vyc/staging/db-<ngày>.dump
# prod cần thêm cờ; dump lấy từ /var/backups/vyc/prod/ hoặc tải từ Drive (rclone copy vyc-crypt:db-<ngày>.dump /tmp/thu/)
/bin/bash /opt/vyc/deploy/backup/restore.sh prod /var/backups/vyc/prod/db-<ngày>.dump --yes-prod
# kèm media (đã có bản sao cục bộ ở /var/backups/vyc/prod/media và media-private)
... --media-dir /var/backups/vyc/prod/media --media-private-dir /var/backups/vyc/prod/media-private
```

Cần chạy trong terminal (script từ chối khi không có tty). Khôi phục xong, `backend` chạy `migrate` để đưa schema về mới nhất.

## 12. Những gì chưa chạy thật được

Máy dựng khung không có Docker, VPS, rclone hay quyền GitHub, nên:

- **Đã kiểm**: `bash -n` mọi script; chạy thử `deploy.sh`, `backup.sh`, `restore.sh` (các nhánh từ chối), `collect-logs.sh`, `compose.sh` với `docker`/`rclone`/`curl` giả: validate tham số, chống tiêm lệnh qua `SSH_ORIGINAL_COMMAND`, deploy lần đầu, deploy khi postgres chưa chạy, lùi khi `up` hỏng, giữ N bản, không đẩy staging ra remote; YAML của workflow phân tích được.
- **Chưa kiểm**: `docker compose` thật (cú pháp `--wait`, `--profile edge`, `run --entrypoint tar`), `rclone` với Drive thật (scope `drive.file`, consent screen, crypt), `pg_dump`/`pg_restore` thật, `logrotate`, cron, workflow trên GitHub (build, SSH, duyệt tay), `shellcheck` và `actionlint` (không có trên máy này; nên chạy ở CI).
- **Bộ file compose** (đã có, #78): `compose.yml` + `compose.prod.yml` dùng chung; prod thêm `compose.edge.yml` (Caddy 80/443, subnet 172.28.0.0/24, thấy mạng và media của staging, `--profile edge`); staging thêm `compose.staging.yml` (mạng ngoài `vyc-staging`, volume `vyc-staging_media` ngoài, alias `backend-staging`/`frontend-staging`). `backup/common.sh` ghép đúng bộ cho từng môi trường. `compose.prod.yml` đọc `IMAGE_TAG` (bắt buộc) và `IMAGE_REPO` (mặc định `ghcr.io/kevindodv`). Dockerfile ở `deploy/backend.Dockerfile` (context `backend/`, kèm `--build-context deploy=deploy` để lấy `backend-entrypoint.sh`) và `deploy/frontend.Dockerfile` (context `frontend/`). Đã kiểm bằng `docker compose config` và `caddy validate` (CI job `infra`), chưa chạy container thật trên máy này.
