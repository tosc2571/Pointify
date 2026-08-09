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
