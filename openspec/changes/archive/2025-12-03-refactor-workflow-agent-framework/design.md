# Design: Refactor Workflow Orchestration to Use Microsoft Agent Framework

## Context
The application currently uses a custom orchestration pattern that manages agent lifecycle and coordination manually. This works for single-agent execution but doesn't scale to multi-agent patterns or leverage the framework's built-in capabilities for state management, streaming, and extensibility.

Microsoft Agent Framework provides:
- **Agents**: Created via `ChatAgent` with a chat client and instructions
- **Workflows**: Directed acyclic graphs (DAGs) of executors (agents or custom executors) using `WorkflowBuilder`
- **Sequential Orchestration**: Agents execute in order; outputs flow to next agent as inputs
- **Event Streaming**: `AgentRunUpdateEvent` and `AgentRunEvent` for progress tracking

## Goals
- Replace custom orchestration with Agent Framework's `WorkflowBuilder` and sequential pattern
- Leverage Agent Framework's built-in streaming and event model for Streamlit integration
- Maintain current user experience (input form → agent execution → blueprint output)
- Position for future multi-agent patterns (writer, reviewer, arranger)
- Reduce custom code; rely on framework conventions

## Non-Goals
- Migrate to concurrent or handoff orchestration (sequential only for now)
- Change UI structure or user interactions
- Implement persistence beyond session state
- Add logging or monitoring infrastructure beyond current setup

## Decisions

### Decision: Use WorkflowBuilder with Sequential Orchestration
Use `agent_framework.WorkflowBuilder()` to define a sequential pipeline:
1. Start with the lyric-template agent
2. Add edges to future agents as they're implemented

**Rationale**: Sequential is deterministic, matches current behavior, and Agent Framework has native support via `SequentialBuilder` or manual edge-building.

**Alternatives Considered**:
- Custom agent coordination: More control but loses framework benefits
- Concurrent orchestration: Overcomplicates current use case
- Handoff pattern: Unnecessary for deterministic workflows

### Decision: Convert LyricTemplateAgent to ChatAgent
Rather than custom agent class, create a `ChatAgent` with:
- Chat client (OpenAI or Azure OpenAI based on config)
- System instructions focused on lyric template generation
- Function tools if needed (TBD)

**Rationale**: Standard pattern, no custom subclassing, easier maintenance.

**Alternatives Considered**:
- Keep custom `BaseAgent` subclass: Adds complexity; framework's `ChatAgent` covers 90% of use cases
- Use Azure AI Foundry Agents Service: Requires Azure infrastructure; local-first constraint violated

### Decision: Use Async/Await in Streamlit via streamlit-runtime
Streamlit doesn't natively support async handlers, but we can:
- Wrap async workflow execution with `asyncio.run()` in button callback
- Use `st.spinner()` for progress feedback
- Stream events by converting `async for` to synchronous iteration with `asyncio.run()`

**Rationale**: Minimal UI changes; leverages framework streaming without over-complicating Streamlit integration.

**Alternatives Considered**:
- Replace Streamlit with FastAPI: Breaks requirement for simple CLI-based UI
- Full async Streamlit app: Requires major refactoring; Streamlit's async support is limited

### Decision: State Management via Agent Threads
Agent Framework manages conversation history via `AgentThread`. We'll:
- Create one thread per workflow session
- Store thread reference in `st.session_state`
- Let framework handle message history

**Rationale**: Reduces custom state logic; framework handles persistence if moved to durable agents later.

**Alternatives Considered**:
- Keep custom `WorkflowState` class: Redundant with Agent Framework's thread model
- Store raw chat history: No structured state; error handling weaker

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Streamlit + async mismatch | Use `asyncio.run()` wrapper; limit async to workflow execution, not UI logic |
| Streaming event complexity | Accumulate events before Streamlit rerun; display final output |
| Migration effort | Phased: agents first, then workflow, then UI integration |
| API key configuration changes | Document new env vars needed; validate in startup |

## Migration Path

1. **Phase 1**: Create Agent Framework agents (ChatAgent-based)
   - Set up chat client factory based on config
   - Define lyric-template agent with system instructions

2. **Phase 2**: Build workflow using WorkflowBuilder
   - Create workflow with start executor (lyric-template agent)
   - Design execution and event handling

3. **Phase 3**: Integrate with Streamlit UI
   - Adapt `run_workflow()` to invoke Agent Framework workflow
   - Handle streaming/events; display results
   - Test end-to-end

## Open Questions
- Should we support both OpenAI and Azure OpenAI APIs? (Yes, keep current config pattern)
- Do we need function tools for agents? (No for MVP; add later if needed)
- Should workflow results be persisted to disk? (No for MVP; session state only)

