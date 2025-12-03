# Change: Generate and Review Lyrics with Human-in-Loop Iteration

## Why
The current workflow generates style templates but doesn't leverage them to produce actual lyrics. To complete the creative pipeline, we need:
1. A lyric writer agent that uses the template to generate lyrics based on a user-provided (or randomly-generated) song idea
2. A lyric reviewer agent that critiques lyrics against the style template and checks for plagiarism
3. An iterative loop where the writer improves lyrics based on reviewer feedback
4. A human-in-loop pause after template generation to gather song ideas before proceeding

This creates an interactive, quality-assured workflow that allows users to refine lyrics until satisfied.

## What Changes
- **New agents**: `LyricWriterAgent` and `LyricReviewerAgent` using Agent Framework's ChatAgent
  - Reviewer uses LLM knowledge for plagiarism/cliché detection (no external tools needed)
- **New capability**: Starter ideas file (`data/starter_ideas.txt`) with 10 song topic ideas
- **New utility**: `pick_random_idea()` function to select a random starter idea if user has none
- **Workflow changes**: Extend `LyricWorkflow` to orchestrate writer → reviewer loop
- **UI changes**: Add human-in-loop step after template generation to collect song ideas, then loop on feedback until reviewer satisfied
- **Session state**: Track reviewer feedback cycles and final lyrics

## Impact
- Affected specs: `workflow-orchestration` (MODIFIED), `streamlit-app` (MODIFIED), `lyric-writer-agent` (NEW), `lyric-reviewer-agent` (NEW)
- Affected code:
  - `agents/lyric_writer_agent.py` - NEW agent for lyric generation
  - `agents/lyric_reviewer_agent.py` - NEW agent for lyric critique
  - `data/starter_ideas.txt` - NEW data file
  - `workflows/lyric_workflow.py` - Extended for writer → reviewer orchestration
  - `app.py` - New UI for idea collection and feedback loop

## User Experience
1. User enters artists/songs/guidance → Template generated (current flow)
2. **[NEW]** UI shows template, asks: "Do you have a song idea/title in mind?"
   - If yes: User enters idea
   - If no: System picks random idea from starter ideas
3. **[NEW]** Lyric writer generates lyrics based on template + idea
4. **[NEW]** Lyric reviewer critiques lyrics (style adherence, plagiarism check)
5. **[NEW]** If satisfied: Display final lyrics
   - If not satisfied: Ask writer to revise, loop to step 4
6. User can export/save final lyrics

## Questions for Clarification
1. Should we cap the number of review iterations (e.g., max 3 revisions)?
2. Should the reviewer output be shown to the user, or only displayed if user requests feedback details?
3. Should we log/persist feedback iterations, or just show the final result?
4. Do you want the starter ideas in a file, database, or hardcoded in the agent?

