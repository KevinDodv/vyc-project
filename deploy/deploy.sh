#!/usr/bin/env bash
# Deploy một môi trường trên VPS: backup, pull image, up, chờ healthcheck, smoke test, tự lùi.
# van-hanh.md mục 9.2. Chạy qua SSH với `command="/opt/vyc/deploy/deploy.sh <prod|staging>"`
# trong authorized_keys; tag/sha do client gửi nằm trong SSH_ORIGINAL_COMMAND (dữ liệu KHÔNG tin cậy).
set -euo pipefail

SCRIPT_NAME=deploy.sh
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=backup/common.sh
. "$HERE/backup/common.sh"

usage() {
  cat <<'USAGE'
Cách dùng:
  deploy.sh <prod|staging> [<tag>] [--no-sync]     (chạy tay trên VPS)
  ssh deploy@vps <tag>                              (qua khoá có command=, tag là đối số duy nhất)

<tag> là sha commit (hex 7-40 ký tự) hoặc tag phát hành vX.Y.Z. Khác mẫu này thì từ chối.
Khi chạy qua SSH, chỉ SSH_ORIGINAL_COMMAND được dùng làm tag và phải đúng MỘT từ.

Các bước: khoá -> đồng bộ git tới <tag> -> backup (trước deploy) -> pull -> up -d --wait
-> smoke test -> ghi tag chạy tốt. Hỏng sau khi pull thì đưa về tag chạy tốt gần nhất
(file /opt/vyc/.last-good-tag.<môi trường>). Quay lui tay: chạy lại với tag cũ.

  --no-sync   không git fetch/checkout (chỉ khi chạy tay và đã đặt sẵn mã nguồn đúng bản)
Mặc định: VYC_ROOT=/opt/vyc.
USAGE
}

TAG_RE_SHA='^[0-9a-f]{7,40}$'
TAG_RE_REL='^v[0-9]+\.[0-9]+\.[0-9]+$'

valid_tag() { [[ "$1" =~ $TAG_RE_SHA ]] || [[ "$1" =~ $TAG_RE_REL ]]; }

# Mem trống (MB) từ /proc/meminfo; in rỗng nếu không đọc được.
mem_available_mb() {
  awk '/^MemAvailable:/ {printf "%d", $2/1024}' /proc/meminfo 2>/dev/null || true
}

# Đồng bộ mã nguồn deploy/ (compose, Caddyfile, script) về đúng bản của tag.
git_sync() {
  local ref="$1"
  [ -d "$VYC_ROOT/.git" ] || die "$VYC_ROOT không phải bản clone git (xem deploy/README.md mục 3)"
  local commit
  # Lấy rõ origin/main (không chỉ tag) để kiểm tra bên dưới dựa trên bản mới nhất.
  git -C "$VYC_ROOT" fetch --quiet --tags origin '+refs/heads/main:refs/remotes/origin/main' || die "git fetch lỗi"
  commit="$(git -C "$VYC_ROOT" rev-parse --verify --quiet "${ref}^{commit}")" || die "không thấy '$ref' trong repo"
  # Chỉ nhận commit nằm trên origin/main. Việc này chạy bằng bản deploy.sh ĐANG có trên VPS, trước khi
  # checkout bất cứ thứ gì, nên mã từ nhánh khác (compose.yml, backup.sh độc) không bao giờ được chạy
  # với quyền nhóm docker (tương đương root, cùng VPS với prod).
  git -C "$VYC_ROOT" merge-base --is-ancestor "$commit" refs/remotes/origin/main ||
    die "commit $commit không nằm trên origin/main, từ chối deploy"
  git -C "$VYC_ROOT" -c advice.detachedHead=false checkout --detach --quiet "$commit" ||
    die "git checkout $ref lỗi (VPS có sửa tay trong $VYC_ROOT? mọi thay đổi phải qua repo)"
}

# Sao lưu trước deploy. Không để set -e làm dừng deploy chỉ vì postgres chưa chạy (finding #788).
pre_deploy_backup() {
  local prev="$1" first_deploy=false
  [ -s "$LAST_GOOD_FILE" ] || first_deploy=true

  if ! postgres_running; then
    if [ "$first_deploy" = true ]; then
      log "Lần đầu (chưa có tag chạy tốt) và postgres chưa chạy: chưa có dữ liệu để sao lưu, bỏ qua backup."
      return 0
    fi
    log "postgres chưa chạy: bật lên trước khi sao lưu..."
    if ! "${COMPOSE[@]}" up -d --wait postgres; then
      if [ "$ENV_NAME" = prod ]; then
        vyc_alert "deploy dừng: không bật được postgres để sao lưu trước deploy"
        die "không bật được postgres; không deploy prod khi chưa sao lưu được"
      fi
      log "cảnh báo: không bật được postgres, staging chỉ có dữ liệu giả nên bỏ qua backup."
      return 0
    fi
  fi

  # backup dùng image đang chạy (tag trước), chưa đụng tới image mới.
  if IMAGE_TAG="${prev:-$IMAGE_TAG}" bash "$HERE/backup/backup.sh" "$ENV_NAME"; then
    return 0
  fi
  if [ "$ENV_NAME" = prod ]; then
    vyc_alert "deploy dừng: backup trước deploy lỗi"
    die "backup trước deploy lỗi; dừng, chưa đụng gì tới prod"
  fi
  log "cảnh báo: backup staging lỗi, vẫn deploy (dữ liệu giả)."
}

