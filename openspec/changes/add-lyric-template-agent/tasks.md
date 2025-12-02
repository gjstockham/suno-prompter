# Tasks: Add Lyric Template Agent

## 1. Implementation

- [x] 1.1 Create `agents/lyric_template_agent.py` with `LyricTemplateAgent` class
- [x] 1.2 Define system prompt for lyric analysis (structure, rhyme, imagery, etc.)
- [x] 1.3 Implement input parsing for song title, artist name, or song list
- [x] 1.4 Implement markdown blueprint output format
- [x] 1.5 Add web search/fetch capability for retrieving lyrics (if not in LLM knowledge)

## 2. Integration

- [x] 2.1 Export agent from `agents/__init__.py`
- [x] 2.2 Add basic error handling for failed lyric lookups

## 3. Verification

- [x] 3.1 Test agent with single song input
- [x] 3.2 Test agent with artist name input (analyze multiple songs)
- [x] 3.3 Test agent with explicit song list input
- [x] 3.4 Verify markdown blueprint contains all required analysis sections
