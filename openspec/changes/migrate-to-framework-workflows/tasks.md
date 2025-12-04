# Tasks: Migrate to Microsoft Agent Framework Workflows

## Phase 1: Core Workflow Infrastructure

### 1.1 Create Executor Base Infrastructure
- [ ] Create `workflows/executors/` directory
- [ ] Create `workflows/executors/__init__.py` with exports
- [ ] Add any shared utilities for executors (prompt building, parsing)

### 1.2 Implement TemplateExecutor
- [ ] Create `workflows/executors/template_executor.py`
- [ ] Implement `@handler` method for template generation
- [ ] Implement HITL request for song idea
- [ ] Add unit tests for TemplateExecutor

### 1.3 Implement LyricExecutor
- [ ] Create `workflows/executors/lyric_executor.py`
- [ ] Implement writer/reviewer loop logic
- [ ] Implement HITL approval for lyrics acceptance
- [ ] Implement optional user feedback loop
- [ ] Add unit tests for LyricExecutor

### 1.4 Implement ProducerExecutor
- [ ] Create `workflows/executors/producer_executor.py`
- [ ] Implement optional HITL for production guidance
- [ ] Implement Suno output generation
- [ ] Add unit tests for ProducerExecutor

### 1.5 Create Workflow Builder
- [ ] Create `workflows/builder.py`
- [ ] Implement `build_suno_workflow()` function
- [ ] Use `SequentialBuilder` to compose executors
- [ ] Add integration test for full workflow (no UI)

## Phase 2: Transport Adapters

### 2.1 Create WorkflowRunner
- [ ] Create `workflows/runner.py`
- [ ] Implement `WorkflowRunner` class
- [ ] Handle event routing to callbacks
- [ ] Handle HITL request/response cycle
- [ ] Add unit tests

### 2.2 Create Streamlit Adapter
- [ ] Create `adapters/` directory
- [ ] Create `adapters/streamlit_adapter.py`
- [ ] Implement session state management
- [ ] Implement HITL UI rendering
- [ ] Handle Streamlit async constraints

### 2.3 Research Streamlit Async Patterns
- [ ] Investigate Streamlit's async execution model
- [ ] Prototype background task with progress polling
- [ ] Determine if WebSocket approach is needed
- [ ] Document chosen approach

## Phase 3: App Refactoring

### 3.1 Refactor app.py
- [ ] Import new workflow components
- [ ] Replace `LyricWorkflow` usage with `StreamlitWorkflowAdapter`
- [ ] Update state management to use adapter
- [ ] Preserve existing UI structure where possible

### 3.2 Migrate UI Components
- [ ] Refactor `render_workflow_form()` for new adapter
- [ ] Refactor `render_idea_collection()` for HITL pattern
- [ ] Refactor `render_lyrics_and_feedback()` for HITL pattern
- [ ] Refactor `render_producer_section()` for HITL pattern
- [ ] Refactor `render_suno_output()` for final output

### 3.3 Handle Edge Cases
- [ ] Implement error handling in adapter
- [ ] Handle workflow cancellation
- [ ] Handle browser refresh during workflow
- [ ] Test rapid HITL responses

## Phase 4: Cleanup & Documentation

### 4.1 Remove Legacy Code
- [ ] Delete `workflows/lyric_workflow.py`
- [ ] Update `workflows/__init__.py` exports
- [ ] Remove unused imports from app.py
- [ ] Remove `nest_asyncio` if no longer needed

### 4.2 Testing
- [ ] Run full regression test suite
- [ ] Manual E2E testing of all workflow paths
- [ ] Test error scenarios
- [ ] Performance comparison with old implementation

### 4.3 Documentation
- [ ] Update README with new architecture
- [ ] Document HITL patterns used
- [ ] Add inline code comments for complex logic
- [ ] Update any existing design docs

## Phase 5: Extended Features (Optional)

### 5.1 Checkpointing
- [ ] Investigate framework checkpointing support
- [ ] Implement checkpoint storage (filesystem or SQLite)
- [ ] Add UI for resuming workflows
- [ ] Test checkpoint/resume cycle

### 5.2 CLI Adapter
- [ ] Create `adapters/cli_adapter.py`
- [ ] Implement terminal-based HITL
- [ ] Add `cli.py` entry point
- [ ] Document CLI usage

### 5.3 API Adapter
- [ ] Create `adapters/api_adapter.py`
- [ ] Implement REST API for workflow execution
- [ ] Add FastAPI or similar framework
- [ ] Document API endpoints

## Dependencies

- `agent-framework>=X.Y.Z` (pin specific version)
- Framework must support:
  - `SequentialBuilder`
  - `Executor` base class with `@handler`
  - `WorkflowContext.request_input()`
  - `WorkflowContext.request_approval()`
  - `RequestInfoEvent`, `WorkflowCompletedEvent`

## Acceptance Criteria

1. [ ] All 4 workflow steps execute in correct order
2. [ ] HITL pauses workflow at each expected point
3. [ ] User input is correctly passed between steps
4. [ ] Workflow can be tested without Streamlit
5. [ ] No regression in user-facing functionality
6. [ ] Event streaming shows real-time progress
7. [ ] Error handling matches or exceeds current behavior
