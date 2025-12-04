# Design: Migrate to Microsoft Agent Framework Workflows

## Overview

This document details the architectural decisions and implementation approach for migrating from custom orchestration to Microsoft Agent Framework native workflows.

## Current Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Streamlit App                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Session State Manager                   │   │
│  │  - workflow inputs/outputs                          │   │
│  │  - status tracking                                  │   │
│  │  - iteration count                                  │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              LyricWorkflow (Custom)                  │   │
│  │  - Manual agent sequencing                          │   │
│  │  - Async loop with nest_asyncio                     │   │
│  │  - JSON parsing for structured outputs              │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│         ┌─────────────────┼─────────────────┐              │
│         ▼                 ▼                 ▼              │
│  ┌───────────┐     ┌───────────┐     ┌───────────┐        │
│  │ Template  │     │  Writer   │     │ Producer  │        │
│  │  Agent    │     │  Agent    │     │  Agent    │        │
│  └───────────┘     └───────────┘     └───────────┘        │
│                         │                                  │
│                         ▼                                  │
│                  ┌───────────┐                             │
│                  │ Reviewer  │                             │
│                  │  Agent    │                             │
│                  └───────────┘                             │
└─────────────────────────────────────────────────────────────┘
```

### Current Pain Points

1. **Tight coupling**: Orchestration logic mixed with UI state management
2. **Manual HITL**: UI buttons trigger workflow continuation, not framework events
3. **No event stream**: Progress shown via polling session state, not reactive events
4. **Single transport**: Only works via Streamlit

## Proposed Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Transport Layer                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │Streamlit │  │   CLI    │  │   API    │                  │
│  │ Adapter  │  │ Adapter  │  │ Adapter  │                  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                  │
│       └─────────────┼─────────────┘                        │
│                     ▼                                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              WorkflowRunner                          │   │
│  │  - Starts workflow                                  │   │
│  │  - Routes events to transport                       │   │
│  │  - Handles HITL responses                           │   │
│  └─────────────────────────────────────────────────────┘   │
│                     │                                       │
│                     ▼                                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         SequentialBuilder Workflow                   │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │   │
│  │  │  Template   │→│   Lyric     │→│  Producer   │  │   │
│  │  │  Executor   │  │  Executor   │  │  Executor   │  │   │
│  │  │             │  │ (w/ loop)   │  │             │  │   │
│  │  │ HITL: idea  │  │ HITL: accept│  │             │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
│                     │                                       │
│                     ▼                                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  Agent Layer                         │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐│   │
│  │  │ Template │ │  Writer  │ │ Reviewer │ │Producer ││   │
│  │  │  Agent   │ │  Agent   │ │  Agent   │ │ Agent   ││   │
│  │  └──────────┘ └──────────┘ └──────────┘ └─────────┘│   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Component Design

### 1. Custom Executors

The framework's `Executor` base class allows custom logic while integrating with the workflow system.

#### TemplateExecutor

```python
from agent_framework import Executor, handler, WorkflowContext, ChatMessage, Role

class TemplateExecutor(Executor):
    """
    Executes template agent and requests song idea from user.

    Input: User's artist/song/guidance references
    Output: Template + song idea ready for lyric generation
    HITL: Requests song idea after template generation
    """

    def __init__(self, template_agent, id: str = "template_executor"):
        super().__init__(id=id)
        self.agent = template_agent

    @handler
    async def execute(
        self,
        conversation: list[ChatMessage],
        ctx: WorkflowContext
    ) -> None:
        # Extract user's reference input
        user_input = conversation[-1].text

        # Generate template
        template_result = await self.agent.run(user_input)
        template = template_result.text

        # Emit template to UI
        await ctx.emit_event("template_generated", {"template": template})

        # Request song idea from user (HITL)
        idea = await ctx.request_input(
            prompt="Template generated! Please provide a song idea or theme:",
            metadata={"template": template}
        )

        # Pass template + idea to next executor
        await ctx.send_message([
            *conversation,
            ChatMessage(role=Role.ASSISTANT, text=template, author_name="template_agent"),
            ChatMessage(role=Role.USER, text=f"Song idea: {idea}", author_name="user"),
        ])
