#!/bin/sh
set -eu

ENV_FILE="${ENV_FILE:-.env.dev}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.dev.yml}"
PROJECT_NAME="${COMPOSE_PROJECT_NAME:-gemshin-nb-test}"
STANDARD_DEPLOY_DIR="${STANDARD_DEPLOY_DIR:-/home/admin/gemshin_nb-test/app}"
export GEMSHIN_ENV_FILE="$ENV_FILE"

if [ ! -f "$ENV_FILE" ]; then
  echo "Missing $ENV_FILE. Copy .env.dev.example and fill dev-only secrets first." >&2
  exit 1
fi

if [ "$(pwd)" != "$STANDARD_DEPLOY_DIR" ]; then
  echo "Warning: standard gemshin_nb test deploy directory is $STANDARD_DEPLOY_DIR; current directory is $(pwd)." >&2
fi

docker volume inspect gemshin-dev_gemshin_dev_mysql_data >/dev/null 2>&1 || docker volume create gemshin-dev_gemshin_dev_mysql_data >/dev/null
docker volume inspect gemshin-dev_gemshin_dev_redis_data >/dev/null 2>&1 || docker volume create gemshin-dev_gemshin_dev_redis_data >/dev/null

docker compose --project-name "$PROJECT_NAME" --env-file "$ENV_FILE" -f "$COMPOSE_FILE" build
docker compose --project-name "$PROJECT_NAME" --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d mysql redis
docker compose --project-name "$PROJECT_NAME" --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d api web
docker compose --project-name "$PROJECT_NAME" --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec api python manage.py migrate
docker compose --project-name "$PROJECT_NAME" --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec api python manage.py seed_modules
docker compose --project-name "$PROJECT_NAME" --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec api python manage.py seed_roles
docker compose --project-name "$PROJECT_NAME" --env-file "$ENV_FILE" -f "$COMPOSE_FILE" ps

curl -fsS http://127.0.0.1:8101/api/v1/health/ >/dev/null
echo "gemshin_nb test health check passed"
