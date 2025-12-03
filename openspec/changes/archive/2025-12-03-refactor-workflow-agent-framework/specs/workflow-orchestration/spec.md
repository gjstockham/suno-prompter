# workflow-orchestration Specification (Agent Framework Implementation)

## MODIFIED Requirements

### Requirement: Workflow Pipeline Execution
The system SHALL execute a sequential pipeline of agents using Microsoft Agent Framework to generate song lyrics.

#### Scenario: Single-agent pipeline execution
- **WHEN** the user provides input (artists, songs, or guidance) and triggers generation
- **THEN** the workflow orchestrator runs the lyric-template agent via Agent Framework
- **AND** the agent produces a blueprint output
- **AND** the output is displayed to the user

#### Scenario: Pipeline error handling
- **WHEN** an agent fails during pipeline execution
- **THEN** the error is captured from Agent Framework events
- **AND** the user is notified of the failure with a clear error message

### Requirement: Workflow State Management
The system SHALL maintain workflow state using Agent Framework's built-in conversation thread model.

#### Scenario: Initialize workflow thread
- **WHEN** the user opens the application
- **THEN** an agent thread is created for the session
- **AND** thread reference is stored in session state

#### Scenario: Preserve conversation history
- **WHEN** an agent completes execution
- **THEN** the conversation history is retained in the thread
- **AND** the user can inspect or reference previous outputs

### Requirement: Agent Framework Integration
The system SHALL use Microsoft Agent Framework's agents and workflow orchestration for deterministic sequential execution.

#### Scenario: Create agent from chat client
- **WHEN** the application initializes
- **THEN** a ChatAgent is created with a configured chat client and system instructions
- **AND** the chat client is initialized based on environment configuration (OpenAI or Azure OpenAI)

#### Scenario: Build and run workflow
- **WHEN** the user triggers generation
- **THEN** the workflow is constructed using WorkflowBuilder with the lyric-template agent as start executor
- **AND** the workflow executes sequentially, passing outputs to subsequent steps (if defined)
- **AND** streaming events are emitted as the agent generates responses

#### Scenario: Handle async execution in Streamlit
- **WHEN** the workflow executes asynchronously
- **THEN** the Streamlit UI wraps async execution with `asyncio.run()` or similar sync wrapper
- **AND** progress is displayed via spinner or status indicators
- **AND** results are displayed upon completion

