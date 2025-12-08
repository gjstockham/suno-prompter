# Design: Flask/React Architecture

This document details the technical design for refactoring the Suno Prompter application into a decoupled Flask backend and React frontend.

## 1. High-Level Architecture

The application will be structured as a monorepo with two main components:

- **`/backend`:** A Python/Flask application serving a REST API.
- **`/frontend`:** A TypeScript/React/Vite single-page application (SPA).

For production, the React app will be built into static files (`index.html`, CSS, JS) and served by the Flask application from a static folder. This allows for a single container deployment.

For development, the Flask server and the Vite development server will run concurrently, with the frontend proxying API requests to the backend to avoid CORS issues.

## 2. Backend (Flask)

- **Framework:** Flask will be used for its simplicity and flexibility.
- **Project Structure:**
    ```
    backend/
    ├── app.py          # Flask app factory and entry point
    ├── api/            # API blueprints/routes
    │   ├── __init__.py
    │   └── prompter.py # Routes for prompt generation
    ├── services/       # Business logic (re-used from existing agents)
    │   ├── __init__.py
    │   └── ...
    ├── Dockerfile
    └── requirements.txt
    ```
- **API Endpoints:** The API will be stateful to manage the iterative lyric generation workflow. It will expose endpoints to create, revise, and finalize a workflow.
    - `POST /api/workflows`: Initiates a new workflow, runs the first generation/review cycle, and returns the initial state with a `workflow_id`.
    - `POST /api/workflows/{workflow_id}/revise`: Runs the next iteration of the review cycle.
    - `POST /api/workflows/{workflow_id}/produce`: Finalizes the workflow and generates the Suno-compatible output.
    - `GET /api/health`: A health check endpoint.
- **Serving Frontend:** In production mode, Flask will be configured to serve the static files from the `frontend/dist` directory.

## 3. Frontend (React/Vite)

- **Framework:** React with Vite for fast development and bundling. TypeScript for type safety.
- **Project Structure:**
    ```
    frontend/
    ├── src/
    │   ├── App.tsx
    │   ├── main.tsx
    │   ├── components/
    │   └── services/
    │       └── api.ts  # Functions for calling the backend API
    ├── package.json
    ├── tsconfig.json
    └── vite.config.ts
    ```
- **UI/UX:** The UI will be rebuilt to be functionally equivalent to the existing Streamlit interface, but with a more polished look and feel.
- **API Communication:** `fetch` or `axios` will be used to communicate with the Flask API.
- **Development Proxy:** `vite.config.ts` will be configured to proxy API requests from `/api` to the Flask development server (e.g., `http://localhost:5000`).

## 4. Containerization and Deployment

- **Dockerfile:** A multi-stage `Dockerfile` will be created:
    1.  **Node.js Stage:** Build the React frontend to produce static assets.
    2.  **Python Stage:** Copy the frontend assets and install Python dependencies.
    3.  **Final Stage:** A lightweight Python image (e.g., `python:3.11-slim`) with the Flask app and static assets.
- **Entrypoint:** The container's entrypoint will be a `gunicorn` or `waitress` server running the Flask application.
- **Azure Deployment:** The container image will be pushed to Azure Container Registry and deployed to Azure Container Apps. Environment variables will be used to configure the application (e.g., API keys).

## 5. Development Workflow

1. **Backend:** `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && flask run`
2. **Frontend:** `npm install && npm run dev`
3. The frontend will be available on `http://localhost:5173` and the backend on `http://localhost:5000`.
4. The frontend will proxy API requests to the backend.
