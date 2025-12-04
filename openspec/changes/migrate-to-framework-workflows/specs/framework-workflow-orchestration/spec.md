# Framework Workflow Orchestration

This capability replaces custom orchestration with Microsoft Agent Framework native workflow patterns.

## ADDED Requirements

### Requirement: Sequential Workflow Orchestration
The system SHALL use the framework's `SequentialBuilder` to orchestrate agents in a pipeline.

#### Scenario: Execute workflow steps in sequence
**Given** a workflow built with `SequentialBuilder`
**And** three executors: TemplateExecutor, LyricExecutor, ProducerExecutor
**When** the workflow is started with user input
**Then** TemplateExecutor runs first
**And** its output is passed to LyricExecutor
**And** LyricExecutor's output is passed to ProducerExecutor
**And** the workflow completes with final output

#### Scenario: Executor receives full conversation history
**Given** a workflow in progress
**When** the second executor (LyricExecutor) receives control
**Then** it has access to the full conversation including user input and template output
**And** it can extract required context from previous messages

---

### Requirement: Human-in-the-Loop via RequestInfoEvent
The system SHALL use framework-native HITL patterns for each workflow step that requires user input.

#### Scenario: Template executor requests song idea
**Given** the TemplateExecutor has generated a blueprint
**When** it needs a song idea from the user
**Then** it emits a `RequestInfoEvent` with prompt "Please provide a song idea"
**And** the workflow pauses until the user responds
**And** the user's response is passed to the next step

#### Scenario: Lyric executor requests acceptance
**Given** the LyricExecutor has generated reviewed lyrics
**When** it needs user acceptance
**Then** it emits a `RequestInfoEvent` with type "approval"
**And** options include "Accept" and "Request Changes"
**And** the workflow pauses until the user responds

#### Scenario: User requests changes to lyrics
**Given** a lyrics acceptance request is pending
**When** the user selects "Request Changes"
**Then** a follow-up `RequestInfoEvent` requests change details
**And** the user's feedback is used to regenerate lyrics
**And** the new lyrics are presented for acceptance

#### Scenario: Producer executor requests optional guidance
**Given** the ProducerExecutor is about to generate Suno output
**When** it offers optional production guidance input
**Then** it emits a `RequestInfoEvent` marked as optional
**And** the user can provide guidance or skip
**And** the workflow continues with or without guidance

---

### Requirement: Workflow Event Streaming
The workflow SHALL emit events for progress tracking and UI updates.

#### Scenario: Progress events during generation
**Given** a workflow is running
**When** an executor starts processing
**Then** an `AgentRunUpdateEvent` is emitted with executor ID
**And** the UI can display which step is active

#### Scenario: Completion event with output
**Given** the workflow has completed all steps
**When** the final executor finishes
**Then** a `WorkflowCompletedEvent` is emitted
**And** it contains the full conversation history
**And** it contains the final Suno output

#### Scenario: Custom events for UI updates
**Given** the LyricExecutor is in a review iteration
**When** a review cycle completes
**Then** a custom event "lyric_review_complete" is emitted
**And** it includes iteration number and satisfaction status
**And** the UI can display review feedback

---

### Requirement: Workflow Runner Adapter
The system SHALL provide a `WorkflowRunner` class that adapts framework workflows for different transports.

#### Scenario: Start workflow with callbacks
**Given** a `WorkflowRunner` initialized with a workflow
**When** `run()` is called with initial input and callbacks
**Then** progress events are routed to `on_progress` callback
**And** HITL requests are routed to `on_hitl_request` callback
**And** the method returns when workflow completes

#### Scenario: Send HITL response
**Given** a HITL request is pending
**When** `send_response()` is called with request ID and user response
**Then** the response is forwarded to the workflow
**And** the workflow resumes execution

---

### Requirement: Streamlit Adapter Integration
The system SHALL provide a `StreamlitWorkflowAdapter` that integrates framework workflows with Streamlit.

#### Scenario: Manage workflow state in session
**Given** a `StreamlitWorkflowAdapter` instance
**When** initialized
**Then** it creates session state entries for workflow status, progress, pending HITL, and outputs

#### Scenario: Render HITL UI for text input
**Given** a pending HITL request with type "text"
**When** `render_hitl_ui()` is called
**Then** a text area is rendered with the request prompt
**And** a submit button sends the response to the workflow

#### Scenario: Render HITL UI for approval
**Given** a pending HITL request with type "approval"
**When** `render_hitl_ui()` is called
**Then** buttons are rendered for each approval option
**And** clicking a button sends that option as the response

## MODIFIED Requirements

### Requirement: Workflow State Management
**Modifies**: `workflow-orchestration/spec.md` - Workflow State Management

State management SHALL move from custom `WorkflowState` dataclass to framework-managed context.

#### Scenario: State flows through conversation
**Given** a workflow using `SequentialBuilder`
**When** state needs to be passed between executors
**Then** it is encoded in `ChatMessage` objects in the conversation
**And** each executor extracts state from conversation history
**And** no external state store is required for basic operation

#### Scenario: Workflow status from events
**Given** a workflow is executing
**When** the UI needs current status
**Then** status is derived from the most recent event type
**And** "running" when `AgentRunUpdateEvent` received
**And** "awaiting_input" when `RequestInfoEvent` received
**And** "complete" when `WorkflowCompletedEvent` received

## REMOVED Requirements

### Requirement: Custom LyricWorkflow Class
The custom `LyricWorkflow` class is removed in favor of framework patterns.

- `LyricWorkflow.__init__()` - Replaced by workflow builder
- `LyricWorkflow.run()` - Replaced by workflow `run_stream()`
- `LyricWorkflow._run_agent_async()` - Replaced by executor handlers
- `LyricWorkflow._generate_and_review_lyrics()` - Replaced by `LyricExecutor`
- `LyricWorkflow.run_producer()` - Replaced by `ProducerExecutor`
- `nest_asyncio` usage - No longer needed with framework event loop handling

## Cross-References

- **Relates to**: `workflow-orchestration` - This capability replaces the custom orchestration spec
- **Relates to**: `streamlit-app` - UI integration changes to use adapter pattern
- **Relates to**: All agent specs - Agents remain unchanged; only orchestration changes
