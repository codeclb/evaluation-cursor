# TXT Analyzer Web App

FastAPI + React web app that lets users upload TXT files, stores raw/transformed results, and returns word occurrence counts.

## Features
- Upload `.txt` files via web UI.
- Persist raw text.
- Persist transformed text and word-frequency map.
- Replace existing records when uploading a file with the same filename.
- Query word count by filename (no upload ID exposed in UI).

## Stack
- Backend: FastAPI + SQLAlchemy
- Frontend: React + TypeScript + Tailwind CSS (Vite)
- Database: PostgreSQL
- Deployment: Docker / Docker Compose

## Local run without Docker

### 1) Start PostgreSQL
Start only the database service with Docker Compose:

```bash
docker compose up -d db
```

Confirm the DB container is up (wait until `healthy`):

```bash
docker compose ps
```

Optional: check DB connectivity directly:

```bash
docker compose exec db psql -U postgres -d txt_analyzer -c '\dt'
```

### 2) Run backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/txt_analyzer
export CORS_ORIGINS=http://localhost:5173
export LOG_LEVEL=DEBUG
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

If this is your first run, tables are created automatically on startup.

### 3) Run frontend
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

### 4) Stop local PostgreSQL (when done)
```bash
docker compose stop db
```

Or stop and remove all project containers/networks:

```bash
docker compose down
```

## Run with Docker (local multi-service)
```bash
docker compose up --build
```

Services:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs

## API Contract

### `POST /uploads`
- Multipart form field: `file`
- Accepts `.txt` files only.
- If the same filename already exists, the previous data is replaced.
- Returns upload metadata (`filename`, `uploaded_at`).

### `GET /uploads/count?filename=...&word=...`
- Returns occurrence count for the requested word in the specified filename.

### `GET /uploads/details?filename=...`
- Returns stored upload details (raw + normalized text) for the filename.

## Tests
```bash
cd backend
pytest
```

## Cloud deployment path
1. Build and push container images:
   - Backend image from `backend/Dockerfile`
   - Frontend image from `frontend/Dockerfile`
2. Deploy backend and frontend containers to a cloud container platform (ECS/Fargate, Azure Container Apps, or Cloud Run).
3. Provision managed PostgreSQL (RDS/Cloud SQL/Azure Database for PostgreSQL).
4. Set env vars:
   - `DATABASE_URL`
   - `CORS_ORIGINS`
   - `VITE_API_BASE_URL` (frontend build arg)
5. Smoke test deployment:
   - Upload sample `.txt`
   - Query a known word count