```

#### LyricExecutor

```python
class LyricExecutor(Executor):
    """
    Executes writer/reviewer loop with user acceptance HITL.

    Input: Template + song idea
    Output: Accepted lyrics
    HITL: User accepts, requests revision, or provides feedback
    """

    def __init__(
        self,
        writer_agent,
        reviewer_agent,
        max_iterations: int = 3,
        id: str = "lyric_executor"
    ):
        super().__init__(id=id)
        self.writer = writer_agent
        self.reviewer = reviewer_agent
        self.max_iterations = max_iterations

    @handler
    async def execute(
        self,
        conversation: list[ChatMessage],
        ctx: WorkflowContext
    ) -> None:
        template = self._extract_template(conversation)
        idea = self._extract_idea(conversation)

        feedback = None
        feedback_history = []

        for iteration in range(self.max_iterations):
            # Emit progress
            await ctx.emit_event("lyric_generation_started", {
                "iteration": iteration + 1,
                "max_iterations": self.max_iterations
            })

            # Generate lyrics
            writer_prompt = self._build_writer_prompt(template, idea, feedback)
            lyrics_result = await self.writer.run(writer_prompt)
            lyrics = lyrics_result.text

            # Review lyrics
            reviewer_prompt = self._build_reviewer_prompt(template, lyrics)
            review_result = await self.reviewer.run(reviewer_prompt)
            review = self._parse_review(review_result.text)

            feedback_history.append({
                "iteration": iteration + 1,
                "lyrics": lyrics,
                "review": review
            })

            await ctx.emit_event("lyric_review_complete", {
                "iteration": iteration + 1,
                "satisfied": review["satisfied"],
                "feedback": review
            })

            if review["satisfied"]:
                break

            feedback = review["revision_suggestions"]

        # Request user acceptance (HITL)
        decision = await ctx.request_approval(
            prompt="Lyrics generated. Please review:",
            content=lyrics,
            options=["Accept", "Request Changes"],
            metadata={"feedback_history": feedback_history}
        )

        if decision == "Request Changes":
            user_feedback = await ctx.request_input(
                prompt="What changes would you like?",
                input_type="text"
            )
            # Could loop again or pass to next iteration
            # For MVP: pass user feedback and regenerate once
            final_prompt = self._build_writer_prompt(template, idea, user_feedback)
            final_result = await self.writer.run(final_prompt)
            lyrics = final_result.text

        # Pass accepted lyrics to next executor
        await ctx.send_message([
            *conversation,
            ChatMessage(role=Role.ASSISTANT, text=lyrics, author_name="lyric_writer"),
        ])
```

#### ProducerExecutor

```python
class ProducerExecutor(Executor):
    """
    Executes producer agent to generate Suno-ready outputs.

    Input: Accepted lyrics + template
    Output: Style prompt + formatted lyric sheet
    HITL: Optional production guidance before generation
    """

    def __init__(self, producer_agent, id: str = "producer_executor"):
        super().__init__(id=id)
        self.agent = producer_agent

    @handler
    async def execute(
        self,
        conversation: list[ChatMessage],
        ctx: WorkflowContext
    ) -> None:
        template = self._extract_template(conversation)
        lyrics = self._extract_lyrics(conversation)

        # Optional: Request production guidance (HITL)
        guidance = await ctx.request_input(
            prompt="Any production guidance? (optional, press Enter to skip)",
            input_type="text",
            optional=True
        )

        # Generate Suno output
        producer_prompt = self._build_producer_prompt(template, lyrics, guidance)
        result = await self.agent.run(producer_prompt)
        output = self._parse_producer_output(result.text)

        # Emit final output
        await ctx.emit_event("workflow_output", {
            "style_prompt": output["style_prompt"],
            "lyric_sheet": output["lyric_sheet"]
        })

        await ctx.send_message([
            *conversation,
            ChatMessage(
                role=Role.ASSISTANT,
                text=json.dumps(output),
                author_name="producer"
            ),
        ])
