# Multi-stage build: Angular production build -> copied into the API's static dir -> slim
# Python runtime image serving both the API and the built SPA from one process.

FROM node:24-alpine AS frontend-build
WORKDIR /src/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npx ng build

FROM python:3.12-slim AS backend-build
WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir --target=/app/deps -r requirements.txt
COPY backend/app/ ./app/
COPY backend/alembic/ ./alembic/
COPY backend/alembic.ini ./
COPY backend/scripts/ ./scripts/
COPY --from=frontend-build /src/frontend/dist/pointify/browser ./app/static

FROM python:3.12-slim AS runtime
WORKDIR /app
COPY --from=backend-build /app/deps /usr/local/lib/python3.12/site-packages
COPY --from=backend-build /app/app ./app
COPY --from=backend-build /app/alembic ./alembic
COPY --from=backend-build /app/alembic.ini ./
COPY --from=backend-build /app/scripts ./scripts

# Fixed internal port and DB location — the only thing a self-hoster changes is the
# docker-compose.yml port mapping, never these.
ENV DATABASE_URL=sqlite:////data/pointify.db
ENV ENVIRONMENT=production
VOLUME /data
EXPOSE 8000

ENTRYPOINT ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
