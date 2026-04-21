# FastAPI + React TXT Analyzer

TXT Analyzer lets users upload `.txt` files, stores raw and transformed outputs in PostgreSQL, and returns word occurrence counts through a React UI.

## Architecture
- **Backend**: FastAPI + SQLAlchemy + Alembic
- **Database**: PostgreSQL 16
- **Frontend**: React + Vite + Tailwind CSS
- **Deployment**: Docker images + `docker compose` for local stack

## Functional Coverage
- Upload `.txt` files from the UI
- Prevent duplicate uploads by filename (returns HTTP `409`)
- Persist raw text in `files.raw_text`
- Persist transformed output (`normalized_text`, `word_frequency`) in `file_transformations`
- Query per-word occurrence count from UI (`GET /files/{file_id}/count`)
- Select previously uploaded files from a dropdown (`GET /files`)
- Hide internal file IDs in UI while still using them for API calls

## Project Layout
- `backend/`: FastAPI API, DB models, migrations, tests
- `frontend/`: React app and API client
- `docker-compose.yml`: local multi-container stack

## Local Development (without Docker)

### 1) Backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set `DATABASE_URL` in `backend/.env` to a running PostgreSQL instance.
Set `LOG_LEVEL` (`DEBUG`, `INFO`, etc.) to control backend log verbosity.

Run migrations and API:
```bash
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### 2) Frontend
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

App runs at `http://localhost:5174`.

## Docker Local Stack

1. Copy env template:
```bash
cp .env.example .env
```

2. Build and run:
```bash
docker compose up --build
```

3. Access services:
- Frontend: `http://localhost:5174`
- Backend API: `http://localhost:8000`
- API health: `http://localhost:8000/health`

The backend container runs `alembic upgrade head` on startup before launching `uvicorn`.

## Cloud Deployment (Generic)

1. Build images:
```bash
docker build -t txt-analyzer-backend:latest ./backend
docker build -t txt-analyzer-frontend:latest --build-arg VITE_API_BASE_URL=https://<api-domain> ./frontend
```

2. Push images to your container registry.
3. Provision managed PostgreSQL.
4. Deploy backend and frontend containers to your cloud runtime.
5. Set runtime env vars for backend:
   - `DATABASE_URL`
   - `BACKEND_CORS_ORIGINS` (include frontend URL)
   - `LOG_LEVEL` (`INFO` recommended for production)
6. Expose frontend and backend through public URLs.

## Testing

### Backend unit/API tests
```bash
cd backend
pytest
```

### Frontend unit tests (Vitest + Testing Library)
```bash
cd frontend
npm install
npm run test:run
```

### Docker smoke test
1. `docker compose up --build`
2. Upload a `.txt` file in the UI
3. Attempt to upload the same filename again and verify duplicate rejection
4. Select an uploaded file from the dropdown
5. Query a word and verify returned count
6. Confirm persisted data in DB:
```bash
docker compose exec db psql -U postgres -d txt_analyzer -c "select id, filename from files;"
docker compose exec db psql -U postgres -d txt_analyzer -c "select file_id, word_frequency from file_transformations;"
```
