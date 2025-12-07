# Change: Add Workflow Orchestration

## Why
The application needs a structured workflow to generate song lyrics by passing data through a pipeline of specialized agents. This proposal introduces orchestration infrastructure starting with the lyric-template agent and designed to accommodate future agents (lyric-writer, lyric-reviewer, song-arranger).

## What Changes
- Replace the chat interface with a workflow-focused landing page
- Add input fields: Artist(s), Song(s), and Other guidance
- Add a workflow orchestration system that runs agents sequentially
- Integrate the existing `LyricTemplateAgent` as the first step in the pipeline
- Store workflow state (inputs, intermediate outputs, final results) in session state
- Design the orchestration to be extensible for future agents

## Impact
- Affected specs: New `workflow-orchestration` capability, modify `streamlit-app`
- Affected code:
  - `workflows/` - New module for orchestration logic
  - `app.py` - Replace chat with workflow input form
  - Remove `agents/chat_agent.py` (no longer needed)
- **BREAKING**: Removes the chat interface in favor of workflow wizard
