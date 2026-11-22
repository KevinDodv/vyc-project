# Image frontend: Astro SSR, adapter Node standalone (van-hanh.md mục 2).
# Build: context = frontend/. Biến runtime (API_INTERNAL_URL, SITE_URL, GTM_ID) đọc lúc chạy
# nên một image dùng cho cả staging và prod (frontend-seo.md mục 5.1).
ARG NODE_IMAGE=node:24-alpine

FROM ${NODE_IMAGE} AS base
# Phiên bản pnpm khớp lockfile v9 và bản dùng ở CI (.github/workflows/ci.yml).
ARG PNPM_VERSION=12.21.0
RUN npm install --global "pnpm@${PNPM_VERSION}"
WORKDIR /app

FROM base AS deps
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

FROM deps AS build
COPY . .
RUN pnpm build

FROM base AS prod-deps
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile --prod

FROM ${NODE_IMAGE} AS runtime
ENV NODE_ENV=production \
    HOST=0.0.0.0 \
    PORT=4321
WORKDIR /app
COPY --from=prod-deps --chown=node:node /app/node_modules ./node_modules
COPY --from=build --chown=node:node /app/dist ./dist
COPY --chown=node:node package.json ./
USER node
EXPOSE 4321
CMD ["node", "dist/server/entry.mjs"]
