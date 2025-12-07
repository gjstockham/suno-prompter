## ADDED Requirements

### Requirement: Collect Prompt Inputs
The frontend SHALL present a form to capture artists, songs, guidance, optional pasted lyrics, a required song idea/title, and a toggle to request Suno producer output.

#### Scenario: Form available on load
- **WHEN** the SPA loads
- **THEN** the user can enter artists, songs, guidance, lyrics, idea/title, producer guidance, and toggle producer output before submitting.

#### Scenario: Client-side validation
- **WHEN** the user submits without an idea/title or without any reference fields (artists, songs, guidance, lyrics)
- **THEN** the UI blocks the submission and shows an inline error explaining what is missing.

### Requirement: Call Backend API
The frontend SHALL invoke `POST /api/generate-prompt` with the captured fields, show progress, and surface backend errors.

#### Scenario: Successful submission
- **WHEN** the user submits a valid form
- **THEN** the UI shows a loading state, sends the JSON payload to `/api/generate-prompt`, and clears the loading state when the response returns.

#### Scenario: Backend errors surfaced
- **WHEN** the backend responds with an error (e.g., configuration or validation failure)
- **THEN** the UI displays a clear error message without crashing or leaving the loading indicator active.

### Requirement: Present Workflow Results
The frontend SHALL render the template, lyrics, reviewer feedback iterations, and Suno outputs returned by the backend.

#### Scenario: Show workflow output
- **WHEN** the API call succeeds
- **THEN** the UI displays the returned template, lyrics, iteration feedback (including satisfied/unsatisfied state), and, when requested, the Suno style prompt and lyric sheet.
