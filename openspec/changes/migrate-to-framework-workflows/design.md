# Design: Migrate to Microsoft Agent Framework Workflows

## Overview

This document details the implementation approach for migrating from custom orchestration to Microsoft Agent Framework native workflows, using idiomatic framework patterns.

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
5. **nest_asyncio hack**: Required to run async code in Streamlit's sync context

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
│  │     workflow.run_stream() / send_responses_streaming()  │
│  │     - Starts workflow                                   │
│  │     - Streams events (RequestInfoEvent, etc.)          │
│  │     - Receives HITL responses                          │
│  └─────────────────────────────────────────────────────┘   │
│                     │                                       │
│                     ▼                                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              WorkflowBuilder Graph                   │   │
│  │                                                       │   │
│  │  template_agent ──► IdeaCollector ──► LyricGenerator │   │
│  │       (auto)         (custom)          (custom)       │   │
│  │                                            │          │   │
│  │                                            ▼          │   │
│  │                    producer_agent ◄────────┘          │   │
│  │                         (auto)                        │   │
│  │                            │                          │   │
│  │                            ▼                          │   │
│  │                    OutputFormatter                    │   │
│  │                        (custom)                       │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Component Design

### 1. Request/Response Types

Plain dataclasses for HITL communication (no inheritance required):

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class SongIdeaRequest:
    """Request song idea from user after template generation."""
    template: str
    prompt: str = "Please provide a song idea or title:"

@dataclass
class LyricApprovalRequest:
    """Request user approval of generated lyrics."""
    lyrics: str
    iterations_used: int
    feedback_history: list = field(default_factory=list)
    prompt: str = "Review the generated lyrics:"

@dataclass
class WorkflowOutput:
    """Final workflow output with Suno-ready data."""
    style_prompt: str
    lyric_sheet: str
    template: str
    original_lyrics: str
    feedback_history: list = field(default_factory=list)
```

### 2. IdeaCollector Executor

Receives template from template_agent, requests song idea from user:

```python
from agent_framework import Executor, WorkflowContext, handler, response_handler
from agent_framework import AgentExecutorResponse

class IdeaCollector(Executor):
    """
    Collects song idea from user after template generation.

    Input: AgentExecutorResponse from template_agent
    Output: dict with template and idea
    HITL: Requests song idea via SongIdeaRequest
    """

    def __init__(self):
        super().__init__(id="idea_collector")

    @handler
    async def on_template(
        self,
        response: AgentExecutorResponse,
        ctx: WorkflowContext
    ) -> None:
        """Receive template from template_agent, request idea from user."""
        template = response.agent_run_response.text

        # Request song idea from user (HITL)
        await ctx.request_info(
            request_data=SongIdeaRequest(template=template),
            response_type=str
        )

    @response_handler
    async def on_idea_response(
        self,
        original_request: SongIdeaRequest,
        idea: str,
        ctx: WorkflowContext
    ) -> None:
        """User provided song idea, forward to lyric generation."""
        await ctx.send_message({
            "template": original_request.template,
            "idea": idea
        })
```

### 3. LyricGenerator Executor

Handles the writer/reviewer iteration loop and user approval:

```python
from agent_framework import Executor, WorkflowContext, handler, response_handler
from agent_framework import ChatAgent
import json

