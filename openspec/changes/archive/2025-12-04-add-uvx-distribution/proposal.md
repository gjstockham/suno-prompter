# Proposal: Add uvx Distribution Support

## Why

Currently, users must manually clone the repository, create a virtual environment, install dependencies, and run `streamlit run app.py`. This requires Python knowledge and multiple steps.

With `uvx` (from the [uv package manager](https://docs.astral.sh/uv/)), users can run the app with a single command without having Python pre-installed. The `uv` tool automatically downloads and manages Python versions as needed.

**Target user experience:**
```bash
# Install uv (one-time, no Python needed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Run the app directly from GitHub
uvx --from git+https://github.com/gjstockham/suno-prompter suno-prompter
```

## What Changes

### 1. Package Structure
Convert the project to a proper Python package with `src/` layout:
- Move application code to `src/suno_prompter/`
- Create CLI entry point that launches Streamlit

### 2. pyproject.toml
Add modern Python packaging configuration:
- Project metadata (name, version, description)
- Dependencies (migrated from requirements.txt)
- Entry point: `suno-prompter` command
- Build system configuration

### 3. CLI Entry Point
Create `src/suno_prompter/__main__.py` and `cli.py`:
- Launches Streamlit programmatically
- Handles the app.py script location within the package

### 4. OpenAI-Compatible Provider Support
Switch from Azure-only to any OpenAI-compatible endpoint:
- Support standard OpenAI API
- Support custom endpoints (Ollama, LM Studio, etc.) via `OPENAI_BASE_URL`
- Use `OpenAIChatClient` from agent-framework instead of Azure-specific client

### 5. Documentation
Update README with uvx installation instructions and LLM configuration

## Out of Scope

- PyPI publishing (GitHub-only distribution for now)
- Docker containerization
- Binary distribution (PyInstaller, etc.)

## Risks

- **Package data handling**: Data files (starter_ideas.txt) need to be included in package
- **Path resolution**: App must find resources relative to package, not working directory
- **Environment variables**: Users still need to configure `.env` with LLM credentials
- **Breaking change**: Azure OpenAI env vars replaced with OpenAI-compatible vars

## References

- [uv Tools Documentation](https://docs.astral.sh/uv/guides/tools/)
- [uv Package Publishing](https://github.com/astral-sh/uv/blob/main/docs/guides/package.md)
