#!/usr/bin/env bash
# Dựng/dọn stack CI (compose.ci.yml) và nạp dữ liệu seed cho job `lighthouse`.
#   deploy/ci/stack.sh up      build image, chạy stack, tạo OWNER và seed, in sẵn thông tin đăng nhập vào $GITHUB_ENV
#   deploy/ci/stack.sh logs    in log các container (khi job đỏ)
#   deploy/ci/stack.sh down    dừng và xoá volume (chỉ project vyc-ci)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
COMPOSE=(docker compose --profile edge -p vyc-ci
  --env-file "$ROOT/deploy/env/dev-defaults" --env-file "$ROOT/deploy/env/ci-defaults"
  -f "$ROOT/deploy/compose.yml" -f "$ROOT/deploy/compose.prod.yml" -f "$ROOT/deploy/compose.ci.yml")

case "${1:-}" in
  up)
    "${COMPOSE[@]}" up -d --build --wait --wait-timeout 240
    # Mật khẩu sinh mỗi lần chạy, không nằm trong repo; chỉ ghi vào biến môi trường của các bước sau.
    password="Ci-$(head -c 24 /dev/urandom | base64 | tr -dc 'A-Za-z0-9' | head -c 20)"
    echo "::add-mask::$password"
    OWNER_PASSWORD="$password" "${COMPOSE[@]}" exec -T -e OWNER_PASSWORD backend \
      python manage.py create_owner --username e2e-owner
    "${COMPOSE[@]}" exec -T backend python manage.py shell < "$ROOT/deploy/ci/seed_catalog.py"
    if [ -n "${GITHUB_ENV:-}" ]; then
      {
        echo "E2E_OWNER_USERNAME=e2e-owner"
        echo "E2E_OWNER_PASSWORD=$password"
      } >> "$GITHUB_ENV"
    fi
    ;;
  logs) "${COMPOSE[@]}" logs --no-color --timestamps ;;
  down) "${COMPOSE[@]}" down -v --remove-orphans ;;
  *) echo "Cách dùng: stack.sh up|logs|down" >&2; exit 2 ;;
esac
