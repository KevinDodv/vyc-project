#!/usr/bin/env bash
# Khôi phục DB (và media nếu có) của một môi trường từ file dump. van-hanh.md mục 6.
# XOÁ DB hiện tại: luôn chụp một bản "prerestore" trước, hỏi xác nhận, prod cần --yes-prod.
set -euo pipefail

SCRIPT_NAME=restore.sh
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=common.sh
. "$HERE/common.sh"

usage() {
  cat <<'USAGE'
Cách dùng: restore.sh <prod|staging> </đường/dẫn/tuyệt/đối/file.dump> [tuỳ chọn]

Tuỳ chọn:
  --yes-prod                 bắt buộc khi môi trường là prod
  --media-dir <thư mục>      chép lại media công khai từ thư mục này vào volume media
  --media-private-dir <thư mục>  chép lại tệp nội bộ vào volume media-private
  --no-safety-dump           bỏ bản prerestore (chỉ khi DB hiện tại hỏng/không có)
  -h, --help                 in trợ giúp

Các bước: chụp prerestore -> dừng backend/frontend -> dropdb -> createdb -> pg_restore
-> (media) -> bật lại backend/frontend (migrate chạy lại, đưa schema về mới nhất).

Quy tắc:
  - Phải gõ lại đúng tên môi trường để xác nhận (cần terminal, không chạy được từ cron).
  - ENVIRONMENT trong /opt/vyc/.env.<môi trường> phải khớp tham số đầu.
  - Không restore dump của prod vào staging (staging chỉ có dữ liệu giả).
  - Dump trên Google Drive: tải về máy trước bằng `rclone copy "$BACKUP_REMOTE"db-<ngày>.dump /thư/mục/`.
USAGE
}

case "${1:-}" in
  -h | --help) usage; exit 0 ;;
  "") usage; exit 2 ;;
esac
[ "$#" -ge 2 ] || { usage; exit 2; }

env_arg="$1"
dump="$2"
shift 2
yes_prod=false
safety=true
media_dir=""
media_private_dir=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --yes-prod) yes_prod=true ;;
    --no-safety-dump) safety=false ;;
    --media-dir) [ "$#" -ge 2 ] || die "--media-dir cần một thư mục"; media_dir="$2"; shift ;;
    --media-private-dir) [ "$#" -ge 2 ] || die "--media-private-dir cần một thư mục"; media_private_dir="$2"; shift ;;
    -h | --help) usage; exit 0 ;;
    *) usage; die "tuỳ chọn lạ: $1" ;;
  esac
  shift
done

vyc_select_env "$env_arg"
umask 077

case "$dump" in /*) ;; *) die "file dump phải là đường dẫn tuyệt đối" ;; esac
[ -f "$dump" ] && [ -s "$dump" ] || die "không thấy file dump (hoặc rỗng): $dump"
for d in "$media_dir" "$media_private_dir"; do
  [ -z "$d" ] && continue
  case "$d" in /*) ;; *) die "thư mục media phải là đường dẫn tuyệt đối: $d" ;; esac
  [ -d "$d" ] || die "không thấy thư mục: $d"
done

[ "$(env_get ENVIRONMENT)" = "$ENV_NAME" ] ||
  die "ENVIRONMENT trong $ENV_FILE ('$(env_get ENVIRONMENT)') không khớp tham số '$ENV_NAME'"
if [ "$ENV_NAME" = prod ] && [ "$yes_prod" != true ]; then
  die "restore prod cần cờ --yes-prod"
fi
if [ "$ENV_NAME" = staging ]; then
  case "$dump" in
    "$BACKUP_ROOT"/prod/*) die "không restore dump của prod vào staging (staging chỉ dùng dữ liệu giả)" ;;
  esac
fi

PGUSER="$(env_get POSTGRES_USER vyc)"
PGDB="$(env_get POSTGRES_DB vyc)"

[ -t 0 ] || die "cần chạy trong terminal để xác nhận (không chạy được từ cron hay CI)"
log "Kiểm dump đọc được..."
"${COMPOSE[@]}" up -d --wait postgres
"${COMPOSE[@]}" exec -T postgres pg_restore --list <"$dump" >/dev/null || die "pg_restore --list không đọc được $dump"

printf 'Sẽ XOÁ DB "%s" của môi trường %s rồi nạp lại từ %s.\nGõ lại tên môi trường (%s) để tiếp tục: ' \
  "$PGDB" "$ENV_NAME" "$dump" "$ENV_NAME" >&2
read -r answer
[ "$answer" = "$ENV_NAME" ] || die "xác nhận không khớp, dừng"

vyc_lock "backup-$ENV_NAME" 600 # không chạy song song với sao lưu

if [ "$safety" = true ]; then
  mkdir -p "$BACKUP_ROOT/$ENV_NAME"
  chmod 700 "$BACKUP_ROOT" "$BACKUP_ROOT/$ENV_NAME" 2>/dev/null || true
  pre="$BACKUP_ROOT/$ENV_NAME/prerestore-$(date +%Y%m%d-%H%M%S).dump"
  log "Chụp DB hiện tại trước khi xoá: $pre"
  if ! "${COMPOSE[@]}" exec -T postgres pg_dump -Fc -U "$PGUSER" "$PGDB" >"$pre" || [ ! -s "$pre" ]; then
    rm -f -- "$pre"
    die "không chụp được bản prerestore; nếu DB hiện tại hỏng thì chạy lại với --no-safety-dump"
  fi
fi

restore_media() {
  local src="$1" container_dir="$2"
  [ -n "$src" ] || return 0
  log "Chép $src vào $container_dir"
  tar -C "$src" -cf - . | "${COMPOSE[@]}" run --rm --no-deps -T --entrypoint tar backend -C "$container_dir" -xf -
}

log "Dừng backend, frontend..."
"${COMPOSE[@]}" stop backend frontend
"${COMPOSE[@]}" exec -T postgres dropdb -U "$PGUSER" --if-exists "$PGDB"
"${COMPOSE[@]}" exec -T postgres createdb -U "$PGUSER" "$PGDB"

rc=0
"${COMPOSE[@]}" exec -T postgres pg_restore -U "$PGUSER" -d "$PGDB" --no-owner <"$dump" || rc=$?
if [ "$rc" -ne 0 ]; then
  log "pg_restore trả mã $rc (có thể chỉ là cảnh báo). Kiểm lại dữ liệu trước khi dùng; bản prerestore ở ${pre:-<không có>}"
fi

restore_media "$media_dir" /data/media
restore_media "$media_private_dir" /data/media-private

log "Bật lại backend, frontend (migrate chạy lại)..."
"${COMPOSE[@]}" up -d --wait backend frontend
log "Xong khôi phục $ENV_NAME từ $dump (pg_restore mã $rc)"
exit "$rc"
