# shellcheck shell=bash
# Hàm dùng chung cho deploy.sh, backup.sh, restore.sh, collect-logs.sh, compose.sh.
# File này được `source`, không chạy trực tiếp. Không in secret ra log.
# Căn cứ: docs/kien-truc/van-hanh.md mục 2.2, 4, 6, 7, 9.2.

# Gốc cài đặt trên VPS và các thư mục dữ liệu. Chỉ đổi khi thử cục bộ; cron và
# `command=` trong authorized_keys không truyền biến môi trường nên luôn là mặc định.
VYC_ROOT="${VYC_ROOT:-/opt/vyc}"
BACKUP_ROOT="${BACKUP_ROOT:-/var/backups/vyc}"
LOG_DIR="${LOG_DIR:-/var/log/vyc}"
STATE_DIR="${STATE_DIR:-/var/lib/vyc}"

log() { printf '%s [%s] %s\n' "$(date '+%Y-%m-%dT%H:%M:%S%z')" "${SCRIPT_NAME:-vyc}" "$*" >&2; }
die() { log "LỖI: $*"; exit 1; }

# Chọn môi trường. Chỉ nhận đúng `prod` hoặc `staging`, không có mặc định.
# Gán: ENV_NAME, PROJECT, ENV_FILE, COMPOSE (mảng), LAST_GOOD_FILE.
vyc_select_env() {
  case "${1:-}" in
    prod) ENV_NAME=prod PROJECT=vyc ;;
    staging) ENV_NAME=staging PROJECT=vyc-staging ;;
    *) die "môi trường phải là 'prod' hoặc 'staging' (nhận: '${1:-}')" ;;
  esac
  ENV_FILE="$VYC_ROOT/.env.$ENV_NAME"
  LAST_GOOD_FILE="$VYC_ROOT/.last-good-tag.$ENV_NAME"
  [ -r "$ENV_FILE" ] || die "không đọc được $ENV_FILE"

  # compose.prod.yml đọc IMAGE_TAG để chọn image. Các lệnh không đổi image (exec, ps, logs)
  # vẫn cần biến này để compose nội suy được, nên mặc định lấy tag chạy tốt gần nhất.
  if [ -z "${IMAGE_TAG:-}" ]; then
    IMAGE_TAG="$(cat "$LAST_GOOD_FILE" 2>/dev/null || true)"
    IMAGE_TAG="${IMAGE_TAG:-none}"
  fi
  export IMAGE_TAG

  # Phần riêng của từng môi trường: prod có Caddy + subnet 172.28 (compose.edge.yml, profile `edge`);
  # staging dùng mạng ngoài vyc-staging, không có Caddy riêng (compose.staging.yml).
  local deploy_dir="$VYC_ROOT/deploy"
  if [ "$ENV_NAME" = prod ]; then
    COMPOSE=(docker compose --profile edge -p "$PROJECT" --env-file "$ENV_FILE"
      -f "$deploy_dir/compose.yml" -f "$deploy_dir/compose.prod.yml" -f "$deploy_dir/compose.edge.yml")
  else
    COMPOSE=(docker compose -p "$PROJECT" --env-file "$ENV_FILE"
      -f "$deploy_dir/compose.yml" -f "$deploy_dir/compose.prod.yml" -f "$deploy_dir/compose.staging.yml")
  fi
}

# Đọc một biến từ env-file mà KHÔNG `source` (giá trị có thể chứa $ hoặc ký tự đặc biệt,
# ví dụ hash bcrypt). Dòng cuối thắng; bỏ cặp nháy bao quanh. In giá trị hoặc mặc định.
env_get() {
  local name="$1" default="${2:-}" line value
  line="$(grep -E "^${name}=" "$ENV_FILE" | tail -n 1 || true)"
  if [ -z "$line" ]; then
    printf '%s' "$default"
    return 0
  fi
  value="${line#*=}"
  case "$value" in
    \"*\") value="${value#\"}"; value="${value%\"}" ;;
    \'*\') value="${value#\'}"; value="${value%\'}" ;;
  esac
  printf '%s' "$value"
}

# rclone đọc cấu hình từ biến RCLONE_* (kể cả RCLONE_CONFIG trỏ tới rclone.conf quyền 600).
# Nạp các dòng đó từ env-file vào môi trường của tiến trình này.
vyc_export_rclone_env() {
  local line name value
  while IFS= read -r line; do
    name="${line%%=*}"
    case "$name" in
      RCLONE_[A-Za-z0-9_]*) ;;
      *) continue ;;
    esac
    value="$(env_get "$name")"
    export "$name=$value"
  done < <(grep -E '^RCLONE_[A-Za-z0-9_]*=' "$ENV_FILE" || true)
}

# Báo lỗi lên kênh Qwork (ALERT_WEBHOOK_URL trong env-file). Không bao giờ làm script hỏng thêm.
# URL webhook là bí mật: đưa qua stdin của curl (-K -) để không lộ trong danh sách tiến trình.
vyc_alert() {
  local text="$1" url payload
  url="$(env_get ALERT_WEBHOOK_URL)"
  [ -n "$url" ] || return 0
  command -v curl >/dev/null 2>&1 || return 0
  text="${text//\\/\\\\}"
  text="${text//\"/\\\"}"
  payload="{\"text\":\"[vyc/$ENV_NAME] $text\"}"
  printf 'url = "%s"\n' "$url" |
    curl -fsS --max-time 10 -K - -H 'Content-Type: application/json' -d "$payload" >/dev/null 2>&1 || true
}

# Khoá để hai lần chạy cùng loại không giẫm lên nhau. Giữ tới khi tiến trình thoát.
# Dùng: vyc_lock <tên> <giây chờ>. Không có flock thì cảnh báo và chạy tiếp.
vyc_lock() {
  local name="$1" wait="${2:-0}" file
  command -v flock >/dev/null 2>&1 || { log "cảnh báo: không có flock, bỏ qua khoá '$name'"; return 0; }
  mkdir -p "$STATE_DIR" 2>/dev/null || die "không tạo được $STATE_DIR"
  file="$STATE_DIR/$name.lock"
  exec 9>"$file" || die "không mở được $file"
  flock -w "$wait" 9 || die "đang có lần chạy '$name' khác, thử lại sau"
}

# Ghi file nguyên tử: ghi ra file tạm cùng thư mục rồi đổi tên.
write_atomic() {
  local dest="$1" content="$2" tmp
  tmp="$(mktemp "$dest.XXXXXX")"
  printf '%s\n' "$content" >"$tmp"
  mv -f "$tmp" "$dest"
}

# Postgres trong compose đang chạy?
postgres_running() {
  "${COMPOSE[@]}" ps --status running --services 2>/dev/null | grep -qx postgres
}
