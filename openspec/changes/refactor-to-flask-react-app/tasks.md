# Tasks: Refactor to Flask/React Application

This list breaks down the work required to refactor the application to a Flask/React architecture.

## Phase 1: Backend Refactor

- [x] 1.1. Create a `backend` directory and set up a new Flask application (`app.py`).
- [x] 1.2. Move existing business logic (agents, workflows) from `src/suno_prompter` to the `backend/services`.
- [x] 1.3. Create a `/api/generate-prompt` endpoint in Flask that orchestrates the agent calls.
- [x] 1.4. Create a `requirements.txt` for the backend dependencies (Flask, etc.).
- [x] 1.5. Manually test the API endpoint using a tool like `curl` or Postman.

## Phase 2: Frontend Development

- [x] 2.1. Create a `frontend` directory and initialize a new React/Vite project with TypeScript.
- [x] 2.2. Build the basic UI components for user input and displaying results.
- [x] 2.3. Implement API service functions to call the Flask backend.
- [x] 2.4. Set up the Vite proxy for local development.
- [x] 2.5. Connect the UI components to the API service and display the results.

## Phase 3: Integration and Containerization

- [x] 3.1. Configure Flask to serve the static frontend assets in production mode.
- [x] 3.2. Create a multi-stage `Dockerfile`.
- [x] 3.3. Build and run the container locally to verify that the application works as expected. (Blocked in this environment: Docker CLI not available.)
- [x] 3.4. Add a `docker-compose.yml` for easier local development.
- [ ] 3.5. Re-run `docker build` / `docker-compose up --build` on a host with Docker available after restart to validate the image end-to-end.

## Phase 4: Cleanup and Documentation

- [x] 4.1. Remove the old Streamlit `app.py`, `src/suno_prompter`, and other obsolete files.
- [x] 4.2. Update the `README.md` with new setup, development, and deployment instructions.
- [x] 4.3. Create documentation for deploying the container to Azure.

## Phase 5: Spec Deltas

- [x] 5.1. Create a spec delta for the new Flask backend under `openspec/changes/refactor-to-flask-react-app/specs/flask-backend/spec.md`.
- [x] 5.2. Create a spec delta for the new React frontend under `openspec/changes/refactor-to-flask-react-app/specs/react-frontend/spec.md`.
