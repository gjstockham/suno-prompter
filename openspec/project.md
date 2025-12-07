# Project Context

## Purpose
A Streamlit application that leverages the Microsoft Agent Framework to generate creative and detailed music prompts for Suno AI music generation. The app helps users create high-quality prompt descriptions that guide the AI music generator to produce specific musical styles, moods, and characteristics.

**Goals:**
- Provide an intuitive interface for music prompt engineering
- Use AI agents to intelligently suggest and refine prompts
- Support iterative prompt refinement
- Generate prompts optimized for Suno's input requirements

## Tech Stack
- **Runtime:** Python 3.10+
- **UI Framework:** Streamlit
- **AI Framework:** Microsoft Agent Framework (autogen or similar)
- **Dependencies:** TBD (will evolve as project develops)
- **Environment:** CLI-based, runs locally or in cloud environments

## Project Conventions

### Code Style
- **Language:** Python following [PEP 8](https://pep8.org/) conventions
- **Naming:** snake_case for functions/variables, PascalCase for classes
- **Formatting:** Use standard Python conventions (4-space indentation)
- **Imports:** Standard library, then third-party, then local imports (organized alphabetically within groups)
- **Docstrings:** Include module and function docstrings; use triple-quoted strings
- **Line Length:** 88 characters (common Python standard, compatible with Black formatter if adopted)

### Architecture Patterns
- **Agent-Based Architecture:** Leverage Microsoft Agent Framework for intelligent prompt generation and refinement
- **Streamlit UI:** Use Streamlit components for user interaction and session state management
- **Modular Design:** Separate agent logic, prompt templates, and UI components into distinct modules
- **Configuration:** Use environment variables or config files for external API keys and settings
- **No premature abstraction:** Keep implementations simple until concrete use cases require complexity

### Testing Strategy
- **Minimal testing focus:** Concentrate on critical agent functionality and prompt generation accuracy
- **Manual testing:** Leverage Streamlit's interactive reload for development
- **Integration points:** Test interactions with Microsoft Agent Framework and Suno API (if applicable)
- **Coverage goals:** Test happy paths for core agent workflows; skip edge cases unless discovered in development

### Git Workflow
- **Branching strategy:** Feature branches from `main`
- **Branch naming:** `feature/description` or `fix/description` (kebab-case)
- **Commit messages:** Clear, descriptive commit messages
- **Review:** Create pull requests for code review before merging to main
- **Merging:** Squash commits where logical; maintain clean history

## Domain Context
- **Suno Music Generation:** Suno is an AI music generation platform that takes text prompts and generates audio. Understanding prompt structure and effective keywords improves output quality.
- **Prompt Engineering:** The application focuses on helping users craft better prompts through AI-assisted suggestions and iteration
- **Agent Framework:** Microsoft's Agent Framework enables autonomous reasoning and tool use, ideal for refining and validating prompts
- **Music Theory Knowledge:** Basic familiarity with musical genres, moods, instruments, and styles is helpful for prompt suggestions

## Important Constraints
- **Local-first development:** Application should run locally without complex infrastructure
- **AI Model costs:** Be mindful of API costs when calling external AI services
- **Rate limiting:** Respect API rate limits for Suno and any external services
- **User privacy:** Avoid logging or storing user prompts without explicit consent
- **Scope:** Focus on prompt generation; not a music production or editing tool

## External Dependencies
- **Microsoft Agent Framework:** Core framework for building intelligent agents
- **Streamlit:** UI framework for the web application
- **Suno API:** May integrate with Suno's API for validation or direct generation (if available)
- **Python ecosystem:** Standard libraries and third-party packages (exact versions TBD)
