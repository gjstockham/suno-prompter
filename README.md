# Suno Prompter

A Flask REST API plus React/Vite frontend that orchestrates Microsoft Agent Framework flows to build lyric blueprints, generate lyrics, collect reviewer feedback, and format Suno-ready prompts.

## Architecture

- **backend/**: Flask API exposing the lyric workflow (template → lyrics → reviewer → producer) plus helper endpoints.
- **frontend/**: React + Vite + TypeScript SPA that proxies `/api` calls to the backend.
- **Container**: Multi-stage Dockerfile builds the frontend, bundles it with the API, and runs via Gunicorn.

## Prerequisites

- Python 3.11+
- Node 20+ and npm
- Docker (optional, for container builds)

## Configuration

1. Copy `.env.example` to `.env` and set your LLM provider details (OpenAI or Azure OpenAI).  
   The backend loads `.env` from the project root or `~/.suno-prompter/.env`.
2. Optional flags: `LOG_LEVEL`, `APP_DEBUG`, `PORT`, `FLASK_DEBUG`.

## Local Development

### Backend (Flask API)
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt
python backend/app.py  # runs on PORT (default 5000)
```

### Frontend (React/Vite)
```bash
cd frontend
npm install
npm run dev  # serves on http://localhost:5173 and proxies /api to the backend
```

### Quick local run (backend + frontend)
1) Start backend in one shell:
```bash
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
python backend/app.py
```
2) Start frontend in another shell:
```bash
cd frontend
npm run dev
```
3) Visit http://localhost:5173 (frontend proxies API calls to the backend on port 5000).

## API

Core workflow (single-call):

`POST /api/generate-prompt`
```json
{
  "artists": "Taylor Swift",
  "songs": "Cruel Summer",
  "guidance": "Upbeat, neon pop",
  "lyrics": "",
  "idea": "Night drive confessions",
  "producer_guidance": "Sparkling synths, crisp drums",
  "include_producer": true
}
```
Responses include `status`, `error` (if any), `outputs.template`, `outputs.lyrics`, `outputs.feedback_history`, and optional `outputs.suno_output` (style_prompt, lyric_sheet).

Stage-specific endpoints (used by the frontend wizard):
- `POST /api/generate-template` — build a style template from references and/or pasted lyrics.
- `POST /api/generate-lyrics` — generate lyrics from a template + idea/title (iterates writer/reviewer).
- `POST /api/generate-production` — format finalized lyrics into Suno style prompt + lyric sheet.
- `GET /api/shuffle-idea` — return a random starter idea.

## Production Build

```bash
# Build static assets
cd frontend && npm run build
cd ..
# Run API + static assets
gunicorn -b 0.0.0.0:5000 "backend.app:create_app()"
```

## Docker

```bash
docker build -t suno-prompter .          # builds frontend + backend
docker-compose up --build                # runs container on :5000
```

## Azure Deployment

See `docs/azure-container.md` for Azure Container Apps deployment steps.

## Troubleshooting

- If `/api/generate-prompt` returns configuration errors, confirm `.env` is loaded and contains the required provider keys.
- For local dev without Docker, ensure the backend is running on port 5000 before starting the Vite dev server.
