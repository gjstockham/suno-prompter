## MODIFIED Requirements

### Requirement: Application Initialization
The system SHALL initialize a Streamlit web application on startup with configuration loaded from environment variables.

#### Scenario: Successful startup with valid configuration
- **WHEN** user runs `streamlit run app.py` with valid `.env` file
- **THEN** the Streamlit server starts and displays the workflow interface
- **AND** configuration is loaded without errors
- **AND** the API key is validated as present (actual validation by agent at first interaction)

#### Scenario: Startup with missing configuration
- **WHEN** user runs `streamlit run app.py` without `.env` file or required variables
- **THEN** the application displays a clear error message
- **AND** the user is instructed to create `.env` with required variables

### Requirement: User Experience
The system SHALL provide a clear workflow interface with input fields and visual feedback.

#### Scenario: Workflow input form display
- **WHEN** user views the application
- **THEN** the interface shows Artist(s), Song(s), and Other guidance input fields
- **AND** a Generate button is visible
- **AND** the layout is clean and easy to understand

#### Scenario: Responsive feedback during agent processing
- **WHEN** the workflow is running
- **THEN** a progress indicator is displayed
- **AND** the user knows the system is processing
- **AND** the Generate button is disabled until processing completes

#### Scenario: Results display
- **WHEN** the workflow completes successfully
- **THEN** the lyric blueprint is displayed below the input form
- **AND** the output is formatted as readable markdown

## REMOVED Requirements

### Requirement: Chat Interface
**Reason**: Replaced with workflow-based interface
**Migration**: Users now use the structured input form instead of chat

### Requirement: Session State Management
**Reason**: Replaced by workflow state management in workflow-orchestration spec
**Migration**: Session state now managed by workflow orchestrator
