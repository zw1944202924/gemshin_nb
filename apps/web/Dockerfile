FROM node:20-alpine AS build

WORKDIR /app/apps/web

RUN corepack enable && corepack prepare pnpm@10.14.0 --activate

COPY apps/web/package.json ./package.json
RUN pnpm install

COPY apps/web /app/apps/web
RUN pnpm build

FROM node:20-alpine AS runtime

ENV NODE_ENV=production
ENV NITRO_HOST=0.0.0.0
ENV NITRO_PORT=3000

WORKDIR /app

COPY --from=build /app/apps/web/.output ./.output

EXPOSE 3000

CMD ["node", ".output/server/index.mjs"]
