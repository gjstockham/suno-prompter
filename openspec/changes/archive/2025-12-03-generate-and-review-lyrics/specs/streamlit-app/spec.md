# streamlit-app Specification (Delta for Lyric Generation)

## MODIFIED Requirements

### Requirement: Workflow Input Form
The system SHALL provide input fields for collecting song ideas before lyric generation.

#### Scenario: Display idea collection interface
- **WHEN** lyric template generation completes successfully
- **THEN** UI displays the generated template
- **AND** UI shows idea collection prompt: "Do you have a song idea or title?"
- **AND** user can enter idea manually or skip to auto-generate

#### Scenario: Manual idea entry
- **WHEN** user enters a song idea in the idea field
- **THEN** input is validated (non-empty, reasonable length)
- **AND** user can proceed with this idea by clicking "Generate Lyrics"

#### Scenario: Auto-generate idea
- **WHEN** user clicks "Surprise Me" without entering an idea
- **THEN** system selects random idea from starter ideas file
- **AND** system displays selected idea to user
- **AND** user can proceed with generated idea or enter own

### Requirement: Workflow Output Display
The system SHALL display generated lyrics with reviewer feedback.

#### Scenario: Display initial lyrics
- **WHEN** writer agent completes
- **THEN** UI displays generated lyrics
- **AND** UI shows reviewer feedback in expandable section
- **AND** feedback includes style assessment and revision suggestions

#### Scenario: Display reviewer satisfaction
- **WHEN** reviewer assessment is available
- **THEN** UI shows whether reviewer is satisfied or requires revision
- **AND** if satisfied: "Finalize" button shown
- **AND** if not satisfied: "Revise Lyrics" button shown with feedback details

#### Scenario: Handle revision loop
- **WHEN** user clicks "Revise Lyrics"
- **THEN** writer receives revision feedback from reviewer
- **AND** new lyrics are generated incorporating feedback
- **AND** reviewer provides updated feedback (loop repeats)
- **AND** UI shows revision iteration count

#### Scenario: Finalize lyrics
- **WHEN** user clicks "Accept and Finalize" or reviewer is satisfied
- **THEN** final lyrics are stored in session state
- **AND** UI displays final lyrics in designated section
- **AND** revision history is available (optional collapse/expand)

### Requirement: Workflow State Management
The system SHALL track idea collection and revision iterations.

#### Scenario: Store collected idea
- **WHEN** idea is collected (manual or auto-generated)
- **THEN** idea is stored in session state
- **AND** idea persists across reruns during revision loop

#### Scenario: Track revision iterations
- **WHEN** revisions occur
- **THEN** each iteration is tracked with feedback and new lyrics
- **AND** iteration count is displayed to user
- **AND** iteration history can be reviewed (optional)

#### Scenario: Cap iterations
- **WHEN** iteration count reaches maximum (e.g., 3)
- **THEN** user is notified that max revisions reached
- **AND** user can accept current lyrics or start over

## ADDED Requirements

### Requirement: Starter Ideas Display
The system SHALL provide access to starter ideas when user opts for auto-generation.

#### Scenario: Show selected starter idea
- **WHEN** user clicks "Surprise Me"
- **THEN** selected idea is displayed in UI
- **AND** user can see source of idea (starter ideas file)
- **AND** user can re-roll for different idea if desired (optional)

