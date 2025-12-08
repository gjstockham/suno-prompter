## ADDED Requirements

### Requirement: Prompt Generation API
The backend SHALL expose a `POST /api/generate-prompt` endpoint that validates inputs, runs the lyric workflow, and optionally produces Suno-ready outputs.

#### Scenario: Successful prompt run
- **WHEN** the request includes a song idea/title and at least one reference field (artists, songs, guidance, or pasted lyrics)
- **AND** the backend configuration is valid
- **THEN** the response is `200 OK` JSON containing `status`, `outputs.template`, `outputs.lyrics`, `outputs.feedback_history`, and, when requested, `outputs.suno_output`.

#### Scenario: Missing references or idea
- **WHEN** the request omits a song idea/title or provides no reference fields
- **THEN** the endpoint responds with `400 Bad Request` and an error message describing the missing inputs.

#### Scenario: Invalid LLM configuration
- **WHEN** required LLM configuration is missing or invalid
- **THEN** the endpoint responds with `400 Bad Request` containing configuration error details without invoking any agents.

### Requirement: Health Check Endpoint
The backend SHALL provide `GET /api/health` that reports service availability.

#### Scenario: Health status
- **WHEN** the endpoint is invoked
- **THEN** it returns `200 OK` with a JSON body containing `"status": "ok"`.

### Requirement: Serve Built Frontend
The backend SHALL serve the built React frontend assets when the `frontend/dist` directory is present.

#### Scenario: Serve SPA assets
- **WHEN** a request targets `/` or a non-API path and the build assets exist
- **THEN** the server returns the matching static asset if it exists, otherwise `index.html` as a SPA fallback.
