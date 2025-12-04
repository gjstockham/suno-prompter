# Tasks: Migrate to Microsoft Agent Framework Workflows

## Phase 1: Core Infrastructure

### 1.1 Setup and Dependencies
- [ ] Add `agent-framework-core` to requirements.txt
- [ ] Pin version to avoid breaking changes
- [ ] Verify package installs correctly

### 1.2 Create Request/Response Types
- [ ] Create `src/suno_prompter/workflows/types.py`
- [ ] Implement `SongIdeaRequest` dataclass
- [ ] Implement `LyricApprovalRequest` dataclass
- [ ] Implement `WorkflowOutput` dataclass
- [ ] Add unit tests for type serialization

### 1.3 Implement IdeaCollector Executor
- [ ] Create `src/suno_prompter/workflows/executors/idea_collector.py`
- [ ] Implement `@handler` for `AgentExecutorResponse` input
- [ ] Implement `ctx.request_info()` call for HITL
- [ ] Implement `@response_handler` for user idea response
- [ ] Add unit tests with mocked context

### 1.4 Implement LyricGenerator Executor
- [ ] Create `src/suno_prompter/workflows/executors/lyric_generator.py`
- [ ] Implement `@handler` for dict input (template + idea)
- [ ] Implement writer/reviewer iteration loop
- [ ] Implement JSON feedback parsing
- [ ] Implement `ctx.request_info()` for approval HITL
- [ ] Implement `@response_handler` for approval response
- [ ] Add unit tests:
  - [ ] Test satisfied on first iteration
  - [ ] Test max iterations limit
  - [ ] Test feedback parsing edge cases

### 1.5 Implement OutputFormatter Executor
- [ ] Create `src/suno_prompter/workflows/executors/output_formatter.py`
- [ ] Implement `@handler` for `AgentExecutorResponse` from producer
- [ ] Implement JSON parsing for producer output
- [ ] Implement `ctx.yield_output()` with `WorkflowOutput`
- [ ] Add unit tests

### 1.6 Create Workflow Builder
- [ ] Create `src/suno_prompter/workflows/builder.py`
- [ ] Implement `build_suno_workflow()` function
- [ ] Use `WorkflowBuilder` with correct edge connections
- [ ] Export from `workflows/__init__.py`
- [ ] Add integration test for workflow construction

## Phase 2: Adapter Layer

### 2.1 Create Streamlit Adapter
- [ ] Create `src/suno_prompter/adapters/` directory
- [ ] Create `src/suno_prompter/adapters/streamlit_adapter.py`
- [ ] Implement `StreamlitWorkflowAdapter` class
- [ ] Implement session state initialization
- [ ] Implement `run_workflow()` with event collection
- [ ] Implement `submit_response()` for HITL
- [ ] Implement `send_responses_streaming()` integration
- [ ] Implement status/output getters
- [ ] Add unit tests with mocked workflow

### 2.2 Test Adapter Integration
- [ ] Create mock workflow for testing
- [ ] Test HITL request/response cycle
- [ ] Test error handling
- [ ] Test session state persistence

## Phase 3: App Refactoring

### 3.1 Refactor app.py - Initialization
- [ ] Import new workflow builder
- [ ] Import `StreamlitWorkflowAdapter`
- [ ] Replace `LyricWorkflow` initialization with `build_suno_workflow()`
- [ ] Wrap workflow in adapter

### 3.2 Refactor app.py - HITL Rendering
- [ ] Create `render_hitl_requests()` function
- [ ] Implement `render_idea_request()` for `SongIdeaRequest`
- [ ] Implement `render_approval_request()` for `LyricApprovalRequest`
- [ ] Wire up `adapter.submit_response()` to form submissions

### 3.3 Refactor app.py - Workflow Execution
- [ ] Replace `run_workflow()` with adapter pattern
- [ ] Replace `run_workflow_with_idea()` with HITL flow
- [ ] Replace `run_producer()` with automatic workflow continuation
- [ ] Update `render_output()` to use adapter state

### 3.4 Refactor app.py - Output Display
- [ ] Update `render_suno_output()` for `WorkflowOutput` type
- [ ] Ensure all existing UI functionality preserved

### 3.5 Integration Testing
- [ ] Test full workflow: template → idea → lyrics → approval → producer
- [ ] Test "Surprise Me" random idea flow
- [ ] Test iteration history display
- [ ] Test error scenarios
- [ ] Compare output quality to current implementation

## Phase 4: Cleanup

### 4.1 Remove Legacy Code
- [ ] Delete `src/suno_prompter/workflows/lyric_workflow.py` (old implementation)
- [ ] Delete `workflows/lyric_workflow.py` (root duplicate)
- [ ] Update `workflows/__init__.py` exports
- [ ] Remove unused imports from app.py

### 4.2 Remove Workarounds
- [ ] Remove `nest_asyncio` from requirements.txt
- [ ] Remove `nest_asyncio.apply()` calls
- [ ] Verify async execution works correctly

### 4.3 Documentation
- [ ] Update README with new architecture overview
- [ ] Add docstrings to all new modules
- [ ] Document HITL request types
- [ ] Add inline comments for complex logic

### 4.4 Final Verification
- [ ] Run full test suite
- [ ] Manual E2E testing of all workflow paths
- [ ] Performance comparison with old implementation
- [ ] Verify Streamlit hot-reload works correctly

## Phase 5: Future Enhancements (Optional)

### 5.1 CLI Adapter
- [ ] Create `src/suno_prompter/adapters/cli_adapter.py`
- [ ] Implement terminal-based HITL prompts
- [ ] Add `cli.py` entry point
- [ ] Document CLI usage

### 5.2 Checkpointing
- [ ] Investigate framework checkpoint storage options
- [ ] Implement checkpoint save/resume
- [ ] Add UI for resuming workflows
- [ ] Test checkpoint/resume cycle

### 5.3 AG-UI Integration
- [ ] Research AG-UI protocol compatibility
- [ ] Evaluate CopilotKit integration
- [ ] Plan web-native HITL implementation

## Acceptance Criteria

1. [ ] Workflow executes in correct order: template → idea HITL → lyrics → approval HITL → producer → output
2. [ ] HITL pauses workflow at `SongIdeaRequest` and `LyricApprovalRequest` points
3. [ ] User responses correctly route through `@response_handler` methods
4. [ ] Writer/reviewer loop respects max_iterations limit
5. [ ] Workflow can be tested without Streamlit (unit/integration tests pass)
6. [ ] No regression in user-facing functionality
7. [ ] `nest_asyncio` dependency removed
8. [ ] All existing UI features work (Surprise Me, iteration history, etc.)

## Dependencies

Required packages:
- `agent-framework-core` (pin specific version)

Framework features used:
- `WorkflowBuilder` - Graph construction
- `Executor` base class - Custom executors
- `@handler` decorator - Message handlers
- `@response_handler` decorator - HITL response handlers
- `WorkflowContext.request_info()` - HITL requests
- `WorkflowContext.send_message()` - Inter-executor messaging
- `WorkflowContext.yield_output()` - Final output
- `RequestInfoEvent` - HITL event detection
- `WorkflowOutputEvent` - Completion detection
- `workflow.run_stream()` - Streaming execution
- `workflow.send_responses_streaming()` - HITL response submission
