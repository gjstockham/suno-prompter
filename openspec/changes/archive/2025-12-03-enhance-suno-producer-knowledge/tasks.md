# Tasks: Enhance Suno Producer Knowledge

## Task List

### 1. Update System Prompt with Comprehensive Meta-Tag Reference
- [x] Expand section tags to include full Suno tag vocabulary
- [x] Add pipe notation syntax documentation and examples
- [x] Add vocal meta-tags section with delivery options
- [x] Add dynamic/effect tags section
- [x] Add instrument solo tag format
- [x] Update style prompt guidelines for v3.5/v4.0 vs v4.5+
- [x] Add restricted terms warning

### 2. Restructure Prompt for Better Organization
- [x] Organize tags by category (structural, vocal, dynamic, etc.)
- [x] Add clear examples for each tag category
- [x] Include "when to use" guidance for advanced tags

### 3. Update Output Format
- [x] Add optional `style_prompt_extended` field for v4.5+ style
- [x] Document that standard `style_prompt` remains ≤200 chars

### 4. Validation
- [x] Manual test with sample lyrics requiring vocal technique tags
- [x] Manual test with lyrics needing dynamic transitions (build/drop)
- [x] Verify JSON output remains valid
- [x] Test pipe notation generation

## Dependencies

- None - tasks are sequential and self-contained

## Parallelization

Tasks 1.1-1.7 can be done together as a single prompt update. Task 2 is organizational refinement of Task 1. Task 3 is a minor output format change. Task 4 is validation after implementation.
