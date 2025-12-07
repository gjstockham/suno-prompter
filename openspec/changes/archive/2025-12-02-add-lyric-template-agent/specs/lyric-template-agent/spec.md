## ADDED Requirements

### Requirement: Lyric Template Agent Input
The system SHALL accept song references as input for lyric analysis.

#### Scenario: Single song input
- **WHEN** the user provides a single song title (optionally with artist)
- **THEN** the agent identifies and analyzes that song's lyrics
- **AND** uses LLM knowledge or web search to retrieve lyrics if needed

#### Scenario: Artist input
- **WHEN** the user provides an artist name without specific songs
- **THEN** the agent selects representative songs from that artist
- **AND** analyzes multiple songs to identify common patterns

#### Scenario: Song list input
- **WHEN** the user provides a list of multiple songs
- **THEN** the agent analyzes all specified songs
- **AND** synthesizes patterns across the collection

### Requirement: Lyric Structure Analysis
The system SHALL analyze and document the structural elements of lyrics.

#### Scenario: Song structure identification
- **WHEN** the agent analyzes a song
- **THEN** the blueprint identifies sections (verse, chorus, bridge, pre-chorus, outro, etc.)
- **AND** documents the arrangement pattern (e.g., Verse-Chorus-Verse-Chorus-Bridge-Chorus)
- **AND** notes section lengths and repetition patterns

#### Scenario: Rhyme scheme analysis
- **WHEN** the agent analyzes lyrics
- **THEN** the blueprint documents rhyme schemes per section (e.g., AABB, ABAB, ABCB)
- **AND** identifies internal rhymes and near-rhymes
- **AND** notes rhyme density and consistency

#### Scenario: Meter and syllable patterns
- **WHEN** the agent analyzes lyrics
- **THEN** the blueprint documents syllable counts per line
- **AND** identifies rhythmic patterns and stressed syllables
- **AND** notes how meter varies between sections

### Requirement: Lyric Content Analysis
The system SHALL analyze thematic and literary elements of lyrics.

#### Scenario: Theme and imagery analysis
- **WHEN** the agent analyzes lyrics
- **THEN** the blueprint identifies central themes and motifs
- **AND** documents imagery patterns (visual, auditory, tactile, etc.)
- **AND** catalogs recurring symbols and metaphors

#### Scenario: Emotional tone analysis
- **WHEN** the agent analyzes lyrics
- **THEN** the blueprint describes the emotional arc of the song
- **AND** notes tone shifts between sections
- **AND** identifies how word choice supports emotional intent

#### Scenario: Literary device identification
- **WHEN** the agent analyzes lyrics
- **THEN** the blueprint catalogs literary devices used (alliteration, assonance, personification, etc.)
- **AND** notes word choice patterns (simple vs. complex, concrete vs. abstract)
- **AND** documents narrative perspective and voice

### Requirement: Blueprint Output Format
The system SHALL produce a structured markdown document as output.

#### Scenario: Markdown blueprint generation
- **WHEN** analysis is complete
- **THEN** the agent produces a markdown document with clear sections
- **AND** the document includes: Overview, Structure Analysis, Rhyme/Meter Patterns, Themes/Imagery, Literary Devices, and Summary
- **AND** the format is human-readable and suitable for downstream agent consumption

#### Scenario: Multi-song blueprint synthesis
- **WHEN** multiple songs are analyzed
- **THEN** the blueprint synthesizes common patterns across songs
- **AND** notes variations and distinguishing characteristics
- **AND** provides a unified template reflecting the collection's style
