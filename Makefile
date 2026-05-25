up:
	docker compose up -d

down:
	docker compose down

api-dev:
	cd apps/api && python3 manage.py runserver 0.0.0.0:8000

web-dev:
	cd apps/web && pnpm install && pnpm dev
