# Proposal: Migrate to Microsoft Agent Framework Workflows

## Summary

Replace the custom `LyricWorkflow` orchestration with Microsoft Agent Framework's native workflow patterns. This uses `WorkflowBuilder` with agents added directly to the workflow graph, conditional edges for routing, and the framework's `request_info()` / `@response_handler` pattern for human-in-the-loop interactions.

## Motivation

### Current State
- Custom `LyricWorkflow` class manually orchestrates 4 agents
- Human-in-the-loop is implicit via Streamlit UI state transitions
- State management is tightly coupled to Streamlit session state
- Async handling requires `nest_asyncio` workarounds

### Problems with Current Approach
1. **Non-standard orchestration** - Custom code instead of framework patterns
2. **No native HITL** - User approval isn't framework-aware; agents can't request input
3. **Limited portability** - Workflow logic is embedded in Streamlit-specific code
4. **No checkpointing** - Long workflows can't be saved/resumed
5. **Testing difficulty** - Hard to test orchestration without full UI

### Benefits of Migration
1. **Framework alignment** - Follow documented Microsoft Agent Framework patterns
2. **Native HITL** - Use `request_info()` to pause for user input at any step
3. **Portability** - Workflow can run via CLI, API, or UI with thin adapters
4. **Checkpointing** - Save/resume workflows across sessions (framework-native)
5. **Better event streaming** - Framework emits typed events for progress tracking
6. **Testability** - Workflow logic is decoupled from UI

## Scope

### In Scope
- Replace `LyricWorkflow` with `WorkflowBuilder`-based workflow
- Add agents directly to workflow graph (framework auto-wraps them)
- Implement HITL using `request_info()` and `@response_handler`
- Create minimal custom executors for HITL coordination
- Refactor Streamlit to consume workflow events via `run_stream()`

### Out of Scope
- Changing agent prompts or behavior
- Adding new agents or capabilities
- Changing the fundamental 4-step workflow structure
- AG-UI integration (future enhancement)

## Proposed Architecture

### Current Flow
```
Streamlit UI
    ↓
LyricWorkflow (custom orchestration)
    ↓
Manual agent calls with async loops
    ↓
Streamlit session state
```

### Proposed Flow
```
Streamlit UI (or CLI/API)
    ↓
workflow.run_stream() / send_responses_streaming()
    ↓
WorkflowBuilder graph with auto-wrapped agents
    ↓
Framework events (RequestInfoEvent, WorkflowOutputEvent)
    ↓
UI adapter handles events and sends responses
```

### Workflow Structure

Agents are added **directly** to the workflow graph. The framework auto-wraps them as executors:

```python
from agent_framework import WorkflowBuilder

workflow = (
    WorkflowBuilder()
    .set_start_executor(template_agent)       # Auto-wrapped
    .add_edge(template_agent, idea_collector) # Custom executor for HITL
    .add_edge(idea_collector, lyric_generator)# Custom executor with loop
    .add_edge(lyric_generator, producer_agent)# Auto-wrapped
    .add_edge(producer_agent, output_formatter)
    .build()
)
```

### Custom Executors (Minimal)

Only **3 small custom executors** are needed:

| Executor | Purpose | HITL |
|----------|---------|------|
| `IdeaCollector` | Receives template, requests song idea from user | Yes |
| `LyricGenerator` | Runs writer/reviewer loop, requests approval | Yes |
| `OutputFormatter` | Parses producer output, yields final result | No |

### Human-in-the-Loop Pattern

Using the framework's native `request_info()` API:

```python
from agent_framework import Executor, handler, response_handler
from dataclasses import dataclass

@dataclass
class SongIdeaRequest:
    template: str

class IdeaCollector(Executor):
    @handler
    async def on_template(self, template_response, ctx):
        await ctx.request_info(
            request_data=SongIdeaRequest(template=template_response.text),
            response_type=str
        )

    @response_handler
    async def on_idea(self, req: SongIdeaRequest, idea: str, ctx):
        await ctx.send_message({"template": req.template, "idea": idea})
```

### HITL Points

| Step | Request Type | User Action |
|------|--------------|-------------|
| After template generation | `SongIdeaRequest` | Provide song idea/title |
| After lyric generation | `LyricApprovalRequest` | Accept or request changes |
| After producer (optional) | None | Copy outputs to Suno |

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Framework API learning curve | Medium | Low | Detailed design doc with examples |
| Streamlit async compatibility | Medium | Medium | Use `send_responses_streaming()` pattern |
| Migration breaks existing functionality | Medium | High | Comprehensive testing, feature flag |
| Framework version changes | Low | Medium | Pin `agent-framework-core` version |

## Dependencies

- `agent-framework-core` package
- Framework patterns used:
  - `WorkflowBuilder` for graph construction
  - `Executor` base class with `@handler` and `@response_handler`
  - `WorkflowContext.request_info()` for HITL
  - `RequestInfoEvent` for event handling
  - `workflow.run_stream()` and `send_responses_streaming()`

## Success Criteria

1. Workflow runs identically to current behavior
2. Each HITL point uses native `request_info()` pattern
3. Workflow can be tested without Streamlit
4. Events stream to UI in real-time via `run_stream()`
5. No regression in user experience
6. Code is simpler than current implementation
