# Design: Workflow Orchestration

## Context
The application needs to coordinate multiple AI agents in a pipeline to generate song lyrics. The pipeline will eventually include: lyric-template → lyric-writer → lyric-reviewer → song-arranger. This design establishes the orchestration pattern starting with one agent.

## Goals
- Create extensible workflow orchestration that supports sequential agent execution
- Provide a simple landing page with workflow inputs
- Store intermediate results for debugging and user review

## Non-Goals
- Chat interface (removed - workflow-only approach)
- Multi-agent parallel execution (not needed for this linear pipeline)
- Complex branching or conditional workflows
- Persistent storage beyond session state (MVP scope)

## Decisions

### Decision: Sequential Pipeline Pattern
Use a simple sequential pipeline where each agent's output becomes the next agent's input.

**Alternatives considered:**
- Orchestrator agent that decides routing → More complex, not needed for linear flow
- Event-driven architecture → Overkill for 4-step pipeline

### Decision: Single-Page Workflow UI
Landing page contains the workflow inputs directly:
- Artist(s) text input
- Song(s) text input
- Other guidance text area
- Generate button

No multi-page navigation needed.

### Decision: Workflow State in Session
Store workflow progress in `st.session_state` with clear structure:

```python
st.session_state.workflow = {
    "inputs": {
        "artists": "",
        "songs": "",
        "guidance": "",
    },
    "outputs": {
        "template": None,  # LyricTemplateAgent output
        "lyrics": None,    # Future: LyricWriterAgent output
        "reviewed": None,  # Future: LyricReviewerAgent output
        "arranged": None,  # Future: SongArrangerAgent output
    },
    "status": "idle",  # idle, running, complete, error
    "error": None,
}
```

### Decision: Orchestrator Class
Create a `LyricWorkflow` class that encapsulates the pipeline logic:

```python
class LyricWorkflow:
    def __init__(self):
        self.agents = {
            "template": LyricTemplateAgent(),
            # Future agents added here
        }

    def run(self, inputs: dict) -> dict:
        """Run the full pipeline, returning all outputs."""
        # Build reference string from inputs
        reference = self._build_reference(inputs)

        outputs = {}
        outputs["template"] = self.agents["template"].analyze(reference)
        # Future steps chain here
        return outputs

    def _build_reference(self, inputs: dict) -> str:
        """Combine artist, songs, guidance into reference string."""
        parts = []
        if inputs.get("artists"):
            parts.append(f"Artist(s): {inputs['artists']}")
        if inputs.get("songs"):
            parts.append(f"Song(s): {inputs['songs']}")
        if inputs.get("guidance"):
            parts.append(f"Additional guidance: {inputs['guidance']}")
        return "\n".join(parts)
```

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Long-running pipeline blocks UI | Show progress indicator |
| Agent failures mid-pipeline | Capture partial results, show error |
| Session state lost on refresh | Accept for MVP; persistence is future enhancement |

## Open Questions
- None currently
