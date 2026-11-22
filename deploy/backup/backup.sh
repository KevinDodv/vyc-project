#!/usr/bin/env bash
# Sao lưu một môi trường: dump DB, media, đẩy ra Google Drive (rclone crypt, chỉ prod).
# van-hanh.md mục 6. Lỗi bất kỳ thì báo ALERT_WEBHOOK_URL và thoát mã khác 0.
set -euo pipefail

SCRIPT_NAME=backup.sh
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=common.sh
. "$HERE/common.sh"

usage() {
  cat <<'USAGE'
Cách dùng: backup.sh <prod|staging>

  1. pg_dump -Fc  -> $BACKUP_ROOT/<môi trường>/db-YYYYmmdd-HHMM.dump (kiểm bằng pg_restore --list)
  2. media, media-private -> bản sao $BACKUP_ROOT/<môi trường>/{media,media-private}/
  3. chỉ prod: đẩy dump và media lên $BACKUP_REMOTE (remote rclone kiểu crypt)
  4. giữ BACKUP_KEEP bản DB mới nhất (mặc định 30), cả cục bộ lẫn đích

staging chỉ giữ cục bộ, KHÔNG đẩy ra remote (dữ liệu giả, chỉ để thử quy trình).
Đọc cấu hình từ /opt/vyc/.env.<môi trường> (POSTGRES_*, BACKUP_REMOTE, BACKUP_KEEP,
ALERT_WEBHOOK_URL, RCLONE_*). Mặc định: BACKUP_ROOT=/var/backups/vyc.
USAGE
}

case "${1:-}" in
  -h | --help) usage; exit 0 ;;
  "") usage; exit 2 ;;
esac
[ "$#" -eq 1 ] || { usage; exit 2; }

vyc_select_env "$1"
umask 077
STEP="khởi tạo"
DEST=""
TMP_FILES=()

cleanup() {
  local rc=$?
  local f
  for f in "${TMP_FILES[@]:-}"; do [ -n "$f" ] && rm -rf -- "$f"; done
  if [ "$rc" -ne 0 ]; then
    log "THẤT BẠI ở bước: $STEP"
    vyc_alert "sao lưu lỗi ở bước: $STEP"
  fi
}
trap cleanup EXIT

vyc_lock "backup-$ENV_NAME" 600

PGUSER="$(env_get POSTGRES_USER vyc)"
PGDB="$(env_get POSTGRES_DB vyc)"
KEEP="$(env_get BACKUP_KEEP 30)"
[[ "$KEEP" =~ ^[0-9]+$ ]] && [ "$KEEP" -ge 1 ] || die "BACKUP_KEEP phải là số nguyên >= 1 (nhận: '$KEEP')"
REMOTE=""
if [ "$ENV_NAME" = prod ]; then
  REMOTE="$(env_get BACKUP_REMOTE)"
  [ -n "$REMOTE" ] || die "prod cần BACKUP_REMOTE trong $ENV_FILE (vd vyc-crypt:)"
  case "$REMOTE" in *: | */) ;; *) die "BACKUP_REMOTE phải kết thúc bằng ':' hoặc '/' (vd vyc-crypt: hoặc vyc-crypt:backups/), nhận '$REMOTE'" ;; esac
  command -v rclone >/dev/null 2>&1 || die "chưa cài rclone"
  vyc_export_rclone_env
fi

DEST="$BACKUP_ROOT/$ENV_NAME"
mkdir -p "$DEST"
chmod 700 "$BACKUP_ROOT" "$DEST" 2>/dev/null || true

# --- 1. DB ---
STEP="pg_dump"
stamp="$(date +%Y%m%d-%H%M)"
dump="$DEST/db-$stamp.dump"
part="$dump.part"
TMP_FILES+=("$part")
"${COMPOSE[@]}" exec -T postgres pg_dump -Fc -U "$PGUSER" "$PGDB" >"$part"
[ -s "$part" ] || die "file dump rỗng"
STEP="kiểm dump bằng pg_restore --list"
"${COMPOSE[@]}" exec -T postgres pg_restore --list <"$part" >/dev/null
mv -f "$part" "$dump"
dump_bytes="$(wc -c <"$dump" | tr -d ' ')"

# --- 2. media (bản sao cục bộ: giải tar vào thư mục tạm rồi đổi chỗ) ---
# Đọc qua một container backend dùng một lần để không cần quyền vào /var/lib/docker.
mirror_volume() {
  local label="$1" container_dir="$2" target tmpdir
  target="$DEST/$label"
  tmpdir="$DEST/.$label.new"
  rm -rf -- "$tmpdir"
  mkdir -p "$tmpdir"
  TMP_FILES+=("$tmpdir")
  "${COMPOSE[@]}" run --rm --no-deps -T --entrypoint tar backend -C "$container_dir" -cf - . | tar -C "$tmpdir" -xf -
  rm -rf -- "$target"
  mv -- "$tmpdir" "$target"
}
STEP="sao chép media"
mirror_volume media /data/media
STEP="sao chép media-private"
mirror_volume media-private /data/media-private

# --- 3. đẩy ra ngoài VPS (chỉ prod) ---
pushed=false
if [ "$ENV_NAME" = prod ]; then
  STEP="rclone copy dump"
  rclone copy "$dump" "$REMOTE"
  STEP="rclone sync media"
  rclone sync "$DEST/media" "${REMOTE}media"
  STEP="rclone sync media-private"
  rclone sync "$DEST/media-private" "${REMOTE}media-private"
  pushed=true
fi

# --- 4. giữ KEEP bản DB mới nhất ---
STEP="xoá bản DB cũ cục bộ"
# Tên có dấu thời gian nên sắp theo tên = sắp theo thời gian.
mapfile -t local_dumps < <(cd "$DEST" && ls -1 -- db-*.dump 2>/dev/null | sort)
if [ "${#local_dumps[@]}" -gt "$KEEP" ]; then
  for f in "${local_dumps[@]:0:${#local_dumps[@]}-KEEP}"; do rm -f -- "$DEST/$f"; done
fi
if [ "$pushed" = true ]; then
  STEP="xoá bản DB cũ trên remote"
  mapfile -t remote_dumps < <(rclone lsf --files-only --include 'db-*.dump' "$REMOTE" | sort)
  if [ "${#remote_dumps[@]}" -gt "$KEEP" ]; then
    for f in "${remote_dumps[@]:0:${#remote_dumps[@]}-KEEP}"; do rclone deletefile "${REMOTE}${f}"; done
  fi
fi

STEP="xong"
printf '{"ts":"%s","event":"backup","env":"%s","file":"%s","bytes":%s,"remote":%s}\n' \
  "$(date '+%Y-%m-%dT%H:%M:%S%z')" "$ENV_NAME" "$(basename "$dump")" "$dump_bytes" "$pushed"
