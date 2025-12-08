# suno-producer-agent Specification

## Purpose
Generate Suno-compatible outputs from finalized lyrics, including a style prompt and formatted lyric sheet with meta-tags.

## ADDED Requirements

### Requirement: Suno Style Prompt Generation
The system SHALL generate a text prompt describing the musical style for Suno input.

#### Scenario: Generate style prompt from guidance
- **WHEN** the user provides production guidance (e.g., "upbeat like Taylor Swift's Shake It Off")
- **AND** clicks "Generate Suno Output"
- **THEN** the producer agent generates a style prompt
- **AND** the prompt describes genre, mood, instruments, tempo, and vocal style
- **AND** the prompt is concise (under 200 characters, Suno's typical limit)

#### Scenario: Generate style prompt without guidance
- **WHEN** the user provides no production guidance
- **AND** clicks "Generate Suno Output"
- **THEN** the producer agent infers style from the lyric template and lyrics
- **AND** generates a reasonable default style prompt

### Requirement: Suno Lyric Sheet Formatting
The system SHALL format lyrics with Suno-compatible section meta-tags.

#### Scenario: Format lyrics with section tags
- **WHEN** the producer agent receives finalized lyrics
- **THEN** it outputs lyrics with appropriate section tags
- **AND** tags include: `[Verse]`, `[Chorus]`, `[Bridge]`, `[Intro]`, `[Outro]`, `[Pre-Chorus]` as applicable
- **AND** section numbering is applied where appropriate (e.g., `[Verse 1]`, `[Verse 2]`)

#### Scenario: Preserve lyric content
- **WHEN** formatting lyrics with meta-tags
- **THEN** the actual lyric text is preserved unchanged
- **AND** only structural tags are added

### Requirement: Production Guidance Input
The system SHALL accept free-form text guidance for production style.

#### Scenario: Enter production guidance
- **WHEN** the user views the Final Lyrics section
- **THEN** a text area is displayed for production guidance
- **AND** placeholder text suggests referencing songs/artists
- **AND** the input is optional (can be left empty)

#### Scenario: Reference existing songs in guidance
- **WHEN** the user enters text like "similar to Billie Eilish's Bad Guy"
- **THEN** the guidance is passed to the producer agent
- **AND** the agent uses this reference to inform the style prompt

### Requirement: Suno Output Display
The system SHALL display generated Suno outputs in copyable panels.

#### Scenario: Display style prompt
- **WHEN** the producer agent completes
- **THEN** the style prompt is displayed in a labeled panel
- **AND** a copy button is available

#### Scenario: Display formatted lyrics
- **WHEN** the producer agent completes
- **THEN** the formatted lyric sheet is displayed in a labeled panel
- **AND** a copy button is available
- **AND** meta-tags are visually distinct (code formatting)

### Requirement: Producer Agent Execution
The system SHALL execute the producer agent as a single-pass step after lyrics are finalized.

#### Scenario: Trigger producer step
- **WHEN** lyrics status is "complete"
- **AND** user clicks "Generate Suno Output"
- **THEN** the producer agent runs once
- **AND** a progress indicator is shown during execution
- **AND** results are stored in workflow state

#### Scenario: Producer error handling
- **WHEN** the producer agent fails
- **THEN** an error message is displayed
- **AND** the user can retry with different guidance
- **AND** the finalized lyrics remain accessible
