# Proposal: Migrate to Microsoft Agent Framework Workflows

## Summary

Replace the custom `LyricWorkflow` orchestration with Microsoft Agent Framework's native workflow patterns (`SequentialBuilder`) and human-in-the-loop support (`approval_mode`, `RequestInfoEvent`). This aligns the codebase with framework best practices and enables native HITL at each workflow step.

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
2. **Native HITL** - Each step can pause for user approval using `RequestInfoEvent`
3. **Portability** - Workflow can run via CLI, API, or UI
4. **Checkpointing** - Save/resume workflows across sessions
5. **Better event streaming** - Use `WorkflowEvent` hierarchy for progress tracking
6. **Testability** - Workflow logic is decoupled from UI

## Scope

### In Scope
- Replace `LyricWorkflow` with `SequentialBuilder`-based workflow
- Implement HITL approval points using `approval_mode` and `RequestInfoEvent`
- Refactor Streamlit to consume workflow events
- Add workflow state persistence (optional phase 2)

### Out of Scope
- Changing agent prompts or behavior
- Adding new agents or capabilities
- Changing the fundamental 4-step workflow structure

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
WorkflowRunner (thin adapter)
    ↓
SequentialBuilder workflow with HITL
    ↓
Framework events (RequestInfoEvent, WorkflowCompletedEvent)
    ↓
UI handles events and sends responses
```

### Workflow Structure

```python
from agent_framework import SequentialBuilder, Executor, handler

# Phase 1: Template Generation
template_executor = TemplateExecutor(template_agent)

# Phase 2: Lyric Generation with Review Loop
lyric_executor = LyricGenerationExecutor(writer_agent, reviewer_agent)

# Phase 3: Production
producer_executor = ProducerExecutor(producer_agent)

workflow = (
    SequentialBuilder()
    .participants([
        template_executor,      # Generates blueprint, requests song idea
        lyric_executor,         # Generates + reviews, requests acceptance
        producer_executor,      # Generates Suno output
    ])
    .build()
)
```

### Human-in-the-Loop Points

| Step | HITL Type | User Action |
|------|-----------|-------------|
| After template generation | `RequestInfoEvent` | Provide song idea |
| After lyric generation | `RequestInfoEvent` | Accept, revise, or provide feedback |
| After producer output | None (final) | Copy outputs to Suno |

### Custom Executors

The framework's `SequentialBuilder` supports custom `Executor` classes for complex logic:

```python
class LyricGenerationExecutor(Executor):
    """Handles the writer/reviewer loop with HITL approval."""

    def __init__(self, writer_agent, reviewer_agent, max_iterations=3):
        self.writer = writer_agent
        self.reviewer = reviewer_agent
        self.max_iterations = max_iterations

    @handler
    async def generate_and_review(self, conversation, ctx):
        template = extract_template(conversation)

        # Request song idea from user
        idea = await ctx.request_input(
            prompt="Please provide a song idea or theme:",
            input_type="text"
        )

        # Iterative generation loop
        for iteration in range(self.max_iterations):
            lyrics = await self.writer.run(template, idea, feedback)
            review = await self.reviewer.run(template, lyrics)

            if review.satisfied:
                break
            feedback = review.revision_suggestions

        # Request user acceptance
        accepted = await ctx.request_approval(
            message=f"Generated lyrics after {iteration+1} iterations:",
            content=lyrics,
            options=["Accept", "Revise", "Regenerate"]
        )

        if accepted == "Revise":
            user_feedback = await ctx.request_input("What changes would you like?")
            # Continue loop with user feedback

        return conversation + [ChatMessage(role="assistant", text=lyrics)]
```

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Framework API changes | Low | High | Pin dependency versions |
| Streamlit event handling complexity | Medium | Medium | Build thin adapter layer |
| Migration breaks existing functionality | Medium | High | Comprehensive testing, feature flags |
| Learning curve for framework patterns | Low | Low | Documentation, incremental adoption |

## Dependencies

- `agent-framework` package with workflows support
- Understanding of `SequentialBuilder`, `Executor`, `RequestInfoEvent` patterns
- Streamlit async compatibility (may need websocket approach for true streaming)

## Success Criteria

1. Workflow runs identically to current behavior
2. Each HITL point uses native framework patterns
3. Workflow can be tested without Streamlit
4. Events stream to UI in real-time
5. No regression in user experience