class LyricGenerator(Executor):
    """
    Generates lyrics with writer/reviewer loop and user approval.

    Input: dict with template and idea
    Output: dict with lyrics and feedback_history
    HITL: Requests lyric approval via LyricApprovalRequest
    """

    def __init__(
        self,
        writer_agent: ChatAgent,
        reviewer_agent: ChatAgent,
        max_iterations: int = 3
    ):
        super().__init__(id="lyric_generator")
        self.writer = writer_agent
        self.reviewer = reviewer_agent
        self.max_iterations = max_iterations

    @handler
    async def generate(
        self,
        input_data: dict,
        ctx: WorkflowContext
    ) -> None:
        """Run writer/reviewer loop, then request user approval."""
        template = input_data["template"]
        idea = input_data["idea"]

        feedback_history = []
        lyrics = None

        for iteration in range(self.max_iterations):
            # Build writer prompt
            if iteration == 0:
                writer_prompt = (
                    f"Style Template:\n{template}\n\n"
                    f"Song Idea/Title: {idea}\n\n"
                    f"Generate complete lyrics matching this template."
                )
            else:
                last_feedback = feedback_history[-1]["feedback"]
                writer_prompt = (
                    f"Style Template:\n{template}\n\n"
                    f"Song Idea/Title: {idea}\n\n"
                    f"Revision Feedback:\n{last_feedback['revision_suggestions']}\n\n"
                    f"Generate revised lyrics incorporating the feedback above."
                )

            # Generate lyrics
            writer_response = await self.writer.run(writer_prompt)
            lyrics = writer_response.text

            # Build reviewer prompt
            reviewer_prompt = (
                f"Style Template:\n{template}\n\n"
                f"Generated Lyrics:\n{lyrics}\n\n"
                f"Provide feedback in JSON format."
            )

            # Review lyrics
            reviewer_response = await self.reviewer.run(reviewer_prompt)
            feedback = self._parse_feedback(reviewer_response.text)

            feedback_history.append({
                "iteration": iteration + 1,
                "lyrics": lyrics,
                "feedback": feedback
            })

            if feedback.get("satisfied", False):
                break

        # Request user approval (HITL)
        await ctx.request_info(
            request_data=LyricApprovalRequest(
                lyrics=lyrics,
                iterations_used=len(feedback_history),
                feedback_history=feedback_history
            ),
            response_type=bool
        )

    @response_handler
    async def on_approval_response(
        self,
        original_request: LyricApprovalRequest,
        approved: bool,
        ctx: WorkflowContext
    ) -> None:
        """User approved or rejected lyrics."""
        if approved:
            # Forward to producer
            await ctx.send_message({
                "lyrics": original_request.lyrics,
                "feedback_history": original_request.feedback_history
            })
        else:
            # User rejected - could request feedback and regenerate
            # For MVP: just re-run generation (user can provide new idea)
            # This is a simplification - could add more sophisticated handling
            await ctx.send_message({
                "lyrics": original_request.lyrics,
                "feedback_history": original_request.feedback_history,
                "user_rejected": True
            })

    def _parse_feedback(self, feedback_text: str) -> dict:
        """Parse JSON feedback from reviewer."""
        try:
            return json.loads(feedback_text)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', feedback_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {
                "satisfied": False,
                "style_feedback": feedback_text,
                "revision_suggestions": "Please try again."
            }
```

### 4. OutputFormatter Executor

Parses producer output and yields final workflow result:

```python
from agent_framework import Executor, WorkflowContext, handler
from agent_framework import AgentExecutorResponse
from typing import Never
import json

class OutputFormatter(Executor):
    """
    Formats final output from producer agent.

    Input: AgentExecutorResponse from producer_agent + context
    Output: WorkflowOutput (yielded as final result)
    """

    def __init__(self):
        super().__init__(id="output_formatter")
        self._pending_context: dict = {}

    @handler
    async def on_lyrics_context(
        self,
        context_data: dict,
        ctx: WorkflowContext
    ) -> None:
        """Store context data for final output."""
        self._pending_context = context_data

    @handler
    async def on_producer_response(
        self,
        response: AgentExecutorResponse,
        ctx: WorkflowContext[Never, WorkflowOutput]
    ) -> None:
        """Parse producer output and yield final result."""
        producer_output = self._parse_producer_output(response.agent_run_response.text)

        final_output = WorkflowOutput(
            style_prompt=producer_output.get("style_prompt", ""),
            lyric_sheet=producer_output.get("lyric_sheet", ""),
            template=self._pending_context.get("template", ""),
            original_lyrics=self._pending_context.get("lyrics", ""),
            feedback_history=self._pending_context.get("feedback_history", [])
        )

        await ctx.yield_output(final_output)

    def _parse_producer_output(self, output: str) -> dict:
        """Parse JSON output from producer agent."""
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', output, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {
                "style_prompt": "Error: Could not parse",
                "lyric_sheet": output
            }
```

### 5. Workflow Builder

```python
from agent_framework import WorkflowBuilder, ChatAgent

def build_suno_workflow(
    template_agent: ChatAgent,
    writer_agent: ChatAgent,
    reviewer_agent: ChatAgent,
    producer_agent: ChatAgent,
    max_iterations: int = 3
):
    """
    Build the Suno Prompter workflow using framework patterns.

    Workflow graph:
        template_agent → IdeaCollector → LyricGenerator → producer_agent → OutputFormatter
                         (HITL: idea)    (HITL: approval)
    """

    # Create custom executors
    idea_collector = IdeaCollector()
    lyric_generator = LyricGenerator(writer_agent, reviewer_agent, max_iterations)
    output_formatter = OutputFormatter()

    # Build workflow graph
    workflow = (
        WorkflowBuilder()
        # Start: user input → template agent (auto-wrapped)
        .set_start_executor(template_agent)
        # Template agent → idea collector (HITL for song idea)
        .add_edge(template_agent, idea_collector)
        # Idea collector → lyric generator (writer/reviewer loop + HITL)
        .add_edge(idea_collector, lyric_generator)
        # Lyric generator → producer agent (auto-wrapped)
        .add_edge(lyric_generator, producer_agent)
        # Producer agent → output formatter
        .add_edge(producer_agent, output_formatter)
        .build()
    )

    return workflow
