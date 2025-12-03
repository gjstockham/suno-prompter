# Tasks: Add uvx Distribution Support

## Task List

### 1. Create Package Structure
- [ ] Create `src/suno_prompter/` directory
- [ ] Move `app.py` to `src/suno_prompter/app.py`
- [ ] Move `agents/` to `src/suno_prompter/agents/`
- [ ] Move `workflows/` to `src/suno_prompter/workflows/`
- [ ] Move `utils/` to `src/suno_prompter/utils/`
- [ ] Move `config.py` to `src/suno_prompter/config.py`
- [ ] Move `data/` to `src/suno_prompter/data/`
- [ ] Create `src/suno_prompter/__init__.py`

### 2. Create CLI Entry Point
- [ ] Create `src/suno_prompter/cli.py` with Streamlit launcher
- [ ] Create `src/suno_prompter/__main__.py` for `python -m suno_prompter`
- [ ] Handle package resource paths for data files

### 3. Create pyproject.toml
- [ ] Add project metadata (name, version, description, author)
- [ ] Add dependencies from requirements.txt
- [ ] Configure `[project.scripts]` entry point: `suno-prompter`
- [ ] Configure build system (hatchling or setuptools)
- [ ] Add package data includes for `data/` files

### 4. Add OpenAI-Compatible Provider Support
- [ ] Update `config.py` to use OpenAI env vars (`OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_CHAT_MODEL_ID`)
- [ ] Update `factory.py` to use `OpenAIChatClient` instead of `AzureOpenAIChatClient`
- [ ] Update `.env.example` with new env var names
- [ ] Support custom `base_url` for Ollama, LM Studio, etc.

### 5. Update Import Paths
- [ ] Update all relative imports in moved modules
- [ ] Update `app.py` imports to use package structure
- [ ] Update `config.py` to find `.env` in user's working directory
- [ ] Update data file loading to use `importlib.resources`

### 6. Test Locally
- [ ] Install package locally with `pip install -e .`
- [ ] Verify `suno-prompter` command launches the app
- [ ] Verify all agents work correctly
- [ ] Verify data files are accessible

### 7. Test uvx Distribution
- [ ] Test `uvx --from .` locally
- [ ] Push to GitHub and test `uvx --from git+https://github.com/gjstockham/suno-prompter suno-prompter`
- [ ] Document any required environment setup (API keys)

### 8. Update Documentation
- [ ] Update README with uvx installation instructions
- [ ] Add section for traditional pip/venv installation as alternative
- [ ] Document LLM configuration options (OpenAI, Ollama, etc.)

## Dependencies

- Task 2 depends on Task 1 (package structure must exist)
- Task 4 can be done independently (LLM provider change)
- Task 5 depends on Tasks 1-4 (imports update after move)
- Task 6 depends on Tasks 1-5
- Task 7 depends on Task 6
- Task 8 can be done in parallel with Task 7

## Parallelization

Tasks 1.1-1.8 can be done together. Tasks 3 and 4 can be started together after Task 1 completes. Task 8 can begin once the approach is validated in Task 6.
