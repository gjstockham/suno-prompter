# lyric-reviewer-agent Specification

## Purpose
The lyric reviewer agent critiques generated lyrics against the style template and checks for potential plagiarism or quality issues.

## ADDED Requirements

### Requirement: Lyric Critique
The system SHALL evaluate generated lyrics for style adherence and quality.

#### Scenario: Critique lyrics against template
- **WHEN** lyrics are generated and a style template is available
- **THEN** the reviewer agent compares lyrics against template requirements
- **AND** reviewer provides feedback on rhyme schemes, meter, thematic consistency
- **AND** reviewer identifies any deviations from the template style

#### Scenario: Check for plagiarism concerns
- **WHEN** lyrics are reviewed
- **THEN** reviewer checks lyrics against its training knowledge of existing songs
- **AND** reviewer identifies any potentially plagiarized phrases or common clichés
- **AND** reviewer flags concerns as warnings (not blockers)
- **AND** reviewer suggests more original phrasing if needed
- **NOTE**: Plagiarism check is based on LLM training knowledge and may not be exhaustive

#### Scenario: Provide revision suggestions
- **WHEN** reviewer identifies issues
- **THEN** reviewer provides specific, actionable feedback for improvement
- **AND** feedback includes examples of better phrasing or structure
- **AND** feedback is constructive and references the style template

### Requirement: Satisfaction Assessment
The system SHALL determine whether reviewed lyrics meet quality standards.

#### Scenario: Evaluate reviewer satisfaction
- **WHEN** review is complete
- **THEN** reviewer provides a satisfaction assessment (satisfied/not satisfied)
- **AND** assessment is based on style adherence, originality, and quality
- **AND** if not satisfied, specific areas for improvement are identified

#### Scenario: Support iterative improvement
- **WHEN** reviewer is not satisfied
- **THEN** feedback is passed to writer for revision
- **AND** revised lyrics incorporate the reviewer's suggestions
- **AND** process repeats until satisfied or iteration limit reached

### Requirement: Feedback Formatting
The system SHALL structure reviewer output for clarity and UI display.

#### Scenario: Structure feedback output
- **WHEN** review is complete
- **THEN** feedback is returned in structured format with:
  - satisfied: boolean
  - style_feedback: string
  - plagiarism_concerns: string
  - revision_suggestions: string
- **AND** feedback is clear and actionable

