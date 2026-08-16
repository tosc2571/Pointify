---
name: build-test
description: Build and test Pointify's backend and frontend, then report a concise pass/fail summary. Use whenever a code change needs to be verified, before reporting a task complete, or when the user asks to "build", "test", or "run the tests".
---

# Build & Test Pointify

## Backend (`backend/`)

1. From `backend/`, with the venv active: `pip install -r requirements.txt`
   (only needed if dependencies changed). If it fails, stop and report the
   error — do not run tests against a broken install.
2. Run `pytest` from `backend/`.
3. Summarize: passed/total, and the name + assertion message of every
   failing test.

Run `pytest -k <name>` to target tests matching a substring, or
`pytest tests/test_themes.py` for a single file, when iterating on one area.

## Frontend (`frontend/`)

1. From `frontend/`: `npx ng build`. If it fails, stop and report the
   compiler/bundler errors — do not run tests against a broken build.
2. Run `npx ng test --watch=false`.
3. Summarize: build OK/failed, tests passed/total with failing test names.

Run `npx ng test --watch=false --include='**/theme-list.spec.ts'` (adjust
the glob) to target a single spec file when iterating on one area.

## Notes specific to this repo

- Backend: FastAPI + SQLAlchemy + Alembic (`backend/app/`), pytest suite in
  `backend/tests/` using `TestClient` + `HttpTestingController`-style
  dependency overrides (see `backend/tests/conftest.py`). No network calls —
  the test DB is a temp SQLite file per test.
- Frontend: Angular, tests run via the `@angular/build:unit-test` builder
  (Vitest under the hood, not Karma) — `ng test` is the right command, not
  `karma`/`jest` directly.
- If both backend and frontend changed (e.g. a new API field consumed by a
  new UI element), verify both, in either order.
- Neither `pytest` nor `ng test` covers a real browser/end-to-end check —
  for UI-visible changes, also run the app for real (`ng serve` + backend
  running locally, or Docker) before reporting the task done.
- Do not attempt a fix for a failing test/build unless asked — report first.
