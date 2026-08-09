#!/bin/sh
set -eu

ENV_FILE="${ENV_FILE:-.env.dev}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.dev.yml}"
PROJECT_NAME="${COMPOSE_PROJECT_NAME:-gemshin-dev}"
export GEMSHIN_ENV_FILE="$ENV_FILE"

if [ ! -f "$ENV_FILE" ]; then
  echo "Missing $ENV_FILE. Copy .env.dev.example and fill dev-only secrets first." >&2
  exit 1
fi

mkdir -p /opt/gemshin-dev/new-api/data /opt/gemshin-dev/new-api/logs

docker compose --project-name "$PROJECT_NAME" --env-file "$ENV_FILE" -f "$COMPOSE_FILE" build
docker compose --project-name "$PROJECT_NAME" --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d mysql redis newapi
docker compose --project-name "$PROJECT_NAME" --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d api web
docker compose --project-name "$PROJECT_NAME" --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec api python manage.py migrate
docker compose --project-name "$PROJECT_NAME" --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec api python manage.py seed_modules
docker compose --project-name "$PROJECT_NAME" --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec api python manage.py seed_roles
docker compose --project-name "$PROJECT_NAME" --env-file "$ENV_FILE" -f "$COMPOSE_FILE" ps

curl -fsS http://127.0.0.1:8101/api/v1/health/ >/dev/null
echo "gemshin-dev health check passed"
