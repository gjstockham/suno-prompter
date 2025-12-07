## ADDED Requirements

### Requirement: Stage Workflow Inputs
The frontend SHALL guide users through staged inputs: artist/song references first, optional lyrics fallback, then idea/title, and finally production guidance.

#### Scenario: Reference-first entry
- **WHEN** the SPA loads
- **THEN** only the artist/song/guidance step is actionable
- **AND** the UI explains that lyrics will be requested only if the reference search fails.

#### Scenario: Lyrics fallback when needed
- **WHEN** the template request returns a `needs_lyrics` status
- **THEN** the UI prompts for pasted lyrics
- **AND** resubmits that text to build the template before unlocking later steps.

#### Scenario: Idea and production steps gated
- **WHEN** a template is ready
- **THEN** the UI unlocks the idea/title step
- **AND** only after lyrics are generated does it show the production guidance step with an option to skip the producer.

### Requirement: Call Staged Backend API
The frontend SHALL call `/api/generate-template`, `/api/generate-lyrics`, and `/api/generate-production` in sequence while surfacing progress and errors.

#### Scenario: Template request with status handling
- **WHEN** the user submits artist/song references
- **THEN** the UI calls `/api/generate-template`
- **AND** if the response status is `needs_lyrics` the UI shows the lyrics fallback instead of progressing
- **AND** backend errors are shown inline while clearing the loading state.

#### Scenario: Lyrics and production requests
- **WHEN** a template exists and the user submits an idea/title
- **THEN** the UI calls `/api/generate-lyrics` and stores the returned template, lyrics, and feedback
- **AND WHEN** the user opts into production, the UI calls `/api/generate-production` with lyrics, template, and producer guidance and surfaces any backend error inline.

### Requirement: Present Workflow Results
The frontend SHALL render the template, lyrics, reviewer feedback iterations, and Suno outputs returned by each stage.

#### Scenario: Progressive results display
- **WHEN** the template stage succeeds
- **THEN** the blueprint appears even before lyrics are generated
- **AND** lyrics, feedback iterations, and Suno outputs appear as their respective stages complete.
