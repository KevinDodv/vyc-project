#!/usr/bin/env bash
# Gom log container ra file trên host để giữ 30 ngày (van-hanh.md mục 7).
# Chạy mỗi giờ từ cron. Không trùng/sót: đọc mốc lần trước, ghi xong mới cập nhật mốc.
set -euo pipefail

SCRIPT_NAME=collect-logs.sh
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=common.sh
. "$HERE/common.sh"

usage() {
  cat <<'USAGE'
Cách dùng: collect-logs.sh <prod|staging>

Nối log từng dịch vụ vào $LOG_DIR/<dịch vụ>.jsonl (prod) hoặc staging-<dịch vụ>.jsonl.
Mốc thời gian nằm ở $STATE_DIR/logs.since/. Dịch vụ không có container (staging đang tắt)
thì bỏ qua, không lỗi. Mặc định: LOG_DIR=/var/log/vyc, STATE_DIR=/var/lib/vyc.
USAGE
}

case "${1:-}" in
  -h | --help) usage; exit 0 ;;
  "") usage; exit 2 ;;
esac

vyc_select_env "$1"
umask 027
SINCE_DIR="$STATE_DIR/logs.since"
mkdir -p "$LOG_DIR" "$SINCE_DIR"
vyc_lock "collect-logs-$ENV_NAME" 60

if [ "$ENV_NAME" = prod ]; then
  services=(backend frontend postgres caddy)
  prefix=""
else
  services=(backend frontend postgres)
  prefix="staging-"
fi

until_ts="$(date +%s)" # cắt tròn tới giây
failed=0
for svc in "${services[@]}"; do
  name="${prefix}${svc}"
  cid="$("${COMPOSE[@]}" ps -aq "$svc" 2>/dev/null | head -n 1 || true)"
  [ -n "$cid" ] || continue

  since_file="$SINCE_DIR/$name"
  if [ -s "$since_file" ] && [[ "$(cat "$since_file")" =~ ^[0-9]+$ ]]; then
    since_ts="$(cat "$since_file")"
  else
    since_ts=$((until_ts - 3600)) # lần đầu: lấy 1 giờ
  fi
  [ "$since_ts" -lt "$until_ts" ] || continue

  tmp="$(mktemp "$LOG_DIR/.collect.XXXXXX")"
  # docker logs ghi stdout của container ra stdout và stderr của container ra stderr: gộp cả hai.
  if docker logs --timestamps --since "$since_ts" --until "$until_ts" "$cid" >"$tmp" 2>&1; then
    cat "$tmp" >>"$LOG_DIR/$name.jsonl"
    write_atomic "$since_file" "$until_ts" # chỉ cập nhật mốc khi đã ghi xong
  else
    log "docker logs $name lỗi, giữ nguyên mốc để lần sau lấy lại"
    failed=1
  fi
  rm -f "$tmp"
done

[ "$failed" -eq 0 ] || exit 1
