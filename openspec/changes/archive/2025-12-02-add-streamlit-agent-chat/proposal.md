# Change: Add Streamlit App with Microsoft Agent Framework Chat

## Why
The project requires a foundational web interface for users to interact with AI agents that generate Suno music prompts. Building this base capability first enables all future prompt generation and refinement features. By establishing the Streamlit UI and agent chat infrastructure now, we create a solid foundation for iterative development of prompt engineering workflows.

## What Changes
- Scaffolds the main Streamlit application with project structure
- Integrates Microsoft Agent Framework for AI agent capabilities
- Implements a basic chat interface for user-agent interaction
- Establishes configuration management for API keys and settings
- Sets up session state handling for multi-turn conversations

## Impact
**Affected specs:**
- New: `streamlit-app` - Streamlit UI and application structure

**Affected code:**
- `app.py` - Main Streamlit application entry point
- `config.py` - Configuration and environment management
- `agents/` - Agent definitions and utilities
- `requirements.txt` - Project dependencies

**Scope:**
- No breaking changes (new capability)
- Establishes architecture pattern for future features
- Creates minimal but complete MVP
