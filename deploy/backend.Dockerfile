# Image backend (docs/kien-truc/van-hanh.md mục 2, 5).
# Build: context = backend/, kèm build context phụ `deploy` (thư mục deploy/) để lấy entrypoint:
#   docker buildx build -f deploy/backend.Dockerfile --build-context deploy=deploy backend
# (compose.prod.yml và deploy.yml đã khai sẵn). Ghim phiên bản: cập nhật có chủ đích, ghi vào PR.
FROM ghcr.io/astral-sh/uv:0.13.9 AS uv

FROM python:3.13-slim-bookworm AS build
COPY --from=uv /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/venv
WORKDIR /app
# Chỉ phụ thuộc production; wheel có sẵn cho psycopg[binary], pillow, argon2 nên không cần trình biên dịch.
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-dev --no-install-project

FROM python:3.13-slim-bookworm AS runtime
ENV PATH="/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app
# User không phải root; thư mục media tạo sẵn để volume đặt tên kế thừa quyền sở hữu khi gắn lần đầu.
RUN useradd --system --uid 10001 --create-home --home-dir /home/vyc vyc \
    && mkdir -p /data/media /data/media-private \
    && chown -R vyc:vyc /data
WORKDIR /app
COPY --from=build /venv /venv
COPY --chown=vyc:vyc . /app
COPY --from=deploy --chmod=755 backend-entrypoint.sh /usr/local/bin/backend-entrypoint.sh
USER vyc
EXPOSE 8000
ENTRYPOINT ["backend-entrypoint.sh"]