```

### 6. Streamlit Adapter

Handles the HITL request/response cycle with Streamlit's execution model:

```python
import streamlit as st
import asyncio
from agent_framework import RequestInfoEvent, WorkflowOutputEvent, WorkflowStatusEvent

class StreamlitWorkflowAdapter:
    """
    Adapts framework workflow to Streamlit's execution model.

    Handles:
    - Running workflow with run_stream()
    - Collecting RequestInfoEvent for HITL
    - Sending responses via send_responses_streaming()
    - Managing session state for persistence
    """

    def __init__(self, workflow):
        self.workflow = workflow
        self._init_session_state()

    def _init_session_state(self):
        """Initialize Streamlit session state."""
        if "wf_state" not in st.session_state:
            st.session_state.wf_state = {
                "status": "idle",
                "pending_requests": [],  # List of RequestInfoEvent
                "responses": {},         # Dict of request_id -> response
                "output": None,
                "error": None,
            }

    async def run_workflow(self, initial_input: str):
        """
        Run workflow and collect events.

        Returns when workflow needs HITL or completes.
        """
        state = st.session_state.wf_state
        state["status"] = "running"
        state["pending_requests"] = []

        try:
            # Choose stream based on whether we have pending responses
            if state["responses"]:
                stream = self.workflow.send_responses_streaming(state["responses"])
                state["responses"] = {}  # Clear after sending
            else:
                stream = self.workflow.run_stream(initial_input)

            # Collect events
            async for event in stream:
                if isinstance(event, RequestInfoEvent):
                    state["pending_requests"].append(event)
                    state["status"] = "awaiting_input"

                elif isinstance(event, WorkflowOutputEvent):
                    state["output"] = event.data
                    state["status"] = "complete"

        except Exception as e:
            state["error"] = str(e)
            state["status"] = "error"

    def submit_response(self, request_id: str, response):
        """Submit user response for a HITL request."""
        state = st.session_state.wf_state
        state["responses"][request_id] = response

        # Remove from pending
        state["pending_requests"] = [
            r for r in state["pending_requests"]
            if r.request_id != request_id
        ]

    def get_pending_requests(self):
        """Get list of pending HITL requests."""
        return st.session_state.wf_state.get("pending_requests", [])

    def get_output(self):
        """Get workflow output if complete."""
        return st.session_state.wf_state.get("output")

    def get_status(self):
        """Get current workflow status."""
        return st.session_state.wf_state.get("status", "idle")

    def reset(self):
        """Reset workflow state."""
        st.session_state.wf_state = {
            "status": "idle",
            "pending_requests": [],
            "responses": {},
            "output": None,
            "error": None,
        }
```

### 7. Streamlit UI Integration

Example of rendering HITL requests in Streamlit:

```python
def render_hitl_requests(adapter: StreamlitWorkflowAdapter):
    """Render UI for pending HITL requests."""
    pending = adapter.get_pending_requests()

    for request_event in pending:
        request_data = request_event.data

        if isinstance(request_data, SongIdeaRequest):
            render_idea_request(adapter, request_event, request_data)

        elif isinstance(request_data, LyricApprovalRequest):
            render_approval_request(adapter, request_event, request_data)