smoke_test() {
  local url
  if [ "$ENV_NAME" = prod ]; then
    url="$(env_get SITE_ORIGIN)"
    [ -n "$url" ] || { log "SITE_ORIGIN trống, không kiểm được HTTPS công khai"; return 1; }
    for _ in 1 2 3 4 5 6 7 8 9 10 11 12; do
      if curl -fsS --max-time 10 -o /dev/null "${url%/}/api/health"; then
        log "Smoke test ${url%/}/api/health: OK"
        return 0
      fi
      sleep 5
    done
    log "Smoke test ${url%/}/api/health: lỗi sau 12 lần thử"
    return 1
  fi
  # staging có basic auth ở Caddy nên không gọi công khai; `up --wait` đã kiểm healthcheck
  # /api/health của backend và /healthz của frontend trong mạng compose.
  log "Staging: healthcheck compose đã đạt, bỏ qua smoke test công khai (có basic auth)."
}

rollback() {
  local prev="$1"
  if [ -z "$prev" ]; then
    log "Không có tag chạy tốt trước đó để lùi (deploy lần đầu). Giữ nguyên trạng thái để chẩn đoán."
    return 1
  fi
  log "Tự lùi về $prev..."
  git -C "$VYC_ROOT" -c advice.detachedHead=false checkout --detach --quiet "$prev" 2>/dev/null ||
    log "cảnh báo: không checkout lại được mã $prev, vẫn thử lùi image"
  IMAGE_TAG="$prev" "${COMPOSE[@]}" up -d --wait --wait-timeout 60 || return 1
}

main() {
  case "${1:-}" in
    -h | --help) usage; exit 0 ;;
    "") usage; exit 2 ;;
  esac
  local env_arg="$1" tag="" sync=true
  shift

  if [ -n "${SSH_ORIGINAL_COMMAND:-}" ]; then
    # Qua SSH: chỉ tin SSH_ORIGINAL_COMMAND, và nó phải là đúng một tag hợp lệ.
    tag="$SSH_ORIGINAL_COMMAND"
    valid_tag "$tag" || die "tham số không hợp lệ: cần đúng một sha hex 7-40 ký tự hoặc tag vX.Y.Z"
  else
    while [ "$#" -gt 0 ]; do
      case "$1" in
        --no-sync) sync=false ;;
        -h | --help) usage; exit 0 ;;
        -*) usage; die "tuỳ chọn lạ: $1" ;;
        *) [ -z "$tag" ] || die "chỉ nhận một tag"; tag="$1" ;;
      esac
      shift
    done
    [ -n "$tag" ] || { usage; exit 2; }
    valid_tag "$tag" || die "tag không hợp lệ: cần sha hex 7-40 ký tự hoặc vX.Y.Z"
  fi

  vyc_select_env "$env_arg"
  [ "$(env_get ENVIRONMENT)" = "$ENV_NAME" ] ||
    die "ENVIRONMENT trong $ENV_FILE ('$(env_get ENVIRONMENT)') không khớp '$ENV_NAME'"
  vyc_lock "deploy-$ENV_NAME" 0

  local prev=""
  if [ -s "$LAST_GOOD_FILE" ]; then
    prev="$(cat "$LAST_GOOD_FILE")"
    valid_tag "$prev" || { log "cảnh báo: $LAST_GOOD_FILE chứa giá trị lạ, bỏ qua"; prev=""; }
  fi

  # Staging cùng VPS: kiểm RAM trước khi bật từ trạng thái tắt (van-hanh.md 2.1).
  if [ "$ENV_NAME" = staging ] && ! postgres_running; then
    local avail
    avail="$(mem_available_mb)"
    if [ -n "$avail" ] && [ "$avail" -lt 1200 ]; then
      die "RAM trống ${avail} MB < 1200 MB: không bật staging (xem van-hanh.md 2.1)"
    fi
  fi

  log "Deploy $ENV_NAME tag=$tag (trước đó: ${prev:-chưa có})"

  if [ "$sync" = true ]; then git_sync "$tag"; fi

  export IMAGE_TAG="$tag"
  pre_deploy_backup "$prev"

  log "Pull image..."
  if ! "${COMPOSE[@]}" pull backend frontend; then
    vyc_alert "deploy $tag lỗi: không pull được image (chưa đổi gì trên server)"
    die "pull lỗi, chưa đổi gì trên server"
  fi

  log "Khởi động (up -d --wait)..."
  if "${COMPOSE[@]}" up -d --wait --wait-timeout 180 && smoke_test; then
    write_atomic "$LAST_GOOD_FILE" "$tag"
    log "Deploy $ENV_NAME $tag: THÀNH CÔNG"
    return 0
  fi

  log "Deploy $tag THẤT BẠI"
  if rollback "$prev"; then
    vyc_alert "deploy $tag lỗi, đã tự lùi về $prev"
    die "deploy $tag lỗi; đã lùi về $prev"
  fi
  vyc_alert "deploy $tag lỗi và KHÔNG lùi được (tag trước: ${prev:-không có}); cần xử lý tay"
  die "deploy $tag lỗi và không lùi được"
}

# Bọc toàn bộ trong hàm và thoát ngay: bash đọc script theo từng đoạn, mà git_sync có thể
# thay chính file này giữa chừng. Parse xong hàm rồi mới chạy thì an toàn.
main "$@"
exit $?
