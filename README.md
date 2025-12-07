# Suno Prompter

A Flask REST API plus React/Vite frontend that orchestrates Microsoft Agent Framework flows to build lyric blueprints, generate lyrics, collect reviewer feedback, and format Suno-ready prompts.

## Architecture

- **backend/**: Flask API (`/api/generate-prompt`) backed by the agent workflow.
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

## API

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