```

### 2. Workflow Builder

```python
from agent_framework import SequentialBuilder

def build_suno_workflow(
    template_agent,
    writer_agent,
    reviewer_agent,
    producer_agent,
    max_iterations: int = 3
):
    """Build the Suno Prompter workflow using framework patterns."""

    template_executor = TemplateExecutor(template_agent)
    lyric_executor = LyricExecutor(
        writer_agent,
        reviewer_agent,
        max_iterations=max_iterations
    )
    producer_executor = ProducerExecutor(producer_agent)

    workflow = (
        SequentialBuilder()
        .participants([
            template_executor,
            lyric_executor,
            producer_executor,
        ])
        .build()
    )

    return workflow
```

### 3. WorkflowRunner (Transport Adapter)

```python
from dataclasses import dataclass
from typing import Callable, Any
from agent_framework import RequestInfoEvent, WorkflowCompletedEvent, WorkflowEvent

@dataclass
class HITLRequest:
    """Represents a human-in-the-loop request."""
    request_id: str
    prompt: str
    input_type: str  # "text", "approval", "choice"
    options: list[str] | None = None
    metadata: dict | None = None

@dataclass
class WorkflowProgress:
    """Represents workflow progress for UI updates."""
    event_type: str
    data: dict

class WorkflowRunner:
    """
    Thin adapter between framework workflow and transport layer.

    Handles:
    - Starting workflows
    - Routing events to callbacks
    - Collecting HITL responses
    - Managing workflow lifecycle
    """

    def __init__(self, workflow):
        self.workflow = workflow
        self.pending_requests: dict[str, HITLRequest] = {}

    async def run(
        self,
        initial_input: str,
        on_progress: Callable[[WorkflowProgress], None],
        on_hitl_request: Callable[[HITLRequest], None],
    ) -> dict:
        """
        Run workflow with callbacks for progress and HITL.

        Args:
            initial_input: User's initial input (artist/songs/guidance)
            on_progress: Callback for progress events
            on_hitl_request: Callback when user input is needed

        Returns:
            Final workflow output
        """
        async for event in self.workflow.run_stream(initial_input):
            if isinstance(event, RequestInfoEvent):
                # HITL: Pause and request user input
                request = HITLRequest(
                    request_id=event.request_id,
                    prompt=event.data.prompt,
                    input_type=event.data.input_type,
                    options=event.data.options,
                    metadata=event.data.metadata
                )
                self.pending_requests[request.request_id] = request
                on_hitl_request(request)

            elif isinstance(event, WorkflowCompletedEvent):
                return event.data

            else:
                # Progress event
                on_progress(WorkflowProgress(
                    event_type=type(event).__name__,
                    data=event.data if hasattr(event, 'data') else {}
                ))

        return {}

    async def send_response(self, request_id: str, response: Any) -> None:
        """Send user response for a HITL request."""
        if request_id in self.pending_requests:
            del self.pending_requests[request_id]
            await self.workflow.send_response(request_id, response)
```

### 4. Streamlit Adapter

```python
import streamlit as st
import asyncio
from typing import Any

