# API Conventions

- Prefix all routes with `/api/v1/`
- Return JSON by default
- Introduce auth before adding business modules
- Keep frontend API access behind a service layer
- Auth endpoints for the current milestone:
  - `POST /api/v1/auth/login/`
  - `GET /api/v1/auth/me/`
  - `POST /api/v1/auth/logout/`
  - `GET /api/v1/protected/`
- Protected APIs use `Authorization: Bearer <token>`
