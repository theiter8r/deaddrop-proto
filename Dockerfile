# syntax=docker/dockerfile:1

# ── Stage 1: Build Next.js frontend ──────────────────────────────────────────
FROM node:20-alpine AS frontend-builder
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
# Empty string → API fetches use same-origin relative paths
ENV NEXT_PUBLIC_API_URL=""
RUN npm run build

# ── Stage 2: Python backend + bundled static frontend ────────────────────────
FROM python:3.12-slim
WORKDIR /app

COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./
# Copy Next.js static export → /app/static
COPY --from=frontend-builder /frontend/out ./static

EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
