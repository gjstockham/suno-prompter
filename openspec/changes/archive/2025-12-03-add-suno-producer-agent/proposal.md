# Proposal: Add Suno Producer Agent

## Summary
Add a final "Producer" agent to the workflow that takes the accepted lyrics and user guidance to generate Suno-compatible outputs: a style prompt and a formatted lyric sheet with meta-tags.

## Motivation
Currently the workflow produces final lyrics but stops short of the actual Suno input format. Users must manually:
1. Write a style/genre prompt describing the music
2. Format lyrics with Suno meta-tags (`[Verse]`, `[Chorus]`, etc.)

Adding a Producer agent automates this final step, completing the end-to-end flow from reference songs to Suno-ready output.

## Scope

### In Scope
- New `SunoProducerAgent` that generates:
  - **Style Prompt**: Genre, mood, instruments, tempo, vocal style (text for Suno's style input)
  - **Lyric Sheet**: Lyrics formatted with Suno-compatible section tags
- UI section after "Final Lyrics" for user to provide production guidance
- Text area for user guidance (references to songs/artists for production style)
- Display of generated Suno outputs (style prompt + formatted lyrics)
- Copy-to-clipboard functionality for easy transfer to Suno

### Out of Scope
- Direct Suno API integration
- Audio preview/generation
- Advanced Suno features (custom mode, instrumental only, etc.)
- Iteration/review loop for producer output (single-pass for MVP)

## Outputs
- `agents/suno_producer_agent.py` - New agent implementation
- Updated `workflows/lyric_workflow.py` - Add producer step
- Updated `app.py` - UI for guidance input and Suno output display
- Spec delta for `suno-producer-agent` capability

## Dependencies
- Requires lyrics to be finalized (status="complete")
- Uses existing agent factory and workflow patterns
