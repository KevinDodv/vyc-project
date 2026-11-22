# Lớp mỏng gọi uv / pnpm / docker compose (docs/kien-truc/van-hanh.md mục 8).
# Chạy trong WSL2/Git Bash hoặc Linux/macOS.
COMPOSE_DEV = docker compose --env-file deploy/env/dev-defaults -f deploy/compose.yml -f deploy/compose.dev.yml
# Chỉ để build image: nạp dev-defaults cho các biến bắt buộc của compose.yml, không chạy gì.
COMPOSE_PROD = IMAGE_TAG=$(or $(IMAGE_TAG),local) docker compose --env-file deploy/env/dev-defaults -f deploy/compose.yml -f deploy/compose.prod.yml
# Lệnh backend chạy trực tiếp (không qua --env-file): settings mặc định là prod nên đặt dev ở đây.
BE_DEV = ENVIRONMENT=dev

.PHONY: dev down reset-db install makemigrations migrate seed test-be test-fe \
	lint-be lint-fe fmt-be build-fe budget image check

dev:
	$(COMPOSE_DEV) up --build

down:
	$(COMPOSE_DEV) down

# Chỉ dev: xoá volume pgdata-dev, có hỏi xác nhận.
reset-db:
	@printf 'Xoá toàn bộ dữ liệu DB dev? [y/N] ' && read ans && [ "$$ans" = "y" ]
	$(COMPOSE_DEV) down -v

install:
	cd backend && uv sync --frozen
	cd frontend && pnpm install --frozen-lockfile

makemigrations:
	cd backend && $(BE_DEV) uv run python manage.py makemigrations

migrate:
	cd backend && $(BE_DEV) uv run python manage.py migrate

seed:
	cd backend && $(BE_DEV) uv run python manage.py seed_dev

test-be:
	cd backend && $(BE_DEV) uv run pytest

test-fe:
	cd frontend && pnpm test

lint-be:
	cd backend && uv run ruff check . && uv run ruff format --check . && $(BE_DEV) uv run mypy . && uv run lint-imports

fmt-be:
	cd backend && uv run ruff check --fix . && uv run ruff format .

lint-fe:
	cd frontend && pnpm check

build-fe:
	cd frontend && pnpm build

budget:
	node scripts/check-budget.mjs

image:
	$(COMPOSE_PROD) build

check: lint-be lint-fe test-be test-fe build-fe
