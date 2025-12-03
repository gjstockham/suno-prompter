# Proposal: Enhance Suno Producer Knowledge

## Summary

Enhance the Suno Producer Agent with comprehensive knowledge of Suno's meta-tag system based on community-documented reference materials. The current agent uses only 8 basic section tags, while Suno supports 50+ meta-tags across multiple categories including control directives, vocal styles, dynamics, tempo/rhythm, harmonics, and instrumentation.

## Problem Statement

The current `suno_producer_agent.py` has limited meta-tag knowledge:
- Only uses basic section tags: `[Intro]`, `[Verse]`, `[Chorus]`, `[Bridge]`, `[Outro]`, `[Instrumental]`, `[Break]`, `[Hook]`
- Style prompt guidance is generic (genre, mood, instruments, tempo, vocal style)
- No knowledge of pipe notation syntax for section-specific overrides
- No awareness of vocal technique tags, dynamic/effects tags, or advanced production tags
- Missing v4.5+ capabilities like hybrid genres and extended style prompts (1000 chars)

## Proposed Solution

### Option A: Embedded Knowledge (Recommended)

Enhance the producer agent's system prompt with comprehensive Suno meta-tag reference:

1. **Expand Section Tags** - Add full set including `[pre-chorus]`, `[drop]`, `[build]`, `[climax]`, `[breakdown]`, `[solo]`, `[interlude]`, `[end]`

2. **Add Pipe Notation Syntax** - Teach the agent to use section-specific overrides:
   ```
   [chorus | style: phonk hook, vocals: autotune-light, instruments: 808 bass]
   ```

3. **Add Vocal Meta-Tags** - Include vocal delivery options:
   - `[whisper]`, `[shout]`, `[spoken word]`, `[rap]`, `[ad-lib]`
   - `[male vocal]`, `[female vocal]`, `[duet]`, `[choir]`
   - `[background-vocals]`, `[harmonies]`

4. **Add Dynamic/Effect Tags** - Teach expression controls:
   - `[crescendo]`, `[decrescendo]`, `[sforzando]`
   - `[accelerando]`, `[ritardando]`
   - `[fade]`, `[silence]`

5. **Add Instrument Solo Tags** - Format `[X solo]` for featured instruments

6. **Update Style Prompt Guidelines** (v4.5+):
   - Support extended ≤1000 character style prompts for richer detail
   - Include restricted term warnings (avoid "kraftwerk", "skank", etc.)
   - Add hybrid genre syntax (Genre1 + Genre2)
   - Add advanced parameters like audio %, style %, weirdness %

### Option B: External Reference Tool

Create a tool the agent can call to look up tag documentation:
- Pros: Keeps prompt smaller, can be updated separately
- Cons: Adds latency, requires tool call overhead

**Recommendation**: Option A - Embedded knowledge is faster and more reliable for a bounded domain.

## Impact Analysis

### Files Modified
- `agents/suno_producer_agent.py` - Enhanced system prompt with comprehensive meta-tag reference

### Dependencies
- None - purely prompt enhancement

### Risk Assessment
- **Low risk**: No structural changes, backward compatible
- Only the agent's knowledge/behavior improves, not the code architecture

## Success Criteria

1. Producer agent correctly uses pipe notation for section-specific overrides
2. Style prompts leverage v4.5+ extended format (up to 1000 chars) with richer detail
3. Agent applies vocal technique tags when lyrics indicate delivery style
4. Agent uses dynamic tags for builds, drops, and emotional transitions
5. Hybrid genres and advanced parameters (audio %, style %, weirdness %) are properly formatted
6. Output remains valid JSON with properly escaped newlines

## Out of Scope

- New agents (e.g., separate "Suno Tag Advisor" agent)
- UI changes for tag selection
- Real-time Suno API validation
- Lyric writer/template agent changes
