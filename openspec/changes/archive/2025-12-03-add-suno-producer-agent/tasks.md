# Tasks: Add Suno Producer Agent

## Implementation Tasks

### 1. Create SunoProducerAgent
- [x] Create `agents/suno_producer_agent.py`
- [x] Define system prompt with Suno meta-tag knowledge
- [x] Output structured JSON (style_prompt, lyric_sheet)
- [x] Export from `agents/__init__.py`

### 2. Extend Workflow
- [x] Add `suno_output` field to `WorkflowOutputs` dataclass
- [x] Add `producer_guidance` field to `WorkflowInputs`
- [x] Create `run_producer()` method in `LyricWorkflow`
- [x] Add new status values for producer step

### 3. Update UI - Guidance Collection
- [x] Add production guidance text area after Final Lyrics
- [x] Add "Generate Suno Output" button
- [x] Wire button to call workflow producer step

### 4. Update UI - Output Display
- [x] Create `render_suno_output()` function
- [x] Display style prompt in copyable panel
- [x] Display formatted lyrics in copyable panel
- [x] Add copy-to-clipboard buttons

### 5. Update Session State
- [x] Add `producer_guidance` to inputs in session state
- [x] Add `suno_output` to outputs in session state
- [x] Handle state reset for new producer fields

### 6. Verification
- [x] App starts without errors
- [x] Full workflow runs: Template → Idea → Lyrics → Producer
- [x] Suno output displays correctly
- [x] Copy functionality works

## Dependencies
- Task 1 must complete before Task 2
- Tasks 3-5 can be done in parallel after Task 2
- Task 6 requires all other tasks complete
