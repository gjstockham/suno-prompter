# Tasks: Add Workflow Orchestration

## 1. Project Structure

- [ ] 1.1 Create `workflows/` module directory with `__init__.py`

## 2. Workflow Orchestration

- [ ] 2.1 Create `workflows/lyric_workflow.py` with `LyricWorkflow` class
- [ ] 2.2 Implement input builder (combine artists, songs, guidance)
- [ ] 2.3 Implement sequential pipeline execution (starting with template agent)
- [ ] 2.4 Add workflow state management (inputs, outputs, status)
- [ ] 2.5 Add error handling for agent failures

## 3. Streamlit UI Update

- [ ] 3.1 Replace chat interface with workflow form in `app.py`
- [ ] 3.2 Add Artist(s) text input field
- [ ] 3.3 Add Song(s) text input field
- [ ] 3.4 Add Other guidance text area
- [ ] 3.5 Add Generate button to trigger workflow
- [ ] 3.6 Add progress indicator during pipeline execution
- [ ] 3.7 Display blueprint output when complete

## 4. Cleanup

- [ ] 4.1 Remove chat-specific code from `app.py`
- [ ] 4.2 Remove or deprecate `agents/chat_agent.py`

## 5. Verification

- [ ] 5.1 Test workflow with artist input only
- [ ] 5.2 Test workflow with song input only
- [ ] 5.3 Test workflow with combined inputs
- [ ] 5.4 Test error handling when agent fails
- [ ] 5.5 Verify blueprint displays correctly
