# Spec: uvx Distribution

## Purpose

Enable users to run the Suno Prompter application using `uvx` without pre-installing Python or manually managing dependencies.

## ADDED Requirements

### Requirement: CLI Entry Point

The application MUST provide a `suno-prompter` command that launches the Streamlit UI.

#### Scenario: Running via uvx from GitHub

**Given** user has `uv` installed
**And** user has configured API keys in `~/.suno-prompter/.env` or current directory `.env`
**When** user runs `uvx --from git+https://github.com/gjstockham/suno-prompter suno-prompter`
**Then** the Streamlit application launches in the default browser
**And** all agent functionality works correctly

#### Scenario: Running via python -m

**Given** the package is installed
**When** user runs `python -m suno_prompter`
**Then** the Streamlit application launches

### Requirement: Package Structure

The project MUST use a `src/` layout with proper Python packaging.

#### Scenario: Package is installable

**Given** user has Python 3.10+
**When** user runs `pip install .` from the project root
**Then** the `suno-prompter` package is installed
**And** the `suno-prompter` command is available in PATH

### Requirement: Environment Configuration

The CLI MUST read API credentials from environment files in predictable locations.

#### Scenario: Load .env from current directory

**Given** a `.env` file exists in the current working directory
**When** user runs `suno-prompter`
**Then** environment variables are loaded from that `.env` file

#### Scenario: Load .env from home directory

**Given** no `.env` file exists in current directory
**And** a `.env` file exists at `~/.suno-prompter/.env`
**When** user runs `suno-prompter`
**Then** environment variables are loaded from the home directory location

#### Scenario: Missing API keys

**Given** no `.env` file is found
**And** required environment variables are not set
**When** user runs `suno-prompter`
**Then** the application displays a clear error message about missing configuration

### Requirement: Package Data Access

Data files bundled with the package MUST be accessible at runtime.

#### Scenario: Starter ideas are available

**Given** the application is running via uvx
**When** the lyric template agent needs starter ideas
**Then** it can read from `data/starter_ideas.txt` bundled in the package

### Requirement: OpenAI-Compatible LLM Provider

The application MUST support any OpenAI-compatible API endpoint.

#### Scenario: Using OpenAI API directly

**Given** user has set `OPENAI_API_KEY` and `OPENAI_CHAT_MODEL_ID` in `.env`
**When** user runs `suno-prompter`
**Then** the application connects to the OpenAI API

#### Scenario: Using custom endpoint (Ollama, LM Studio)

**Given** user has set `OPENAI_BASE_URL=http://localhost:11434/v1`
**And** user has set `OPENAI_CHAT_MODEL_ID=llama3`
**When** user runs `suno-prompter`
**Then** the application connects to the custom endpoint

#### Scenario: Missing LLM configuration

**Given** `OPENAI_API_KEY` is not set
**And** `OPENAI_BASE_URL` is not set
**When** user runs `suno-prompter`
**Then** the application displays a clear error about missing LLM configuration

## Notes

- The package is distributed via GitHub only (not PyPI)
- Users must install `uv` separately (single curl command)
- Traditional `pip install` workflow remains supported
