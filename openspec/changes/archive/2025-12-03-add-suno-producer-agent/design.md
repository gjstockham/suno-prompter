# Design: Add Suno Producer Agent

## Context
The application currently generates lyrics through a Template → Writer → Reviewer pipeline. The final step should format these lyrics for Suno's input requirements.

## Architecture Decisions

### Decision: Single Producer Agent (Not Writer + Formatter Split)
Use one agent that handles both style prompt generation and lyric formatting.

**Rationale**:
- Both outputs derive from the same context (lyrics + guidance)
- Keeps workflow simple with one additional step
- Style and structure are interrelated (e.g., genre affects section structure)

**Alternatives Considered**:
- Separate StyleAgent + FormatterAgent: Adds complexity without clear benefit
- Pure templating (no LLM): Loses intelligence for genre-appropriate styling

### Decision: User Guidance via Text Area (Not Structured Form)
Collect production guidance as free-form text rather than dropdowns/selectors.

**Rationale**:
- Suno prompts work best as natural language descriptions
- Users can reference specific songs/artists for production style
- More flexible than predefined genre lists
- Matches the "chat box" concept from requirements

**Alternatives Considered**:
- Structured form with genre/mood/tempo dropdowns: Too restrictive
- No guidance input: Loses user control over production style

### Decision: Suno Meta-Tag Format
Use standard Suno section tags for the lyric sheet output.

**Known Suno Tags**:
- `[Intro]` - Instrumental introduction
- `[Verse]`, `[Verse 1]`, `[Verse 2]` - Verse sections
- `[Pre-Chorus]` - Pre-chorus section
- `[Chorus]` - Chorus section
- `[Bridge]` - Bridge section
- `[Outro]` - Ending section
- `[Instrumental]`, `[Break]` - Non-vocal sections
- `[Hook]` - Catchy repeated phrase

**Rationale**:
- These tags are recognized by Suno's lyric parser
- Help Suno understand song structure for generation
- Producer agent will map existing lyric sections to these tags

### Decision: Single-Pass Generation (No Iteration Loop)
Producer runs once without a reviewer loop.

**Rationale**:
- Style prompts and formatting are more deterministic than lyric writing
- User can easily tweak the text output manually
- Reduces workflow complexity
- Can add iteration later if needed

**Alternatives Considered**:
- Producer + Producer-Reviewer loop: Over-engineering for formatting task

## Data Flow

```
[Final Lyrics] + [User Guidance]
        ↓
  SunoProducerAgent
        ↓
┌───────────────────────────────────────┐
│ Output:                               │
│ - style_prompt: str                   │
│ - lyric_sheet: str (with meta-tags)   │
└───────────────────────────────────────┘
```

## UI Flow

1. After user clicks "Accept & Finalize" and sees Final Lyrics
2. New section appears: "Create Suno Output"
3. Text area for production guidance (placeholder: "Describe the sound you want, reference songs/artists...")
4. "Generate Suno Output" button
5. Display:
   - **Style Prompt** panel (copyable)
   - **Formatted Lyrics** panel (copyable)
6. Copy buttons for easy transfer to Suno

## Agent Prompt Strategy

The Producer agent will receive:
- The finalized lyrics
- The original template (for style context)
- User's production guidance

It will output structured JSON:
```json
{
  "style_prompt": "Upbeat indie pop, acoustic guitar, female vocals...",
  "lyric_sheet": "[Verse 1]\nLyrics here...\n\n[Chorus]\nMore lyrics..."
}
```
