# Tasks: Generate and Review Lyrics with Human-in-Loop Iteration

## 1. Foundation & Data

- [x] 1.1 Create `data/starter_ideas.txt` with 10 initial song topic ideas (one per line)
- [x] 1.2 Implement `pick_random_idea()` utility function in utils module
- [x] 1.3 Test `pick_random_idea()` independently: load file, select random, return idea

## 2. Lyric Writer Agent

- [x] 2.1 Create `agents/lyric_writer_agent.py` using ChatAgent from Agent Framework
- [x] 2.2 Define system prompt that emphasizes:
  - Adhering to style template structure (verse, chorus, bridge, etc.)
  - Matching rhyme schemes and meter from template
  - Incorporating user's song idea/theme
  - Originality and not copying existing songs
- [x] 2.3 Wire chat client from factory based on environment config
- [x] 2.4 Implement `create_lyric_writer_agent()` factory function
- [x] 2.5 Test writer agent standalone: provide template + idea, verify lyrics are generated

## 3. Lyric Reviewer Agent

- [x] 3.1 Create `agents/lyric_reviewer_agent.py` using ChatAgent from Agent Framework
- [x] 3.2 Define system prompt that instructs agent to:
  - Compare lyrics against style template requirements
  - Evaluate rhyme scheme and meter adherence
  - Check for plagiarism/clichés using LLM training knowledge
  - Flag plagiarism concerns as warnings (not blockers)
  - Provide constructive revision suggestions
  - Output satisfaction assessment (satisfied or not)
- [x] 3.3 Implement structured feedback output (dataclass with: satisfied, style_feedback, plagiarism_concerns, revision_suggestions)
- [x] 3.4 Wire chat client from factory
- [x] 3.5 Implement `create_lyric_reviewer_agent()` factory function
- [x] 3.6 Test reviewer agent standalone: provide template + lyrics, verify feedback is structured and plagiarism concerns are included

## 4. Workflow Orchestration

- [x] 4.1 Extend `workflows/lyric_workflow.py`:
  - Add `idea` field to `WorkflowInputs`
  - Add `idea`, `feedback_history` fields to `WorkflowOutputs`
  - Add new status: "idea_collection", "generating_lyrics", "reviewing"
- [x] 4.2 Extend `LyricWorkflow` to support writer → reviewer loop:
  - Add `lyric_writer_agent` and `lyric_reviewer_agent` initialization
  - Add `_generate_and_review_lyrics()` method that handles idea + writer + reviewer loop
  - Implement iteration limit (max 3)
  - Store feedback history in outputs
- [x] 4.3 Update workflow to integrate writer and reviewer agents:
  - Set up sequential execution: template → writer → reviewer
  - Configure for async/await execution
  - Implement JSON feedback parsing
- [x] 4.4 Test workflow: provide template + idea, verify writer generates lyrics and reviewer critiques

## 5. Streamlit UI Integration

- [ ] 5.1 Update `app.py`:
  - Add `render_idea_collection()` function after template display
  - Show template and ask for idea (text input + "Surprise Me" button)
  - Call `pick_random_idea()` on "Surprise Me"
- [ ] 5.2 Update session state structure:
  - Add `idea` field to workflow inputs
  - Add `feedback_history` to workflow outputs
  - Add iteration counter and max iterations config
- [ ] 5.3 Extend `run_workflow()` to:
  - Capture user-provided or auto-generated idea
  - Call workflow with idea
  - Handle multiple iterations (loop based on satisfaction)
- [ ] 5.4 Add `render_lyrics_and_feedback()` function:
  - Display generated lyrics
  - Display reviewer feedback (expandable)
  - Show iteration count and revision suggestions
  - Buttons: "Accept and Finalize" or "Revise Lyrics"
- [ ] 5.5 Add `render_final_lyrics()` function:
  - Display final accepted lyrics
  - Show revision history (optional collapse)
  - Prepare for future export functionality
- [ ] 5.6 Test UI flow manually:
  - Generate template
  - Enter idea or use "Surprise Me"
  - See lyrics generated
  - See reviewer feedback
  - Iterate if needed
  - Finalize and display

## 6. Configuration & Testing

- [ ] 6.1 Validate agents initialize with current Azure OpenAI config
- [ ] 6.2 Test writer agent with multiple template styles
- [ ] 6.3 Test reviewer agent with various lyrics (good adherence, poor adherence, potential plagiarism)
- [ ] 6.4 Test idea collection:
  - Manual idea entry
  - "Surprise Me" with random selection
  - Verify ideas persist across iterations
- [ ] 6.5 Test iteration loop:
  - Verify max 3 iterations enforced
  - Verify feedback accumulates correctly
  - Verify user can force finalize after max iterations
- [ ] 6.6 Run app locally: `streamlit run app.py`
  - Complete full workflow: template → idea → lyrics → feedback → accept
  - Test iteration loop (request revision, see new lyrics)
  - Verify session state persists correctly

## 7. Cleanup & Documentation

- [x] 7.1 Update `agents/__init__.py` to export new factory functions
- [x] 7.2 Add docstrings to new agent factory functions
- [x] 7.3 Document iteration limit and feedback thresholds in code comments
- [ ] 7.4 Clean up any debug logging or temporary prints
- [ ] 7.5 Update README with new features (idea collection, iteration loop)
- [ ] 7.6 Verify no unused imports or dead code

## Dependencies
- Sections 1–3 can run in parallel (agents and data independent)
- Section 4 depends on completion of sections 1–3
- Section 5 depends on completion of section 4
- Sections 6–7 depend on all prior sections

## Validation Checkpoints
1. After 1–3: Each agent produces expected output independently
2. After 4: Workflow orchestrates agents correctly with iteration loop
3. After 5: UI renders all new screens without errors
4. After 6: Full end-to-end test passes with manual verification
5. After 7: Code is clean and documented for handoff

