# Design: Generate and Review Lyrics with Human-in-Loop Iteration

## Context
The application currently has a single-agent pipeline (lyric-template agent). We now need to:
1. Collect a song idea from the user (or auto-generate one)
2. Generate lyrics using a writer agent
3. Review lyrics using a reviewer agent
4. Iterate on writer feedback until the reviewer is satisfied

## Architecture Decisions

### Decision: Two-Agent Loop (Writer → Reviewer → Feedback)
Use `WorkflowBuilder` to orchestrate:
```
LyricTemplateAgent → [USER PAUSE] → LyricWriterAgent → LyricReviewerAgent → [Feedback Loop]
```

**Rationale**:
- Separates concerns (generation vs. critique)
- Allows iteration without regenerating template
- Reviewer provides structured feedback (style, plagiarism, etc.)

**Alternatives Considered**:
- Single "writer-reviewer" agent: More fragile; harder to isolate feedback
- External review service: Adds complexity; loses Agent Framework benefits

### Decision: User-Provided vs. Auto-Generated Ideas
Collect idea from user first; if user declines, pick random from `data/starter_ideas.txt`.

**Rationale**:
- Prioritizes user intent
- Fallback ensures workflow always proceeds
- Easy to expand starter ideas over time

**Alternatives Considered**:
- Always auto-generate: Removes user control
- Manual entry only: Blocks workflow if user has no idea

### Decision: Iteration Until Reviewer Satisfied
The reviewer agent outputs a "satisfied" flag; loop continues until true or max iterations reached.

**Rationale**:
- Ensures quality before finalizing
- Allows user to see feedback process
- Caps runaway loops with max iteration limit (suggest 3)

**Alternatives Considered**:
- Single pass: No quality assurance
- Ask user to manually approve: More UI complexity

### Decision: Starter Ideas in Text File
Store 10 starter ideas in `data/starter_ideas.txt` (one per line).
Agents access via `pick_random_idea()` tool.

**Rationale**:
- Simple, version-controllable
- Easy for user to add more over time (edit file + git)
- No database needed for MVP

**Alternatives Considered**:
- Hardcoded in agent: Harder to extend
- Database: Over-engineered for MVP

### Decision: Feedback Loop in Streamlit UI
After writer output, display reviewer feedback with options:
- "Accept and finalize"
- "Revise (generate new lyrics with feedback)"

**Rationale**:
- Gives user control
- Shows reasoning behind revisions
- Simple UI (no complex state machines)

**Alternatives Considered**:
- Fully automated iterations: Removes user visibility
- Manual feedback entry: More work for user

## Agent Implementations

### LyricWriterAgent (ChatAgent)
**System Prompt**: Instructs agent to generate lyrics based on style template + song idea.
```
- Input: Style template + song idea
- Output: Complete set of lyrics (verse, chorus, bridge, etc.)
- Tools: None (uses template context directly)
```

### LyricReviewerAgent (ChatAgent)
**System Prompt**: Instructs agent to critique lyrics.
```
- Input: Lyrics + style template
- Output: Feedback object with:
  - satisfied: boolean (does it match template?)
  - style_feedback: string (specific issues)
  - plagiarism_concerns: string (potential matches from training knowledge)
  - revision_suggestions: string (how to improve)
- Tools: None (uses LLM knowledge directly)
- Special instruction: Check for phrases that resemble famous songs or overused clichés
  based on training knowledge; flag as warnings, not blockers
```

## Session State Extension
```python
workflow_state = {
  "inputs": { "artists", "songs", "guidance" },
  "outputs": {
    "template": str,
    "idea": str,  # NEW
    "lyrics": str,  # NEW
    "feedback_history": [  # NEW - track iterations
      { "iteration": 1, "feedback": {...}, "lyrics": {...} },
      ...
    ]
  },
  "status": "idea_collection" | "generating_lyrics" | "reviewing" | "complete" | "error"
}
```

## UI Flow
1. **Display Template** (current)
2. **Collect Idea** (NEW)
   - Show template
   - Input field: "Song idea or title"
   - Button: "Use My Idea" or "Surprise Me"
3. **Generate & Review Loop** (NEW)
   - Show spinner: "Generating lyrics..."
   - Display lyrics with reviewer feedback
   - Loop controls: "Accept" or "Revise"
4. **Final Output** (NEW)
   - Display final lyrics
   - Show revision history (optional)
   - Export options (future)

## Risks & Trade-offs

| Risk | Mitigation |
|------|-----------|
| Iteration loop never converges | Cap at 3 iterations; allow manual acceptance |
| Reviewer too strict | Adjust system prompt; expose satisfaction threshold |
| Plagiarism detection naive | Use simple phrase matching for MVP; improve later |
| User overwhelmed by feedback | Show concise feedback; offer "details" expansion |

## Open Questions
1. Max iteration count: 3 or configurable?
2. Show full feedback history or just current iteration?
3. Should plagiarism_check tool be real API call or simple pattern matching?
4. Starter ideas: exactly 10, or more/fewer?

