# suno-meta-tag-knowledge Specification

## Purpose
TBD - created by archiving change enhance-suno-producer-knowledge. Update Purpose after archive.
## Requirements
### Requirement: Structural Meta-Tag Knowledge

The producer agent MUST know and correctly apply all Suno structural meta-tags to organize song sections.

#### Scenario: Basic section tag application
- **Given** lyrics with verse and chorus structure
- **When** the producer agent formats the lyrics
- **Then** it applies appropriate section tags: `[intro]`, `[verse]`, `[pre-chorus]`, `[chorus]`, `[bridge]`, `[interlude]`, `[break]`, `[outro]`, `[end]`

#### Scenario: Dynamic section tag application
- **Given** lyrics that build toward a climax or drop
- **When** the producer agent identifies energy transitions
- **Then** it applies dynamic tags: `[build]`, `[drop]`, `[climax]`, `[breakdown]`

#### Scenario: Instrumental section marking
- **Given** lyrics with indicated instrumental breaks
- **When** the producer agent formats those sections
- **Then** it applies `[solo]` or `[instrumental]` tags as appropriate

---

### Requirement: Pipe Notation Syntax

The producer agent MUST understand and apply pipe notation for section-specific overrides when production guidance indicates section-specific requirements.

#### Scenario: Section-specific style override
- **Given** a chorus that should have different characteristics than verses
- **When** the producer agent formats the chorus
- **Then** it may use pipe notation: `[chorus | style: hook, vocals: powerful]`

#### Scenario: Instrument specification per section
- **Given** production guidance requesting specific instruments in specific sections
- **When** the producer formats those sections
- **Then** it applies pipe notation with instrument overrides: `[bridge | instruments: piano only]`

---

### Requirement: Vocal Meta-Tag Knowledge

The producer agent MUST know and apply vocal delivery meta-tags to specify how lyrics should be performed.

#### Scenario: Vocal delivery style
- **Given** lyrics indicating whispered, shouted, or spoken delivery
- **When** the producer formats those lines
- **Then** it applies appropriate tags: `[whisper]`, `[shout]`, `[spoken word]`, `[rap]`

#### Scenario: Vocal arrangement
- **Given** lyrics with harmonies or multiple voices
- **When** the producer formats those sections
- **Then** it applies arrangement tags: `[duet]`, `[choir]`, `[background-vocals]`, `[harmonies]`

#### Scenario: Gender-specific vocals
- **Given** production guidance specifying vocal gender
- **When** the producer generates the style prompt and lyric sheet
- **Then** it applies `[male vocal]` or `[female vocal]` tags appropriately

---

### Requirement: Dynamic and Effect Meta-Tags

The producer agent MUST know and apply dynamic/effect meta-tags to control musical expression and energy.

#### Scenario: Volume dynamics
- **Given** lyrics with indicated crescendos or quiet sections
- **When** the producer formats those sections
- **Then** it applies dynamic tags: `[crescendo]`, `[decrescendo]`, `[sforzando]`, `[fade]`

#### Scenario: Tempo dynamics
- **Given** lyrics indicating tempo changes
- **When** the producer formats those sections
- **Then** it applies tempo tags: `[accelerando]`, `[ritardando]`

#### Scenario: Silence and space
- **Given** lyrics with dramatic pauses
- **When** the producer formats those moments
- **Then** it may apply `[silence]` or `[break]` tags

---

### Requirement: Style Prompt Generation (v4.5+)

The producer agent MUST generate style prompts optimized for Suno v4.5+ with extended formatting capabilities.

#### Scenario: Extended style prompt formatting
- **Given** production guidance and lyrics
- **When** the producer generates a style prompt
- **Then** the `style_prompt` field uses up to 1000 characters with detailed genre, mood, instruments, tempo, vocal style, and production parameters

#### Scenario: Hybrid genre specification
- **Given** production guidance requesting genre fusion
- **When** the producer generates the style prompt
- **Then** it uses hybrid syntax: "Genre1 + Genre2" (e.g., "jazz + hip-hop")

#### Scenario: Advanced production parameters
- **Given** production guidance with specific creative direction
- **When** the producer generates the style prompt
- **Then** it may include advanced parameters like "audio 45%, style 50%, weirdness 55%" for fine-tuned creative output

#### Scenario: Restricted term avoidance
- **Given** style requirements that might use restricted terms
- **When** the producer generates style prompts
- **Then** it avoids restricted terms like "kraftwerk" (use "krautrock" instead) and "skank" (use "ska stroke" instead)

---

