# Local Setup

## Prerequisites

- Python 3.10+
- Node.js 20+
- pnpm
- Docker Desktop or Docker Engine with Compose

## API Setup

1. Copy `.env.example` to `.env`
2. Start MySQL and Redis from the repository root:

```bash
docker compose up -d
```

If your local `mysql_data` volume was initialized by a different MySQL major version, recreate the volume before switching versions. This repository defaults to MySQL `8.4`; do not downgrade an existing `8.4` data volume to `8.0`.

3. Create a virtual environment and install Python dependencies:

```bash
cd apps/api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

4. Apply Django migrations:

```bash
python manage.py migrate
```

5. Start the API server:

```bash
python manage.py runserver 0.0.0.0:8000
```

6. Verify MySQL and Redis connectivity through the health endpoint:

```bash
curl http://127.0.0.1:8000/api/v1/health/
```

Expected response:

```json
{"status":"ok","service":"api","checks":{"mysql":"ok","redis":"ok"}}
```

If MySQL or Redis is unavailable, the endpoint returns HTTP `503` with the failing dependency marked as `fail`.

## Web Setup

```bash
cd apps/web
pnpm install
pnpm dev
```
