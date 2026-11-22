#!/usr/bin/env bash
# Chạy `docker compose` đúng project, env-file và file compose của một môi trường.
# Dùng cho cron và thao tác tay để khỏi gõ dòng lệnh dài (van-hanh.md mục 2.1, 6).
set -euo pipefail

SCRIPT_NAME=compose.sh
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=common.sh
. "$HERE/common.sh"

usage() {
  cat <<'USAGE'
Cách dùng: compose.sh <prod|staging> <lệnh docker compose...>

Ví dụ:
  compose.sh prod ps
  compose.sh prod exec -T backend python manage.py purge_throttle
  compose.sh staging stop        # tắt staging, giữ volume (KHÔNG dùng down -v)

Biến tuỳ chọn: VYC_ROOT (mặc định /opt/vyc).
USAGE
}

case "${1:-}" in
  "" | -h | --help) usage; [ -n "${1:-}" ] && exit 0 || exit 2 ;;
esac
[ "$#" -ge 2 ] || { usage; exit 2; }

vyc_select_env "$1"
shift
exec "${COMPOSE[@]}" "$@"
