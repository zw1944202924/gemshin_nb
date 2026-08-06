#!/bin/sh
set -eu

ENV_FILE="${ENV_FILE:-.env.production}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
export GEMSHIN_ENV_FILE="$ENV_FILE"

if [ ! -f "$ENV_FILE" ]; then
  echo "Missing $ENV_FILE. Copy .env.production.example and fill production secrets first." >&2
  exit 1
fi

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" build
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d mysql redis
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d api web
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec api python manage.py migrate
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec api python manage.py seed_modules
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec api python manage.py seed_roles
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec api python manage.py collectstatic --noinput
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" ps
