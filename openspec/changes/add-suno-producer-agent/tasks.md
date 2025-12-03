# Tasks: Add Suno Producer Agent

## Implementation Tasks

### 1. Create SunoProducerAgent
- [ ] Create `agents/suno_producer_agent.py`
- [ ] Define system prompt with Suno meta-tag knowledge
- [ ] Output structured JSON (style_prompt, lyric_sheet)
- [ ] Export from `agents/__init__.py`

### 2. Extend Workflow
- [ ] Add `suno_output` field to `WorkflowOutputs` dataclass
- [ ] Add `producer_guidance` field to `WorkflowInputs`
- [ ] Create `run_producer()` method in `LyricWorkflow`
- [ ] Add new status values for producer step

### 3. Update UI - Guidance Collection
- [ ] Add production guidance text area after Final Lyrics
- [ ] Add "Generate Suno Output" button
- [ ] Wire button to call workflow producer step

### 4. Update UI - Output Display
- [ ] Create `render_suno_output()` function
- [ ] Display style prompt in copyable panel
- [ ] Display formatted lyrics in copyable panel
- [ ] Add copy-to-clipboard buttons

### 5. Update Session State
- [ ] Add `producer_guidance` to inputs in session state
- [ ] Add `suno_output` to outputs in session state
- [ ] Handle state reset for new producer fields

### 6. Verification
- [ ] App starts without errors
- [ ] Full workflow runs: Template → Idea → Lyrics → Producer
- [ ] Suno output displays correctly
- [ ] Copy functionality works

## Dependencies
- Task 1 must complete before Task 2
- Tasks 3-5 can be done in parallel after Task 2
- Task 6 requires all other tasks complete