def render_idea_request(adapter, event, request: SongIdeaRequest):
    """Render song idea input form."""
    st.subheader("Template Generated!")

    with st.expander("View Template", expanded=True):
        st.markdown(request.template)

    st.markdown(request.prompt)

    idea = st.text_input(
        "Song idea or title",
        placeholder="e.g., 'Midnight Reflections' or 'Breaking Free'"
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Generate Lyrics", type="primary", disabled=not idea.strip()):
            adapter.submit_response(event.request_id, idea)
            st.rerun()

    with col2:
        if st.button("Surprise Me"):
            random_idea = pick_random_idea()
            adapter.submit_response(event.request_id, random_idea)
            st.rerun()


def render_approval_request(adapter, event, request: LyricApprovalRequest):
    """Render lyric approval form."""
    st.subheader("Generated Lyrics")
    st.markdown(f"*Completed in {request.iterations_used} iteration(s)*")

    st.markdown(request.lyrics)

    with st.expander("View Feedback History"):
        for entry in request.feedback_history:
            st.markdown(f"**Iteration {entry['iteration']}**")
            st.markdown(entry["feedback"].get("style_feedback", ""))

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Accept & Continue", type="primary"):
            adapter.submit_response(event.request_id, True)
            st.rerun()

    with col2:
        if st.button("Regenerate"):
            adapter.submit_response(event.request_id, False)
            st.rerun()
```

## File Structure

```
src/suno_prompter/
├── workflows/
│   ├── __init__.py              # Exports build_suno_workflow
│   ├── builder.py               # build_suno_workflow function
│   ├── types.py                 # Request/response dataclasses
│   └── executors/
│       ├── __init__.py
│       ├── idea_collector.py    # IdeaCollector executor
│       ├── lyric_generator.py   # LyricGenerator executor
│       └── output_formatter.py  # OutputFormatter executor
├── adapters/
│   ├── __init__.py
│   └── streamlit_adapter.py     # StreamlitWorkflowAdapter
└── app.py                       # Refactored Streamlit app
```

## Event Flow

### Happy Path

```
1. User submits artist/songs/guidance
   └─► workflow.run_stream("Artist: X, Songs: Y")

2. template_agent generates blueprint
   └─► AgentRunUpdateEvent (streaming)
   └─► Sends AgentExecutorResponse to IdeaCollector

3. IdeaCollector receives template
   └─► Calls ctx.request_info(SongIdeaRequest)
   └─► RequestInfoEvent emitted
   └─► Workflow pauses

4. Streamlit renders idea input form
   └─► User enters "Midnight Dreams"
   └─► adapter.submit_response(request_id, "Midnight Dreams")

5. workflow.send_responses_streaming({request_id: "Midnight Dreams"})
   └─► IdeaCollector.on_idea_response receives idea
   └─► Sends {template, idea} to LyricGenerator

6. LyricGenerator runs writer/reviewer loop
   └─► (Internal iteration - no events)
   └─► Calls ctx.request_info(LyricApprovalRequest)
   └─► RequestInfoEvent emitted
   └─► Workflow pauses

7. Streamlit renders approval form
   └─► User clicks "Accept"
   └─► adapter.submit_response(request_id, True)

8. workflow.send_responses_streaming({request_id: True})
   └─► LyricGenerator.on_approval_response
   └─► Sends lyrics to producer_agent

9. producer_agent generates Suno output
   └─► AgentRunUpdateEvent (streaming)
   └─► Sends AgentExecutorResponse to OutputFormatter

10. OutputFormatter yields final result
    └─► WorkflowOutputEvent with WorkflowOutput
    └─► Workflow completes

11. Streamlit displays Suno outputs
```

## Testing Strategy

### Unit Tests

```python
# Test executors in isolation
async def test_idea_collector():
    executor = IdeaCollector()
    # Mock context and verify request_info is called correctly

async def test_lyric_generator_satisfied_first_try():
    # Mock agents that return satisfied=true immediately
    # Verify only 1 iteration

async def test_lyric_generator_max_iterations():
    # Mock agents that never satisfy
    # Verify stops at max_iterations
```

### Integration Tests

```python
# Test full workflow without UI
async def test_workflow_happy_path():
    workflow = build_suno_workflow(...)

    # Start workflow
    events = []
    async for event in workflow.run_stream("Artist: Beatles"):
        events.append(event)
        if isinstance(event, RequestInfoEvent):
            break

    # Should have idea request
    assert isinstance(events[-1], RequestInfoEvent)
    assert isinstance(events[-1].data, SongIdeaRequest)

    # Send idea response
    async for event in workflow.send_responses_streaming({
        events[-1].request_id: "Yellow Submarine"
    }):
        events.append(event)
        if isinstance(event, RequestInfoEvent):
            break

    # Should have approval request
    assert isinstance(events[-1].data, LyricApprovalRequest)

    # ... continue testing
```

## Migration Path

### Phase 1: Core Infrastructure
1. Create `workflows/types.py` with dataclasses
2. Create `workflows/executors/` with 3 executors
3. Create `workflows/builder.py`
4. Add unit tests

### Phase 2: Adapter Layer
1. Create `adapters/streamlit_adapter.py`
2. Test adapter with mock workflow

### Phase 3: App Integration
1. Refactor `app.py` to use adapter
2. Remove old `LyricWorkflow` class
3. Integration testing

### Phase 4: Cleanup
1. Remove `nest_asyncio` dependency
2. Update documentation
3. Performance testing

## Open Questions (Resolved)

1. **Streamlit async model**: Use `send_responses_streaming()` pattern - workflow pauses at HITL, Streamlit reruns handle responses.

2. **Framework version**: Use `agent-framework-core` package, pin version in requirements.

3. **Writer/reviewer loop**: Encapsulate in `LyricGenerator` executor - cleaner than graph-level conditional edges for this use case.

4. **Custom executors needed**: Yes, 3 minimal executors for HITL coordination. Agents are auto-wrapped.