class StreamlitWorkflowAdapter:
    """
    Adapts framework workflow to Streamlit's execution model.

    Handles:
    - Session state management
    - Async execution in Streamlit
    - HITL via st.form and st.button
    - Progress display
    """

    def __init__(self, workflow_runner: WorkflowRunner):
        self.runner = workflow_runner
        self._init_session_state()

    def _init_session_state(self):
        if "workflow_state" not in st.session_state:
            st.session_state.workflow_state = {
                "status": "idle",
                "progress": [],
                "pending_hitl": None,
                "outputs": {},
                "error": None
            }

    def start_workflow(self, initial_input: str):
        """Start workflow execution."""
        st.session_state.workflow_state["status"] = "running"

        # Run in background (simplified - actual impl needs careful async handling)
        asyncio.create_task(self._run_workflow(initial_input))

    async def _run_workflow(self, initial_input: str):
        try:
            result = await self.runner.run(
                initial_input,
                on_progress=self._handle_progress,
                on_hitl_request=self._handle_hitl_request
            )
            st.session_state.workflow_state["outputs"] = result
            st.session_state.workflow_state["status"] = "complete"
        except Exception as e:
            st.session_state.workflow_state["error"] = str(e)
            st.session_state.workflow_state["status"] = "error"

    def _handle_progress(self, progress: WorkflowProgress):
        st.session_state.workflow_state["progress"].append(progress)
        st.rerun()  # Trigger UI update

    def _handle_hitl_request(self, request: HITLRequest):
        st.session_state.workflow_state["pending_hitl"] = request
        st.session_state.workflow_state["status"] = "awaiting_input"
        st.rerun()

    def send_hitl_response(self, response: Any):
        """Send user response for pending HITL request."""
        pending = st.session_state.workflow_state["pending_hitl"]
        if pending:
            asyncio.create_task(
                self.runner.send_response(pending.request_id, response)
            )
            st.session_state.workflow_state["pending_hitl"] = None
            st.session_state.workflow_state["status"] = "running"

    def render_hitl_ui(self):
        """Render UI for pending HITL request."""
        pending = st.session_state.workflow_state.get("pending_hitl")
        if not pending:
            return

        st.subheader(pending.prompt)

        if pending.input_type == "text":
            with st.form("hitl_form"):
                response = st.text_area("Your input:")
                if st.form_submit_button("Submit"):
                    self.send_hitl_response(response)

        elif pending.input_type == "approval":
            cols = st.columns(len(pending.options or ["Accept", "Reject"]))
            for i, option in enumerate(pending.options or ["Accept", "Reject"]):
                if cols[i].button(option):
                    self.send_hitl_response(option)
```

## Migration Strategy

### Phase 1: Core Workflow (Week 1-2)
1. Create custom executors for each workflow stage
2. Build workflow using `SequentialBuilder`
3. Implement `WorkflowRunner` adapter
4. Unit test workflow without UI

### Phase 2: Streamlit Integration (Week 2-3)
1. Create `StreamlitWorkflowAdapter`
2. Refactor `app.py` to use adapter
3. Implement HITL UI components
4. Integration testing

### Phase 3: Cleanup & Polish (Week 3-4)
1. Remove old `LyricWorkflow` class
2. Add error handling and edge cases
3. Add progress streaming
4. Documentation

### Phase 4: Extended Features (Optional)
1. Add checkpointing for workflow resume
2. Add CLI adapter for non-UI usage
3. Add API adapter for programmatic access

## File Changes

| File | Change |
|------|--------|
| `workflows/lyric_workflow.py` | Delete (replaced by executors) |
| `workflows/__init__.py` | Export new workflow builder |
| `workflows/executors/` | New directory for custom executors |
| `workflows/executors/template_executor.py` | New |
| `workflows/executors/lyric_executor.py` | New |
| `workflows/executors/producer_executor.py` | New |
| `workflows/builder.py` | New - workflow construction |
| `workflows/runner.py` | New - `WorkflowRunner` adapter |
| `adapters/streamlit_adapter.py` | New - Streamlit integration |
| `app.py` | Refactor to use adapter |

## Testing Strategy

1. **Unit tests**: Each executor in isolation
2. **Integration tests**: Full workflow without UI
3. **E2E tests**: Workflow via Streamlit adapter
4. **Regression tests**: Compare outputs to current implementation

## Open Questions

1. **Streamlit async model**: Streamlit's execution model doesn't natively support long-running async workflows. May need:
   - WebSocket-based approach
   - Background task with polling
   - Streamlit's experimental async features

2. **Framework version**: Pin to specific `agent-framework` version to avoid breaking changes

3. **Checkpointing storage**: If implementing resume, where to store checkpoints?
   - Local filesystem
   - SQLite
   - Session state (ephemeral)

4. **Error recovery**: How to handle mid-workflow failures?
   - Retry from last checkpoint
   - Restart entire workflow
   - Manual intervention
