# Change: Add Lyric Template Agent

## Why
Users need a way to analyze existing songs to create a "lyric blueprint" that captures the structural and stylistic patterns of reference material. This blueprint will guide downstream lyric generation agents to produce lyrics that match the desired style.

## What Changes
- Add a new `LyricTemplateAgent` that accepts song titles, artist names, or song lists as input
- Agent uses LLM knowledge and web search/fetch to retrieve and analyze lyrics
- Agent produces a comprehensive markdown blueprint analyzing:
  - Song structure (verse, chorus, bridge, etc.)
  - Rhyme schemes and patterns
  - Syllable/meter patterns
  - Themes, metaphors, and imagery
  - Emotional tone and narrative arc
  - Literary devices and word choice patterns
- New agent module in `agents/` directory following existing patterns

## Impact
- Affected specs: New `lyric-template-agent` capability
- Affected code: `agents/lyric_template_agent.py` (new file)
- Dependencies: May require web search capability (to be determined during implementation)
