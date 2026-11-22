#!/bin/sh
# Chạy migrate rồi exec gunicorn (van-hanh.md mục 5). Migration chỉ thêm, nên mã cũ vẫn chạy được
# với schema mới (quay lui không cần lùi migration).
set -eu

python manage.py migrate --noinput

# Access log JSON một dòng, KHÔNG có IP, X-Forwarded-For hay cookie (van-hanh.md mục 7): %(U)s là
# đường dẫn không kèm query; %(M)s là thời gian xử lý (ms).
ACCESS_LOG_FORMAT='{"ts":"%(t)s","method":"%(m)s","path":"%(U)s","status":%(s)s,"bytes":%(B)s,"ms":%(M)s}'

exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers "${WEB_CONCURRENCY:-3}" \
  --max-requests 1000 --max-requests-jitter 100 \
  --worker-tmp-dir /dev/shm \
  --access-logfile - --error-logfile - \
  --access-logformat "$ACCESS_LOG_FORMAT"
