# lyric-writer-agent Specification

## Purpose
The lyric writer agent generates original lyrics based on a style template and user-provided song idea.

## ADDED Requirements

### Requirement: Lyric Generation
The system SHALL generate complete lyrics using a style template and song idea as input.

#### Scenario: Generate lyrics from template and idea
- **WHEN** the user provides a song idea/title and a style template is available
- **THEN** the lyric writer agent generates lyrics matching the template style
- **AND** lyrics include all sections from the template (verse, chorus, bridge, etc.)
- **AND** lyrics are original and incorporate the user's song idea/theme

#### Scenario: Handle missing ideas gracefully
- **WHEN** the user declines to provide an idea
- **THEN** a random idea is selected from starter ideas
- **AND** the writer agent uses this idea to generate lyrics

### Requirement: Agent Configuration
The system SHALL configure the lyric writer agent with appropriate system instructions and tools.

#### Scenario: Initialize writer agent
- **WHEN** the workflow starts
- **THEN** the lyric writer agent is instantiated with system instructions
- **AND** instructions emphasize style adherence and originality
- **AND** the agent has access to the style template context

### Requirement: Output Validation
The system SHALL ensure generated lyrics meet basic quality thresholds.

#### Scenario: Validate lyrics structure
- **WHEN** lyrics are generated
- **THEN** output includes identifiable sections (verses, chorus, etc.)
- **AND** lyrics meet minimum length requirements
- **AND** lyrics are formatted for readability (line breaks, stanzas)

