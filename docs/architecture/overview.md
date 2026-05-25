# Architecture Overview

Current target stack:

- `apps/web`: Nuxt frontend
- `apps/api`: Django + DRF backend
- `mysql`: primary relational database
- `redis`: cache and async task foundation

First milestone:

- stand up web and api skeletons
- align environment variables
- keep API routes under `/api/v1/`
- add auth as the first end-to-end capability
