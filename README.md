# Pointify

A small app for weighing up pro/contra points on themes and sub-themes.

## Status

This repository is being restructured from an earlier prototype into a
frontend/backend split with Docker packaging and CI, following the scaffolding
conventions of [FinFlow](https://github.com/tosc2571/FinFlow). Details will be
filled in as each part lands.

## Stack

- **Backend:** FastAPI (Python), SQLAlchemy + Alembic, SQLite
- **Frontend:** Angular
- **Packaging:** Docker (single image, backend serves the built frontend)

## Docker

```
cp .env.example .env   # then set POINTIFY_SECRET_KEY (see the comment in .env.example)
docker compose -f docker-compose.yml -f docker-compose.build.yml up -d --build
```

This builds the image locally and starts it, storing data in `./data` (configurable via
`POINTIFY_DATA_LOCATION` in `.env`). To run a published image instead of building locally,
drop the `-f docker-compose.build.yml` part.

To create the first admin user once the container is running:

```
docker exec -it pointify python -m scripts.set_admin <username> <password>
```
